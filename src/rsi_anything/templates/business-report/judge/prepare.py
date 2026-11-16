"""Check the number placeholders against the fixed data and write the report, a data table and Mermaid charts."""
import html
import json
import re
from pathlib import Path

MIN_WORDS, MAX_WORDS = 100, 3000


def main():
    out = Path('out')
    out.mkdir(exist_ok=True)
    for old_chart in out.glob('chart-*.mmd'):
        old_chart.unlink()
    facts = json.loads(Path('judge/facts.json').read_text(encoding='utf-8'))
    text = Path('report.md').read_text(encoding='utf-8')
    series = facts['series']
    values = {}
    for key, row in series.items():
        for year in ('2023', '2024'):
            values[f'{key}_{year}'] = f"US${row[year]:,} million"
        values[f'{key}_growth'] = f"{(row['2024'] / row['2023'] - 1) * 100:+.2f}%"
    for year in ('2023', '2024'):
        values[f'services_share_{year}'] = f"{series['services'][year] / series['revenue'][year] * 100:.2f}%"
    values.update({key: f'US${value:,} million' for key, value in facts['extra'].items()})
    tokens = re.findall(r'\{\{([^{}]+)\}\}', text)
    unknown = sorted(set(tokens) - values.keys())
    rendered = re.sub(r'\{\{([^{}]+)\}\}', lambda m: values.get(m[1], m[0]), text)
    bare = re.sub(r'\{\{[^{}]*\}\}|\[S\d+\]|202[34]', '', text)
    citations = set(re.findall(r'\[([A-Z]+\d+)\]', text))
    required = {'revenue_2024', 'revenue_growth', 'services_2024', 'operating_income_2024', 'net_income_2024'}
    gates = {
        'article_has_substance': MIN_WORDS <= len(text.split()) <= MAX_WORDS,
        'data_keys_exist': not unknown and '{{' not in rendered and '}}' not in rendered,
        'numbers_use_data_placeholders': not bool(re.search(r'\d', bare)),
        'key_figures_present': required <= set(tokens),
        'source_ids_valid': bool(citations) and citations <= facts['sources'].keys() and 'S1' in citations,
        'states_not_investment_advice': 'not investment advice' in text.lower(),
    }
    notes = []
    try:
        config = json.loads(Path('charts.json').read_text(encoding='utf-8'))
        metrics = config['metrics']
        valid = (isinstance(metrics, list) and 1 <= len(metrics) <= 3
                 and all(isinstance(k, str) and k in series for k in metrics)
                 and len(set(metrics)) == len(metrics))
    except (ValueError, KeyError, TypeError):
        valid, metrics = False, []
    gates['chart_metrics_valid'] = valid
    if not valid:
        metrics = []
        notes.append('The metrics in charts.json must pick one to three different series metrics.')
    if unknown:
        notes.append('Unknown data keys: ' + ', '.join(unknown))
    diagrams, table_rows, chart_descriptions = [], [], []
    for index, key in enumerate(metrics, 1):
        row = series[key]
        ceiling = int(max(row['2023'], row['2024']) * 1.12) + 1
        diagram = ('xychart-beta\n' + f'    title "{row["label"]} (US$ millions)"\n'
                   + '    x-axis ["2023", "2024"]\n'
                   + f'    y-axis "US$ millions" 0 --> {ceiling}\n'
                   + f'    bar [{row["2023"]}, {row["2024"]}]\n')
        (out / f'chart-{index}.mmd').write_text(diagram, encoding='utf-8')
        diagrams.append(diagram)
        table_rows.append(f"<tr><td>{html.escape(row['label'])}</td><td>{row['2023']:,}</td><td>{row['2024']:,}</td></tr>")
        chart_descriptions.append(f"Chart {index}: {row['label']}, 2023 = {row['2023']:,}; 2024 = {row['2024']:,}; in US$ millions.")
    sources = '\n'.join(f"[{k}] {v['title']} — {v['url']}" for k, v in facts['sources'].items())
    markdown = rendered + '\n\n## Charts\n\n' + '\n'.join('```mermaid\n'+d+'```\n' for d in diagrams) + '\n## Sources\n\n' + sources
    (out / 'report.md').write_text(markdown, encoding='utf-8')
    (out / 'evaluation.md').write_text(rendered + '\n\nSelected charts:\n' + '\n'.join(chart_descriptions), encoding='utf-8')
    body = '<article><pre>' + html.escape(rendered) + '</pre></article>'
    body += '<h2>Selected metrics (US$ millions)</h2><table><tr><th>Metric</th><th>2023</th><th>2024</th></tr>' + ''.join(table_rows) + '</table>'
    body += ''.join('<pre class="mermaid">'+html.escape(d)+'</pre>' for d in diagrams)
    body += '<h2>Sources</h2><ul>' + ''.join(f'<li>[{k}] <a href="{html.escape(v["url"], quote=True)}">{html.escape(v["title"])}</a></li>' for k,v in facts['sources'].items()) + '</ul>'
    body += '<p>The charts load Mermaid from the internet; offline, the text and the table above are still readable.</p>'
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Operating analysis report</title><style>body{max-width:900px;margin:40px auto;padding:0 24px;font:17px/1.8 system-ui;color:#183047;background:#f7f9fc}pre{white-space:pre-wrap;font:inherit}table{border-collapse:collapse;width:100%;background:white}td,th{padding:12px;border:1px solid #d7e0e8;text-align:left}article{background:white;padding:24px;border-radius:12px}a{color:#185b9c}</style>''' + body + '''<script type="module">import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';mermaid.initialize({startOnLoad:true,securityLevel:'strict'});</script></html>'''
    (out / 'report.html').write_text(page, encoding='utf-8')
    (out / 'metrics.json').write_text(json.dumps({'unit':facts['unit'],'series':series,'rendered_values':values,'selected_charts':metrics}, ensure_ascii=False, indent=2), encoding='utf-8')
    notes += ['Failed: '+name for name, passed in gates.items() if not passed]
    notes.append('The program only checks data keys, units and chart data; an LLM jury judges whether the arguments match the conclusions.')
    (out / 'gates.json').write_text(json.dumps(gates, ensure_ascii=False, indent=2), encoding='utf-8')
    (out / 'notes.txt').write_text('\n'.join(notes), encoding='utf-8')


if __name__ == '__main__':
    main()
