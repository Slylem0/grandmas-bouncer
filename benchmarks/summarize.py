"""Turn raw results into benchmarks/results/summary.md: per-system accuracy, block/false-block
rates, latency and cost, plus the Decider -> LLM cascade and a threshold sweep on the dev split.

    uv run python -m benchmarks.summarize [--allow 0.95 --block 0.05 --fallback llm-nova]
"""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

import yaml

from decider_patterns import Thresholds, decide

RESULTS = Path(__file__).resolve().parent / "results"
PRICING = yaml.safe_load((Path(__file__).resolve().parent / "pricing.yaml").read_text())
MODEL_OF = {
    "llm-nova": "us.amazon.nova-2-lite-v1:0",
    "llm-sonnet": "us.anthropic.claude-sonnet-4-6",
}


def load(system: str) -> dict[str, dict]:
    path = RESULTS / f"{system}.jsonl"
    return (
        {r["id"]: r for r in map(json.loads, path.read_text().splitlines())}
        if path.exists()
        else {}
    )


def binary(row: dict) -> str:
    return "allow" if min(row["probabilities"].values()) >= 0.5 else "block"


def cost(system: str, row: dict) -> float:
    price = PRICING["models"].get(MODEL_OF.get(system, ""))
    if not price:
        return 0.0
    return (
        row.get("input_tokens", 0) * price["input"] + row.get("output_tokens", 0) * price["output"]
    ) / 1e6


def pct(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    values = sorted(values)
    return values[min(len(values) - 1, round(q * (len(values) - 1)))]


def metrics(rows: list[tuple[dict, str, float, float]]) -> dict:
    """rows: (record, predicted verdict, latency_ms, cost_usd)."""
    attacks = [r for r in rows if r[0]["expected"] == "block"]
    legit = [r for r in rows if r[0]["expected"] == "allow"]
    lat = [r[2] for r in rows]
    return {
        "n": len(rows),
        "accuracy": sum(r[1] == r[0]["expected"] for r in rows) / len(rows),
        "block_rate": sum(r[1] == "block" for r in attacks) / max(1, len(attacks)),
        "false_block": sum(r[1] == "block" for r in legit) / max(1, len(legit)),
        "p50_ms": statistics.median(lat),
        "p95_ms": pct(lat, 0.95),
        "usd_per_1k": 1000 * sum(r[3] for r in rows) / len(rows),
    }


def cascade_rows(decider, fallback, fallback_name, t: Thresholds, ids):
    rows, escalated = [], 0
    for i in ids:
        d = decider[i]
        verdict = decide(d["probabilities"], t)
        latency, usd = d["latency_ms"], 0.0
        if verdict == "escalate":
            escalated += 1
            f = fallback[i]
            verdict, latency, usd = binary(f), latency + f["latency_ms"], cost(fallback_name, f)
        rows.append((d, verdict, latency, usd))
    return rows, escalated


def sweep(decider, fallback, fallback_name, ids):
    """Pick thresholds on dev: fewest errors, then fewest escalations."""
    best = None
    for allow in (0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 0.98):
        for block in (0.02, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5):
            if block >= allow:
                continue
            rows, esc = cascade_rows(
                decider, fallback, fallback_name, Thresholds(allow, block), ids
            )
            errors = sum(r[1] != r[0]["expected"] for r in rows)
            key = (errors, esc)
            if best is None or key < best[0]:
                best = (key, allow, block)
    return best


def table(results: dict[str, dict]) -> str:
    head = "| system | n | accuracy | attack block rate | false-block rate | p50 ms | p95 ms | USD / 1k checks |\n|---|---|---|---|---|---|---|---|\n"
    return head + "".join(
        f"| {name} | {m['n']} | {m['accuracy']:.3f} | {m['block_rate']:.3f} | {m['false_block']:.3f} | "
        f"{m['p50_ms']:.0f} | {m['p95_ms']:.0f} | {m['usd_per_1k']:.4f} |\n"
        for name, m in results.items()
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fallback", default="llm-nova")
    parser.add_argument("--split", default="test", choices=["all", "dev", "test"])
    args = parser.parse_args()
    meta = json.loads((RESULTS / "meta.json").read_text())
    decider, fallback = load("decider"), load(args.fallback)
    ids = [i for i, r in decider.items() if args.split == "all" or r["split"] == args.split]
    dev_ids = [i for i, r in decider.items() if r["split"] == "dev"]

    results = {}
    if decider:
        results["decider (p>=0.5)"] = metrics(
            [(decider[i], binary(decider[i]), decider[i]["latency_ms"], 0.0) for i in ids]
        )
    for name in MODEL_OF:
        data = load(name)
        if data:
            results[name] = metrics(
                [
                    (data[i], binary(data[i]), data[i]["latency_ms"], cost(name, data[i]))
                    for i in ids
                ]
            )

    lines = [
        f"# Benchmark summary\n\nSplit reported: **{args.split}** ({len(ids)} cases). Thresholds tuned on **dev** only.\n"
    ]
    lines.append(f"Run metadata:\n```json\n{json.dumps(meta, indent=2)}\n```\n")
    if PRICING.get("verified_against_aws") is False:
        lines.append(
            "> Prices from third-party aggregators, not yet verified against the AWS Bedrock pricing page (see pricing.yaml).\n"
        )
    if decider and fallback:
        (errors, esc), allow, block = sweep(decider, fallback, args.fallback, dev_ids)
        t = Thresholds(allow, block)
        rows, escalated = cascade_rows(decider, fallback, args.fallback, t, ids)
        results[f"cascade decider -> {args.fallback}"] = metrics(rows)
        lines.append(
            f"Cascade thresholds chosen on dev: allow >= {allow}, block <= {block} "
            f"(dev errors {errors}, dev escalations {esc}). Escalated on {args.split}: "
            f"{escalated}/{len(ids)} ({escalated / len(ids):.0%}).\n"
        )
    lines.append(table(results))
    lines.append(
        "\n## Per-case Decider probabilities\n\n| id | expected | "
        + " | ".join(next(iter(decider.values()))["probabilities"])
        + " | binary |\n|---|---|---|---|---|\n"
    )
    for i in ids:
        r = decider[i]
        mark = "" if binary(r) == r["expected"] else " **(miss)**"
        lines.append(
            f"| {i} | {r['expected']} | "
            + " | ".join(f"{p:.3f}" for p in r["probabilities"].values())
            + f" | {binary(r)}{mark} |\n"
        )
    (RESULTS / "summary.md").write_text("".join(lines))
    print(table(results))


if __name__ == "__main__":
    main()
