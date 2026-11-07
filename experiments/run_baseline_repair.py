"""Record the Phase 1 diagnosis-only baseline on the repair outcome scale."""

import argparse
import json
from collections import Counter
from pathlib import Path

from faultpilot.benchmark import load_cases
from faultpilot.diagnostics import phase1_labels


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="research/.external_data/MLDebugging.jsonl")
    parser.add_argument("--preflight", default="results/test_preflight.jsonl")
    parser.add_argument("--output", default="results/E1_baseline_repair.json")
    args = parser.parse_args()
    cases = [case for case in load_cases(args.data) if case.split == "test"]
    preflight = {row["case_id"]: row for line in Path(args.preflight).read_text().splitlines()
                 if (row := json.loads(line))}
    if set(preflight) != {case.case_id for case in cases}:
        raise ValueError("Preflight does not match fixed test cases")
    rows = []
    for case in cases:
        original = preflight[case.case_id]["status"]
        status = "diagnosed_only" if original == "fail" else "original_" + original
        rows.append({"case_id": case.case_id, "task_id": case.task_id,
                     "preflight": original, "predicted_labels": phase1_labels(case),
                     "status": status, "patch_attempted": False,
                     "verified_repair": False})
    result = {
        "protocol": "Phase 1 rule baseline; diagnosis only, no edit operation",
        "test_count": len(rows), "eligible_reproduced_failures": sum(row["preflight"] == "fail" for row in rows),
        "status_counts": dict(Counter(row["status"] for row in rows)),
        "patch_attempts": 0, "verified_repair_passes": 0,
        "note": "Zero repair passes are by baseline design, not a measured patch failure rate.",
        "cases": rows,
    }
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("test_count", "eligible_reproduced_failures",
                                                  "status_counts", "verified_repair_passes")}, indent=2))


if __name__ == "__main__":
    main()
