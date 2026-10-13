# CLI 指令与输出参考

状态：0.1.0 已实现，基于 TypeScript 与 Commander；npm 包名为 `real-api-pricing`，维护者发布后可用 `npm install -g real-api-pricing` 安装，当前可从仓库构建或安装本地 tarball。默认自动联网，失败时依次使用有效缓存、内置快照，正常回退不增加选项或网络警告。

下列数值与 `Source: bundled` 示例来自 **2026-10-01** 的历史验证；show/compare 的英文证据节选使用 **2026-10-02** 快照已有的译文。表格按字段整理，较长的详情只列节选；帮助采用当前英文输出。

同步主仓库 main 的 `9be0bb9` 后，当前内置快照为 **2026-10-03**，与本次验证的线上文件一致。该快照重新完成 Chromium 61 个场景、累计 5,176 行，以及英文详情、compare、CSV 和移动端检查，均通过。Droid 月额度已按上游调整，历史示例不代表当前价格或额度；实际日期与来源以每次查询的元信息为准。验证范围与 CSV 对账规则见 [CLI 设计规范](cli-design.md)，安装见 [CLI README](../cli/README.md)。

命令名为 `rap`。默认表格、默认返回全部匹配记录；表头、套餐显示、帮助及错误信息固定使用英文。`Model`、`Company`、`Channel`、`Plan` 在每张价格记录表中独立成列，即使筛选后值相同也保留。`Company` 是模型开发公司，对应网站 `vendors`；`Channel` 是提供套餐的访问渠道。例如 Claude 由 Anthropic 开发，Droid Max 的渠道是 Factory。

下文标为 **stdout** 的 Markdown 表格是对应终端表格的字段示意，省略边框及换行；标为 **stderr** 的代码块是独立的结果说明，不混入表格、JSON 或 CSV。完整 Point ID 可以在窄终端换行，但不得截断。月额度的 B 表示十亿 token，真实单价单位为 USD/MTok；月费保留美元符号，原币 CNY 价格附在同一格。没有月额度或月费的值显示 —。Billing、Confidence 与网站使用相同英文显示名；JSON/CSV 保留原始标识和数值。排名与查询价格使用紧凑格式，show/compare 主价最多 6 位有效数字；query 分数最多 2 位小数，详情分数最多 4 位小数。排序使用原始精度。

## 1. 指令总览

| 指令 | 用途 | 默认次序 |
| --- | --- | --- |
| `rap price` | 对齐网站真实单价排名，包含订阅和按量 API | 真实单价升序 |
| `rap allowance` | 对齐网站月额度排名，只保留有月额度的订阅 | 月额度降序 |
| `rap list models` | 发现模型 ID、公司与覆盖记录数 | 模型 ID 升序 |
| `rap list companies` | 发现模型开发公司的标识与显示名 | 公司 ID 升序 |
| `rap list plans` | 发现套餐 ID、渠道及覆盖模型数 | 套餐 ID 升序 |
| `rap list channels` | 发现访问渠道及覆盖记录数 | 渠道名称升序 |
| `rap list boards` | 发现榜单、指标与独立快照日期 | 榜单 ID 升序 |
| `rap query` | 通用表格查询；自定义排序、评测配置与前沿 | 真实单价升序 |
| `rap show <point-id>` | 一条记录的价格、额度、采用依据与配置映射 | 指定记录 |
| `rap compare <point-id> <point-id>...` | 比较至少两条记录 | 保留输入顺序 |
| `rap info` | 查询依据、数量、负载与汇率口径 | 固定字段次序 |
| `rap --help` / `rap <command> --help` | 全局或子命令帮助 | — |
| `rap --version` | CLI 软件版本 | — |

全局数据选项为 `--data <site.json>`、`--format table|json|csv`，没有额外联网、离线或刷新选项。软件版本与数据快照日期分开；数据命令默认请求 `https://realapipricing.com/data/site.json`，利用 ETag/304 复用已校验缓存，失败时自动回退到缓存或内置快照。请求及响应体读取总超时为 3 秒。

数据保存在本地：仓库的 `data/adopted.csv` 与 `derived/*.json` 通过共享适配器分别生成网站的 `web/public/data/site.json` 和 CLI 的 `cli/data/site.json`；两者的快照内容相同。`npm pack` 将 CLI 快照随本地安装包携带，数据路径相对安装位置定位，在任意工作目录均可读取。`--data <site.json>` 可指定其他本地快照，显式文件覆盖会完全跳过联网和缓存。默认缓存位置及读取规则见 [CLI README](../cli/README.md#data-and-freshness)。

## 2. `rap price`：真实单价排名

对应网页 `#lang=en&view=price&vendors=Anthropic`。默认返回 Anthropic 的全部 29 条价格记录，包括第三方渠道和按量 API。下面显式限制为前三条：

```sh
rap price --company Anthropic --limit 3
```

**stdout**：

| Rank | Model | Company | Channel | Plan | USD/MTok | Monthly tokens | Monthly fee USD | Billing | Confidence | Point ID |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| 1 | Claude Sonnet 5 | Anthropic | Anthropic | Claude Pro | $0.00309 | 6.472 B | $20 | Subscription | Medium | claude_pro::claude-sonnet-5 |
| 2 | Claude Sonnet 5 | Anthropic | Anthropic | Claude Max 20x (9/14+) | $0.0051 | 39.25 B | $200 | Subscription | Medium | claude_max_20x::claude-sonnet-5 |
| 3 | Claude Sonnet 5 | Anthropic | Anthropic | Claude Max 5x (9/14+) | $0.0051 | 19.625 B | $100 | Subscription | Low | claude_max_5x::claude-sonnet-5 |

**stderr**：

```text
Snapshot: 2026-10-01 | Source: bundled | View: price
Total: 29 | Returned: 3 | Truncated: true
Order: USD/MTok ascending; ties by Point ID.
```

Company 与 Channel 可以同时筛选。以下查询仍然选择 Anthropic 模型，但只看 Factory 渠道：

```sh
rap price --company Anthropic --channel Factory --limit 3
```

**stdout**：

| Rank | Model | Company | Channel | Plan | USD/MTok | Monthly tokens | Monthly fee USD | Billing | Confidence | Point ID |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| 1 | Claude Sonnet 5.5 | Anthropic | Factory | Droid Max | $0.01979 | 10.104 B | $200 | Subscription | Medium | droid_max::claude-sonnet-5.5 |
| 2 | Claude Opus 5.5 | Anthropic | Factory | Droid Max | $0.03959 | 5.052 B | $200 | Subscription | Medium | droid_max::claude-opus-5.5 |
| 3 | Claude Opus 4.8 | Anthropic | Factory | Droid Max | $0.04949 | 4.042 B | $200 | Subscription | Medium | droid_max::claude-opus-4.8 |

**stderr**：

```text
Snapshot: 2026-10-01 | Source: bundled | View: price
Total: 7 | Returned: 3 | Truncated: true
Order: USD/MTok ascending; ties by Point ID.
```

price 始终一点一行，内部固定选最高匹配配置；`--sort`、`--min-score`、`--scored-only`、`--frontier` 和显式 `--config` 不适用于排名视图。直接传给 price 时 Commander 报未知参数；通过 query 的排名视图传入时会报告只适用于 table。

按量 API 仍能在 price 中查询，它的月额度和月费为不适用：

```sh
rap price --company Anthropic --model claude-opus-5.5 --billing metered
```

**stdout**：

| Rank | Model | Company | Channel | Plan | USD/MTok | Monthly tokens | Monthly fee USD | Billing | Confidence | Point ID |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| 1 | Claude Opus 5.5 | Anthropic | Anthropic | Claude Opus 5.5 API | $0.419 | — | — | Metered API | High | anthropic_opus55_api::claude-opus-5.5 |

**stderr**：

```text
Snapshot: 2026-10-01 | Source: bundled | View: price
Total: 1 | Returned: 1 | Truncated: false
Order: USD/MTok ascending; ties by Point ID.
```

原币为 CNY 的套餐同时保留采用美元月费与原币价，不重新按汇率覆盖采用值：

```sh
rap price --plan kimi_allegretto_cn --model kimi-k3
```

**stdout**，`<br>` 表示同一单元格内换行：

| Rank | Model | Company | Channel | Plan | USD/MTok | Monthly tokens | Monthly fee USD | Billing | Confidence | Point ID |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| 1 | Kimi K3 (v1) | Kimi | Kimi | Kimi Allegretto | $0.02688 | 1.451 B | $39<br>¥199 | Subscription | Medium | kimi_allegretto_cn::kimi-k3 |

**stderr**：

```text
Snapshot: 2026-10-01 | Source: bundled | View: price
Total: 1 | Returned: 1 | Truncated: false
Order: USD/MTok ascending; ties by Point ID.
```

不计额度促销点没有月 token 分母，额度列显示 —；促销说明在该记录的续行：

```sh
rap price --plan devin_pro --model swe-2
```

**stdout**：

| Rank | Model | Company | Channel | Plan | USD/MTok | Monthly tokens | Monthly fee USD | Billing | Confidence | Point ID |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| 1 | SWE-2 | Devin | Devin | Devin Pro (promo until 10/31) | ≈$0 | — | $20 | Subscription | Medium | devin_pro::swe-2 |

该行之后的续行字段：

```text
Point ID: devin_pro::swe-2
Promotion: promo until 2026-10-31, unmetered · $20 / mo
```

**stderr**：

```text
Snapshot: 2026-10-01 | Source: bundled | View: price
Total: 1 | Returned: 1 | Truncated: false
Order: USD/MTok ascending; ties by Point ID.
```

## 3. `rap allowance`：月额度排名

对应网页 `#lang=en&view=allowance&vendors=Anthropic`。API 的月额度不适用，不进入这个排名；也不把未知额度解释为无限额度。Anthropic 筛选共有 24 条：

```sh
rap allowance --company Anthropic --limit 3
```

**stdout**：

| Rank | Model | Company | Channel | Plan | USD/MTok | Monthly tokens | Monthly fee USD | Billing | Confidence | Point ID |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| 1 | Claude Sonnet 5 | Anthropic | Anthropic | Claude Max 20x (9/14+) | $0.0051 | 39.25 B | $200 | Subscription | Medium | claude_max_20x::claude-sonnet-5 |
| 2 | Claude Opus 5.5 | Anthropic | Anthropic | Claude Max 20x (9/14+) | $0.00634 | 31.538 B | $200 | Subscription | Medium | claude_max_20x::claude-opus-5.5 |
| 3 | Claude Sonnet 5 | Anthropic | Anthropic | Claude Max 5x (9/14+) | $0.0051 | 19.625 B | $100 | Subscription | Low | claude_max_5x::claude-sonnet-5 |

**stderr**：

```text
Snapshot: 2026-10-01 | Source: bundled | View: allowance
Total: 24 | Returned: 3 | Truncated: true
Order: monthly tokens descending; ties by Point ID.
Fee band: all
```

月费档位与网站一致，`0-30` 包含 $30，`30-100` 不包含 $30、包含 $100，`100-300` 不包含 $100、包含 $300；`all` 也保留超过 $300 的套餐。

```sh
rap allowance --company Anthropic --fee-band 0-30 --limit 3
```

**stdout**：

| Rank | Model | Company | Channel | Plan | USD/MTok | Monthly tokens | Monthly fee USD | Billing | Confidence | Point ID |
| ---: | --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| 1 | Claude Sonnet 5 | Anthropic | Anthropic | Claude Pro | $0.00309 | 6.472 B | $20 | Subscription | Medium | claude_pro::claude-sonnet-5 |
| 2 | Claude Opus 5.5 | Anthropic | Anthropic | Claude Pro | $0.00655 | 3.054 B | $20 | Subscription | High | claude_pro::claude-opus-5.5 |
| 3 | Claude Opus 4.8 | Anthropic | Anthropic | Claude Pro | $0.00772 | 2.589 B | $20 | Subscription | Low | claude_pro::claude-opus-4.8 |

**stderr**：

```text
Snapshot: 2026-10-01 | Source: bundled | View: allowance
Total: 6 | Returned: 3 | Truncated: true
Order: monthly tokens descending; ties by Point ID.
Fee band: 0-30
```

## 4. `rap list`：发现可查询资源

list 搜索资源自身的 ID 和显示名，返回资源汇总，不展开价格点。先按适用的 Company/Channel 条件确定统计范围，再按资源搜索和 limit 输出；计数为该范围内的记录数。支持情况如下，不相关参数直接报错：

| 资源 | `--search` / `--limit` | `--company` / `--vendor` | `--channel` |
| --- | --- | --- | --- |
| models | 支持 | 支持 | 支持 |
| companies | 支持 | 不适用 | 支持 |
| plans | 支持 | 支持 | 支持 |
| channels | 支持 | 支持 | 不适用 |
| boards | 支持 | 不适用 | 不适用 |

### `rap list models`

用途：查准确的 Model ID；Company 单列，不混入模型名。

```sh
rap list models --company Anthropic --search claude-opus-5.5
```

**stdout**：

| Model ID | Model | Company ID | Company | Plans | Channels | Points |
| --- | --- | --- | --- | ---: | ---: | ---: |
| claude-opus-5.5 | Claude Opus 5.5 | Anthropic | Anthropic | 7 | 3 | 7 |

**stderr**：

```text
Snapshot: 2026-10-01 | Source: bundled | Resource: models
Total: 1 | Returned: 1 | Truncated: false
```

### `rap list companies`

用途：查模型开发公司的原始标识和显示名。`--company` 精确筛选用 Company ID；例如 Muse 的显示名是 Meta，Cognition 的显示名是 Devin，仍保留原始 ID。

```sh
rap list companies --search Anthropic
```

**stdout**：

| Company ID | Company | Models | Plans | Points |
| --- | --- | ---: | ---: | ---: |
| Anthropic | Anthropic | 7 | 12 | 29 |

**stderr**：

```text
Snapshot: 2026-10-01 | Source: bundled | Resource: companies
Total: 1 | Returned: 1 | Truncated: false
```

### `rap list plans`

用途：查套餐 ID 和访问渠道。一个套餐可以覆盖多个模型、多个开发公司；`Models` 是覆盖的不同模型数，不能把套餐视为只属于一个公司。

```sh
rap list plans --channel Factory --search droid_max
```

**stdout**：

| Plan ID | Plan | Channel | Companies (IDs) | Models | Points |
| --- | --- | --- | --- | ---: | ---: |
| droid_max | Droid Max | Factory | Alibaba, Anthropic, DeepSeek, Google, Kimi, MiniMax, Mistral, OpenAI, SpaceXAI, Zhipu, other | 27 | 27 |

**stderr**：

```text
Snapshot: 2026-10-01 | Source: bundled | Resource: plans
Total: 1 | Returned: 1 | Truncated: false
```

### `rap list channels`

用途：查访问渠道。以下输出统计 Factory 提供的 Anthropic 模型，不是 Factory 全部模型。

```sh
rap list channels --company Anthropic --search Factory
```

**stdout**：

| Channel | Models | Plans | Points |
| --- | ---: | ---: | ---: |
| Factory | 6 | 2 | 7 |

**stderr**：

```text
Snapshot: 2026-10-01 | Source: bundled | Resource: channels
Total: 1 | Returned: 1 | Truncated: false
```

### `rap list boards`

用途：查独立榜单的 ID、指标和快照。榜单日期不同于价格快照日期；分数不能跨榜单混比。

```sh
rap list boards --search aa_intelligence_index
```

**stdout**：

| Board ID | Board | Metric | Board snapshot | Configurations |
| --- | --- | --- | --- | ---: |
| aa_intelligence_index | Artificial Analysis Intelligence Index v4.3 | Intelligence Index | 2026-09-22 | 126 |

**stderr**：

```text
Snapshot: 2026-10-01 | Source: bundled | Resource: boards
Total: 1 | Returned: 1 | Truncated: false
```

## 5. `rap query`：通用查询

默认 `--view table`，可筛选精确模型、公司、渠道、套餐、计费类型、置信度和数值范围，默认按真实单价升序。表格不要求有评测分数。

```sh
rap query --model claude-opus-5.5 --channel Factory
```

**stdout**：

| Model | Company | Channel | Plan | USD/MTok | Monthly tokens | Monthly fee USD | Billing | Confidence | Point ID |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| Claude Opus 5.5 | Anthropic | Factory | Droid Max | $0.03959 | 5.052 B | $200 | Subscription | Medium | droid_max::claude-opus-5.5 |
| Claude Opus 5.5 | Anthropic | Factory | Droid Pro | $0.05236 | 0.382 B | $20 | Subscription | Low | droid_pro::claude-opus-5.5 |

**stderr**：

```text
Snapshot: 2026-10-01 | Source: bundled | View: table
Total: 2 | Returned: 2 | Truncated: false
Order: price:asc
```

`rap query --view price` 与 `rap price` 的参数、数据、排序和输出相同；`rap query --view allowance` 与 `rap allowance` 相同，不另造一套排名：

```sh
rap query --view price --company Anthropic --limit 3
# stdout/stderr 与第 2 节第一个示例一致。

rap query --view allowance --company Anthropic --limit 3
# stdout/stderr 与第 3 节第一个示例一致。
```

评测查询只在 table 中展开配置。以下同一价格点输出三个配置，价格与额度重复是因为配置不同；不是三份可累加额度。

```sh
rap query --plan droid_max --model claude-opus-5.5 \
  --board aa_intelligence_index --config all --sort score:desc \
  --limit 3
```

**stdout**，价格区域：

| Model | Company | Channel | Plan | USD/MTok | Monthly tokens | Monthly fee USD | Billing | Confidence | Point ID |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| Claude Opus 5.5 | Anthropic | Factory | Droid Max | $0.03959 | 5.052 B | $200 | Subscription | Medium | droid_max::claude-opus-5.5 |
| Claude Opus 5.5 | Anthropic | Factory | Droid Max | $0.03959 | 5.052 B | $200 | Subscription | Medium | droid_max::claude-opus-5.5 |
| Claude Opus 5.5 | Anthropic | Factory | Droid Max | $0.03959 | 5.052 B | $200 | Subscription | Medium | droid_max::claude-opus-5.5 |

**stdout**，核心表下方的评测区域节选，按相同行序展示；完整输出另含 Point ID、Harness、Mode、Estimated、Self-reported、Best ties：

| Score | Effort | Variant | Configuration ID | Mapping confidence | Quota effort matched |
| ---: | --- | --- | --- | --- | --- |
| 57.62 | Max | Claude Opus 5.5 (max with fallback) | aa_intelligence_index:6df46e4e9119d1e1 | Medium | unverified |
| 55.99 | xhigh | Claude Opus 5.5 (xhigh with fallback) | aa_intelligence_index:4c3fe13d36952d4f | Medium | unverified |
| 53.58 | High | Claude Opus 5.5 (high with fallback) | aa_intelligence_index:c4632b7e15588786 | Medium | unverified |

**stderr**：

```text
Snapshot: 2026-10-01 | Source: bundled | View: table
Board: aa_intelligence_index | Board snapshot: 2026-09-22 | Config: all
Total: 5 | Returned: 3 | Truncated: true
Order: score:desc
```

`--config best` 默认选所筛配置中的最高分；`--frontier` 须指定 `--board`，在完整筛选结果上计算后才应用 limit。无分记录默认保留，只有 `--min-score`、`--scored-only` 或 `--frontier` 才排除它们。JSON/CSV 的字段结构、前沿与缺失值规则见设计规范。

## 6. `rap show`：单条记录与采用依据

用途：用精确 Point ID 查看数据及证据。默认展示全部已映射榜单；下面用 `--board` 缩小到一个榜单，仍展示该榜单所有匹配配置。

```sh
rap show 'droid_max::claude-opus-5.5' --board aa_intelligence_index
```

**stdout**，核心数据：

| Model | Company | Channel | Plan | USD/MTok | Monthly tokens | Monthly fee USD | Billing | Confidence | Point ID |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| Claude Opus 5.5 | Anthropic | Factory | Droid Max | $0.0395883 | 5.052 B | $200 | Subscription | Medium | droid_max::claude-opus-5.5 |

**stdout**，原始数值与采用依据字段节选；完整表还包括 Promotion、List blended USD/MTok：

| Field | Value |
| --- | --- |
| Model ID | claude-opus-5.5 |
| Company ID | Anthropic |
| Plan ID | droid_max |
| Original monthly fee | 200 USD |
| Local price | — |
| Monthly tokens, raw | 5,052,000,000 |
| USD/MTok, raw | 0.039588282 |
| Workload | Anthropic workload: 97% cache reads / 2.5% cache writes / 0.5% output |
| Data date | 2026-09-29 |
| Date kind | sample |
| Date inherited from | — |
| Unmetered | false |
| Promotion until | — |
| Plan generation |  |
| Official model prices | Official API list (cached / in / out, per MTok): $0.2 / $4 / $20 |
| Subscription price assumption | Full use of the adopted allowance |

**stdout**，`Source` 和 `Decision note` 优先显示网站的现有英文译文，缺译文时使用原文，允许按终端宽度换行。此处 `note_en` 与 `decision_note_en` 相同，因此不重复输出 `Note`：

```text
Source:
Maintainer's local Factory Droid measurement: weekly quota (7-day rolling) used 1%→5% segment (xhigh) +35,598,616 tok and 5%@08:13→9%@12:40 segment (high, new session 47f9711d) +36,567,946 tok, total +72,166,562 tok all claude-opus-5-5 (auto 0 delta; glm-5.3-flash +50,317 belongs to the free Droid Core pool and is not counted); total breakdown in 793,017 / out 375,172 / cache_create 3,640,056 / cache_read 67,311,924 / thinking 46,393; droid-opus55-max-round1-2026-09-29.json; https://factory.ai/pricing Max $200/month

Decision note:
First Factory Droid point, normalized on the same basis as devin_max×opus-5.5: the combined 1→9 segment mix — cache read 93.27% / cache write 5.04% / input 1.10% / output 0.52% / thinking 0.06% (hit 93.82%) — deviates from the standard tier; at Opus 5.5 list prices cached $0.2 / 5m write $5 / in $4 / out $20 (thinking 46,393 unbilled per ruling; consistent with factoryCredits 16,935,482 ≈ worth÷$4×1.6), segment worth $42.34 ÷8%×4 weeks = $2,116.91/month list-worth ÷ Anthropic-tier blended price $0.419/MTok = 5.052B; 1%/9% are rounded readings — Δpp∈[7,9] maps to about 4.491B~5.774B; the cache-write-at-1h-$8 sensitivity 5.391B not adopted; the raw-total basis 72,166,562÷8%×4 weeks = 3.608B (weekly pool 902,082,025 raw) kept for comparison; factoryCredits 16,935,482 ≈ 212M credits/week; the two 4pp segments each carry 8.90M/9.14M tok per pp (2.7% apart) — effort only affects rate; Factory also has 5h and 30-day rolling windows — if the 30-day window is below 4× the weekly pool this value skews high; the Pro $20 / Plus $100 official pages state only about 1/10 and 1/5 of Max usage, not derived
```

**stdout**，证据链接：

| Evidence | URL |
| --- | --- |
| https://factory.ai/pricing | https://factory.ai/pricing |
| droid-opus55-max-round1-2026-09-29.json | /data/evidence/droid-opus55-max-round1-2026-09-29.json |

证据的 `/data/...` 是快照保存的相对网站路径，CLI 原样保留该路径。

**stdout**，榜单与配置字段节选；完整输出另含 Board ID、Harness、Mode，以及每条配置的完整字段表。Benchmark source 与 Record note 优先使用配置中的 source_en 与 record_note_en：

| Board ID | Board | Board snapshot |
| --- | --- | --- |
| aa_intelligence_index | Artificial Analysis Intelligence Index v4.3 | 2026-09-22 |

| Configuration ID | Variant | Score | Effort | Estimated | Self-reported | Mapping confidence | Quota effort matched |
| --- | --- | ---: | --- | --- | --- | --- | --- |
| aa_intelligence_index:6df46e4e9119d1e1 | Claude Opus 5.5 (max with fallback) | 57.6224 | Max | false | false | Medium | unverified |
| aa_intelligence_index:4c3fe13d36952d4f | Claude Opus 5.5 (xhigh with fallback) | 55.9874 | xhigh | false | false | Medium | unverified |
| aa_intelligence_index:c4632b7e15588786 | Claude Opus 5.5 (high with fallback) | 53.5832 | High | false | false | Medium | unverified |
| aa_intelligence_index:b44090b237d31264 | Claude Opus 5.5 (medium with fallback) | 51.2435 | Medium | false | false | Medium | unverified |
| aa_intelligence_index:4dae1243cd80cd14 | Claude Opus 5.5 (low with fallback) | 42.3078 | Low | false | false | Medium | unverified |

```text
Benchmark source: https://artificialanalysis.ai/leaderboards/models
Record note: v4.3.2 original precision (page shows integer 58). Released 9/22, all five tiers listed the same day and topped the board (next-highest Fable 5.1 max 53.35). A slug without a -max suffix is the max tier. The AA page notes releaseDate 2026-09-22; the other four tiers are marked 9-17 (per-tier measurement dates).
Mapping kind: model_configuration_reference
Mapping note: Exact served-model reference; quota-measurement effort is unverified.
```

**stderr**：

```text
Snapshot: 2026-10-01 | Source: bundled
Board: aa_intelligence_index | Board snapshot: 2026-09-22
Total: 1 | Returned: 1 | Truncated: false
```

## 7. `rap compare`：比较指定价格点

用途：比较官方套餐与第三方渠道，不将同一模型视为同一套餐。保留输入次序，先展示两条核心记录，再逐项对齐采用依据；指定榜单时附加最高配置。至少需要两个不同的精确 Point ID。

```sh
rap compare 'claude_max_20x::claude-opus-5.5' \
  'droid_max::claude-opus-5.5' --board aa_intelligence_index
```

**stdout**，核心数据：

| Model | Company | Channel | Plan | USD/MTok | Monthly tokens | Monthly fee USD | Billing | Confidence | Point ID |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| Claude Opus 5.5 | Anthropic | Anthropic | Claude Max 20x (9/14+) | $0.00634156 | 31.538 B | $200 | Subscription | Medium | claude_max_20x::claude-opus-5.5 |
| Claude Opus 5.5 | Anthropic | Factory | Droid Max | $0.0395883 | 5.052 B | $200 | Subscription | Medium | droid_max::claude-opus-5.5 |

**stdout**，比较字段节选：

| Field | Claude Max 20x (9/14+) | Droid Max |
| --- | --- | --- |
| Point ID | claude_max_20x::claude-opus-5.5 | droid_max::claude-opus-5.5 |
| Monthly tokens, raw | 31,538,000,000 | 5,052,000,000 |
| USD/MTok, raw | 0.0063415562 | 0.039588282 |
| Original monthly fee | 200 USD | 200 USD |
| Workload | Anthropic workload: 97% cache reads / 2.5% cache writes / 0.5% output | Anthropic workload: 97% cache reads / 2.5% cache writes / 0.5% output |
| Data date | 2026-09-22~2026-09-27 | 2026-09-29 |
| Date kind | sample | sample |
| Date inherited from | — | — |
| Promotion until | — | — |
| Unmetered | false | false |
| Plan generation |  |  |
| Board | aa_intelligence_index | aa_intelligence_index |
| Board snapshot | 2026-09-22 | 2026-09-22 |
| Score | 57.6224 | 57.6224 |
| Effort | Max | Max |
| Variant | Claude Opus 5.5 (max with fallback) | Claude Opus 5.5 (max with fallback) |
| Configuration ID | aa_intelligence_index:6df46e4e9119d1e1 | aa_intelligence_index:6df46e4e9119d1e1 |
| Estimated | false | false |
| Self-reported | false | false |
| Mapping confidence | Medium | Medium |
| Quota effort matched | unverified | unverified |

**stdout**，Claude Max 的英文证据区域；与 Decision note 相同的 Note 不重复输出：

```text
Point ID: claude_max_20x::claude-opus-5.5
Source:
X @MiaAI_lab tweet (screenshot provided by the maintainer): xHigh burned 1.0305B raw in 1h2m = ~75% of the 5h limit; claude-opus55-round1-2026-09-23.json; round10 item #15 Max 20x ≈5.5 full windows/week (claude-adoption-round10-2026-09-25.json); Claude Pro × Opus 5.5 adopted sample (issue #52 + Reddit segment) ×10; claude-opus55-max20x-round2-2026-09-30.json

Decision note:
30.17B→31.538B (2026-09-30 decision, Anthropic tier): each path converted to Max 20x weekly-quota percentage points, then merged per pp — (i) the MiaAI window worth $471.10 (write at 5m; closes against the tweet's $482.63) = 75% of a window ÷ 5.5 windows/week = 13.636 weekly pp, 32.981B alone; (ii) the Pro × Opus 5.5 merged worth $628.00 / 196.333 Pro pp ÷ Max 20x weekly quota = Pro×10 → 19.633 weekly pp, 30.536B alone; the two paths differ by 8%. Not adopted: Pro 5h/week 13.333% (7.5 windows) applied directly to Max 20x gives 44.97B (Max 20x windows 20×, week 10× — the window/week ratio differs from Pro's); the official-multiplier derivation with 3.75 windows/week gives 22.49B (the MiaAI window is only 15.5× a Pro window, not 20× — inconsistent with both multipliers at once); equal-weight mean 31.758B; the #65 mixed sample not yet handled. Original 301.7 decision text — new 30.17B: 5h pool 1.0305B÷~75% = 1.374B raw (the 9/22 release had already raised Pro/Max/Team 5h caps, so the window pool reflects release-period basis); implied weight 7.15/13.74 = 0.5204×Opus5 → monthly pool 157÷0.5204; the list-price blend ratio 0.5143 independently corroborates (alternative 30.528B differs by 1.2%); the sample closes at the new price $471.1≈tweet $482.63 (+2.4%); n=1 tweet with no panel, ~75% rounded reading (monthly interval about 28.3B~32.2B), effort only affects rate; if official weights deviate from the price ratio (Fable 6.5× precedent) it must be re-derived; direct weekly-pool panel measurement or post-reset controlled saturation could raise it to high
```

| Evidence | URL |
| --- | --- |
| claude-adoption-round10-2026-09-25.json | /data/evidence/claude-adoption-round10-2026-09-25.json |
| claude-opus55-max20x-round2-2026-09-30.json | /data/evidence/claude-opus55-max20x-round2-2026-09-30.json |
| claude-opus55-round1-2026-09-23.json | /data/evidence/claude-opus55-round1-2026-09-23.json |

其后输出 `Point ID: droid_max::claude-opus-5.5` 对应的 Source、Decision note 和 Evidence，内容与第 6 节相同；本页不重复这段长文本。比较保留原始采用理由，不自动归纳为推荐结论，也不合计同套餐不同模型的额度。

**stderr**：

```text
Snapshot: 2026-10-01 | Source: bundled
Board: aa_intelligence_index | Board snapshot: 2026-09-22 | Config: best
Total: 2 | Returned: 2 | Truncated: false
```

## 8. `rap info`：快照与口径

用途：确认本次查询读哪份数据、数据规模与采用口径。这里的快照字段本身是命令数据，写 stdout。

```sh
rap info
```

**stdout**：

| Field | Value |
| --- | --- |
| Data source | bundled |
| Data snapshot | 2026-10-01 |
| Dataset version | 1 |
| Price points | 318 |
| Models | 74 |
| Companies | 18 |
| Channels | 17 |
| Plans | 95 |
| Boards | 8 |
| Benchmark configurations | 330 |
| Price/configuration mappings | 1854 |
| Subscription price assumption | Full use of the adopted allowance |
| Allowances across models in one plan | Alternative use; do not add together |
| Generic month | 4 weeks; vendor-specific monthly pools retain their adopted basis |
| Standard workload | 97% cache reads / 2.5% fresh input / 0.5% output |
| Anthropic workload | 97% cache reads / 2.5% cache writes / 0.5% output |
| Low-cache workload | 85% cache reads / 14.5% fresh input / 0.5% output |
| Measured workload | Raw sample tokens; not workload-normalized |
| Adopted exchange rate | 1 USD = 6.7787 CNY |
| Exchange rate date | 2026-09-04 |
| Exchange rate source | CFETS central parity, via Xinhua |

**stderr**：

```text
Total: 1 | Returned: 1 | Truncated: false
```

当前默认联网成功时，Data source 为 `remote`；ETag/304 复用或网络失败时读取有效缓存则为 `cache: <绝对路径>`，没有有效缓存时为 `bundled`。以下来源示意不代表固定快照日期：

| Field | Value |
| --- | --- |
| Data source | remote |
| Data snapshot | 2026-10-03 |

带 `--data` 时完全跳过联网和缓存，source 显示文件来源与解析后的路径；数据快照取文件中的 `generatedAt`，不取文件修改时间：

```sh
rap info --data ./web/public/data/site.json
```

在仓库根目录调用时，其余字段与上表一致，前两项为：

| Field | Value |
| --- | --- |
| Data source | file: /workspace/real-api-pricing/web/public/data/site.json |
| Data snapshot | 2026-10-01 |

## 9. 帮助与版本

### `rap --help`

用途：发现入口及全局选项。帮助由 Commander 自动生成，不加载快照、不读写缓存、不联网。以下为当前英文帮助文本：

```sh
rap --help
```

**stdout**：

```text
Usage: rap [options] [command]

Read model prices and monthly allowances with automatic offline fallback.

Options:
  -V, --version                     output the version number
  --data <site.json>                Read a specified local snapshot
  --format <format>                 Output format: table | json | csv (default:
                                    "table")
  -h, --help                        display help for command

Commands:
  price [options]                   Real price ranking, lowest first; includes
                                    metered APIs and unscored points.
  allowance [options]               Monthly allowance ranking, largest first;
                                    subscriptions with known monthly tokens.
  query [options]                   Query price points; optionally filter
                                    benchmark configurations.
  list                              Discover exact model, company, channel, plan
                                    and board IDs.
  show [options] <point-id>         Show price, allowance, evidence and all
                                    mapped benchmark configurations.
  compare [options] <point-ids...>  Compare at least two distinct price points,
                                    in input order.
  info                              Show snapshot, coverage and calculation
                                    conventions.

Examples:
  rap price --company Anthropic
  rap allowance --company Anthropic --fee-band 0-30
  rap list models --search claude
  rap query --board aa_intelligence_index --frontier --format json

Run rap <command> --help for command-specific options.
```

帮助与版本不会附加查询统计到 stderr。`--format` 面向数据命令，help/version 始终输出文本。

### `rap price --help`

```sh
rap price --help
```

**stdout**：

```text
Usage: rap price [options]

Real price ranking, lowest first; includes metered APIs and unscored points.

Options:
  --company <id>          Exact model developer ID; repeatable
  --vendor <id>           Alias of --company; values are combined
  --channel <name>        Exact access channel; repeatable
  --model <id>            Exact model ID; repeatable
  --plan <id>             Exact plan ID; repeatable
  --billing <kind>        subscription | metered; repeatable
  --confidence <level>    high | medium | low; repeatable
  --search <text>         Whole-substring website search (default: "")
  --min-fee <USD>         Inclusive lower monthly-fee bound
  --max-fee <USD>         Inclusive upper monthly-fee bound
  --min-price <USD/MTok>  Inclusive lower real-price bound
  --max-price <USD/MTok>  Inclusive upper real-price bound
  --min-tokens <integer>  Inclusive lower monthly-token bound
  --max-tokens <integer>  Inclusive upper monthly-token bound
  --board <id>            Independent benchmark board
  --harness <name>        Benchmark harness; requires --board; repeatable
  --effort <name>         Reasoning effort; requires --board; repeatable
  --mode <name>           Service mode; requires --board; repeatable
  --limit <integer>       Return at most this many rows; default: all
  -h, --help              display help for command

Global Options:
  -V, --version           output the version number
  --data <site.json>      Read a specified local snapshot
  --format <format>       Output format: table | json | csv (default: "table")

Global options: --data <site.json> --format table|json|csv --version
Use query --view table for custom sorting, score filters and configuration expansion.
```

`rap allowance --help` 同样列出公共筛选，增加 `--fee-band all|0-30|30-100|100-300`，说明只保留有月额度的订阅且额度降序。`rap query --help` 列出 `--view`、`--sort` 和评测选项的依赖；`rap list <resource> --help` 按第 4 节的适用矩阵列参数；show/compare 的查询选项只有 `--board`，不接受排名的过滤、排序与 limit。

### `rap --version`

当前软件版本为 `0.1.0`；内置数据日期另由 `rap info` 查询。

```sh
rap --version
```

**stdout**：

```text
rap 0.1.0
```

## 10. 空结果与参数错误

查询无匹配记录是成功，stdout 显示空结果，退出码为 0：

```sh
rap price --company Anthropic --search no-such-model-123
```

**stdout**：

```text
No matching results.
```

**stderr**：

```text
Snapshot: 2026-10-01 | Source: bundled | View: price
Total: 0 | Returned: 0 | Truncated: false
Order: USD/MTok ascending; ties by Point ID.
```

精确 ID、参数枚举或依赖错误的退出码为 2；stdout 为空，错误只写 stderr。例如：

```sh
rap price --company Factory
```

```text
error: Unknown company ID "Factory". Factory is a Channel. Use --channel Factory.
```

```sh
rap price --company Anthropic --sort fee:asc
```

```text
error: unknown option '--sort'
(Did you mean one of --effort, --format?)
```

Commander 随后附加 price 的帮助。自定义排序使用 `rap query --view table --sort fee:asc`。

```sh
rap query --frontier
```

```text
error: --frontier requires --board.
```

```sh
rap list boards --company Anthropic
```

```text
error: unknown option '--company'
```

Commander 随后附加 list boards 的帮助。

显式 --data 文件或最终内置兜底数据读取、格式错误退出码为 1，不能输出半份成功结果；默认网络失败、超时或线上数据无效会自动回退，不作为查询错误输出。JSON 和 CSV 使用与表格相同的记录集合，空 JSON 返回 `rows: []`，空 CSV 保留表头；诊断仍写 stderr。CLI CSV 保持对应命令排序；网站排名视图的“Table · CSV”采用明细表排序（allowance 下载也按价格），固定列 schema 也不同，因此按 Point ID 对账共享原始字段，不要求文件逐字一致。比较榜单引用字段时显式选择同一榜单。完整导出契约见 [CLI 设计规范](cli-design.md)。
