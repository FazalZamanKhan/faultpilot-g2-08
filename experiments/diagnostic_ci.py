"""Task-group bootstrap intervals and an honest static diagnosis figure."""

import argparse
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import f1_score

from faultpilot.data import CATEGORIES


def binary(rows, key):
    return np.array([[int(label in row[key]) for label in CATEGORIES] for row in rows])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="results/diagnostic_evaluation.json")
    parser.add_argument("--output", default="results/diagnostic_ci.json")
    parser.add_argument("--figure", default="paper/diagnosis_macro_f1.png")
    parser.add_argument("--replicates", type=int, default=2000)
    args = parser.parse_args()
    rows = json.loads(Path(args.input).read_text())["predictions"]
    truth = binary(rows, "truth")
    modes = {"Phase 1 rules": binary(rows, "phase1"),
             "Learned diagnosis": binary(rows, "classifier"),
             "Retrieval fusion 0.2": binary(rows, "fusion_0_2")}
    groups = defaultdict(list)
    for index, row in enumerate(rows):
        groups[row["task_id"]].append(index)
    names = sorted(groups)
    rng = np.random.default_rng(17)
    bootstrap = {name: [] for name in modes}
    differences = []
    for _ in range(args.replicates):
        sampled = rng.choice(names, size=len(names), replace=True)
        indices = [index for task in sampled for index in groups[task]]
        scores = {name: float(f1_score(truth[indices], predicted[indices],
                                       average="macro", zero_division=0))
                  for name, predicted in modes.items()}
        for name, score in scores.items():
            bootstrap[name].append(score)
        differences.append(scores["Learned diagnosis"] - scores["Phase 1 rules"])
    result = {
        "test_records": len(rows), "task_groups": len(names), "bootstrap_replicates": args.replicates,
        "seed": 17, "resampling_unit": "task_id",
        "macro_f1": {name: {
            "observed": round(float(f1_score(truth, prediction, average="macro", zero_division=0)), 5),
            "ci95": [round(float(q), 5) for q in np.quantile(bootstrap[name], [0.025, 0.975])],
        } for name, prediction in modes.items()},
        "learned_minus_rules": {
            "observed": round(float(f1_score(truth, modes["Learned diagnosis"], average="macro", zero_division=0)
                                    - f1_score(truth, modes["Phase 1 rules"], average="macro", zero_division=0)), 5),
            "ci95": [round(float(q), 5) for q in np.quantile(differences, [0.025, 0.975])],
        },
    }
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + "\n")
    names_plot = list(modes)
    observed = [result["macro_f1"][name]["observed"] for name in names_plot]
    lower = [observed[i] - result["macro_f1"][name]["ci95"][0] for i, name in enumerate(names_plot)]
    upper = [result["macro_f1"][name]["ci95"][1] - observed[i] for i, name in enumerate(names_plot)]
    fig, ax = plt.subplots(figsize=(6.8, 3.1), dpi=200)
    bars = ax.bar(names_plot, observed, color=["#64748b", "#2563eb", "#16a34a"], width=0.62)
    ax.errorbar(range(len(names_plot)), observed, yerr=[lower, upper], fmt="none",
                ecolor="#111827", capsize=4, linewidth=1.1)
    ax.set_ylabel("Macro F1 on 234 held-out records")
    ax.set_ylim(0, max(0.42, max(observed) + max(upper) + 0.05))
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="x", labelsize=8)
    for bar, value in zip(bars, observed):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.015, f"{value:.3f}",
                ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    figure = Path(args.figure)
    figure.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(figure)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
