"""Generate factual LaTeX tables from complete saved Phase 2 results."""

import argparse
import json
from pathlib import Path

from experiments.run_repairs import MODES


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--diagnosis", default="results/diagnostic_evaluation.json")
    parser.add_argument("--baseline", default="results/E1_baseline_repair.json")
    parser.add_argument("--aggregate", default="results/repair_aggregate.json")
    parser.add_argument("--output", default="paper/tables.tex")
    args = parser.parse_args()
    diagnosis = json.loads(Path(args.diagnosis).read_text())["metrics"]
    baseline_repair = json.loads(Path(args.baseline).read_text())
    if baseline_repair["test_count"] != 234 or baseline_repair["verified_repair_passes"] != 0:
        raise ValueError("Phase 1 repair-scale baseline is incomplete or inconsistent")
    aggregate = json.loads(Path(args.aggregate).read_text())
    runs = aggregate["runs"]
    eligible_count = aggregate["preflight"]["repair_eligible"]
    missing = [name for name in MODES if name not in runs or runs[name]["evaluated"] != 234]
    if missing:
        raise ValueError(f"Cannot build final tables from incomplete runs: {missing}")
    end = chr(92) * 2
    base = diagnosis["E1_phase1_rule_baseline"]
    learned = diagnosis["trained_diagnosis_no_retrieval"]
    fusion = diagnosis["retrieval_score_fusion_alpha_0_2_ablation"]
    rows = [
        "% Generated from saved results. Do not hand-edit measured values.",
        r"\begin{table}[t]", r"\centering",
        r"\caption{[Author: write an original diagnosis-table caption.]}",
        r"\label{tab:diagnosis}", r"\begin{tabular}{lrr}", r"\toprule",
        "Method & Macro F1 & Exact match " + end, r"\midrule",
        f"Phase 1 rules & {base['macro_f1']:.3f} & {base['exact_match']:.3f} " + end,
        f"Learned diagnosis & {learned['macro_f1']:.3f} & {learned['exact_match']:.3f} " + end,
        f"Retrieval fusion 0.2 & {fusion['macro_f1']:.3f} & {fusion['exact_match']:.3f} " + end,
        r"\bottomrule", r"\end{tabular}", r"\end{table}", "",
        r"\begin{table*}[t]", r"\centering",
        r"\caption{[Author: write an original repair-results caption.]}",
        r"\label{tab:repair}", r"\begin{tabular}{lrrrrrr}", r"\toprule",
        r"Mode & Verified & Eligible rate (\%) & Abstained & Audit pass & Mean seconds & Mean tool calls " + end,
        r"\midrule",
        "E1 rules (no edit) & 0 & 0.0 & 0 & 0 & -- & 0.00 " + end,
    ]
    display = [("E2 adaptation", "E2_repairagent_style"), ("E3 full", "E3_full"),
               ("No retrieval", "E5_no_retrieval"),
               ("No verification", "E5_no_verification"), ("No gate", "E5_no_gate")]
    for label, key in display:
        run = runs[key]
        rows.append(
            f"{label} & {run['verified_passes']} & {100 * run['verified_rate_on_repair_eligible']:.1f} & "
            f"{run['status_counts'].get('abstained_insufficient_evidence', 0)} & "
            f"{run['offline_audit_passes_for_unverified_proposals']} & "
            f"{run['mean_agent_wall_s_excluding_offline_audit']:.1f} & "
            f"{run['mean_tool_calls']:.2f} " + end
        )
    e2 = runs["E2_repairagent_style"]
    e3 = runs["E3_full"]
    no_verify = runs["E5_no_verification"]
    no_gate = runs["E5_no_gate"]
    rows += [
        r"\bottomrule", r"\end{tabular}", r"\end{table*}", "",
        r"\begin{table*}[t]", r"\centering",
        r"\caption{[Author: write an original gap-resolution caption.]}",
        r"\label{tab:gaps}",
        r"\begin{tabular}{p{0.5cm}p{2.6cm}p{2.0cm}p{2.1cm}p{4.5cm}p{1.0cm}}",
        r"\toprule",
        "Gap & Component & Metric & E2 adaptation & Our result & Status " + end,
        r"\midrule",
        f"1 & Evidence retrieval & Macro F1 & No diagnosis score & Learned {learned['macro_f1']:.3f}; rules {base['macro_f1']:.3f}; fusion {fusion['macro_f1']:.3f} & [Author: status] " + end,
        f"2 & Test verification & Passing cases & {e2['verified_passes']}/{eligible_count} pass & Full {e3['verified_passes']}; unverified audit {no_verify['offline_audit_passes_for_unverified_proposals']} & [Author: status] " + end,
        f"3 & Evidence gate & Pass / abstain & {e2['verified_passes']}/{eligible_count}; no gate & Full {e3['verified_passes']} / {e3['status_counts'].get('abstained_insufficient_evidence', 0)}; no gate {no_gate['verified_passes']} / {no_gate['status_counts'].get('abstained_insufficient_evidence', 0)} & [Author: status] " + end,
        r"\bottomrule", r"\end{tabular}", r"\end{table*}", "",
    ]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(rows))
    print(f"Wrote {output} from complete E1--E6 saved results")


if __name__ == "__main__":
    main()
