"""Freeze benchmark execution outcomes before any model comparison."""

import argparse
import json
from collections import Counter
from pathlib import Path

from faultpilot.benchmark import load_cases
from faultpilot.sandbox import run_tests


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="research/.external_data/MLDebugging.jsonl")
    parser.add_argument("--split", choices=("development", "test"), default="test")
    parser.add_argument("--timeout", type=float, default=8.0)
    parser.add_argument("--output", default="results/test_preflight.jsonl")
    args = parser.parse_args()
    cases = [case for case in load_cases(args.data) if case.split == args.split]
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    completed = {}
    if destination.exists():
        for line in destination.read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                completed[row["case_id"]] = row
    with destination.open("a") as file:
        for index, case in enumerate(cases, 1):
            if case.case_id in completed:
                continue
            outcome = run_tests(case.bug_code, case.test_code, timeout=args.timeout)
            row = {"case_id": case.case_id, "task_id": case.task_id,
                   "split": case.split, "labels": case.labels, **outcome}
            file.write(json.dumps(row) + "\n")
            file.flush()
            completed[case.case_id] = row
            if index % 20 == 0 or index == len(cases):
                print(f"{index}/{len(cases)} {dict(Counter(r['status'] for r in completed.values()))}", flush=True)
    if len(completed) != len(cases):
        raise RuntimeError(f"Expected {len(cases)} records, found {len(completed)}")


if __name__ == "__main__":
    main()
