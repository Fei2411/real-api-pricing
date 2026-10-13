"""Validate exported files, bilingual links, data coverage and source JSON."""
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from publish_charts import exports

data = json.loads((ROOT/'derived/points.json').read_text(encoding='utf-8'))
with (ROOT/'data/adopted.csv').open(encoding='utf-8-sig', newline='') as f:
    adopted = list(csv.DictReader(f))
assert len(adopted) == len(data['points'])
assert {r['plan_id']+'::'+r['served_model'] for r in adopted} == {p['id'] for p in data['points']}
assert len({p['id'] for p in data['points']}) == len(data['points'])
for p in ROOT.joinpath('data').rglob('*.json'):
    json.loads(p.read_text(encoding='utf-8-sig'))

exported = list(exports())
assert len(exported) == 163
assert len({d for _,d in exported}) == len(exported)
for source,destination in exported:
    assert destination.is_file(), destination
    assert hashlib.sha256(source.read_bytes()).digest() == hashlib.sha256(destination.read_bytes()).digest(), destination
assert set(ROOT.joinpath('charts').rglob('*.svg')) == {d for _,d in exported if d.suffix == '.svg'}

# Frontier exports must preserve benchmark configuration identity.
frontier = json.loads((ROOT / '_build' / '前沿筛选结果.json').read_text(encoding='utf-8'))
for board in frontier['boards'].values():
    for row in board['frontier']:
        for field in ('agent_harness', 'reasoning_effort', 'mapping_kind',
                      'mapping_confidence', 'mapping_note'):
            assert field in row
for table in ROOT.joinpath('_build').glob('前沿*.txt'):
    assert any('Harness' in line for line in table.read_text(encoding='utf-8').splitlines()), table
for doc in [ROOT/'README.md',ROOT/'README.zh.md',ROOT/'BUILD.md',ROOT/'SOURCES.md',ROOT/'charts/README.md']:
    for target in re.findall(r'\]\(([^)]+)\)', doc.read_text(encoding='utf-8')):
        if not target.startswith(('http:', 'https:', '#')):
            assert (doc.parent/target).exists(), (doc,target)
readmes={'en':(ROOT/'README.md').read_text(encoding='utf-8'),
         'zh':(ROOT/'README.zh.md').read_text(encoding='utf-8')}
for lang,s in readmes.items():
    pictures=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',s)
    assert len(pictures)==12 and len(set(pictures))==12, (lang,pictures)
    assert all(p.startswith(f'charts/{lang}/') for p in pictures), (lang,pictures)
svgs=sorted(ROOT.joinpath('charts').glob('*/pareto/*.svg'))
svgs+=sorted(ROOT.joinpath('charts/en/overview').glob('real-price-overview.svg'))
svgs+=sorted(ROOT.joinpath('charts/zh/overview').glob('单价总览.svg'))
svgs+=sorted(ROOT.joinpath('charts').glob('en/overview/*fee-*.svg'))
svgs+=sorted(ROOT.joinpath('charts').glob('zh/overview/*月费*.svg'))
assert len(svgs)==16+2+6
for doc,s in readmes.items():
    for svg in svgs:
        rel=svg.relative_to(ROOT).as_posix()
        assert f']({rel})' in s, (doc,rel)
        assert f']({rel[:-4]}.png)' in s, (doc,rel)
for f in ROOT.joinpath('charts/en').rglob('*'):
    if f.suffix in ('.txt', '.svg', '.html'):
        leaks = sorted(set(re.findall(r'[\u4e00-\u9fff]', f.read_text(encoding='utf-8'))))
        assert not leaks, f'{f}: CJK characters in English output: {"".join(leaks)}'
print(f'PASS: {len(adopted)} adopted rows, {len(exported)} exported files match build hashes, all JSON and bilingual links valid')
for board in data['boards']:
    missing=sorted({p['model'] for p in data['points'] if p[board+'__score'] is None})
    print(board, sum(p[board+'__score'] is not None for p in data['points']), 'scored; missing:', ', '.join(missing))
