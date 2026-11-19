#!/usr/bin/env python3
"""Draw saved54-case medians as standalone SVG and interactive HTML; no engine runs."""
import argparse
import hashlib
import html
import json
import math
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--results', required=True, type=Path)
p.add_argument('--output', required=True, type=Path)
a = p.parse_args()
s = json.loads((a.results/'summary.json').read_text())
assert s['complete'] and len(s['caseSummaries']) == 54
record = json.loads((Path(__file__).parent/'result.json').read_text())
assert hashlib.sha256((a.results/'summary.json').read_bytes()).hexdigest() == record['evidence']['receipts']['summary.json']['sha256']
a.output.mkdir(parents=True, exist_ok=True)
variants = [('native', 'Native PGO', '#2563eb'), ('node', 'Node / WASM', '#d97706'), ('chromium', 'Chromium / WASM', '#059669')]
rows = [dict(case=key, **s['caseSummaries'][key]) for key in sorted(s['caseSummaries'])]
for variant, _, _ in variants:
    assert math.isclose(sum(row[variant]['cpu']['median'] for row in rows), record['totals'][variant]['cpu'])
width, height, left, top, plot, step = 1120, 2725, 115, 155, 670, 46
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
 '<title id="title">Rook: CPU timing for each of the 54 cases</title>',
 '<desc id="desc">Grouped bars compare native PGO, Node WASM and Chromium WASM; each is the median of three measured runs, with sample min/max whiskers.</desc>',
 '<rect width="100%" height="100%" fill="white"/>',
 '<g font-family="Arial, sans-serif" fill="#172033">',
 '<text x="24" y="35" font-size="24" font-weight="bold">54-case CPU timing: native, Node and Chromium</text>',
 '<text x="24" y="61" font-size="15">Median of three measured runs per case; startup excluded. Whiskers show the sample range.</text>',
 '<text x="24" y="85" font-size="14">Native uses PGO; WASM does not. Chromium CPU covers its renderer and engine worker.</text>']
maximum = math.ceil(max(row[v]['cpu']['maximum'] for row in rows for v, _, _ in variants))
for i, (v, label, color) in enumerate(variants):
    x = 24 + i*235
    parts += [f'<rect x="{x}" y="103" width="16" height="12" fill="{color}"/>',f'<text x="{x+23}" y="114" font-size="15">{label}</text>']
for tick in range(maximum+1):
    x = left + plot*tick/maximum
    parts += [f'<line x1="{x}" y1="145" x2="{x}" y2="{top+54*step}" stroke="#dce2eb"/>',f'<text x="{x}" y="138" text-anchor="middle" font-size="13">{tick} s</text>']
for j, (_, label, color) in enumerate(variants):
    parts.append(f'<text x="{840+j*92}" y="138" text-anchor="middle" fill="{color}" font-size="13">{label.split(" /")[0]}</text>')
for i, row in enumerate(rows):
    y = top + i*step
    if i % 2 == 0: parts.append(f'<rect x="5" y="{y-2}" width="1105" height="{step}" fill="#f3f6fa" fill-opacity="0.7"/>')
    parts.append(f'<text x="{left-12}" y="{y+21}" text-anchor="end" font-size="15">{html.escape(row["case"])}</text>')
    for j, (v, _, color) in enumerate(variants):
        stat = row[v]['cpu']; cy = y + 5 + j*11
        median, lo, hi = [plot*stat[k]/maximum for k in ['median','minimum','maximum']]
        parts += [f'<rect x="{left}" y="{cy}" width="{median}" height="8" fill="{color}"><title>{row["case"]} {v}: {stat["median"]:.6f} CPU s</title></rect>',
                  f'<path d="M {left+lo} {cy+4} H {left+hi} M {left+lo} {cy+1} V {cy+7} M {left+hi} {cy+1} V {cy+7}" stroke="#172033" fill="none" stroke-width="1"/>',
                  f'<text x="{840+j*92}" y="{y+21}" text-anchor="middle" font-size="14" fill="{color}">{stat["median"]:.3f}</text>']
parts += [f'<text x="24" y="{top+54*step+37}" font-size="14">Sum of case medians: native {record["totals"]["native"]["cpu"]:.3f} s · Node {record["totals"]["node"]["cpu"]:.3f} s · Chromium {record["totals"]["chromium"]["cpu"]:.3f} s.</text>', '</g></svg>']
svg = '\n'.join(parts)
(a.output/'case-cpu.svg').write_text(svg)
page = '''<!doctype html><html lang="en"><meta charset="utf-8"><title>Rook54 timing comparison</title>
<style>body{font:16px system-ui;margin:24px;color:#172033}select{font:inherit;margin:0 18px 0 6px}table{border-collapse:collapse;width:100%;max-width:1450px}th{position:sticky;top:0;background:white;padding:12px;text-align:left;border-bottom:2px solid #ccd4df}td{padding:8px 12px;border-bottom:1px solid #e0e5ed}tr:nth-child(even){background:#f4f6fa}.bar{height:9px;margin:3px 0;min-width:1px}.num{text-align:right;font-variant-numeric:tabular-nums}td:nth-child(2){width:55%}.legend{margin:18px 0}.legend span{margin-right:24px}small{color:#526076}</style>
<h1>54-case timing comparison</h1>
<p>Each value is the median of three measured runs. Startup is excluded. Hover over a bar for its sample range.</p>
<p>Native is PGO; WASM is non-PGO. Chromium CPU covers its renderer and engine worker.</p>
<label>Metric<select id="metric"><option value="cpu">CPU time</option><option value="wall">Wall time</option></select></label>
<label>View<select id="view"><option value="seconds">Seconds</option><option value="ratio">Relative to native</option></select></label>
<label>Sort<select id="sort"><option value="case">Case number</option><option value="native">Native time, largest first</option><option value="node">Node time, largest first</option><option value="chromium">Chromium time, largest first</option><option value="slowdown">Node/native ratio, largest first</option></select></label>
<div class="legend"><span style="color:#2563eb">■ Native PGO</span><span style="color:#d97706">■ Node/WASM</span><span style="color:#059669">■ Chromium/WASM</span></div>
<table><thead><tr><th>Case</th><th>Timing comparison</th><th>Native</th><th>Node</th><th>Chromium</th></tr></thead><tbody id="rows"></tbody></table>
<p><small>These are saved matched54 measurements, not a new benchmark. Sample ranges are descriptive, not confidence intervals.</small></p>
<script>
const data=DATA;
const variants=[['native','#2563eb'],['node','#d97706'],['chromium','#059669']];
function render(){
 const metric=document.querySelector('#metric').value, ratio=document.querySelector('#view').value==='ratio', sort=document.querySelector('#sort').value;
 const value=(row,v)=>row[v][metric].median/(ratio?row.native[metric].median:1);
 const rows=[...data].sort((a,b)=>sort==='case'?a.case.localeCompare(b.case):sort==='slowdown'?b.node[metric].median/b.native[metric].median-a.node[metric].median/a.native[metric].median:b[sort][metric].median-a[sort][metric].median);
 const max=Math.max(...rows.flatMap(row=>variants.map(([v])=>value(row,v))));
 document.querySelector('#rows').innerHTML=rows.map(row=>`<tr><td>${row.case}</td><td>${variants.map(([v,color])=>`<div class="bar" style="background:${color};width:${100*value(row,v)/max}%" title="${v}: ${row[v][metric].median.toFixed(6)} s; range ${row[v][metric].minimum.toFixed(6)}–${row[v][metric].maximum.toFixed(6)} s"></div>`).join('')}</td>${variants.map(([v,color])=>`<td class="num" style="color:${color}">${value(row,v).toFixed(3)}${ratio?'×':' s'}</td>`).join('')}</tr>`).join('');
}
document.querySelectorAll('select').forEach(el=>el.onchange=render);render();
</script></html>'''
(a.output/'timings.html').write_text(page.replace('DATA',json.dumps(rows,separators=(',',':'))))
print(a.output/'case-cpu.svg')
print(a.output/'timings.html')
