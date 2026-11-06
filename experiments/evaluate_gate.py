"""Frozen evidence-gate coverage and selective diagnosis accuracy on test."""

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import f1_score

from faultpilot.data import CATEGORIES, EXPECTED_SHA256


def binary(rows, key):
    return np.array([[int(label in row[key]) for label in CATEGORIES] for row in rows])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--diagnosis", default="results/diagnostic_evaluation.json")
    parser.add_argument("--config", default="experiments/diagnostic_config.json")
    parser.add_argument("--output", default="results/gate_evaluation.json")
    args = parser.parse_args()
    diagnosis = json.loads(Path(args.diagnosis).read_text())
    config = json.loads(Path(args.config).read_text())
    if diagnosis["dataset_sha256"] != EXPECTED_SHA256 or config["dataset_sha256"] != EXPECTED_SHA256:
        raise ValueError("Dataset checksum mismatch")
    rows = diagnosis["predictions"]
    floor = config["selected_gate"]["confidence_floor"]
    kept = [index for index, row in enumerate(rows)
            if row["confidence"] >= floor and bool(row["evidence"])]
    truth = binary(rows, "truth")
    pred = binary(rows, "full")
    exact_all = float(np.mean(np.all(truth == pred, axis=1)))
    exact_kept = float(np.mean(np.all(truth[kept] == pred[kept], axis=1))) if kept else None
    result = {
        "dataset_sha256": EXPECTED_SHA256, "test_count": len(rows),
        "selected_on": "development validation only", "confidence_floor": floor,
        "answered": len(kept), "abstained": len(rows) - len(kept),
        "coverage": round(len(kept) / len(rows), 5),
        "always_answer_exact_match": round(exact_all, 5),
        "selective_exact_match": round(exact_kept, 5) if exact_kept is not None else None,
        "exact_match_change": round(exact_kept - exact_all, 5) if exact_kept is not None else None,
        "always_answer_macro_f1": round(float(f1_score(truth, pred, average="macro", zero_division=0)), 5),
        "answered_subset_macro_f1": round(float(f1_score(truth[kept], pred[kept], average="macro",
                                                            zero_division=0)), 5) if kept else None,
        "note": "Selective scores apply only to answered cases; abstentions remain in the full-set coverage denominator.",
    }
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
