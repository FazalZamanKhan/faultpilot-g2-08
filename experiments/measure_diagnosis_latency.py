"""Measure the diagnosis work omitted from repair-loop wall-clock traces."""

import argparse
import json
import statistics
import time
from pathlib import Path

from faultpilot.benchmark import load_cases
from faultpilot.diagnostics import DiagnosticModel


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="research/.external_data/MLDebugging.jsonl")
    parser.add_argument("--config", default="experiments/diagnostic_config.json")
    parser.add_argument("--output", default="results/diagnosis_latency.json")
    args = parser.parse_args()
    cases = load_cases(args.data)
    config = json.loads(Path(args.config).read_text())
    started = time.monotonic()
    model = DiagnosticModel([case for case in cases if case.split == "development"])
    train_s = time.monotonic() - started
    durations = {}
    for case in cases:
        if case.split != "test":
            continue
        started = time.monotonic()
        model.diagnose(case, retrieval=True, alpha=config["selected"]["alpha"],
                       threshold=config["selected"]["threshold"])
        durations[case.case_id] = round(time.monotonic() - started, 5)
    result = {"count": len(durations), "train_once_s": round(train_s, 3),
              "mean_per_case_s": round(statistics.mean(durations.values()), 5),
              "median_per_case_s": round(statistics.median(durations.values()), 5),
              "per_case_s": durations,
              "note": "Measured separately; concurrent workloads can affect wall-clock values."}
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("count", "train_once_s", "mean_per_case_s",
                                                  "median_per_case_s")}, indent=2))


if __name__ == "__main__":
    main()
