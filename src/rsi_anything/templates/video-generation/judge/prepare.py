"""Call the public Gradio video service; save the event id and reuse the finished video for identical requests."""
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_ENDPOINT = 'https://lightricks-ltx-video-distilled.hf.space'
API_NAME = 'text_to_video'
INPUT_LABELS = ['Prompt','Negative Prompt','image_n','video_n','Height','Width','task',
                'Video Duration (seconds)','Frames to use from input video','Seed',
                'Randomize Seed','Guidance Scale (CFG)','Improve Texture (multi-scale)']


def now():
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path, data):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    temp.replace(path)


def url_ok(url):
    parsed=urllib.parse.urlsplit(url)
    if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('service and video URLs must be HTTP(S) addresses without embedded credentials')
    return url


def payload(config):
    if not isinstance(config,dict) or set(config)!={'prompt','negative','seed'}:
        raise ValueError('generation.json may only contain prompt, negative and seed')
    if not isinstance(config['prompt'],str) or not 10<=len(config['prompt'].strip())<=3500:
        raise ValueError('prompt must be a description of 10 to 3500 characters')
    if not isinstance(config['negative'],str) or len(config['negative'])>1500:
        raise ValueError('negative must be text of at most 1500 characters')
    seed=config['seed']
    if not isinstance(seed,int) or isinstance(seed,bool) or not 0<=seed<=4294967295:
        raise ValueError('seed must be an integer from 0 to 4294967295')
    return {'data':[config['prompt'],config['negative'],None,None,512,704,'text-to-video',2,9,seed,False,1,False]}


def cache_root():
    custom=os.environ.get('RSI_VIDEO_CACHE')
    if custom:
        return Path(custom).expanduser().resolve()
    return Path(os.environ.get('XDG_CACHE_HOME',str(Path.home()/'.cache'))).expanduser()/'rsi-anything'/'video-generation'


@contextmanager
def cache_lock(folder):
    """The OS releases the lock when the process exits, so a timed-out run never leaves it held for good."""
    handle=(folder/'request.lock').open('a+b')
    try:
        if os.name=='nt':
            import msvcrt
            handle.seek(0); handle.write(b'0'); handle.flush(); handle.seek(0)
            msvcrt.locking(handle.fileno(),msvcrt.LK_NBLCK,1)
        else:
            import fcntl
            fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except OSError as exc:
        handle.close()
        raise RuntimeError('the same video request is already running; wait for it to finish and retry') from exc
    try:
        yield
    finally:
        handle.close()


def request_json(url, body=None, timeout=30):
    data=json.dumps(body).encode('utf-8') if body is not None else None
    req=urllib.request.Request(url,data=data,headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=timeout) as response:
        return json.loads(response.read().decode('utf-8'))


def verify_service(endpoint):
    config=request_json(endpoint+'/config')
    components={item['id']:item for item in config['components']}
    dep=next((d for d in config['dependencies'] if d.get('api_name')==API_NAME),None)
    if dep is None:
        raise RuntimeError('the service has no text_to_video endpoint; nothing was submitted')
    labels=[components[i].get('props',{}).get('label') for i in dep['inputs']]
    if labels!=INPUT_LABELS:
        raise RuntimeError('the service input order has changed; update the adapter first to avoid a wrong submission')
    return {'gradio_version':config.get('version'),'input_labels':labels,
            'declared_model':'LTX 0.9.8 13B distilled (as publicly stated upstream)','checked_at':now()}


def sse_events(lines):
    """Parse a Gradio event stream, handling heartbeats, CRLF and multi-line data fields."""
    event, parts = '', []
    for raw in lines:
        line=raw.decode('utf-8') if isinstance(raw,bytes) else raw
        line=line.rstrip('\r\n')
        if not line:
            if event or parts:
                yield event or 'message','\n'.join(parts)
            event,parts='',[]
        elif line.startswith('event:'):
            event=line[6:].strip()
        elif line.startswith('data:'):
            parts.append(line[5:].lstrip())
    if event or parts:
        yield event or 'message','\n'.join(parts)


def wait_result(endpoint,event_id,log_path,timeout):
    url=endpoint+'/gradio_api/call/'+API_NAME+'/'+urllib.parse.quote(event_id,safe='')
    started=time.monotonic()
    with urllib.request.urlopen(url,timeout=timeout) as response, log_path.open('a',encoding='utf-8') as log:
        for event,data in sse_events(response):
            log.write('event: '+event+'\ndata: '+data+'\n\n'); log.flush()
            if event=='complete':
                value=json.loads(data)
                item=value[0]['video']
                return {'video_url':url_ok(item['url']),'returned_seed':value[1] if len(value)>1 else None,'complete_event':value}
            if event=='error':
                raise RuntimeError('the video service returned an error: '+data[:600])
            if time.monotonic()-started>timeout:
                raise TimeoutError('timed out waiting for the generation result; the event id is saved and waiting can resume')
    raise RuntimeError('the event stream ended without a completed result; the event id is saved and waiting can resume')


def download_video(url,destination):
    part=destination.with_suffix('.part')
    total=0
    with urllib.request.urlopen(url,timeout=120) as response, part.open('wb') as stream:
        while True:
            block=response.read(1024*1024)
            if not block:
                break
            total+=len(block)
            if total>128*1024*1024:
                raise RuntimeError('the returned file exceeds 128 MiB; this example stops the download')
            stream.write(block)
    if total==0:
        raise RuntimeError('the returned video is empty')
    part.replace(destination)


def probe_video(path):
    result=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,width,height,codec_name',
                           '-of','json',str(path)],capture_output=True,text=True,timeout=30)
    if result.returncode:
        raise RuntimeError('ffprobe cannot read the service video: '+result.stderr[-400:])
    data=json.loads(result.stdout)
    videos=[s for s in data.get('streams',[]) if s.get('codec_type')=='video']
    if not videos:
        raise RuntimeError('the service file has no video stream')
    duration=float(data.get('format',{}).get('duration',0))
    stream=videos[0]
    if not 1<=duration<=3.5 or stream.get('width')!=704 or stream.get('height')!=512:
        raise RuntimeError('the returned video duration or size does not match this example')
    return {'duration_seconds':duration,'width':stream['width'],'height':stream['height'],
            'codec':stream.get('codec_name'),'has_audio':any(s.get('codec_type')=='audio' for s in data['streams'])}


def generate(endpoint,body,folder,timeout=480):
    folder.mkdir(parents=True,exist_ok=True)
    with cache_lock(folder):
        state_file=folder/'state.json'
        state=json.loads(state_file.read_text()) if state_file.exists() else {}
        cached=folder/'video.mp4'
        if cached.exists() and state.get('status')=='ready':
            digest=hashlib.sha256(cached.read_bytes()).hexdigest()
            if digest!=state.get('video_sha256'):
                raise RuntimeError('Cached video checksum mismatch; the request record is kept, inspect the cache before continuing')
            return cached,state,True
        if not state:
            service=verify_service(endpoint)
            state={'status':'submission_pending','endpoint':endpoint,'api_name':API_NAME,'request':body,
                   'service':service,'started_at':now()}
            atomic_json(state_file,state)
            try:
                receipt=request_json(endpoint+'/gradio_api/call/'+API_NAME,body)
                event_id=receipt['event_id']
                if not isinstance(event_id,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}',event_id):
                    raise ValueError('the generation service did not return a valid event id')
            except Exception as exc:
                state.update(status='submission_unknown',error=str(exc),updated_at=now())
                atomic_json(state_file,state)
                raise RuntimeError('the submission outcome is unknown and was not resent automatically; check the submission record in the cache first') from exc
            state.update(status='submitted',event_id=event_id,submit_response=receipt,updated_at=now())
            atomic_json(state_file,state)
        elif not state.get('event_id'):
            raise RuntimeError('the last submission outcome is unknown, so automatic regeneration is blocked; confirm the service state by hand, then deal with this cache record')
        if state.get('request')!=body or state.get('endpoint')!=endpoint:
            raise RuntimeError('the cached request does not match the current input')
        if not state.get('video_url'):
            completed=wait_result(endpoint,state['event_id'],folder/'events.txt',timeout)
            state.update(completed,status='complete',updated_at=now())
            atomic_json(state_file,state)
        if not cached.exists():
            download_video(state['video_url'],cached)
        probe=probe_video(cached)
        state.update(status='ready',video_sha256=hashlib.sha256(cached.read_bytes()).hexdigest(),
                     video_bytes=cached.stat().st_size,probe=probe,finished_at=now())
        atomic_json(state_file,state)
        return cached,state,False


def main():
    out=Path('out'); out.mkdir(exist_ok=True)
    for filename in ('video.mp4','preview.html','metadata.json','error.json','request.json','events.txt'):
        (out/filename).unlink(missing_ok=True)
    folder=None
    try:
        if not shutil.which('ffprobe') or not shutil.which('ffmpeg'):
            raise RuntimeError('ffmpeg and ffprobe are required; nothing was submitted')
        config=json.loads(Path('generation.json').read_text(encoding='utf-8'))
        body=payload(config)
        endpoint=url_ok(os.environ.get('RSI_VIDEO_ENDPOINT',DEFAULT_ENDPOINT).rstrip('/'))
        identity={'adapter_version':1,'endpoint':endpoint,'api_name':API_NAME,'request':body}
        key=hashlib.sha256(json.dumps(identity,sort_keys=True,ensure_ascii=False).encode('utf-8')).hexdigest()
        folder=cache_root()/key
        atomic_json(out/'request.json',identity)
        video,state,reused=generate(endpoint,body,folder,int(os.environ.get('RSI_VIDEO_TIMEOUT','480')))
        shutil.copyfile(video,out/'video.mp4')
        probe=probe_video(out/'video.mp4')
        receipt={**state,'cache_key':key,'cache_reused':reused,'probe':probe}
        atomic_json(out/'metadata.json',receipt)
        if (folder/'events.txt').exists():
            shutil.copyfile(folder/'events.txt',out/'events.txt')
        atomic_json(out/'gates.json',{'real_service_result_obtained':True,'video_readable_with_expected_size_and_duration':True})
        (out/'notes.txt').write_text(f"Real generation event {state['event_id']}; {probe['duration_seconds']:.2f} s, 704×512; reused cache for identical request={reused}. The jury sees only sampled frames; sound and full motion still need to be checked by playing the video.",encoding='utf-8')
        page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Generated short video</title><style>body{max-width:900px;margin:40px auto;padding:20px;font:17px/1.7 system-ui;background:#f8f4ee}video{width:100%;background:#222}pre{white-space:pre-wrap}</style><h1>Ceramic mug in morning light</h1><video controls preload="metadata" src="video.mp4"></video><h2>Prompt for this generation</h2><pre>'+html.escape(config['prompt'])+'</pre><p>Actual event: '+html.escape(state['event_id'])+'; the evaluation covers only visible still frames, so play the video to check full motion.</p></html>'
        (out/'preview.html').write_text(page,encoding='utf-8')
        return 0
    except Exception as exc:
        error={'stage':'video_generation','error':str(exc),'time':now(),'quality_result':'unknown'}
        if folder is not None and (folder/'state.json').exists():
            error['request_state']=json.loads((folder/'state.json').read_text())
        atomic_json(out/'error.json',error)
        atomic_json(out/'gates.json',{'real_service_result_obtained':False})
        (out/'notes.txt').write_text('The video service or environment did not finish, so the quality of the work is unknown: '+str(exc),encoding='utf-8')
        print(str(exc),file=sys.stderr)
        return 2


if __name__=='__main__':
    sys.exit(main())
