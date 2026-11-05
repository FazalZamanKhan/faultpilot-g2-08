"""Choose diagnostic settings on development tasks only."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import f1_score

from faultpilot.benchmark import load_cases
from faultpilot.data import CATEGORIES, EXPECTED_SHA256
from faultpilot.diagnostics import DiagnosticModel


def label_matrix(cases, labels):
    return np.array([[int(label in selected) for label in CATEGORIES] for selected in labels])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="research/.external_data/MLDebugging.jsonl")
    parser.add_argument("--output", default="experiments/diagnostic_config.json")
    args = parser.parse_args()
    cases = [case for case in load_cases(args.data) if case.split == "development"]
    def fold(case):
        return int(hashlib.sha256(case.task_id.encode()).hexdigest(), 16) % 5
    train = [case for case in cases if fold(case) in (2, 3, 4)]
    validation = [case for case in cases if fold(case) == 1]
    model = DiagnosticModel(train)
    truth = label_matrix(validation, [case.labels for case in validation])
    trials = []
    for alpha in (0.0, 0.2, 0.4, 0.6):
        for threshold in (0.25, 0.35, 0.45, 0.55):
            predictions = [model.diagnose(case, retrieval=alpha > 0,
                                          alpha=alpha, threshold=threshold).labels
                           for case in validation]
            score = f1_score(truth, label_matrix(validation, predictions), average="macro", zero_division=0)
            trials.append({"alpha": alpha, "threshold": threshold, "macro_f1": round(float(score), 5)})
    winner = sorted(trials, key=lambda row: (-row["macro_f1"], row["alpha"], row["threshold"]))[0]
    diagnoses = [model.diagnose(case, retrieval=True, alpha=winner["alpha"],
                                threshold=winner["threshold"]) for case in validation]
    gate_trials = []
    for floor in (0.40, 0.50, 0.60, 0.70, 0.80):
        kept = [index for index, row in enumerate(diagnoses)
                if row.confidence >= floor and bool(row.evidence)]
        exact = (sum(set(diagnoses[index].labels) == set(validation[index].labels)
                     for index in kept) / len(kept)) if kept else 0.0
        gate_trials.append({"confidence_floor": floor, "coverage": round(len(kept) / len(validation), 5),
                            "selective_exact_match": round(exact, 5)})
    feasible = [trial for trial in gate_trials if trial["coverage"] >= 0.50]
    gate_winner = sorted(feasible, key=lambda row: (-row["selective_exact_match"],
                                                     -row["coverage"]))[0]
    output = {
        "dataset_sha256": EXPECTED_SHA256,
        "training_groups": "sha256(task_id) modulo 5 in {2,3,4}",
        "validation_groups": "sha256(task_id) modulo 5 == 1",
        "train_count": len(train),
        "validation_count": len(validation),
        "selection_metric": "multi-label macro F1",
        "selected": winner,
        "trials": trials,
        "gate_selection_rule": "Maximum selective exact match subject to >=0.50 coverage on development validation",
        "selected_gate": gate_winner,
        "gate_trials": gate_trials,
        "note": "Chosen without reading or scoring the held-out test set.",
    }
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({key: output[key] for key in ("train_count", "validation_count", "selected")}, indent=2))


if __name__ == "__main__":
    main()
