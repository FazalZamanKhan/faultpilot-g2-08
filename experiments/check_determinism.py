"""Repeat one development prompt to check local greedy decoding stability."""

import argparse
import hashlib
import json
from pathlib import Path

from faultpilot.agent import AgentSettings, OllamaClient, build_prompt
from faultpilot.benchmark import load_cases
from faultpilot.diagnostics import DiagnosticModel


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="research/.external_data/MLDebugging.jsonl")
    parser.add_argument("--config", default="experiments/diagnostic_config.json")
    parser.add_argument("--model", default="qwen2.5-coder:0.5b")
    parser.add_argument("--output", default="results/determinism_check.json")
    args = parser.parse_args()
    cases = load_cases(args.data)
    def fold(case):
        return int(hashlib.sha256(case.task_id.encode()).hexdigest(), 16) % 5
    training = [case for case in cases if fold(case) in (2, 3, 4)]
    validation = [case for case in cases if fold(case) == 1]
    validation.sort(key=lambda case: hashlib.sha256(case.case_id.encode()).hexdigest())
    case = validation[0]
    config = json.loads(Path(args.config).read_text())
    diagnosis = DiagnosticModel(training).diagnose(case, retrieval=True,
                                                  alpha=config["selected"]["alpha"],
                                                  threshold=config["selected"]["threshold"])
    settings = AgentSettings(model=args.model)
    client = OllamaClient(settings)
    prompt = build_prompt(case, diagnosis, previous="", retrieval=True)
    calls = []
    for _ in range(3):
        proposal, usage = client.propose(prompt)
        calls.append({"proposal": proposal, "usage": usage})
    result = {
        "split": "development_validation", "case_id": case.case_id,
        "model": args.model, "digest": client.model_digest(),
        "temperature": settings.temperature, "seed": settings.seed,
        "identical_proposals": all(row["proposal"] == calls[0]["proposal"] for row in calls),
        "calls": calls,
        "note": "This checks one repeated development prompt; it does not prove global determinism.",
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("case_id", "model", "identical_proposals")}, indent=2))


if __name__ == "__main__":
    main()
