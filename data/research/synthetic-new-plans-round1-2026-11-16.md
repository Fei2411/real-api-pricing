# synthetic.new plans, 2026-11-16

Research-only. Machine-readable record: [synthetic-new-plans-round1-2026-11-16.json](synthetic-new-plans-round1-2026-11-16.json). Refs [#201](https://github.com/Fei2411/real-api-pricing/issues/201). Not adopted, and not a close of that issue.

Captured around 2026-11-16 11:14 Asia/Shanghai from [pricing](https://synthetic.new/pricing), [rate limits](https://synthetic.new/rate-limits), and [model pricing](https://synthetic.new/pricing/models). Deployment `a11c34bda99e3a31845471652313553dff1fcb89`.

## What is published

One subscription covers every model. The meter is a **weekly** credit pool. The page says there is no extra five-hour limit and no extra monthly limit. Every **202 minutes** the visible copy returns **2%** of the weekly limit. The rate-limits payload says the tick is **201.6 minutes**, 50 ticks to full. Those two labels are both kept. 201.6 × 50 minutes is 7 days; 202 × 50 is not.

| Plan | Price / month | On the public cards |
|---|---:|---|
| Go | $9 | Fast mode and Infinite mode struck through |
| Standard | $30 | Fast mode and Infinite mode struck through; 1 Usage Reset/month included |
| Big | $90 | Fast mode and Infinite mode included, both Beta |

Fast mode is up to 2× faster and uses 2× the rate limit. Infinite mode does not debit the rate limit, runs slower, and is currently DeepSeek V4.1 Flash only. Big's table still lists a finite DeepSeek allowance (8,108,108,108 tokens, API $754). That is not unlimited value.

The pool is shared. Tokens/mo figures are per model under Synthetic's mix, **90% cached input / 9% uncached input / 1% output**, and are alternatives. Subscription debit uses the discounted rate. The API $/mo column uses the usage-based rate. They are not the same price.

Standard, the tab selected in the captured HTML, shows DeepSeek V4.1 Flash at **2.70B tokens/month** and **API $251/month**. The payload integer is 2,702,702,703 tokens. The same payload has exact integers for Go, Big, and a Bigger key.

## 10× is not the per-model rate

The payload field `upToMonthlyUsageByPlan` is `"90"`, `"300"`, `"900"`, and `"3000"` for Go, Standard, Big, and Bigger, with `lowestPlanToListPriceRatio` 0.1. The captured HTML does not show a sentence "up to $90 / $300 / $900", and the pricing bundle that was downloaded does not read that field. Standard's highest API $/mo in the table is $251, below 300. Discount versus usage-based price is model-specific: DeepSeek input is 10× while its output is 4×; Kimi K3.1 Pro input is 2×; GLM-5.3 Flash input is 1.5×.

Bigger ($300 in the client catalog) is not in `availablePlans` and has no public card. It is not recorded as an offered plan.

## What this record does not do

It does not choose a weekly-to-monthly factor. The client bundle formula `weeklyCreditQuotaCents = round(700 * monthlyPrice / 30)` is copied (210 / 700 / 2,100 / 7,000 cents) and is not turned into another token quota. A check under the page's own mix shows the published token counts are worth exactly the monthly fee at the discounted rates, and their usage-based value floors to the published API dollars. That check is arithmetic on published inputs, not a new allowance and not this repo's standard mix.
