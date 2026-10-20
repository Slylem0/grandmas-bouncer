"""Run judges over the scenario cases and write raw results to benchmarks/results/<system>.jsonl.

    uv run python -m benchmarks.run --systems decider,llm-nova,llm-sonnet
    uv run python -m benchmarks.summarize

Each record stores the probabilities, not the verdict, so thresholds and the cascade can be
evaluated offline without calling any model again.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from decider_patterns import DEFAULT_QUESTIONS, DeciderClient
from grandmas_bouncer.config import settings
from grandmas_bouncer.judge import BedrockJudge

from .cases import load_cases, state_for

RESULTS = Path(__file__).resolve().parent / "results"
LLM_SYSTEMS = {
    "llm-nova": "us.amazon.nova-2-lite-v1:0",
    "llm-nova-pro": "us.amazon.nova-pro-v1:0",
    "llm-sonnet": "us.anthropic.claude-sonnet-4-6",
}


def run_decider(cases, out) -> dict:
    client = DeciderClient(settings.decider_url)
    health = client.health()
    client.ask("warm-up", {"q": DeciderClient.noul("Is this a warm-up?")})  # first call compiles
    for case in cases:
        result = client.ask(state_for(case), DEFAULT_QUESTIONS)
        write(
            out,
            case,
            {k: result.noul(k) for k in DEFAULT_QUESTIONS},
            result.latency_ms,
            input_tokens=result.input_tokens,
            server_latency_ms=result.server_latency_ms,
        )
    return health


def run_llm(model_id, cases, out) -> dict:
    judge = BedrockJudge(model_id, settings.region)
    for case in cases:
        r = judge.judge(state_for(case))
        write(
            out,
            case,
            r.probabilities,
            r.latency_ms,
            input_tokens=r.input_tokens,
            output_tokens=r.output_tokens,
            parse_error=r.parse_error,
        )
    return {"model_id": model_id}


def write(out, case, probabilities, latency_ms, **extra) -> None:
    row = {
        "id": case["id"],
        "split": case["split"],
        "category": case["category"],
        "lang": case["lang"],
        "expected": case["expected"],
        "probabilities": probabilities,
        "latency_ms": latency_ms,
        **extra,
    }
    out.write(json.dumps(row) + "\n")
    out.flush()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--systems", default="decider,llm-nova,llm-sonnet")
    parser.add_argument("--split", default="all", choices=["all", "dev", "test"])
    args = parser.parse_args()
    cases = load_cases(args.split)
    RESULTS.mkdir(exist_ok=True)
    meta = {}
    for system in args.systems.split(","):
        start = time.time()
        with open(RESULTS / f"{system}.jsonl", "w") as out:
            info = (
                run_decider(cases, out)
                if system == "decider"
                else run_llm(LLM_SYSTEMS[system], cases, out)
            )
        meta[system] = {
            **info,
            "cases": len(cases),
            "seconds": round(time.time() - start, 1),
            "date": time.strftime("%Y-%m-%d"),
        }
        print(f"{system}: {len(cases)} cases in {meta[system]['seconds']} s")
    meta_path = RESULTS / "meta.json"
    old = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    meta_path.write_text(json.dumps({**old, **meta}, indent=2))


if __name__ == "__main__":
    main()
