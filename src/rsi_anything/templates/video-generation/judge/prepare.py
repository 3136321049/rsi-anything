"""调用公开 Gradio 视频服务；保存事件编号并复用相同请求的成片。"""
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
        raise ValueError('服务与视频URL必须是无内嵌凭据的HTTP(S)地址')
    return url


def payload(config):
    if not isinstance(config,dict) or set(config)!={'prompt','negative','seed'}:
        raise ValueError('generation.json只能包含prompt、negative和seed')
    if not isinstance(config['prompt'],str) or not 10<=len(config['prompt'].strip())<=3500:
        raise ValueError('prompt需为10至3500字的描述')
    if not isinstance(config['negative'],str) or len(config['negative'])>1500:
        raise ValueError('negative需为不超过1500字的文本')
    seed=config['seed']
    if not isinstance(seed,int) or isinstance(seed,bool) or not 0<=seed<=4294967295:
        raise ValueError('seed需为0至4294967295的整数')
    return {'data':[config['prompt'],config['negative'],None,None,512,704,'text-to-video',2,9,seed,False,1,False]}


def cache_root():
    custom=os.environ.get('RSI_VIDEO_CACHE')
    if custom:
        return Path(custom).expanduser().resolve()
    return Path(os.environ.get('XDG_CACHE_HOME',str(Path.home()/'.cache'))).expanduser()/'rsi-anything'/'video-generation'


@contextmanager
def cache_lock(folder):
    """操作系统在进程结束时释放锁，超时停止后不会留下永久占用。"""
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
        raise RuntimeError('相同视频请求正在执行，请等待该任务结束后重试') from exc
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
        raise RuntimeError('服务未提供text_to_video接口；未提交生成')
    labels=[components[i].get('props',{}).get('label') for i in dep['inputs']]
    if labels!=INPUT_LABELS:
        raise RuntimeError('服务输入顺序已变化；为避免错误提交，请先更新适配器')
    return {'gradio_version':config.get('version'),'input_labels':labels,
            'declared_model':'LTX 0.9.8 13B distilled（上游公开说明）','checked_at':now()}


def sse_events(lines):
    """解析Gradio事件流，支持心跳、CRLF和多行data字段。"""
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
                raise RuntimeError('视频服务返回错误：'+data[:600])
            if time.monotonic()-started>timeout:
                raise TimeoutError('等待生成结果超时；事件编号已保存，可恢复等待')
    raise RuntimeError('事件流结束但没有完成结果；事件编号已保存，可恢复等待')


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
                raise RuntimeError('返回文件超过128MiB，本例停止下载')
            stream.write(block)
    if total==0:
        raise RuntimeError('返回视频为空')
    part.replace(destination)


def probe_video(path):
    result=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,width,height,codec_name',
                           '-of','json',str(path)],capture_output=True,text=True,timeout=30)
    if result.returncode:
        raise RuntimeError('ffprobe无法读取服务视频：'+result.stderr[-400:])
    data=json.loads(result.stdout)
    videos=[s for s in data.get('streams',[]) if s.get('codec_type')=='video']
    if not videos:
        raise RuntimeError('服务文件没有视频轨')
    duration=float(data.get('format',{}).get('duration',0))
    stream=videos[0]
    if not 1<=duration<=3.5 or stream.get('width')!=704 or stream.get('height')!=512:
        raise RuntimeError('返回视频时长或尺寸不符合本例约定')
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
                raise RuntimeError('缓存视频校验不一致；保留请求记录，先检查缓存再处理')
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
                    raise ValueError('生成服务没有返回有效事件编号')
            except Exception as exc:
                state.update(status='submission_unknown',error=str(exc),updated_at=now())
                atomic_json(state_file,state)
                raise RuntimeError('提交结果不确定，未自动重发；请先检查缓存中的提交记录') from exc
            state.update(status='submitted',event_id=event_id,submit_response=receipt,updated_at=now())
            atomic_json(state_file,state)
        elif not state.get('event_id'):
            raise RuntimeError('上次提交结果不确定，禁止自动重复生成；请人工确认服务状态后处理该缓存记录')
        if state.get('request')!=body or state.get('endpoint')!=endpoint:
            raise RuntimeError('缓存请求与当前输入不一致')
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
            raise RuntimeError('需要ffmpeg和ffprobe；未提交生成')
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
        atomic_json(out/'gates.json',{'真实服务结果已取得':True,'视频可读取且尺寸时长符合':True})
        (out/'notes.txt').write_text(f"真实生成事件 {state['event_id']}；{probe['duration_seconds']:.2f}秒，704×512；相同请求缓存复用={reused}。评委仅看抽帧，声音与完整运动仍需播放检查。",encoding='utf-8')
        page='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>真实生成短视频</title><style>body{max-width:900px;margin:40px auto;padding:20px;font:17px/1.7 system-ui;background:#f8f4ee}video{width:100%;background:#222}pre{white-space:pre-wrap}</style><h1>晨光陶瓷杯</h1><video controls preload="metadata" src="video.mp4"></video><h2>本次生成描述</h2><pre>'+html.escape(config['prompt'])+'</pre><p>实际事件：'+html.escape(state['event_id'])+'；评价只覆盖可见静帧，需播放检查完整运动。</p></html>'
        (out/'preview.html').write_text(page,encoding='utf-8')
        return 0
    except Exception as exc:
        error={'stage':'video_generation','error':str(exc),'time':now(),'quality_result':'unknown'}
        if folder is not None and (folder/'state.json').exists():
            error['request_state']=json.loads((folder/'state.json').read_text())
        atomic_json(out/'error.json',error)
        atomic_json(out/'gates.json',{'真实服务结果已取得':False})
        (out/'notes.txt').write_text('视频服务或环境未完成，作品质量未知：'+str(exc),encoding='utf-8')
        print(str(exc),file=sys.stderr)
        return 2


if __name__=='__main__':
    sys.exit(main())
