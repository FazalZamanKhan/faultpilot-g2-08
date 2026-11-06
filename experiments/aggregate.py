"""Paired summaries and task-group bootstrap intervals for saved repair runs."""

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from experiments.run_repairs import MODES, summarize


def latest(path):
    return {row["case_id"]: row for line in path.read_text().splitlines()
            if line.strip() and (row := json.loads(line))}


def paired_interval(left, right, *, allowed_ids=None, right_audit=False, repeats=2000, seed=17):
    ids = sorted((set(left) & set(right)) & (set(allowed_ids) if allowed_ids is not None else set(left)))
    groups = defaultdict(list)
    for case_id in ids:
        groups[left[case_id]["task_id"]].append(case_id)
    names = sorted(groups)
    if not names:
        return None
    def left_success(row):
        return row["status"] == "verified_by_supplied_tests"
    def right_success(row):
        if right_audit:
            return any(step["step"] == "offline_audit" and step["result"]["status"] == "pass"
                       for step in row["trace"])
        return row["status"] == "verified_by_supplied_tests"
    rng = np.random.default_rng(seed)
    differences = []
    for _ in range(repeats):
        selected = rng.choice(names, size=len(names), replace=True)
        sample = [case_id for name in selected for case_id in groups[name]]
        l_rate = np.mean([left_success(left[case_id]) for case_id in sample])
        r_rate = np.mean([right_success(right[case_id]) for case_id in sample])
        differences.append(float(l_rate - r_rate))
    observed = (sum(left_success(left[case_id]) for case_id in ids)
                - sum(right_success(right[case_id]) for case_id in ids)) / len(ids)
    return {"paired_cases": len(ids), "task_groups": len(names),
            "observed_difference": round(observed, 5),
            "ci95": [round(float(x), 5) for x in np.quantile(differences, [0.025, 0.975])],
            "right_condition": "offline_audit_pass" if right_audit else "verified_by_supplied_tests",
            "unit": "percentage-point difference as fraction; multiply by 100",
            "bootstrap_replicates": repeats, "seed": seed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", default="results/repairs")
    parser.add_argument("--preflight", default="results/test_preflight.jsonl")
    parser.add_argument("--output", default="results/repair_aggregate.json")
    args = parser.parse_args()
    input_dir = Path(args.input_dir)
    preflight = [json.loads(line) for line in Path(args.preflight).read_text().splitlines() if line.strip()]
    eligible = sum(row["status"] == "fail" for row in preflight)
    eligible_ids = {row["case_id"] for row in preflight if row["status"] == "fail"}
    runs = {}
    summary = {}
    for mode in MODES:
        path = input_dir / f"{mode}.jsonl"
        if path.exists():
            runs[mode] = latest(path)
            summary[mode] = summarize(path, len(preflight), eligible)
    comparisons = {}
    if "E3_full" in runs:
        for name in ("E2_repairagent_style", "E5_no_retrieval", "E5_no_verification", "E5_no_gate"):
            if name in runs:
                comparisons[f"E3_minus_{name}"] = paired_interval(
                    runs["E3_full"], runs[name], allowed_ids=eligible_ids,
                    right_audit=name == "E5_no_verification")
    result = {
        "preflight": {"test_count": len(preflight), "repair_eligible": eligible},
        "runs": summary,
        "paired_verified_pass_differences": comparisons,
        "warning": "Paired intervals use repair-eligible cases and sample task groups; they do not cover model randomness or semantic correctness.",
    }
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
