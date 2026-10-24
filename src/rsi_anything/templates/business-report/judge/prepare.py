"""核对固定资料的数字插值，输出报告、数据表和 Mermaid 图表。"""
import html
import json
import re
from pathlib import Path


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
            values[f'{key}_{year}'] = f"{row[year]:,} 百万美元"
        values[f'{key}_growth'] = f"{(row['2024'] / row['2023'] - 1) * 100:+.2f}%"
    for year in ('2023', '2024'):
        values[f'services_share_{year}'] = f"{series['services'][year] / series['revenue'][year] * 100:.2f}%"
    values.update({key: f'{value:,} 百万美元' for key, value in facts['extra'].items()})
    tokens = re.findall(r'\{\{([^{}]+)\}\}', text)
    unknown = sorted(set(tokens) - values.keys())
    rendered = re.sub(r'\{\{([^{}]+)\}\}', lambda m: values.get(m[1], m[0]), text)
    bare = re.sub(r'\{\{[^{}]*\}\}|\[S\d+\]|202[34]', '', text)
    citations = set(re.findall(r'\[([A-Z]+\d+)\]', text))
    required = {'revenue_2024', 'revenue_growth', 'services_2024', 'operating_income_2024', 'net_income_2024'}
    gates = {
        '正文有实质内容': 150 <= len(text.strip()) <= 5000,
        '数字资料键存在': not unknown and '{{' not in rendered and '}}' not in rendered,
        '金额和比率使用资料插值': not bool(re.search(r'\d', bare)),
        '关键数字齐全': required <= set(tokens),
        '来源编号有效': bool(citations) and citations <= facts['sources'].keys() and 'S1' in citations,
        '限定经营分析用途': '不构成投资建议' in text,
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
    gates['图表指标有效'] = valid
    if not valid:
        metrics = []
        notes.append('charts.json 的 metrics 需要选择一至三个不同的 series 指标。')
    if unknown:
        notes.append('未知资料键：' + ', '.join(unknown))
    diagrams, table_rows, chart_descriptions = [], [], []
    for index, key in enumerate(metrics, 1):
        row = series[key]
        ceiling = int(max(row['2023'], row['2024']) * 1.12) + 1
        diagram = ('xychart-beta\n' + f'    title "{row["label"]}（百万美元）"\n'
                   + '    x-axis ["2023", "2024"]\n'
                   + f'    y-axis "百万美元" 0 --> {ceiling}\n'
                   + f'    bar [{row["2023"]}, {row["2024"]}]\n')
        (out / f'chart-{index}.mmd').write_text(diagram, encoding='utf-8')
        diagrams.append(diagram)
        table_rows.append(f"<tr><td>{html.escape(row['label'])}</td><td>{row['2023']:,}</td><td>{row['2024']:,}</td></tr>")
        chart_descriptions.append(f"图{index}：{row['label']}，2023={row['2023']:,}；2024={row['2024']:,}；单位百万美元。")
    sources = '\n'.join(f"[{k}] {v['title']} — {v['url']}" for k, v in facts['sources'].items())
    markdown = rendered + '\n\n## 数据图表\n\n' + '\n'.join('```mermaid\n'+d+'```\n' for d in diagrams) + '\n## 来源\n\n' + sources
    (out / 'report.md').write_text(markdown, encoding='utf-8')
    (out / 'evaluation.md').write_text(rendered + '\n\n所选图表：\n' + '\n'.join(chart_descriptions), encoding='utf-8')
    body = '<article><pre>' + html.escape(rendered) + '</pre></article>'
    body += '<h2>所选指标（百万美元）</h2><table><tr><th>指标</th><th>2023</th><th>2024</th></tr>' + ''.join(table_rows) + '</table>'
    body += ''.join('<pre class="mermaid">'+html.escape(d)+'</pre>' for d in diagrams)
    body += '<h2>资料来源</h2><ul>' + ''.join(f'<li>[{k}] <a href="{html.escape(v["url"], quote=True)}">{html.escape(v["title"])}</a></li>' for k,v in facts['sources'].items()) + '</ul>'
    body += '<p>图形需联网加载 Mermaid；离线时正文与上方数值表仍可阅读。</p>'
    page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>经营分析报告</title><style>body{max-width:900px;margin:40px auto;padding:0 24px;font:17px/1.8 system-ui;color:#183047;background:#f7f9fc}pre{white-space:pre-wrap;font:inherit}table{border-collapse:collapse;width:100%;background:white}td,th{padding:12px;border:1px solid #d7e0e8;text-align:left}article{background:white;padding:24px;border-radius:12px}a{color:#185b9c}</style>''' + body + '''<script type="module">import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';mermaid.initialize({startOnLoad:true,securityLevel:'strict'});</script></html>'''
    (out / 'report.html').write_text(page, encoding='utf-8')
    (out / 'metrics.json').write_text(json.dumps({'unit':facts['unit'],'series':series,'rendered_values':values,'selected_charts':metrics}, ensure_ascii=False, indent=2), encoding='utf-8')
    notes += ['未通过：'+name for name, passed in gates.items() if not passed]
    notes.append('程序只核对资料键、单位及图表数据；论据和结论是否相称由模型评委判断。')
    (out / 'gates.json').write_text(json.dumps(gates, ensure_ascii=False, indent=2), encoding='utf-8')
    (out / 'notes.txt').write_text('\n'.join(notes), encoding='utf-8')


if __name__ == '__main__':
    main()
