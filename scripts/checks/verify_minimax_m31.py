"""Verify the six generated M3.1 rows and all archived screenshot hashes."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from minimax_m31_rows import EVIDENCE, MODEL, subscription_specs


def main() -> None:
    conventions = json.loads((ROOT / 'data/conventions.json').read_text(encoding='utf-8'))
    specs = subscription_specs(conventions)
    doc = json.loads((ROOT / 'data/research' / EVIDENCE).read_text(encoding='utf-8'))
    for source in doc['sources']:
        files = source.get('files', []) + ([source] if 'file' in source else [])
        for item in files:
            p = ROOT / item['file']
            assert p.is_file(), p
            assert hashlib.sha256(p.read_bytes()).hexdigest() == item['sha256'], p
    with (ROOT / 'data/adopted.csv').open(encoding='utf-8-sig', newline='') as f:
        all_rows = list(csv.DictReader(f))
    by_id = {r['plan_id']: r for r in all_rows if r['served_model'] == MODEL}
    assert len(by_id) == 6, f'Expected 6 M3.1 rows, got {len(by_id)}'
    for spec in specs:
        pid, _, price, currency, _, yi, confidence, *_ = spec
        r = by_id[pid]
        tokens = round(round(yi, 3) * 100_000_000)
        expected = price / conventions['usdPerCny'] / tokens * 1_000_000
        assert int(r['monthly_tokens']) == tokens, pid
        assert r['currency'] == currency and r['confidence'] == confidence, pid
        assert r['workload'] == 'measured', pid
        assert r['data_date'] == '2026-10-01', pid
        if pid == 'minimax_m_plan_go_cn':
            assert r['data_date_kind'] == 'sample' and not r['data_date_from'], pid
        else:
            assert r['data_date_kind'] == 'derived', pid
            assert r['data_date_from'] == f'MiniMax M Plan Go (CN) · {MODEL}', pid
        assert '未折算' in r['decision_note'] and '暂估' in r['decision_note'], pid
        assert math.isclose(float(r['price']), price, rel_tol=1e-12), pid
        assert math.isclose(float(r['real_usd_per_mtok']), expected, rel_tol=1e-7), pid
        if pid.endswith('_annual'):
            assert '整年预付' in r['decision_note'], pid
            monthly = by_id[pid.removesuffix('_annual')]
            assert r['monthly_tokens'] == monthly['monthly_tokens'], pid
            assert math.isclose(float(r['price']) / float(monthly['price']), 5 / 6, rel_tol=1e-12), pid
    print('PASS: 6 M3.1 rows; raw notes; annual precision; confidence; screenshot hashes.')


if __name__ == '__main__':
    main()
