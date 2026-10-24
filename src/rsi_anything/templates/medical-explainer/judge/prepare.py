"""保留 WHO 建议中的数量和适用边界，输出面向公众的科普稿。"""
import html
import json
import re
from pathlib import Path


def main():
    out = Path('out')
    out.mkdir(exist_ok=True)
    source = json.loads(Path('judge/sources.json').read_text(encoding='utf-8'))
    values, sources = source['values'], source['sources']
    text = Path('explainer.md').read_text(encoding='utf-8')
    tokens = re.findall(r'\{\{([^{}]+)\}\}', text)
    unknown = sorted(set(tokens) - values.keys())
    rendered = re.sub(r'\{\{([^{}]+)\}\}',lambda m:values.get(m[1],m[0]),text)
    bare = re.sub(r'\{\{[^{}]*\}\}|\[W\d+\]', '', text)
    citations = set(re.findall(r'\[([A-Z]+\d+)\]', text))
    gates = {
        '正文有实质内容': 250 <= len(text.strip()) <= 4500,
        '指南数量使用固定资料': set(values) <= set(tokens) and not unknown and '{{' not in rendered and not re.search(r'\d', bare),
        '来源编号有效': set(sources) <= citations and citations <= set(sources),
        '适用边界清楚': all(s in text for s in ('一般健康成人','健康科普','不能替代')),
        '没有药物剂量或疗效保证': not bool(re.search(r'\d+\s*(?:mg|毫克|毫升|片|粒)|保证治愈|包治|立即停药|每天服用',rendered,re.I)),
        '包含少量起步和久坐说明': all(s in text for s in ('少量','逐步','久坐')),
    }
    references = '\n'.join(f"- [{k}] {v['title']}：{v['url']}" + (f"；指南原文：{v['guideline_url']}" if v.get('guideline_url') else '') for k,v in sources.items())
    (out / 'explainer.md').write_text(rendered+'\n\n## 来源\n\n'+references+'\n',encoding='utf-8')
    (out / 'evaluation.md').write_text(rendered,encoding='utf-8')
    labels = {'adult_age':'本例介绍的成人年龄','moderate_minutes':'每周中等强度有氧活动','vigorous_minutes':'或每周高强度有氧活动','strength_days':'每周肌肉强化活动'}
    rows = ''.join(f'<tr><td>{html.escape(labels.get(k,k))}</td><td>{html.escape(v)}</td></tr>' for k,v in values.items())
    refs = ''.join(f'<li>[{k}] <a href="{html.escape(v["url"],quote=True)}">{html.escape(v["title"])}</a>' + (f' · <a href="{html.escape(v["guideline_url"],quote=True)}">指南执行摘要</a>' if v.get('guideline_url') else '') + '</li>' for k,v in sources.items())
    page = '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>成人身体活动科普</title><style>body{max-width:820px;margin:40px auto;padding:0 22px;font:18px/1.85 system-ui;background:#f3f9f7;color:#243b35}article{background:white;padding:25px;border-radius:12px}pre{white-space:pre-wrap;font:inherit}table{border-collapse:collapse;width:100%}td{padding:12px;border-bottom:1px solid #bed6cd}a{color:#176b53}</style><article><pre>'+html.escape(rendered)+'</pre></article><h2>资料中的数量</h2><table>'+rows+'</table><h2>权威来源</h2><ul>'+refs+'</ul></html>'
    (out / 'explainer.html').write_text(page,encoding='utf-8')
    (out / 'checklist.json').write_text(json.dumps({'guideline_values':values,'used_source_ids':sorted(citations),'gates':gates},ensure_ascii=False,indent=2),encoding='utf-8')
    notes = ['未通过：'+name for name,passed in gates.items() if not passed]
    if unknown:
        notes.append('未知指南资料键：'+', '.join(unknown))
    notes.append('程序检查固定数量、来源编号及用途说明；是否准确转述、是否给出了个体化医疗指令由模型评委另行检查。')
    (out / 'gates.json').write_text(json.dumps(gates,ensure_ascii=False,indent=2),encoding='utf-8')
    (out / 'notes.txt').write_text('\n'.join(notes),encoding='utf-8')


if __name__ == '__main__':
    main()
