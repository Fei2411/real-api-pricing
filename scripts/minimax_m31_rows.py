"""Proposed CN M Plan rows. Raw estimates, not standardized API prices."""
from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Any

EVIDENCE = 'minimax-m31-flash-preview-cn-round1-2026-10-01.json'
MODEL = 'minimax-m3.1-flash-preview'
D = Decimal


def subscription_specs(conventions: dict[str, Any]) -> list[tuple]:
    """Return existing build_adopted.sub_row positional arguments.

    Annual subscriptions use upfront annual CNY / 12 as their comparison
    monthly fee, without rounding it to cents before calculating unit prices.
    sub_row remains responsible for the repository's allowance precision.
    """
    root = Path(__file__).resolve().parent.parent
    evidence = json.loads((root / 'data/research' / EVIDENCE).read_text(encoding='utf-8'))
    if evidence['measurement']['accountPlan'] != 'Go':
        raise ValueError('M3.1 baseline must be the contributor-confirmed Go tier.')
    usage = evidence['calculations']['usage']
    start, _, end = evidence['measurement']['checkpoints']
    consumed = D(end['weeklyUsedPercent'] - start['weeklyUsedPercent']) / D(100)
    if consumed <= 0:
        raise ValueError('Weekly quota delta must be positive and within one window.')
    total = sum(usage['endBucketCumulative'].values())
    if total != 23_970_451 or total != usage['endBucketTotal']:
        raise ValueError('Unexpected cumulative token total; re-review the evidence.')
    monthly_go = D(total) / consumed * D(str(conventions['monthWeeks'])) / D(100_000_000)
    source = (
        'https://platform.minimax.cn/docs/m-plan/faq；'
        'https://platform.minimax.cn/docs/m-plan/intro；'
        f'{EVIDENCE}；维护者截图及2026-10-01确认Go'
    )
    common = (
        '未折算、暂估：缺M3.1独立公开计价比例，不借用M3价格；'
        '有分项样本的临时raw例外，2026-10-01 裁定接受（MiniMax 官方未公布 M3.1 价格，暂不折算）。'
        'Go小时累计23,970,451 tok对应周已用4%→10%，5h已用41%→100%；'
        '并非0%→100%完整5h窗口。12:00至12:01起点累计未截图，'
        '全段以起始小时计数为0、期间无其他共享池消耗为假设，两项未单独确认。'
        '周整数显示取整敏感性约13.6974~19.1764亿/月(4周)，不是统计置信区间；'
        '中末差分12,201,679 tok/3pp对应16.2689亿/月，仅作对照。'
        '全口径cache/input/output约95.1823%/3.4854%/1.3323%，'
        '页面96.5%是输入缓存命中率，不等同标准负载缓存占比。'
        '按相同负载与饱和使用比较，不是官方固定token额度。'
    )
    rows = []
    for plan in evidence['calculations']['prices']:
        name = plan['plan']
        multiplier = plan['usageRelativeToGo']
        for annual in (False, True):
            monthly_price = D(plan['annualCny']) / D(12) if annual else D(plan['monthlyCny'])
            pid = f"minimax_m_plan_{name.lower()}_cn" + ('_annual' if annual else '')
            label = f"MiniMax M Plan {name} (CN{' Annual' if annual else ''})"
            note = common
            if multiplier != 1:
                note += f'本档为Go×{multiplier}外推，假设官网倍率适用于周池，非本档独立实测。'
            if annual:
                note += (f"年付¥{plan['annualCny']}，月比较费=年费/12；需整年预付，"
                         '不是按月售价。假设同档年付与月付周池相同，不是一次发放全年token。')
            else:
                note += f"月付常规价¥{plan['monthlyCny']}，由年付实价÷10及官方FAQ还原，不含首月促销。"
            if name == 'Explore':
                note += '截图年付划线价¥1490与119×12=1428不符；保留冲突，不用划线价倒推月付。'
            confidence = 'medium' if name == 'Go' and not annual else 'low'
            rows.append((pid, label, float(monthly_price), 'CNY', MODEL,
                         float(monthly_go * multiplier), confidence, source, note, 'full'))
    if len(rows) != 6 or len({r[0] for r in rows}) != 6:
        raise ValueError('Expected exactly six unique plan/billing-cycle rows.')
    return rows
