"""Offline tests for contract issue location and model answer grading; the model replies are unit-test inputs only."""
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

BASE = Path(__file__).resolve().parents[1] / 'src/rsi_anything/templates'


def contract(tmp_path, change=None):
    project=tmp_path/'contract'
    shutil.copytree(BASE/'contract-review',project)
    data=json.loads((project/'review.json').read_text())
    if change:
        change(data)
        (project/'review.json').write_text(json.dumps(data,ensure_ascii=False))
    result=subprocess.run([sys.executable,'judge/prepare.py'],cwd=project,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    return project,json.loads((project/'out/gates.json').read_text())


def test_contract_baseline_reports_partial_coverage(tmp_path):
    project,gates=contract(tmp_path)
    assert all(gates.values())
    coverage=json.loads((project/'out/coverage.json').read_text())
    assert coverage['covered']==['I1','I2']
    assert len(coverage['missing'])==5
    assert (project/'out/review.html').exists()


@pytest.mark.parametrize('field,value',[('clause_id','C7'),('quote','This sentence is not in the contract'),('suggestion','Add it')])
def test_contract_rejects_wrong_location_or_empty_advice(tmp_path,field,value):
    _,gates=contract(tmp_path,lambda d:d['issues'][0].update({field:value}))
    assert gates['location_quote_and_advice_complete'] is False


def test_contract_duplicate_issue_is_not_more_coverage(tmp_path):
    project,gates=contract(tmp_path,lambda d:d['issues'].append(d['issues'][0].copy()))
    assert gates['location_quote_and_advice_complete'] is False
    assert len(json.loads((project/'out/coverage.json').read_text())['covered'])==2


@pytest.fixture
def lesson_module():
    spec=importlib.util.spec_from_file_location('lesson_test',BASE/'lesson-builder/judge/evaluate.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_student_prompt_omits_answer_key_and_solution(lesson_module):
    exercises=[{'id':'T1','question':'An original number question','unit':'yuan','expected':987654,'solution':'Secret solution that must not be passed on'}]
    prompt=lesson_module.build_prompt('Lesson content',exercises)
    assert '987654' not in prompt and 'Secret solution' not in prompt
    assert 'An original number question' in prompt


def test_student_scoring_counts_wrong_answers_and_missing_evidence(lesson_module):
    lesson='To find a part, multiply the whole by the matching proportion.'
    exercises=[{'id':f'T{i}','question':'Question','expected':12,'unit':'books','solution':'Solution'} for i in range(3)]
    replies={'answers':[
        {'id':'T0','answer':12,'reason':'Multiplying the whole by the proportion gives the result.','lesson_quote':lesson},
        {'id':'T1','answer':13,'reason':'Multiplying the whole by the proportion gives the result.','lesson_quote':lesson},
        {'id':'T2','answer':12,'reason':'This result comes from what the model already knew.','lesson_quote':'A sentence that is not actually in the lesson.'}]}
    result=lesson_module.grade(lesson,exercises,replies)
    assert result['correct']==1
    assert result['score']==33.33
    assert result['numeric_accuracy']==66.67


def test_student_duplicate_ids_are_protocol_error(lesson_module):
    with pytest.raises(ValueError):
        lesson_module.grade('Lesson',[{'id':'T1'}],{'answers':[{'id':'T1'},{'id':'T1'}]})


def test_student_main_saves_real_call_metadata_using_mock_only_in_test(tmp_path,monkeypatch,lesson_module):
    project=tmp_path/'lesson'
    shutil.copytree(BASE/'lesson-builder',project)
    monkeypatch.chdir(project)
    monkeypatch.setenv('RSI_TASK_MODEL','cli:codex:test-student')
    monkeypatch.setenv('RSI_RESULT',str(tmp_path/'result.json'))
    exercises=json.loads((project/'judge/exercises.json').read_text())['exercises']
    quote='To find a percentage of an amount, multiply the whole amount by the matching decimal.'
    response={'answers':[{'id':e['id'],'answer':None,'reason':'Test reply saying the lesson method is not enough; not real student behavior.','lesson_quote':quote} for e in exercises]}
    monkeypatch.setattr(lesson_module.llm,'ask',lambda *a,**k:SimpleNamespace(text=json.dumps(response),model='unit-test-only',usage={'total_tokens':12},seconds=0.1,cost_usd=None))
    assert lesson_module.main()==0
    data=json.loads((project/'out/results.json').read_text())
    assert data['actual_model']=='unit-test-only' and data['correct']==0
    assert len(json.loads((project/'out/mistakes.json').read_text()))==10
    assert (project/'out/lesson.html').exists()


def test_student_missing_model_is_configuration_error(tmp_path,monkeypatch,lesson_module):
    project=tmp_path/'lesson'
    shutil.copytree(BASE/'lesson-builder',project)
    monkeypatch.chdir(project)
    monkeypatch.delenv('RSI_TASK_MODEL',raising=False)
    assert lesson_module.main()==2
    assert json.loads((project/'out/error.json').read_text())['stage']=='configuration'
