"""Turn the structured review into a readable report and check the preset issues and clause locations."""
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
            raise ValueError('issues must be a list of objects')
        gates['valid_structure'] = 1 <= len(issues) <= len(guide['issues'])
        scope = review.get('scope', '')
        gates['marked_as_example'] = isinstance(scope,str) and 'example' in scope.lower() and 'not legal advice' in scope.lower()
        seen = set()
        for item in issues:
            iid, cid = item.get('issue_id'), item.get('clause_id')
            quote, risk, suggestion = (item.get(k, '') for k in ('quote','risk','suggestion'))
            valid_id = isinstance(iid,str) and iid in guide['issues']
            locate = valid_id and cid == guide['issues'][iid]['clause_id']
            quoted = isinstance(quote,str) and len(quote.strip()) >= 15 and quote in contract['clauses'].get(cid,'')
            substantive = all(isinstance(v,str) and 30 <= len(v.strip()) <= 4000 for v in (risk,suggestion))
            unique = isinstance(iid,str) and iid not in seen
            passed = bool(locate and quoted and substantive and unique)
            if isinstance(iid,str):
                seen.add(iid)
            details.append({'issue_id':iid,'clause_id':cid,'valid':passed})
            label = guide['issues'].get(iid, {}).get('name','Unknown issue') if isinstance(iid,str) else 'Unknown issue'
            rows.append(f"## {iid} {label} · {cid}\n\nOriginal wording: {quote}\n\nPossible dispute: {risk}\n\nSuggested change: {suggestion}\n")
        gates['location_quote_and_advice_complete'] = bool(details) and all(d['valid'] for d in details)
        rendered = f"# {review.get('title','Example contract review')}\n\n{scope}\n\n{review.get('overview','')}\n\n"+'\n'.join(rows)
    except (ValueError, KeyError, TypeError, AttributeError):
        gates['valid_structure'] = False
        rendered = '# Example contract review\n\nreview.json is malformed; fix it to follow the structure of the starting draft.\n'
    covered = {d['issue_id'] for d in details if d['valid']}
    missing = sorted(set(guide['issues']) - covered)
    summary = {'covered':sorted(covered),'missing':missing,'total':len(guide['issues']),
               'coverage_percent':round(100*len(covered)/len(guide['issues']),1),'checks':details}
    notes = f"Correctly located {len(covered)}/{len(guide['issues'])} preset issue types; still missing: {', '.join(missing) or 'none'}."
    notes += '\n'+'\n'.join('Failed: '+k for k,v in gates.items() if not v)
    notes += '\nThe program checks locations and text length; an LLM jury judges whether the suggestions really resolve the disputes.'
    (out/'review.md').write_text(rendered,encoding='utf-8')
    (out/'evaluation.md').write_text(rendered+'\n\nProgram coverage record: '+notes,encoding='utf-8')
    (out/'coverage.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'gates.json').write_text(json.dumps(gates,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'notes.txt').write_text(notes,encoding='utf-8')
    page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Example contract review</title><style>body{max-width:900px;margin:35px auto;padding:20px;font:17px/1.8 system-ui;background:#f5f7fb;color:#263650}pre{white-space:pre-wrap;font:inherit}article{background:white;padding:24px;border-left:5px solid #6383a8}</style><article><pre>'+html.escape(rendered)+'</pre></article><p>'+html.escape(notes)+'</p></html>'
    (out/'review.html').write_text(page,encoding='utf-8')


if __name__=='__main__':
    main()
