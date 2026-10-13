# CONVENTIONS.md · 项目口径与规则

本文件记录**口径与规则**：怎么算、什么能采、怎么画。每条采用值的取舍（旧值 → 新值 → 依据）记在 [`DECISIONS.md`](DECISIONS.md)；数值型口径（负载比例、汇率、月周数、促销期）只在 [`data/conventions.json`](data/conventions.json) 维护，本文件不重复写数字，以免两处不同步。

口径有变更时：改本文件 + `conventions.json`，在 `DECISIONS.md` 记一笔，证据写入新的 `data/research/*.json`。Agent 工作流程说明在本地 `AGENTS.md`（不入库），不记口径。

## 1. 核心公式

**真实单价 = 订阅月费 ÷ 用户每月实际可用 token**，作 X 轴；Y 轴复用外部榜单分数，画帕累托前沿。核心资产是 X 轴数据的可信度，Y 轴只是转载。

## 2. Token 口径

1. **全口径**：输入 + 缓存读 + 缓存写 + 输出一视同仁，用工具上报的 total。实测值里缓存已经包含在分布中，不单独建模。
2. **饱和使用，默认 1 月 = 4 周**。这是"用满时的价格下限"，对外要明说。厂商明确另设独立月池时保留厂商口径（当前 Kimi 月池 = 周池 × 5）。
3. **每个点 = (订阅套餐, 实际服务模型)**，Y 轴按实际服务模型查分。
4. **负载折算**：凡是美元额度、credits 额度、三段价、模型间价格比换算成 token 的，统一按 `conventions.json` 的负载档折算，这是比较基准，不代表任何平台的实测负载。
   - **标准档** `standardTokenMix`：默认。
   - **低缓存档** `lowCacheTokenMix`：只用于经裁定、实测确实打不到标准缓存的渠道（当前 Step 全系、Google）。缓存固定，输出占比跟随标准档，余量归输入。
   - **Anthropic 档** `anthropicTokenMix`：Anthropic 单独收缓存写入费、未命中输入几乎全部走缓存写，故标准档的普通输入份额按 5 分钟缓存写入价计；用于 Anthropic 按量 API 行，以及经裁定折算的 Anthropic 面板实测。
   - 不为单个渠道或单个用户样本另设专用负载档。某家实测缓存偏低时，先区分是渠道本身的属性还是客户端 harness 的问题。
   - **带 token 分项的实测样本**（面板反推、本地日志、ccusage）：按该模型标价把段内 token 折成 list-worth，÷ 段占额度 → 周 worth × 4 周，再 ÷ 该渠道负载档的混合价得到月 token（2026-09-30 裁定统一；此前只有 Devin Max、Claude Pro × Opus 5.5、Droid Max 这样做）。例外：Factory Droid 的 30 天窗 = 2× 7 天窗，月 = 周 worth × 2（2026-10-03 裁定）。Anthropic 样本的缓存写按实际档位（1h / 5m）计价。
   - **缺分项的样本**（只有合计、只有部分分项、多源加权）和**官方绝对 token 表**：保留 raw total，`workload` 标 `measured`，网页和 README 注明「未折算」。有了分项再补算。
   - 负载比例的修订依据全库带分项的样本审计（见 `standard-token-mix-round*.json`）。修订后要统一重算所有受影响的点，不单独调整某一家。
5. **缓存写入**不单列：标准档里它算作普通输入；Anthropic 档里普通输入份额即按缓存写入价计。
6. **官方倍率各家含义不同，不能直接相乘**：Claude 是 5h 窗口倍率，Max 20x 的周池只有 5x 的约 2 倍；Google 是 token worth；Cursor 是 Agent limits。
7. **同套餐推其他模型**：按官方 credits 比（OpenAI）或标价混合价比（Cursor、Anthropic Sonnet/Opus）推算，置信度标 medium/low。Anthropic Fable 例外：订阅内权重是 Opus 的 4–6.5 倍，而且受周额度 50% 上限约束。
8. **分词器差异、利用率 < 100% 这类二阶修正不做**，脚注一句即可。

## 3. 证据等级

| 级别 | 是什么 |
|---|---|
| high | 维护者面板截图反推、受控打满实测、官方绝对 token/积分表 |
| medium | ccusage + 维护者口述百分比、官方倍率 × 一个 high 基准、多个独立中等来源同量级 |
| low | 单一口述、第三方综述、跨区域/跨档位假设同额度 |

- 每个数字都必须能追到 URL 或维护者原话；找不到就记 notFound，不编数，不用记忆里的旧价格。
- 维护者确认的数字优先级最高。但如果多个独立来源指向别的值，要把矛盾摆出来请维护者裁定，不默默采用，也不默默改掉。
- 同一项有互相矛盾的来源时全部记录，不自行择一。
- **数据日期**（`adopted.csv` 的 `data_date` / `data_date_kind` / `data_date_from`，网页详情面板显示）：记这条额度数据是哪一天的，不是采用值的更新日期。`sample` 取样本的采样日期，多源加权取全部入权样本的起止；`official` 取官方博文/公告的发布日，没有发布日的价表取项目核对该页的日期；`derived` 沿用锚点日期并记锚点。维护者提供的本机截图，以提供当天为采样日期。新增或改数时在 `build_adopted.py` 的 `DATA_DATES` 同步更新，缺日期构建直接报错。

## 4. 各渠道现行口径

- **MiniMax M Plan × M3.1 Flash Preview（暂估例外，2026-10-01）**：投稿者确认国区 Go 基准，提出在缺少可核实的 M3.1 标价比例时临时保留 raw 反推，`workload=measured` 并显式标注未折算。起点小时累计为零、无其他共享池消耗尚未单独确认；月付 Go 标 medium，其余年付/跨档派生标 low。此例外经2026-10-01 裁定接受（MiniMax 官方未公布 M3.1 价格），不改变其他带分项样本必须归一的规则；补齐价格比例后应重新折算。年付以实付年费/12参与月单价比较，保留整年预付说明，不代表一次发放全年额度。

具体采用值与历史演变见 `DECISIONS.md`，这里只记口径层面的约定。

- **Claude Max**：按 2026-09-14 起的永久口径估算。5x 由 20x 按裁定的周池比 2 推出，不用 5h 窗口倍数，也不用旧的 2.25 比。
- **Cursor**：与 SuperGrok 是不同渠道。现行决策见 `cursor-adoption-round8-2026-09-06.json`；round6/7 为历史证据，不覆盖。
- **Kimi**：月池 = 周池 × 5，不套通用的 4 周。¥49 档无 K3 调用权限，只排除该档的 K3 点；K2.7 Standard 所有会员可用。
- **GLM Coding Plan**：按官方周积分和三段积分系数套标准负载。忙时 1×、中间值 1.5×、闲时 2× 是三个独立情景点，不互相替代。
- **Step Plan**：按阶跃国内站官方月度 Credit 池（1M Credit = ¥1）经人民币三段价折算，用低缓存档 `lowCacheTokenMix`；国际站美元牌价不同，不采用；旧 Coding Plan 的 Prompt/5h 口径仅留作证据。
- **Google**：Antigravity 额度按 API worth 合池扣减（官方机制，段内已实证）。实测样本按 Gemini 标价折 worth 后用低缓存档换算（实测缓存 82~84%，打不到标准档；2026-09-30 裁定，取代 2026-09-21 的 raw 口径）；Ultra 5x/20x 按官方 worth 倍率派生，置信度 low。
- **汇率**：取 `conventions.json` 的 `usdPerCny`（历史字段名，实际方向为 CNY/USD），来源日期在 `exchangeRate`。不改历史 research 文件里的旧汇率。
- **促销**：促销口径必须标截止日，到期后复核。订阅内明确不计额度的模型，真实单价记为 ≈$0，用专用刻度位表示。
- **数据快照日期**：`data/conventions.json` 的 `updatedAt` 是网页与 README 显示的快照日期（经 compute.py 写入 `derived/points.json` 的 generatedAt）；改采用值或口径时同步改为当天；CI 会在 adopted.csv 变化而 updatedAt 未推进过 base 分支时报错；base 已是当天时，updatedAt 与 base 相同且为今天（UTC 或 UTC+8 任一）也算通过（`scripts/checks/verify_snapshot_date.py`）。

## 5. 出图规则

- X 轴对数，右侧更便宜（和 Arena 一致）。先画所有点，再连右上包络作为前沿；非前沿点用淡色。
- 前沿线两端延伸：最高分点向左（更贵一侧）水平延伸，最便宜点向右延伸。
- 同位置的点合并成一个，标签用 `/` 连。
- 免费档不画（对数轴画不了）；Y 轴没分的模型不画，但要在输出里列出来。
- 每张榜单一张图，标题写清榜单名和快照日期；不同榜单的分数不混合。
- 公开 README 和 charts 默认使用全量图；精选图只作内部对照，不作为默认公开视图。
- **配色**：用明亮、干净的高饱和色，不用深灰或脏色。OpenAI 绿、Claude 橙（深陶土橙）、SpaceXAI（原 xAI）紫、Cursor 黄、Kimi 天蓝、GLM 黑、MiniMax 粉、Alibaba 红、OpenCode 青、DeepSeek 蓝、小米橙（亮橙，与 Claude 深陶土靠明度区分）、StepFun 电青 #00F4E5；Gemini 若入库用黄绿。前沿线用近黑色。具体色值只在 [`config/channel-colors.json`](config/channel-colors.json) 维护（网站与全部 Python 图共用），同文件 `channels` 数组也是唯一的 id 前缀 → 渠道映射；未指定色相的渠道中 Command Code、Ollama 用浅色调区分，Devin 用中性灰 #A1A1AA（指定；中灰，不是深灰）。Factory（Droid）用群青 #0A0ABF。改色后跑 `scripts/checks/verify_palette.py`：数据中出现的渠道两两 CIEDE2000 色差须 ≥ 15，不为品牌色开例外（确需例外时登记在 `brandPairs`）。
- **单价精度**：`real_usd_per_mtok` 存 8 位有效数字，排序与前沿判定都用原值；图表、排名、表格按至多 5 位小数的短格式显示，网页详情弹窗显示 6 位有效数字完整值。不要为了显示好看在数据里截短单价。
- **额度/单价总览**：双栏对数轴，不分量级面板；中文额度用"亿"，英文用 billion；每行数值旁加渠道缩写，图例置顶。
- **按榜前沿精简版**：从全量订阅/API（含不计额度的 ≈$0 促销点，与帕累托图一致）中按"单价越低、分数越高"筛选，至少一项严格更好才算支配；同价同分的不同套餐都保留。
