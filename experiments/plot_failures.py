"""Plot final-system outcome categories from the saved failure analysis."""

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


LABELS = {
    "supplied_tests_passed": "Supplied tests passed",
    "evidence_gate_abstention": "Evidence gate abstained",
    "provider_unavailable": "Provider unavailable",
    "environment_blocked": "Original environment blocked",
    "original_already_passes": "Original already passed",
    "malformed_model_response": "Malformed model response",
    "candidate_did_not_load": "Candidate failed to load",
    "candidate_timed_out": "Candidate timed out",
    "candidate_failed_tests": "Candidate failed tests",
    "all_edits_rejected": "All edits rejected",
    "other": "Other",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="results/failure_analysis.json")
    parser.add_argument("--output", default="paper/failure_categories.png")
    args = parser.parse_args()
    analysis = json.loads(Path(args.input).read_text())
    counts = analysis["failure_category_counts_evaluated"]
    if analysis["evaluated_repair_cases"] != 234 or sum(counts.values()) != 234:
        raise ValueError("Plot requires the complete held-out failure analysis")
    ordered = sorted(counts.items(), key=lambda item: (item[1], item[0]))
    names = [LABELS.get(key, key.replace("_", " ")) for key, _ in ordered]
    values = [value for _, value in ordered]
    fig, ax = plt.subplots(figsize=(6.2, max(2.8, 0.39 * len(ordered) + 0.9)), dpi=220)
    colors = ["#2d6a4f" if key == "supplied_tests_passed" else "#3b5b92"
              for key, _ in ordered]
    bars = ax.barh(names, values, color=colors, height=0.66)
    ax.bar_label(bars, padding=3, fontsize=8)
    ax.set_xlim(0, max(values) * 1.16 if values else 1)
    ax.set_xlabel("Held-out cases (n = 234)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=8)
    ax.tick_params(axis="x", labelsize=8)
    ax.grid(axis="x", color="#e7e7e7", linewidth=0.5)
    ax.set_axisbelow(True)
    fig.tight_layout()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {output} from {len(ordered)} saved outcome categories")


if __name__ == "__main__":
    main()
