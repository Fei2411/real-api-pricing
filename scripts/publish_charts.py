"""Export all full-data charts with bilingual filenames and a browsable index."""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / '_build'
CHARTS = ROOT / 'charts'
BOARDS = {
    'AA智力榜': ('aa-intelligence', 'AA Intelligence'),
    'AA编程Agent榜': ('aa-coding-agent', 'AA Coding Agent'),
    'CodeArena榜': ('code-arena', 'Code Arena'),
    'AgentArena榜': ('agent-arena', 'Agent Arena'),
    'OpenDesign设计榜': ('open-design-arena', 'OpenDesign Arena'),
    'TB4终端榜': ('terminal-bench-4', 'Terminal-Bench 4.0'),
    'TB4·AA榜': ('aa-terminal-bench-4', 'Terminal-Bench 4.0 (AA)'),
    'DeepSWE榜': ('deepswe-1-1', 'DeepSWE v1.1'),
}
OVERVIEWS = [
    ('monthly-allowance-overview-fee-0-30-usd', 'Monthly allowance · $0–30 / 月额度 · $0–30'),
    ('monthly-allowance-overview-fee-30-100-usd', 'Monthly allowance · $30–100 / 月额度 · $30–100'),
    ('monthly-allowance-overview-fee-100-300-usd', 'Monthly allowance · $100–300 / 月额度 · $100–300'),
    ('monthly-allowance-overview', 'Monthly allowance · all plans / 月额度 · 全部'),
    ('monthly-allowance-overview-hybrid-scale', 'Monthly allowance · hybrid scale / 月额度 · 混合比例'),
    ('real-price-overview', 'Real unit price / 真实单价总览'),
]
FRONTIER_KINDS = [
    ('frontier-price', 'Frontier price', '前沿单价'),
    ('frontier-allowance', 'Frontier allowance', '前沿额度'),
]


def exports():
    yield BUILD / '帕累托交互图.html', CHARTS / 'zh' / 'pareto' / '帕累托交互图.html'
    for source in sorted(BUILD.iterdir()):
        if source.suffix not in ('.svg', '.png', '.txt'):
            continue
        stem = source.stem
        language = 'en' if '_英文' in stem else 'zh'
        base = stem.replace('_英文', '')
        if base.startswith('帕累托_'):
            if not base.endswith('_全量'):
                continue
            tag = base.removeprefix('帕累托_').removesuffix('_全量')
            slug, title = BOARDS[tag]
            name = f'pareto-{slug}' if language == 'en' else f'帕累托_{tag}'
            category = 'pareto'
        elif '总览' in base:
            category = 'overview'
            name = base
            if language == 'en':
                name = ('monthly-allowance' if base.startswith('额度') else 'real-price') + '-overview'
                if '_月费' in base:
                    name += '-fee-' + base.split('_月费', 1)[1].removesuffix('美元') + '-usd'
                if '混合比例' in base:
                    name += '-hybrid-scale'
                if '表' in base:
                    name += '-table'
        elif base.startswith('前沿'):
            category = 'frontier'
            prefix, tag = base.split('_', 1)
            slug, title = BOARDS[tag]
            name = base if language == 'zh' else f'frontier-{"allowance" if "额度" in prefix else "price"}-{slug}' + ('-table' if '表' in prefix else '')
        else:
            continue
        yield source, CHARTS / language / category / (name + source.suffix)


def main():
    exported = []
    for source, destination in exports():
        destination.parent.mkdir(parents=True, exist_ok=True)
        if '--fee-bands-only' not in sys.argv or '_月费' in source.stem:
            shutil.copyfile(source, destination)
        exported.append(destination)
    destinations = {destination: source for source, destination in exports()}

    def zh_pair(en):
        source = destinations[en]
        return next(d for s, d in exports()
                    if s == source.with_name(source.name.replace('_英文', '')))

    lines = ['# Charts / 图表目录', '',
             'All Pareto charts use the full dataset. Static charts summarize the highest archived configuration reference. / 帕累托图均使用全量套餐；静态图为最高存档配置参考汇总。', '',
             '[All-configuration interactive view / 全配置交互图（中文）](zh/pareto/帕累托交互图.html) · Download the HTML to open locally; Plotly requires network access. / 下载HTML后本地打开，Plotly需要联网。', '',
             'Token mixes and conversion rules: [CONVENTIONS.md](../CONVENTIONS.md). / 负载与换算口径见 [CONVENTIONS.md](../CONVENTIONS.md)。', '']
    header = ['| Chart / 图表 | English SVG | 中文 SVG | English PNG | 中文 PNG |',
              '|---|---|---|---|---|']

    def chart_row(label, en_name, category):
        en = CHARTS / 'en' / category / (en_name + '.svg')
        zh = zh_pair(en)
        links = [f'[{text}]({p.relative_to(CHARTS).as_posix()})' for text, p in [
            ('SVG', en), ('SVG', zh), ('PNG', en.with_suffix('.png')), ('PNG', zh.with_suffix('.png'))]]
        lines.append('| ' + label + ' | ' + ' | '.join(links) + ' |')

    lines += ['## Pareto charts / 帕累托图', ''] + header
    for tag, (slug, title) in BOARDS.items():
        chart_row(f'{title} / {tag}', f'pareto-{slug}', 'pareto')
    lines += ['', '## Overviews / 总览', ''] + header
    for en_name, label in OVERVIEWS:
        chart_row(label, en_name, 'overview')
    lines += ['', '## Frontier subsets / 按榜前沿', ''] + header
    for en_prefix, en_kind, zh_kind in FRONTIER_KINDS:
        for tag, (slug, title) in BOARDS.items():
            chart_row(f'{en_kind} · {title} / {zh_kind} · {tag}', f'{en_prefix}-{slug}', 'frontier')
    tables = [('frontier', f'{en_prefix}-{slug}-table', f'{en_kind} · {title} / {zh_kind} · {tag}')
              for en_prefix, en_kind, zh_kind in FRONTIER_KINDS
              for tag, (slug, title) in BOARDS.items()]
    tables += [('overview', en_name + '-table', label) for en_name, label in OVERVIEWS]
    lines += ['', '## Data tables / 数据表', '',
              '| Table | 中文 TXT | English TXT |', '|---|---|---|']
    for category, en_name, label in tables:
        en = CHARTS / 'en' / category / (en_name + '.txt')
        if en not in destinations:
            continue
        zh = zh_pair(en)
        lines.append(f'| {label} | [TXT]({zh.relative_to(CHARTS).as_posix()}) '
                     f'| [TXT]({en.relative_to(CHARTS).as_posix()}) |')
    (CHARTS / 'README.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    (BUILD / 'published-charts.json').write_text(json.dumps([p.relative_to(ROOT).as_posix() for p in exported], ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Published {len(exported)} files with bilingual index')


if __name__ == '__main__':
    main()
