# Magpie single-model weekly capacity, round3 / 单模型周额度官方等价值

Statistical window: **2026-11-09 00:00 inclusive through 2026-11-16 00:00 exclusive, Asia/Shanghai** (`2026-11-08T16:00:00Z` through `2026-11-15T16:00:00Z`). The Devin weekly cycle that started `2026-11-08T08:00:00Z` and reset `2026-11-15T08:00:00Z` completed during this window and is the cycle used below; the selected calibration intervals also fall inside the natural week. File timestamps are UTC. [Machine-readable evidence](magpie-single-model-weekly-round3-2026-11-16.json). [Aligned request rows](magpie-single-model-weekly-round3-2026-11-16-aligned-evidence.csv).

**Research-only, not adopted.** This is round3 of the Magpie research series. Round1 remains [local + Tokyo evidence](magpie-local-tokyo-round1-2026-10-21.md) (cutoff 2026-10-21, [PR #130](https://github.com/Fei2411/real-api-pricing/pull/130)). Round2 remains [single-model weekly capacity](magpie-single-model-weekly-round2-2026-11-09.md) for 2026-11-02..11-09 ([PR #225](https://github.com/Fei2411/real-api-pricing/pull/225), merged). This round answers the same question for the next natural week and does not replace those files or any adopted row.

Open [PR #237](https://github.com/Fei2411/real-api-pricing/pull/237) (Copilot / synthetic.new, 2026-11-16) is a different topic. It is not a duplicate of this evidence.

## What is measured / 口径

One anonymous subscription account × only Claude Opus 5.5 × 100% of the weekly quota, valued with official API rates at the observed cache mix. USD/week = `100 × sum(sample official API dollars) / sum(weekly quota delta percentage points)`. Each contiguous pure-model run is one segment. Accounts are independent repeated measurements and are not added or averaged. Daily and weekly pools are not added.

The Devin plan tier is **unknown**. The logs do not verify Pro, Max or any other tier, and no subscription price was used to fit or check the estimate. A05 and A06 are close to each other at the observed mix. A07 is about ten times larger on the same model and must not be averaged with them.

The sensitivity range is an envelope from shifting request timestamps by ±2 minutes and ±5 minutes and moving each run's quota delta by ±1 percentage point, plus the alternate maximum-overlap input treatment. It is not a statistical confidence interval. The figure describes the observed cache-heavy workload only. It is not a workload-independent entitlement and not a guaranteed full-week throughput. Project standard mix (97% / 2.5% / 0.5%) and the Anthropic mix are not applied.

Official Claude Opus 5.5 standard global rates, per million tokens, checked 2026-11-16 11:30 Asia/Shanghai: input $4, cache read $0.20, 5-minute cache write $5, 1-hour cache write $8, output $20. Source: [Claude API pricing](https://platform.claude.com/docs/en/about-claude/pricing). Cache field rules: [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching). Official `input_tokens` exclude cache reads and cache creation. The 5-minute and 1-hour write counts are parts of cache creation, not a second charge on top of that total. Output includes thinking; reasoning is not added again. Full 1M context is priced at these standard rates. No batch, fast-mode, region, tool or tax premium is assumed. These rates are unchanged from the 2026-11-09 round2 check.

Grades use the same local rubric as round1 and round2 (`delta_sample_stability_v1`). Medium requires at least 10pp, 30 token-bearing calls, effective segments ≥1.5, weighted CV ≤50%, leave-one-out change ≤35% and rounding ≤25%. High also requires at least 200 calls and effective segments ≥4. These thresholds are not vendor rules or probabilities. Effective segments are computed on merged contiguous runs, not on the smaller ≥5pp bins inside a run.

## Medium records / 中置信记录

| Account | Model | Interval (UTC) | USD/week | Sensitivity envelope (USD/week) | Calls | Delta | Segments | Effective segments | Weighted CV | Whole-run leave-one-out | Rounding ratio | Grade |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| A05 | Claude Opus 5.5 | 2026-11-08 17:04:48Z → 2026-11-09 16:17:38Z | 30.74 | 19.32–41.02 | 189 | 74pp | 3 | 2.246103 | 1.6082% | 0.9114% | 4.0541% | medium |
| A06 | Claude Opus 5.5 | 2026-11-08 17:04:46Z → 2026-11-09 16:48:02Z | 33.03 | 21.85–35.70 | 111 | 90pp | 2 | 1.984321 | 6.4064% | 7.0036% | 2.2222% | medium |
| A07 | Claude Opus 5.5 | 2026-11-09 16:49:28Z → 2026-11-10 11:23:08Z | 301.02 | 234.20–346.37 | 1407 | 64pp | 3 | 1.917603 | 1.3103% | 0.4451% | 4.6875% | medium |

Exact values are in the JSON: A05 `30.74054945945946` (sample official value `22.7480066`); A06 `33.03454222222222` (sample official value `29.731088`); A07 `301.0235059375` (sample official value `192.6550438`). All three pass medium and miss high, because each has fewer than 4 effective segments; A05 and A06 also have fewer than 200 calls.

A05 intervals: `2026-11-08T17:04:48Z`–`2026-11-08T18:46:54Z` (7pp, 20 calls), `2026-11-08T19:20:41Z`–`2026-11-08T20:47:07Z` (25pp, 28 calls) and `2026-11-09T15:16:00Z`–`2026-11-09T16:17:38Z` (42pp, 141 calls). A06 intervals: `2026-11-08T17:04:46Z`–`2026-11-08T23:03:16Z` (49pp, 60 calls) and `2026-11-09T16:18:57Z`–`2026-11-09T16:48:02Z` (41pp, 51 calls). A07 intervals: `2026-11-09T16:49:28Z`–`2026-11-09T17:44:12Z` (10pp, 256 calls), `2026-11-10T01:06:45Z`–`2026-11-10T08:40:45Z` (44pp, 883 calls) and `2026-11-10T10:03:56Z`–`2026-11-10T11:23:08Z` (10pp, 268 calls).

Observed token mix in the selected intervals, as a share of input + cache-read + cache-write + output: A05 cache-read 91.16%, cache-write 8.46%, output 0.39%, ordinary input 0.0016%; A06 cache-read 88.38%, cache-write 11.25%, output 0.37%, ordinary input 0.0007%; A07 cache-read 93.75%, cache-write 5.81%, output 0.44%, ordinary input 0.0010%. All recorded cache writes in these samples are 5-minute writes (1-hour subcount is 0). Input-overlap versus exclusive-input sensitivity is below 0.02% on each estimate. Results are conditional on this cache-heavy mix.

Independent same-account daily-window evidence, not added to the weekly figure, supports treating the weekly pool as the bottleneck for A05 and A06 under a workload that can be spread across days (daily 100pp official equivalent about $15.4–$17.3 versus weekly about $31–$33). A07 has almost no daily-window inventory in the local history, so other unsaved daily constraints are unknown for that account.

Contribution fields left blank where the logs do not say: plan name, price, currency and region. Measurement tool is a Magpie aligned request log. Quota deltas above are weekly-window percentage points, not a 5-hour window.

## Exclusions / 排除

- **A04**, Devin, Opus 5.5: **inestimable** this week. No ≥5pp same-cycle pure-model weekly interval survived mixed-model and ±2-minute contamination checks. This account qualified in round2; it does not this week. No figure is imported.
- **Argon**: low-confidence exclusion only. No Argon weekly capacity is recorded.
- **SWE-2**: not a public official-API weekly capacity. Self-serve SWE-2 remains free through 2026-11-30 ([Devin models](https://docs.devin.ai/desktop/models), checked 2026-11-16 Asia/Shanghai).
- **Codex**: low-confidence exclusion only. The cycle that resets around 2026-11-16T04:40:17Z had not completed by week end. Earlier 7-day markers in the week are short mid-cycle reissues, not a completed natural weekly window. This is not a republication of round2. No Codex official-equivalent figure is recorded.
- **SuperGrok**: low-confidence exclusion only. The completed 7-day cycle that reset 2026-11-13T14:14:17Z has a single 5pp pure-model run, so effective segments = 1 and leave-one-run-out is undefined. The following cycle had not completed by week end. No SuperGrok official-equivalent figure is recorded.
- **Cursor**: low-confidence exclusion only. Cursor Models / Total pools reset after week end. A Grok Bot weekly pool did complete, but attribution across mixed and partly unpriced models fails. No Cursor weekly capacity is recorded.
- **MiniMax Code**, **Antigravity**, and **WorkBuddy Free**: inestimable or reference-only. See the JSON `excluded` list. Five-hour windows are not multiplied into a weekly figure, and a free credit pool is not a paid weekly subscription capacity.

The public CSV has 1714 rows in the selected A05/A06/A07 intervals. Seven are zero-token rows (2 on A05, 5 on A07) and contribute $0. Counted calls are the positive-token Opus 5.5 calls inside those intervals: 189, 111 and 1407.

## Limits / 限度

Request-level official-value fields in the public alignment reproduce the sample totals, and each cache-creation total equals its 5-minute plus 1-hour subcounts. That checks arithmetic inside the supplied windows. It does not authenticate quota endpoints, omitted usage, cycle markers or activity outside those windows. No raw quota history, invoice or collector-adapter audit is in this public file. Public aggregates can reproduce the arithmetic; they cannot independently authenticate private account attribution.

Overnight and idle reading gaps longer than 6 hours appear in the surrounding weekly history and truncate interval construction. The selected runs themselves do not span such a gap. A longer mid-week gap on A05 and A06 occurs after weekly remaining was already at or near 0. A07's last weekly reading in this cycle is already 0; later cycle-end snapshots for that account are missing. These coverage limits are why the records stay at medium and are not raised to high.

Anonymous labels A05, A06 and A07 are stable references carried over from round2, not service identifiers. No email, credential, host address, request id, prompt or private path is included.

The adopted table, derived prices and charts stay the maintainer's current decisions under [CONVENTIONS.md §3](../../CONVENTIONS.md#3-证据等级).
