"""Reconstruct reviewer-readable prompts and patches for saved representative traces."""

import argparse
import json
from pathlib import Path

from faultpilot.agent import apply_edit, build_prompt
from faultpilot.benchmark import load_cases
from faultpilot.diagnostics import Diagnosis


def expand(row, case):
    saved = row["diagnosis"]
    diagnosis = None if saved is None else Diagnosis(
        tuple(saved["labels"]), saved["confidence"], {}, saved["evidence"], saved["retrieved"])
    previous = ""
    proposal = None
    steps = []
    for step in row["trace"]:
        enriched = dict(step)
        if step["step"] in ("propose", "provider_error", "model_response_error"):
            enriched["prompt"] = build_prompt(case, diagnosis, previous=previous,
                                               retrieval=row["configuration"]["retrieval"])
        if step["step"] == "propose":
            proposal = step["proposal"]
        elif step["step"] == "edit":
            patched, edit_status = apply_edit(case.bug_code, proposal)
            if edit_status != step["status"]:
                raise ValueError(f"Edit status mismatch for {case.case_id}")
            if patched is None:
                previous = (f"The edit was rejected: {edit_status}. Choose a numbered BUG CODE line "
                            "and give a different valid replacement for that whole line.")
            else:
                enriched["patched_source"] = patched
        elif step["step"] == "test":
            previous = json.dumps(step["result"].get("details", {}))[-1800:]
        steps.append(enriched)
    return {"case_id": row["case_id"], "task_id": row["task_id"], "mode": row["mode"],
            "status": row["status"], "prompt_version": row["prompt_version"],
            "reconstruction_note": "Prompts and patched sources regenerated from the pinned case and saved trajectory; model outputs and test results are the original recorded values.",
            "steps": steps}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="research/.external_data/MLDebugging.jsonl")
    parser.add_argument("--analysis", default="results/failure_analysis.json")
    parser.add_argument("--output", default="results/trace_samples.json")
    args = parser.parse_args()
    analysis = json.loads(Path(args.analysis).read_text())
    selected = analysis["representative_successes"] + analysis["representative_failures"]
    cases = {case.case_id: case for case in load_cases(args.data) if case.split == "test"}
    result = {"selected_case_ids": [row["case_id"] for row in selected],
              "traces": [expand(row, cases[row["case_id"]]) for row in selected],
              "note": "No success case is fabricated when fewer than two exist."}
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Wrote {len(selected)} expanded traces to {output}")


if __name__ == "__main__":
    main()
