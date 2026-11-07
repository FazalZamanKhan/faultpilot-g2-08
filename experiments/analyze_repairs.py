"""Classify final repair traces and select reproducible representative cases."""

import argparse
import json
from collections import Counter
from pathlib import Path


def category(row):
    if row["status"] == "verified_by_supplied_tests":
        return "supplied_tests_passed"
    if row["status"] == "abstained_insufficient_evidence":
        return "evidence_gate_abstention"
    if row["status"] == "provider_error":
        return "provider_unavailable"
    if row["status"] in ("environment_blocked", "original_already_passes"):
        return row["status"]
    if row["status"] == "malformed_model_response":
        return "malformed_model_response"
    tests = [step["result"] for step in row["trace"] if step["step"] == "test"]
    if any(result["status"] == "setup_error" for result in tests):
        return "candidate_did_not_load"
    if any(result["status"] == "timeout" for result in tests):
        return "candidate_timed_out"
    if tests:
        return "candidate_failed_tests"
    if any(step["step"] == "edit" for step in row["trace"]):
        return "all_edits_rejected"
    return "other"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="results/repairs/E3_full.jsonl")
    parser.add_argument("--preflight", default="results/test_preflight.jsonl")
    parser.add_argument("--output", default="results/failure_analysis.json")
    args = parser.parse_args()
    latest = {row["case_id"]: row for line in Path(args.input).read_text().splitlines()
              if line.strip() and (row := json.loads(line))}
    rows = sorted(latest.values(), key=lambda row: row["case_id"])
    counts = Counter(category(row) for row in rows)
    preflight = [json.loads(line) for line in Path(args.preflight).read_text().splitlines() if line.strip()]
    successes = [row for row in rows if category(row) == "supplied_tests_passed"][:2]
    failures = []
    for name, _ in counts.most_common():
        if name in ("supplied_tests_passed", "environment_blocked", "original_already_passes"):
            continue
        candidate = next((row for row in rows if category(row) == name), None)
        if candidate is not None:
            failures.append(candidate)
        if len(failures) >= 2:
            break
    if len(failures) < 2:
        failures.extend(row for row in rows if category(row) not in
                        ("supplied_tests_passed", "environment_blocked", "original_already_passes")
                        and row not in failures)
        failures = failures[:2]
    result = {
        "evaluated_repair_cases": len(rows),
        "preflight_counts_all_held_out": dict(Counter(row["status"] for row in preflight)),
        "failure_category_counts_evaluated": dict(counts),
        "representative_successes": successes,
        "representative_failures": failures,
        "coverage_note": "If fewer than two successes exist, no success case is invented.",
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("evaluated_repair_cases", "preflight_counts_all_held_out",
                                                  "failure_category_counts_evaluated")}, indent=2))


if __name__ == "__main__":
    main()
