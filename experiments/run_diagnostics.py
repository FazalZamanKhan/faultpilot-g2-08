"""Frozen held-out diagnosis evaluation; never selects settings on test data."""

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import f1_score, precision_score, recall_score

from faultpilot.benchmark import load_cases
from faultpilot.data import CATEGORIES, EXPECTED_SHA256
from faultpilot.diagnostics import DiagnosticModel, phase1_labels


def matrix(label_rows):
    return np.array([[int(label in labels) for label in CATEGORIES] for labels in label_rows])


def metrics(cases, predictions):
    truth = matrix([case.labels for case in cases])
    predicted = matrix(predictions)
    return {
        "count": len(cases),
        "macro_f1": round(float(f1_score(truth, predicted, average="macro", zero_division=0)), 5),
        "micro_f1": round(float(f1_score(truth, predicted, average="micro", zero_division=0)), 5),
        "macro_precision": round(float(precision_score(truth, predicted, average="macro", zero_division=0)), 5),
        "macro_recall": round(float(recall_score(truth, predicted, average="macro", zero_division=0)), 5),
        "exact_match": round(float(np.mean(np.all(truth == predicted, axis=1))), 5),
        "per_category_f1": {name: round(float(score), 5) for name, score in zip(
            CATEGORIES, f1_score(truth, predicted, average=None, zero_division=0))},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="research/.external_data/MLDebugging.jsonl")
    parser.add_argument("--config", default="experiments/diagnostic_config.json")
    parser.add_argument("--output", default="results/diagnostic_evaluation.json")
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    if config["dataset_sha256"] != EXPECTED_SHA256:
        raise ValueError("Configuration was selected on a different dataset")
    cases = load_cases(args.data)
    train = [case for case in cases if case.split == "development"]
    test = [case for case in cases if case.split == "test"]
    model = DiagnosticModel(train)
    threshold = config["selected"]["threshold"]
    alpha = config["selected"]["alpha"]
    phase1 = [phase1_labels(case) for case in test]
    classifier = [model.diagnose(case, retrieval=False, threshold=threshold) for case in test]
    full = [model.diagnose(case, retrieval=True, alpha=alpha, threshold=threshold) for case in test]
    fusion = [model.diagnose(case, retrieval=True, alpha=0.2, threshold=threshold) for case in test]
    output = {
        "protocol": "Held-out task-grouped test; model trained on all 941 development cases; hyperparameters frozen on development validation",
        "dataset_sha256": EXPECTED_SHA256,
        "configuration": config["selected"],
        "metrics": {
            "E1_phase1_rule_baseline": metrics(test, phase1),
            "trained_diagnosis_no_retrieval": metrics(test, [row.labels for row in classifier]),
            "full_evidence_retrieval": metrics(test, [row.labels for row in full]),
            "retrieval_score_fusion_alpha_0_2_ablation": metrics(test, [row.labels for row in fusion]),
        },
        "evidence_coverage": {
            "with_local_code_lines": sum(bool(row.evidence) for row in full),
            "with_retrieved_examples": sum(bool(row.retrieved) for row in full),
            "denominator": len(test),
            "note": "Evidence availability is not localization correctness; no gold fault line is provided.",
        },
        "predictions": [
            {"case_id": case.case_id, "task_id": case.task_id, "truth": case.labels,
             "phase1": phase1[index], "classifier": classifier[index].labels,
             "full": full[index].labels, "fusion_0_2": fusion[index].labels,
             "confidence": full[index].confidence, "evidence": full[index].evidence,
             "retrieved": full[index].retrieved}
            for index, case in enumerate(test)
        ],
    }
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output["metrics"], indent=2))


if __name__ == "__main__":
    main()
