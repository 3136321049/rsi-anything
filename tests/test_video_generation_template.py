"""视频接口与恢复测试；所有网络和视频探测均替换为单元测试对象。"""
import importlib.util
import json
from pathlib import Path

import pytest


ROOT=Path(__file__).resolve().parents[1]/'src/rsi_anything/templates/video-generation'


@pytest.fixture
def module():
    spec=importlib.util.spec_from_file_location('video_prepare_test',ROOT/'judge/prepare.py')
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def body(module):
    return module.payload({'prompt':'A small ceramic mug on a desk.','negative':'text','seed':42})


def mocks(module,monkeypatch):
    calls={'submit':0,'wait':0,'download':0}
    monkeypatch.setattr(module,'verify_service',lambda endpoint:{'gradio_version':'unit-test'})
    def submit(*args,**kwargs):
        calls['submit']+=1
        return {'event_id':'test-event'}
    def wait(*args,**kwargs):
        calls['wait']+=1
        return {'video_url':'https://example.org/unit-test.mp4','returned_seed':42,'complete_event':[]}
    def download(url,path):
        calls['download']+=1
        path.write_bytes(b'unit-test-data-not-a-real-video')
    monkeypatch.setattr(module,'request_json',submit)
    monkeypatch.setattr(module,'wait_result',wait)
    monkeypatch.setattr(module,'download_video',download)
    monkeypatch.setattr(module,'probe_video',lambda path:{'duration_seconds':2,'width':704,'height':512})
    return calls


def test_video_payload_matches_verified_parameter_order(module):
    data=body(module)['data']
    assert data[2:9]==[None,None,512,704,'text-to-video',2,9]
    assert data[9:]==[42,False,1,False]


@pytest.mark.parametrize('change',[{'seed':-1},{'seed':True},{'prompt':''},{'width':1920}])
def test_video_rejects_invalid_candidate_configuration(module,change):
    config={'prompt':'A small ceramic mug on a desk.','negative':'text','seed':42}
    config.update(change)
    with pytest.raises(ValueError):
        module.payload(config)


def test_sse_parses_heartbeat_crlf_and_multiline_data(module):
    lines=[b'event: heartbeat\r\n',b'data: null\r\n',b'\r\n',b'event: complete\n',b'data: [\n',b'data: 1]\n',b'\n']
    assert list(module.sse_events(lines))==[('heartbeat','null'),('complete','[\n1]')]


def test_identical_video_request_reuses_download_without_new_generation(tmp_path,module,monkeypatch):
    calls=mocks(module,monkeypatch)
    folder=tmp_path/'cache'
    first=module.generate('https://example.org',body(module),folder)
    second=module.generate('https://example.org',body(module),folder)
    assert first[2] is False and second[2] is True
    assert calls=={'submit':1,'wait':1,'download':1}
    state=json.loads((folder/'state.json').read_text())
    assert state['event_id']=='test-event' and state['video_sha256']


def test_wait_interruption_resumes_saved_event_without_resubmitting(tmp_path,module,monkeypatch):
    calls=mocks(module,monkeypatch)
    original=module.wait_result
    monkeypatch.setattr(module,'wait_result',lambda *a,**k:(_ for _ in ()).throw(TimeoutError('test timeout')))
    folder=tmp_path/'cache'
    with pytest.raises(TimeoutError):
        module.generate('https://example.org',body(module),folder)
    assert json.loads((folder/'state.json').read_text())['event_id']=='test-event'
    monkeypatch.setattr(module,'wait_result',original)
    module.generate('https://example.org',body(module),folder)
    assert calls['submit']==1 and calls['download']==1


def test_unknown_submission_is_never_automatically_reposted(tmp_path,module,monkeypatch):
    calls=mocks(module,monkeypatch)
    def unknown(*a,**k):
        calls['submit']+=1
        raise TimeoutError('connection lost after submission')
    monkeypatch.setattr(module,'request_json',unknown)
    folder=tmp_path/'cache'
    for _ in range(2):
        with pytest.raises(RuntimeError):
            module.generate('https://example.org',body(module),folder)
    assert calls['submit']==1
    assert json.loads((folder/'state.json').read_text())['status']=='submission_unknown'


def test_download_retry_reuses_completed_generation(tmp_path,module,monkeypatch):
    calls=mocks(module,monkeypatch)
    original=module.download_video
    monkeypatch.setattr(module,'download_video',lambda *a,**k:(_ for _ in ()).throw(TimeoutError('test download')))
    folder=tmp_path/'cache'
    with pytest.raises(TimeoutError):
        module.generate('https://example.org',body(module),folder)
    monkeypatch.setattr(module,'download_video',original)
    module.generate('https://example.org',body(module),folder)
    assert calls['submit']==1 and calls['wait']==1 and calls['download']==1


def test_corrupt_cached_video_does_not_silently_regenerate(tmp_path,module,monkeypatch):
    calls=mocks(module,monkeypatch)
    folder=tmp_path/'cache'
    module.generate('https://example.org',body(module),folder)
    (folder/'video.mp4').write_bytes(b'changed')
    with pytest.raises(RuntimeError,match='缓存视频校验'):
        module.generate('https://example.org',body(module),folder)
    assert calls['submit']==1


def test_changed_service_schema_stops_before_submit(module,monkeypatch):
    monkeypatch.setattr(module,'request_json',lambda *a,**k:{'components':[],'dependencies':[]})
    with pytest.raises(RuntimeError,match='未提交生成'):
        module.verify_service('https://example.org')


def test_cache_lock_prevents_same_request_concurrency(tmp_path,module):
    with module.cache_lock(tmp_path):
        with pytest.raises(RuntimeError,match='正在执行'):
            with module.cache_lock(tmp_path):
                pass


def test_main_reports_configuration_failure_without_placeholder_video(tmp_path,module,monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(module.shutil,'which',lambda name:None)
    assert module.main()==2
    assert not (tmp_path/'out/video.mp4').exists()
    error=json.loads((tmp_path/'out/error.json').read_text())
    assert error['quality_result']=='unknown'
