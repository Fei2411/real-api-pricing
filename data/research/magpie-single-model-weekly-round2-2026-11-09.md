# Magpie single-model weekly capacity, round2 / 单模型周额度官方等价值

Statistical window: **2026-11-02 00:00 inclusive through 2026-11-09 00:00 exclusive, Asia/Shanghai** (`2026-11-01T16:00:00Z` through `2026-11-08T16:00:00Z`). File timestamps are UTC. [Machine-readable evidence](magpie-single-model-weekly-round2-2026-11-09.json). [Aligned request rows](magpie-single-model-weekly-round2-2026-11-09-aligned-evidence.csv).

**Research-only, not adopted.** This is round2 of the Magpie research series. Round1 remains [local + Tokyo evidence](magpie-local-tokyo-round1-2026-10-21.md) (cutoff 2026-10-21, [PR #130](https://github.com/Fei2411/real-api-pricing/pull/130)). This round answers a different question and does not replace that file or any adopted row.

Merged [PR #218](https://github.com/Fei2411/real-api-pricing/pull/218) is another contributor's Devin Pro samples from issue #210 (2026-10-22 and 2026-11-03). It is not this evidence: request counts, weekly deltas and the claimed Pro label do not match these anonymous A04/A06 intervals. Merged [PR #217](https://github.com/Fei2411/real-api-pricing/pull/217) is Droid Pro issue #131, a different product. Open pull requests #205, #207, #208, #209, #216 and #223 were re-checked on 2026-11-10 Asia/Shanghai; none is the same week and the same source.

## What is measured / 口径

One anonymous subscription account × only Claude Opus 5.5 × 100% of the weekly quota, valued with official API rates at the observed cache mix. USD/week = `100 × sum(sample official API dollars) / sum(weekly quota delta percentage points)`. Each contiguous pure-model run is one segment. Accounts are independent repeated measurements and are not added. Daily and weekly pools are not added.

The Devin plan tier is **unknown**. The logs do not verify Pro, Max or any other tier, and no subscription price was used to fit or check the estimate.

The sensitivity range is an envelope from shifting request timestamps by ±2 minutes and ±5 minutes and moving each run's quota delta by ±1 percentage point, plus the alternate maximum-overlap input treatment. It is not a statistical confidence interval. The figure describes the observed cache-heavy workload only. It is not a workload-independent entitlement and not a guaranteed full-week throughput. Project standard mix (97% / 2.5% / 0.5%) and the Anthropic mix are not applied.

Official Claude Opus 5.5 standard global rates, per million tokens, checked 2026-11-09 Asia/Shanghai: input $4, cache read $0.20, 5-minute cache write $5, 1-hour cache write $8, output $20. Source: [Claude API pricing](https://platform.claude.com/docs/en/about-claude/pricing). Cache field rules: [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching). Official `input_tokens` exclude cache reads and cache creation. The 5-minute and 1-hour write counts are parts of cache creation, not a second charge on top of that total. Output includes thinking; reasoning is not added again. Full 1M context is priced at these standard rates. No batch, fast-mode, region, tool or tax premium is assumed.

Grades use the same local rubric as round1 (`delta_sample_stability_v1`). Medium requires at least 10pp, 30 token-bearing calls, effective segments ≥1.5, weighted CV ≤50%, leave-one-out change ≤35% and rounding ≤25%. High also requires at least 200 calls and effective segments ≥4. These thresholds are not vendor rules or probabilities.

## Medium records / 中置信记录

| Account | Model | Interval (UTC) | USD/week | Sensitivity envelope (USD/week) | Calls | Delta | Segments | Effective segments | Weighted CV | Whole-run leave-one-out | Rounding ratio | Grade |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| A04 | Claude Opus 5.5 | 2026-11-02 07:37:57Z → 2026-11-03 11:10:14Z | 30.36 | 22.87–31.76 | 124 | 79pp | 2 | 1.790818 | 0.4152% | 0.5928% | 2.5316% | medium |
| A06 | Claude Opus 5.5 | 2026-11-02 12:40:13Z → 2026-11-03 14:56:10Z | 30.73 | 26.83–33.53 | 171 | 68pp | 2 | 1.840764 | 0.8451% | 1.1442% | 2.9412% | medium |

Exact values are in the JSON: A04 `30.36141797468355` (sample official value `23.985520200000003`); A06 `30.726950000000002` (sample official value `20.894326`). Both pass medium and miss high, because each has fewer than 200 calls and fewer than 4 effective segments.

A04 intervals: `2026-11-02T07:37:57Z`–`2026-11-02T09:47:10Z` (53pp, 95 calls) and `2026-11-03T10:33:23Z`–`2026-11-03T11:10:14Z` (26pp, 29 calls). A06 intervals: `2026-11-02T12:40:13Z`–`2026-11-02T13:50:57Z` (24pp, 66 token-bearing calls) and `2026-11-03T04:44:26Z`–`2026-11-03T14:56:10Z` (44pp, 105 calls).

Contribution fields left blank where the logs do not say: plan name, price, currency and region. Measurement tool is a Magpie aligned request log. Quota deltas above are weekly-window percentage points, not a 5-hour window.

## Exclusions / 排除

- **A05**, Devin, Opus 5.5 only: recalculated at about $32.23/week (envelope about $27.46–$32.89; 69 calls, 50pp) but **low**, and omitted from `measurements`. It has one contiguous pure-model interval, so effective segments = 1 and leave-one-run-out is undefined. Splitting that interval into smaller bins does not create independent samples.
- **A07**: low-confidence exclusion only. No calculation is imported.
- **Argon**: low-confidence exclusion only. No Argon weekly capacity is recorded. The aligned CSV keeps one A04 zero-token error row at `2026-11-03T10:29:55Z` tagged `gemini-4-argon`, official value $0. It is not part of the Opus 5.5 valuation.
- **Codex Sol**: low-confidence exclusion only. No Codex Sol official-equivalent figure is recorded in this round.

The public CSV has 338 A04/A06 rows. Nineteen are zero-token errors (18 on A06, and the Argon row on A04). Counted calls are the positive-token Opus 5.5 calls inside the selected intervals: 124 and 171. A06's first interval has more log rows than token-bearing calls.

## Limits / 限度

Request-level official-value fields in the reviewed alignment reproduce exactly, and each cache-creation total equals its 5-minute plus 1-hour subcounts. That checks arithmetic inside the supplied windows. It does not authenticate quota endpoints, omitted usage, cycle markers or activity outside those windows. No raw quota history, invoice or collector-adapter audit is in this public file. Public aggregates can reproduce the arithmetic; they cannot independently authenticate private account attribution.

Anonymous labels A04 and A06 are stable references for this round, not service identifiers. No email, credential, host address, request id, prompt or private path is included.

The adopted table, derived prices and charts stay the maintainer's current decisions under [CONVENTIONS.md §3](../../CONVENTIONS.md#3-证据等级).
