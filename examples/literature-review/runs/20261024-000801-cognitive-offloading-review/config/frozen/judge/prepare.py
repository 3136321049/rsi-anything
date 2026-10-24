"""检查引用编号与正文证据映射，生成可阅读的综述与来源清单。"""
import html
import json
import re
from pathlib import Path


def normalized(text):
    return re.sub(r'\s+', '', text)


def main():
    out = Path('out')
    out.mkdir(exist_ok=True)
    text = Path('review.md').read_text(encoding='utf-8')
    sources = json.loads(Path('judge/sources.json').read_text(encoding='utf-8'))['sources']
    citations = set(re.findall(r'\[([A-Z]+\d+)\]', text))
    links = set(re.findall(r'https?://[^\s<>）)]+', text))
    known_links = {v['url'] for v in sources.values()} | {'https://doi.org/'+v['doi'] for v in sources.values()}
    gates = {'正文有实质内容': 250 <= len(text.strip()) <= 6000,
             '来源编号有效': bool(citations) and citations <= sources.keys(),
             '覆盖给定三份资料': set(sources) <= citations,
             '未引入资料外链接': links <= known_links}
    details, covered, seen = [], set(), set()
    try:
        data = json.loads(Path('evidence.json').read_text(encoding='utf-8'))
        claims = data['claims']
        if not isinstance(claims, list):
            raise ValueError('claims 必须为列表')
        for item in claims:
            claim, refs = item.get('claim', ''), item.get('sources', [])
            valid_refs = isinstance(refs, list) and bool(refs) and all(isinstance(r, str) and r in sources for r in refs)
            valid_claim = isinstance(claim, str) and 12 <= len(claim.strip()) <= 500
            in_text = valid_claim and normalized(claim) in normalized(text)
            paragraphs = [p for p in text.split('\n\n') if valid_claim and normalized(claim) in normalized(p)]
            local_refs = valid_refs and any(all(f'[{r}]' in p for r in refs) for p in paragraphs)
            unique = valid_claim and normalized(claim) not in seen
            if valid_claim:
                seen.add(normalized(claim))
            passed = bool(valid_refs and in_text and local_refs and unique)
            details.append({'claim':claim,'sources':refs,'in_text':bool(in_text),'cited_near_claim':bool(local_refs),'passed':passed})
            if passed:
                covered.update(refs)
        gates['证据映射有效'] = 3 <= len(claims) <= 12 and all(row['passed'] for row in details)
    except (ValueError, KeyError, TypeError, AttributeError):
        gates['证据映射有效'] = False
    gates['映射覆盖全部来源'] = set(sources) <= covered
    bibliography = '\n'.join(f"- [{key}] {s['authors']}（{s['year']}），{s['title']}；{s['kind']}。{s['url']}" for key,s in sources.items())
    rendered = text + '\n\n## 给定资料来源\n\n' + bibliography + '\n'
    (out / 'review.md').write_text(rendered, encoding='utf-8')
    (out / 'evaluation.md').write_text(text, encoding='utf-8')
    (out / 'source-map.json').write_text(json.dumps({'claims':details,'covered_sources':sorted(covered),'all_sources':sources},ensure_ascii=False,indent=2),encoding='utf-8')
    body = '<article><pre>'+html.escape(text)+'</pre></article><h2>来源与证据类型</h2><ul>'
    body += ''.join(f'<li>[{key}] {html.escape(s["kind"])} · <a href="{html.escape(s["url"],quote=True)}">{html.escape(s["title"])}</a><p>{html.escape(s["limit"])}</p></li>' for key,s in sources.items()) + '</ul>'
    body += '<h2>正文证据映射</h2><ol>' + ''.join('<li>'+html.escape(str(row['claim']))+' — '+html.escape(str(row['sources']))+'</li>' for row in details) + '</ol>'
    page = '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>资料综述</title><style>body{max-width:900px;margin:40px auto;padding:0 24px;font:17px/1.8 system-ui;background:#faf9f5;color:#292f39}pre{white-space:pre-wrap;font:inherit}article{padding:24px;background:white;border-left:5px solid #b18c4f}li{margin-bottom:12px}a{color:#1d588d}</style>'+body+'</html>'
    (out / 'review.html').write_text(page,encoding='utf-8')
    notes = ['未通过：'+name for name,passed in gates.items() if not passed]
    notes.append('程序核对真实来源编号、引用位置和正文映射；来源是否真正支持论断、证据类型是否混淆由模型评委判断。')
    (out / 'gates.json').write_text(json.dumps(gates,ensure_ascii=False,indent=2),encoding='utf-8')
    (out / 'notes.txt').write_text('\n'.join(notes),encoding='utf-8')


if __name__ == '__main__':
    main()
