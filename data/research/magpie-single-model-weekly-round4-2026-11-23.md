# Magpie single-model weekly capacity, round4 / 单模型周额度官方等价值

Statistical window: **2026-11-16 00:00 inclusive through 2026-11-23 00:00 exclusive, Asia/Shanghai** (2026-11-15T16:00:00Z through 2026-11-22T16:00:00Z). The Devin weekly cycle that started 2026-11-15T08:00:00Z and reset 2026-11-22T08:00:00Z completed during this window and is the cycle used below; both selected calibration intervals also fall inside the natural week. File timestamps are UTC. [Machine-readable evidence](magpie-single-model-weekly-round4-2026-11-23.json). [Aligned request rows](magpie-single-model-weekly-round4-2026-11-23-aligned-evidence.csv).

**Research-only, not adopted.** This is round4 of the Magpie research series. Round1 remains [local + Tokyo evidence](magpie-local-tokyo-round1-2026-10-21.md) (cutoff 2026-10-21, [PR #130](https://github.com/Fei2411/real-api-pricing/pull/130)). Round2 remains [single-model weekly capacity](magpie-single-model-weekly-round2-2026-11-09.md) for 2026-11-02..11-09 ([PR #225](https://github.com/Fei2411/real-api-pricing/pull/225), merged). Round3 remains [single-model weekly capacity](magpie-single-model-weekly-round3-2026-11-16.md) for 2026-11-09..11-16 ([PR #238](https://github.com/Fei2411/real-api-pricing/pull/238), merged). This round answers the same question for the next natural week and does not replace those files or any adopted row.

Same-day merged research PRs #253, #254 and #255 (OpenCode Go / Command Code GOAT catalog items, 2026-11-23) are different topics. They are not duplicates of this evidence.

## What is measured / 口径

One anonymous subscription account x only Claude Opus 5.5 x 100% of the weekly quota, valued with official API rates at the observed cache mix. USD/week = 100 * sum(sample official API dollars) / sum(weekly quota delta percentage points). Each contiguous pure-model run is one segment. Accounts are independent repeated measurements and are not added or averaged. Daily and weekly pools are not added.

The Devin plan tier is **unknown**. The logs do not verify Pro, Max or any other tier, and no subscription price was used to fit or check the estimate.

The sensitivity range is an envelope from shifting request timestamps by +/-2 minutes and +/-5 minutes and moving each run's quota delta by +/-1 percentage point, plus the alternate maximum-overlap input treatment. It is not a statistical confidence interval. The figure describes the observed cache-heavy workload only. It is not a workload-independent entitlement and not a guaranteed full-week throughput.

## Official prices / 官方价

Checked **2026-11-23 11:30 Asia/Shanghai**.

Claude Opus 5.5 standard global API: input $4, cache read $0.20, 5-minute cache write $5, 1-hour cache write $8, output $20 per million tokens. Sources: [Claude API pricing](https://platform.claude.com/docs/en/about-claude/pricing), [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching). Rates are unchanged from the 2026-11-16 round3 check. Full 1M context at standard prices. No batch, fast-mode, region, tool or tax premium is assumed.

## Medium record / 中置信记录

There are **no high-confidence records**. One medium record is published.

| Account | Model | USD / week | Sensitivity envelope USD/week | Plan | Official price source | Qualification | Sample | Attribution | Confidence |
|---|---|---:|---|---|---|---|---|---|---|
| A06 | Claude Opus 5.5 | 29.63 | 15.71-34.81 | Unknown; tier not recorded | Above, checked 2026-11-23 11:30 Asia/Shanghai | 18pp, 34 token-bearing calls, 2 contiguous runs, effective segments 1.67, weighted CV 4.91%, leave-one-out 7.92%, rounding 11.11% | Official sample value $5.3335702; cache-read 93.76% / write 5.94% / output 0.30% / input 0.0010% | Same account, same completed weekly cycle, no remaining rises in the cycle; >=5pp bins merged into contiguous pure-model runs; +/-2-minute window must not contain another token-bearing model | medium (misses high: delta, calls, effective segments, rounding) |

USD/week = 5.3335702 / 0.18 = 29.630945555555556.

Calibration intervals (UTC; Beijing = UTC+8):

- A06 run 1: 2026-11-16 08:25:13-08:53:42 UTC (16:25:13-16:53:42 Asia/Shanghai), remaining 74->61, 13pp, 21 calls, $30.5334 / 100pp. Two zero-token swe-2 HTTP 499 rows inside the window are not counted.
- A06 run 2: 2026-11-16 09:53:02-10:05:28 UTC (17:53:02-18:05:28 Asia/Shanghai), remaining 40->35, 5pp, 13 calls, $27.2846 / 100pp.

Between the two runs, remaining fell 61->40 (about 21pp) on mixed swe-2 / Opus / Sonnet traffic. That interval is excluded. The two runs are not a mechanical split of one contiguous sample.

The completed weekly cycle was observed 100->0. The last cycle reading is 2026-11-18T01:50:47Z, already at 0, leaving 102.2 hours unobserved before the 2026-11-22T08:00:00Z reset. Four collector gaps over 6 hours in the cycle truncated candidate bins conservatively; they are not used to discard the already-clean runs. Input-overlap sensitivity on the published sample is 0.0072%.

This is the same anonymous A06 account as in round2 (medium $30.73 / week) and round3 (medium $33.03 / week) at a similar cache-heavy mix. Those earlier windows are not resubmitted, and the three figures must not be averaged into a new entitlement.

## Important exclusions

Low-confidence diagnostics are listed only as exclusions. They are not medium or high weekly-capacity results.

- **A05 Devin, Claude Opus 5.5**: one completed-cycle pure Opus run (48pp, 69 calls) fails medium because leave-one-out is undefined for a single run. A 7pp GLM-5.3 slice also fails. Mixed-model traffic and a 102.2h unobserved tail after remaining reached 0. No weekly-capacity figure is published.
- **A04 and A07 Devin**: no snapshots or requests in this natural week (last snapshots 2026-11-11). Prior-round figures are not imported.
- **A18 and A19 Devin**: new accounts; 7-day cycles starting 2026-11-22T08:00:00Z had not completed by week end.
- **SWE-2**: still free for self-serve Desktop/CLI through 2026-11-30 (docs.devin.ai/desktop/models, checked 2026-11-23). Nominal list pricing is not used as a public API replacement price.
- **Codex A02, plan plus**: the 7-day cycle that reset 2026-11-16T04:40:17Z completed in this week (100->0) but mixed gpt-6-astra, gpt-6.1-terra and gpt-6.1-sol. Surviving pure astra slices grade low (weighted CV 0.70). A later 7-day marker with pure terra slices had not completed by week end (reset 2026-11-23T04:44:39Z).
- **SuperGrok A09 (Heavy, user-confirmed 2026-11-09; not recorded in logs)**: completed cycle 2026-11-13T14:14:17Z to 2026-11-20T14:14:17Z, observed 100->47. Two pure grok-4.7-build runs (5pp + 25pp, 3073 calls, CV 1.0%, LOO 2.3%) fail medium because effective segments are 1.385 < 1.5. Official global standard grok-4.7 rates, checked 2026-11-23: $2 / $0.50 / $6 per MTok below 200k prompt, 2x above. Fast / Priority / US-regional were not used. The later cycle had not completed. Not published as weekly capacity.
- **Cursor A03 Ultra**: Grok Bot weekly completed 100->0.5 but is a shared pool (grok-bot-default, grok-bot-automation, helios-alpha, grok-bot-cua and others). Most of those labels have no official public API price here. Attribution fails. Cursor Models / Total are monthly-like.
- **MiniMax Code A08, M Plan Build annual**: completed 7-day cycle observed 95->57, almost all MiniMax-M3.1-Flash. One 23pp / 137-call run fails medium (leave-one-out undefined). Credits have no completed issuance period. Official M3.1-Flash rates checked 2026-11-23: $0.15 / $0.015 / $0.60 per MTok. A12 is Free.
- **Antigravity A01**: no snapshots in the natural week (last 2026-11-06). Do not multiply 5-hour windows by 33.6 or add 5-hour and 7-day pools.
- **Antigravity A16**: late appearance, remaining rises, unstable cycle markers, and no local request rows to attribute quota drops.
- **OpenCode Go A17**: a completed 7-day cycle (99->94) has zero local requests, so it is inestimable. The next cycle had not completed.
- **WorkBuddy A10, A11, A13, A14, A15**: snapshot plan is Free plan. Monthly credits reset 2026-11-30, not completed. Free-plan reference only; not paid weekly capacity.

## Method notes and data-quality issues

- Analysis is read-only on local snapshots, quota history and request logs, plus official pricing pages checked 2026-11-23 11:30 Asia/Shanghai. Qualification follows delta_sample_stability_v1 on merged contiguous runs, independently recounted. Already-claimed medium results were rechecked against the same gates and not stretched to fit.
- First-to-last net remaining is not used as weekly consumption. Only same-cycle, non-rising, <=6h-adjacent, >=5pp, +/-2-minute-pure, >=3 token-bearing-request intervals are valued, then merged into contiguous runs.
- Collector cadence has several gaps over 6 hours, including about 21.7h on 2026-11-19/20 UTC, plus 15.6h and 17.3h gaps later in the week. Those truncate bins, which is conservative.
- Identity maps, mailboxes, keys, private account ids and raw transcripts are not in these public files.

## Recommendation

Open a research-only PR: yes, because there is one independently verified medium record (A06). Do not open a PR if that record is later dropped. Do not promote excluded low-confidence diagnostics into the measurements table.
