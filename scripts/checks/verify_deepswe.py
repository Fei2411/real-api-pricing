"""Check DeepSWE configuration identity, attempt rates and task costs."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
archive = json.loads((ROOT / "data/research/scores-deepswe-1.1-2026-10-13.json").read_text(encoding="utf-8"))
assert archive["taskCount"] == 113
assert len(archive["scores"]) == 70
assert len({s["secondary"]["config"] for s in archive["scores"]}) == 70
for row in archive["scores"]:
    sec = row["secondary"]
    assert abs(row["score"] - 100 * sec["passed"] / sec["attempted"]) < 1e-9
    assert sec["ciMinus"] >= 0 and sec["ciPlus"] >= 0
    assert sec["meanCostUsdPerTask"] >= 0
    assert sec["medianCostPerTaskUsd"] >= 0
    assert sec["agentHarness"] == "mini-swe-agent"
configs = json.loads((ROOT / "derived/benchmark-configurations.json").read_text(encoding="utf-8"))
deep = [c for c in configs if c["board"] == "deepswe_1_1"]
# Official snapshot rows map 1:1 to configurations. Vendor self-reports arrive as
# supplements, so pin them by value rather than by a total that every supplement bumps.
assert len([c for c in deep if not c["score_is_self_reported"]]) == len(archive["scores"])
assert {(c["model"], c["score"]) for c in deep if c["score_is_self_reported"]} == {
    ("deepseek-v4.1-flash", 74.2), ("grok-4.7", 71.0),
    ("mimo-v2.6-pro", 71.9), ("mimo-v2.6-flash", 67.9), ("mimo-v2.5-pro", 19.0),
    ("muse-wonder-full", 79.0), ("muse-wonder", 78.8),
    ("claude-opus-5.5", 74.2), ("claude-fable-5.1", 67.4), ("step-5-preview", 67.7)}
assert len(deep) == len(archive["scores"]) + 10
assert all(c["score_low"] is None and c["mean_cost_usd_per_task"] is None
           for c in deep if c["score_is_self_reported"])
assert {c["agent_harness"] for c in deep
        if c["score_is_self_reported"] and c["model"] not in
        ("deepseek-v4.1-flash", "muse-wonder", "muse-wonder-full",
         "claude-opus-5.5", "claude-fable-5.1", "step-5-preview")} == {"mini-swe-agent"}
astra = [c for c in deep if c["model"] == "gpt-6-astra"]
assert {c["reasoning_effort"] for c in astra} == {"low", "medium", "high", "xhigh", "max"}
assert max(astra, key=lambda c: c["score"])["reasoning_effort"] == "xhigh"
vendor = next(c for c in deep if c["model"] == "deepseek-v4.1-flash")
assert vendor["score"] == 74.2 and vendor["score_is_self_reported"]
assert vendor["agent_harness"] == "mini-SWE"
assert vendor["score_low"] is None and vendor["mean_cost_usd_per_task"] is None
print("PASS: DeepSWE attempt rates, intervals, effort levels, costs and vendor provenance")
