"""Prepare and score the fixed 50-case source-evidence relevance audit."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

from faultpilot.benchmark import load_cases


FIELDS = ("case_id", "task_id", "predicted_categories", "evidence", "runtime_feedback",
          "bug_code", "relevant_yes_no", "reviewer_notes")


def prepare(path: Path, data: str, diagnoses: str):
    cases = {case.case_id: case for case in load_cases(data) if case.split == "test"}
    predictions = {row["case_id"]: row for row in json.loads(Path(diagnoses).read_text())["predictions"]}
    if set(cases) != set(predictions) or len(cases) != 234:
        raise ValueError("Prediction IDs do not match the frozen held-out split")
    selected = sorted(cases, key=lambda case_id: (hashlib.sha256(case_id.encode()).hexdigest(), case_id))[:50]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for case_id in selected:
            case, prediction = cases[case_id], predictions[case_id]
            evidence = prediction["evidence"]
            writer.writerow({"case_id": case_id, "task_id": case.task_id,
                             "predicted_categories": json.dumps(prediction["full"]),
                             "evidence": json.dumps(evidence),
                             "runtime_feedback": case.runtime_feedback,
                             "bug_code": case.bug_code,
                             "relevant_yes_no": "" if evidence else "no",
                             "reviewer_notes": "" if evidence else "No extracted source span"})
    print(f"Prepared {len(selected)} fixed cases in {path}; absent spans are marked no, "
          "and all other relevance judgments remain blank.")


def score(path: Path, output: Path, reviewer_kind: str = "human"):
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 50 or any(row["relevant_yes_no"].strip().lower() not in ("yes", "no")
                              for row in rows):
        raise SystemExit("Fill relevant_yes_no with yes or no for all 50 cases before scoring.")
    if len({row["case_id"] for row in rows}) != 50:
        raise SystemExit("Duplicate or missing case IDs in audit.")
    no_evidence = sum(not json.loads(row["evidence"]) for row in rows)
    invalid = [row["case_id"] for row in rows if not json.loads(row["evidence"])
               and row["relevant_yes_no"].strip().lower() == "yes"]
    if invalid:
        raise SystemExit(f"Cannot mark absent evidence as relevant: {invalid}")
    relevant = sum(row["relevant_yes_no"].strip().lower() == "yes" for row in rows)
    result = {"sample_size": 50, "relevant": relevant, "relevant_fraction": relevant / 50,
              "no_evidence": no_evidence,
              "selection": "First 50 held-out case IDs sorted by SHA-256 of case_id",
              "reviewer_kind": reviewer_kind,
              "judgment": "Item-by-item yes/no review against source code and runtime feedback",
              "protocol_position": "Post-hoc review of frozen predictions; no model parameters or held-out outputs changed",
              "note": "AI-assisted review is not independent human validation. This script only counts supplied judgments."}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="research/.external_data/MLDebugging.jsonl")
    parser.add_argument("--diagnoses", default="results/diagnostic_evaluation.json")
    parser.add_argument("--sheet", default="results/evidence_audit_50.csv")
    parser.add_argument("--output", default="results/evidence_audit_score.json")
    parser.add_argument("--score", action="store_true", help="Score 50 manually completed yes/no judgments")
    parser.add_argument("--reviewer-kind", choices=("human", "ai_assisted"), default="human")
    args = parser.parse_args()
    if args.score:
        score(Path(args.sheet), Path(args.output), args.reviewer_kind)
    else:
        prepare(Path(args.sheet), args.data, args.diagnoses)


if __name__ == "__main__":
    main()
