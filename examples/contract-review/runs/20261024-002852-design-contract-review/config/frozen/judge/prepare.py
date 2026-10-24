"""把结构化审阅结果生成可读报告，核对预设问题与条款定位。"""
import html
import json
from pathlib import Path


def main():
    out = Path('out')
    out.mkdir(exist_ok=True)
    contract = json.loads(Path('judge/contract.json').read_text(encoding='utf-8'))
    guide = json.loads(Path('judge/review-guide.json').read_text(encoding='utf-8'))
    gates, rows, details = {}, [], []
    try:
        review = json.loads(Path('review.json').read_text(encoding='utf-8'))
        issues = review['issues']
        if not isinstance(issues, list) or not all(isinstance(x, dict) for x in issues):
            raise ValueError('issues 必须是对象列表')
        gates['结构有效'] = 1 <= len(issues) <= len(guide['issues'])
        scope = review.get('scope', '')
        gates['示例用途明确'] = isinstance(scope,str) and '示例' in scope and '不构成法律意见' in scope
        seen = set()
        for item in issues:
            iid, cid = item.get('issue_id'), item.get('clause_id')
            quote, risk, suggestion = (item.get(k, '') for k in ('quote','risk','suggestion'))
            valid_id = isinstance(iid,str) and iid in guide['issues']
            locate = valid_id and cid == guide['issues'][iid]['clause_id']
            quoted = isinstance(quote,str) and len(quote.strip()) >= 6 and quote in contract['clauses'].get(cid,'')
            substantive = all(isinstance(v,str) and 12 <= len(v.strip()) <= 1200 for v in (risk,suggestion))
            unique = isinstance(iid,str) and iid not in seen
            passed = bool(locate and quoted and substantive and unique)
            if isinstance(iid,str):
                seen.add(iid)
            details.append({'issue_id':iid,'clause_id':cid,'valid':passed})
            label = guide['issues'].get(iid, {}).get('name','未知问题') if isinstance(iid,str) else '未知问题'
            rows.append(f"## {iid} {label} · {cid}\n\n原句：{quote}\n\n潜在争议：{risk}\n\n修改建议：{suggestion}\n")
        gates['定位引用和建议完整'] = bool(details) and all(d['valid'] for d in details)
        rendered = f"# {review.get('title','示例合同检查')}\n\n{scope}\n\n{review.get('overview','')}\n\n"+'\n'.join(rows)
    except (ValueError, KeyError, TypeError, AttributeError):
        gates['结构有效'] = False
        rendered = '# 示例合同检查\n\nreview.json 格式有误，请按初稿结构修正。\n'
    covered = {d['issue_id'] for d in details if d['valid']}
    missing = sorted(set(guide['issues']) - covered)
    summary = {'covered':sorted(covered),'missing':missing,'total':len(guide['issues']),
               'coverage_percent':round(100*len(covered)/len(guide['issues']),1),'checks':details}
    notes = f"已准确定位 {len(covered)}/{len(guide['issues'])} 类预设问题；尚缺：{', '.join(missing) or '无'}。"
    notes += '\n'+'\n'.join('未通过：'+k for k,v in gates.items() if not v)
    notes += '\n程序检查定位与内容长度；建议是否真正解决争议由模型评委判断。'
    (out/'review.md').write_text(rendered,encoding='utf-8')
    (out/'evaluation.md').write_text(rendered+'\n\n程序覆盖记录：'+notes,encoding='utf-8')
    (out/'coverage.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'gates.json').write_text(json.dumps(gates,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'notes.txt').write_text(notes,encoding='utf-8')
    page='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>示例合同审阅</title><style>body{max-width:900px;margin:35px auto;padding:20px;font:17px/1.8 system-ui;background:#f5f7fb;color:#263650}pre{white-space:pre-wrap;font:inherit}article{background:white;padding:24px;border-left:5px solid #6383a8}</style><article><pre>'+html.escape(rendered)+'</pre></article><p>'+html.escape(notes)+'</p></html>'
    (out/'review.html').write_text(page,encoding='utf-8')


if __name__=='__main__':
    main()
