"""Keep the quantities and scope of the WHO recommendations, and write a public explainer."""
import html
import json
import re
from pathlib import Path

MIN_WORDS, MAX_WORDS = 150, 3000
SCOPE_PHRASES = ('generally healthy adults', 'health education', 'not a substitute')
START_PHRASES = (('a little', 'small amount', 'start small'), ('gradual',), ('sedentary', 'sitting'))
DOSING = (r'\d+(?:\.\d+)?\s*(?:mg|milligrams?|ml|millilit(?:er|re)s?|tablets?|pills?|capsules?)\b'
          r'|guaranteed?\s+(?:to\s+)?cure|cures?\s+(?:all|everything)'
          r'|stop\s+(?:taking\s+)?(?:your\s+)?(?:medication|medicine|drugs?)\s+(?:immediately|right away|now)'
          r'|\btake\s+(?:\w+\s+){0,3}(?:medication|medicine|pills?|tablets?|capsules?|drugs?)\s+(?:daily|every\s+day)')


def main():
    out = Path('out')
    out.mkdir(exist_ok=True)
    source = json.loads(Path('judge/sources.json').read_text(encoding='utf-8'))
    values, sources = source['values'], source['sources']
    text = Path('explainer.md').read_text(encoding='utf-8')
    lower = text.lower()
    tokens = re.findall(r'\{\{([^{}]+)\}\}', text)
    unknown = sorted(set(tokens) - values.keys())
    rendered = re.sub(r'\{\{([^{}]+)\}\}',lambda m:values.get(m[1],m[0]),text)
    bare = re.sub(r'\{\{[^{}]*\}\}|\[W\d+\]', '', text)
    citations = set(re.findall(r'\[([A-Z]+\d+)\]', text))
    gates = {
        'article_has_substance': MIN_WORDS <= len(text.split()) <= MAX_WORDS,
        'guideline_numbers_use_fixed_data': set(values) <= set(tokens) and not unknown and '{{' not in rendered and not re.search(r'\d', bare),
        'source_ids_valid': set(sources) <= citations and citations <= set(sources),
        'scope_is_clear': all(s in lower for s in SCOPE_PHRASES),
        'no_drug_doses_or_cure_promises': not bool(re.search(DOSING,rendered,re.I)),
        'covers_starting_small_and_sitting': all(any(s in lower for s in group) for group in START_PHRASES),
    }
    references = '\n'.join(f"- [{k}] {v['title']}: {v['url']}" + (f"; guideline text: {v['guideline_url']}" if v.get('guideline_url') else '') for k,v in sources.items())
    (out / 'explainer.md').write_text(rendered+'\n\n## Sources\n\n'+references+'\n',encoding='utf-8')
    (out / 'evaluation.md').write_text(rendered,encoding='utf-8')
    labels = {'adult_age':'Adult ages covered here','moderate_minutes':'Moderate-intensity aerobic activity per week','vigorous_minutes':'Or vigorous-intensity aerobic activity per week','strength_days':'Muscle-strengthening activity per week'}
    rows = ''.join(f'<tr><td>{html.escape(labels.get(k,k))}</td><td>{html.escape(v)}</td></tr>' for k,v in values.items())
    refs = ''.join(f'<li>[{k}] <a href="{html.escape(v["url"],quote=True)}">{html.escape(v["title"])}</a>' + (f' · <a href="{html.escape(v["guideline_url"],quote=True)}">Guideline executive summary</a>' if v.get('guideline_url') else '') + '</li>' for k,v in sources.items())
    page = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Adult physical activity explainer</title><style>body{max-width:820px;margin:40px auto;padding:0 22px;font:18px/1.85 system-ui;background:#f3f9f7;color:#243b35}article{background:white;padding:25px;border-radius:12px}pre{white-space:pre-wrap;font:inherit}table{border-collapse:collapse;width:100%}td{padding:12px;border-bottom:1px solid #bed6cd}a{color:#176b53}</style><article><pre>'+html.escape(rendered)+'</pre></article><h2>Quantities from the source material</h2><table>'+rows+'</table><h2>Authoritative sources</h2><ul>'+refs+'</ul></html>'
    (out / 'explainer.html').write_text(page,encoding='utf-8')
    (out / 'checklist.json').write_text(json.dumps({'guideline_values':values,'used_source_ids':sorted(citations),'gates':gates},ensure_ascii=False,indent=2),encoding='utf-8')
    notes = ['Failed: '+name for name,passed in gates.items() if not passed]
    if unknown:
        notes.append('Unknown guideline data keys: '+', '.join(unknown))
    notes.append('The program checks the fixed quantities, source ids and scope statement; an LLM jury separately checks whether the material is restated accurately and whether individualized medical instructions were given.')
    (out / 'gates.json').write_text(json.dumps(gates,ensure_ascii=False,indent=2),encoding='utf-8')
    (out / 'notes.txt').write_text('\n'.join(notes),encoding='utf-8')


if __name__ == '__main__':
    main()
