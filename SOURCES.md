# Sources and third-party notices

The project's original software is licensed under [MIT](LICENSE). This does not relicense third-party material, quotations, or source datasets. Their applicable terms and attribution continue to apply.

## Awesome Coding Plan

- Work: [awesome-coding-plan](https://github.com/mahonzhan/awesome-coding-plan)
- Creator identification requested by the upstream license: mahonzhan@gmail.com
- License notice: Licensed under the Creative Commons Attribution 4.0 International License.
- [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) · [upstream LICENCE](https://github.com/mahonzhan/awesome-coding-plan/blob/main/LICENCE)
- Used for: historical ChatGPT Plus / Codex Sol and Claude Pro / Opus 4.8 usage measurements. See `data/research/quotas-web-2026-09.json` and `scripts/build_adopted.py`.
- Changes: selected measurements are mapped to this project's served-model identities, normalized to four-week months, combined with separate quota evidence, and transformed into real unit prices and charts. Derived plan estimates and adoption decisions are this project's work, not upstream endorsements. Other upstream figures were not necessarily adopted.

## 《财经》 / Caijing

- Article: 《Token经济，中国账本｜〈财经〉封面》
- Authors and date recorded in the project's evidence: 吴俊宇、周源; 2026-08-17.
- [Archived source URL on NetEase](https://www.163.com/dy/article/L4ILFQL60519DDOA.html)
- Used for: comparison of saturated subscription usage, corroboration of the ChatGPT/Codex estimate, and the Alibaba flagship-model cost estimate. The Alibaba plan tier is an assumption documented in the adoption script, not a confirmed claim of the article.
- Reference record: `data/research/caijing-2026-08.json`. Its historical statements may differ from current adoption decisions.
- No open-content license has been verified. Article text, illustrations and other protected material are not covered by this project's MIT license. Attribution does not itself grant republication permission. The article URL could not be retrieved during the 2026-09-06 license check; its bibliographic details above come from the existing evidence record.

## Lobe Icons / Simple Icons

- [lobehub/lobe-icons](https://github.com/lobehub/lobe-icons), MIT, Copyright (c) 2023 LobeHub. Used for most provider SVG marks in `web/src/assets/provider-logos/`.
- [Simple Icons](https://github.com/simple-icons/simple-icons), CC0. Used for the Xiaomi mark.
- Command Code uses the official commandcode.ai/brand symbol (dark plate + rounded frame + ⌘).
- StepFun five-square mark follows the icon in [stepfun.com](https://www.stepfun.com/assets/logo-B0FsyLQP.svg); the lime–cyan gradient follows the current public avatar.
- Alibaba uses the official Qwen blue mark cut from the chat.qwen.ai lockup; MiniMax uses the official Brand VI (2026-09-14) vector with the gradient rebuilt as #E21680 → #FF633A; OpenCode is cut from the opencode.ai/brand ornate logo in light and dark variants; Zhipu uses the official z.ai mark; SpaceXAI (formerly xAI, rebranded July 2026) uses the official SpaceXAI symbol (squared variant).
- Kimi uses the official Kimi Logomark tile from the Kimi brand kit (Light variant for light theme, Dark variant for dark theme); Devin uses the official Devin mark from the Devin design system (dark-ink and white variants).
- Factory uses the official favicon tile from [factory.ai](https://factory.ai/favicon.svg); Cursor uses the official cursor-brand-assets Avatars/Square 2D tiles (dark tile for light theme, light tile for dark theme); Ollama uses the official apple-touch-icon tile from ollama.com for dark theme.
- Brand logos remain trademarks of their owners and are used only to identify the corresponding model developer.

## Leaderboards and other evidence

- [Code Arena](https://arena.ai/leaderboard/code) and [Agent Arena](https://arena.ai/leaderboard/agent): separate score snapshots.
- [Artificial Analysis Intelligence Index](https://artificialanalysis.ai/leaderboards/models) and [Coding Agent Index](https://artificialanalysis.ai/agents/coding-agents): separate score snapshots; coding-agent configuration names are retained.
- [OpenDesign Arena](https://open-design.ai/llm-arena-for-design/): 0–100 average task-score snapshot from OpenDesign's private frontend-design benchmark; requirements and design-quality scores are used, while cost/speed recommendation weights are excluded.
- [Terminal-Bench 4.0](https://www.tbench.ai/leaderboard): official 66-task leaderboard hosted by Stanford / Harbor / the Laude Institute; every harness × model × effort row is retained with its 95% interval and run cost. See `data/research/scores-terminal-bench4-round1-2026-09-10.json`.
- Terminal-Bench 4.0 (AA): Artificial Analysis independently benchmarks the same 66 tasks on its own `Artificial Analysis` harness (its pages note "Independently benchmarked by Artificial Analysis"); scored as a separate board because same-task results are not interchangeable with official-harness runs. Source site: [artificialanalysis.ai](https://artificialanalysis.ai/). Rows are recorded as `boardId=terminal_bench_4` with `secondary.agentHarness="Artificial Analysis"` in `data/research/scores-stepfun-step5-round1-2026-09-21.json`, `scores-new-models-round1-2026-09-23.json`, `scores-gpt6sol-round1-2026-09-24.json` and `scores-gpt6luna-round1-2026-09-26.json`.
- [DeepSWE v1.1](https://deepswe.datacurve.ai/): 113 tasks, Pass@1 %; official rows run on the mini-swe-agent harness; snapshot 2026-09-03. Additional vendor self-reported supplement rows are marked self-reported. Files: `data/research/scores-deepswe-1.1-2026-09-12.json`, `scores-deepswe-selfreport-2026-09-12.json`, `scores-deepswe-mimo-v26-grok47-selfreport-2026-09-22.json`.
- Official pricing and quota documents, community reports and aggregate local usage measurements: individual sources and adoption rationale are recorded in the data and adoption script.

See [PUBLICATION.md](PUBLICATION.md) for the redaction scope.
