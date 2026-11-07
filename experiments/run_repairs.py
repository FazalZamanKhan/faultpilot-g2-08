"""Run frozen, paired RepairAgent-style and FaultPilot experiments."""

import argparse
import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path

from faultpilot.agent import AgentSettings, OllamaClient, PROMPT_VERSION, run_agent
from faultpilot.benchmark import load_cases
from faultpilot.data import EXPECTED_SHA256
from faultpilot.diagnostics import DiagnosticModel

MODES = {
    "E2_repairagent_style": dict(retrieval=False, verification=True, evidence_gate=False),
    "E3_full": dict(retrieval=True, verification=True, evidence_gate=True),
    "E5_no_retrieval": dict(retrieval=False, verification=True, evidence_gate=True),
    "E5_no_verification": dict(retrieval=True, verification=False, evidence_gate=True),
    "E5_no_gate": dict(retrieval=True, verification=True, evidence_gate=False),
}


def summarize(path: Path, denominator: int, eligible: int) -> dict:
    latest = {row["case_id"]: row for line in path.read_text().splitlines()
              if line.strip() and (row := json.loads(line))}
    rows = list(latest.values())
    statuses = Counter(row["status"] for row in rows)
    eligible_rows = [row for row in rows if row["trace"][0]["result"]["status"] == "fail"]
    attempted_rows = [row for row in rows if any(step["step"] == "propose" for step in row["trace"])]
    agent_times = [row.get("agent_wall_s", row["wall_s"]) for row in rows]
    audited = sum(any(step["step"] == "offline_audit" and step["result"]["status"] == "pass"
                      for step in row["trace"]) for row in rows)
    return {
        "evaluated": len(rows), "fixed_test_denominator": denominator, "eligible_after_preflight": eligible,
        "evaluated_repair_eligible": len(eligible_rows), "model_attempted": len(attempted_rows),
        "status_counts": dict(statuses),
        "verified_passes": statuses["verified_by_supplied_tests"],
        "offline_audit_passes_for_unverified_proposals": audited,
        "offline_audit_failures_for_unverified_proposals": statuses["unverified_proposal"] - audited,
        "verified_rate_on_evaluated": round(statuses["verified_by_supplied_tests"] / len(rows), 5) if rows else None,
        "verified_rate_on_repair_eligible": round(statuses["verified_by_supplied_tests"] / eligible, 5) if eligible else None,
        "mean_wall_s": round(statistics.mean(row["wall_s"] for row in rows), 3) if rows else None,
        "mean_agent_wall_s_excluding_offline_audit": round(statistics.mean(agent_times), 3) if rows else None,
        "median_agent_wall_s_across_cases": round(statistics.median(agent_times), 3) if rows else None,
        "std_agent_wall_s_across_cases": round(statistics.stdev(agent_times), 3) if len(rows) > 1 else None,
        "mean_agent_wall_s_on_model_attempts": round(statistics.mean(
            row.get("agent_wall_s", row["wall_s"]) for row in attempted_rows), 3) if attempted_rows else None,
        "mean_tool_calls": round(statistics.mean(row["tool_calls"] for row in rows), 3) if rows else None,
        "mean_tool_calls_on_repair_eligible": round(statistics.mean(
            row["tool_calls"] for row in eligible_rows), 3) if eligible_rows else None,
        "sum_prompt_tokens": sum(row["prompt_tokens"] for row in rows),
        "sum_output_tokens": sum(row["output_tokens"] for row in rows),
        "mean_prompt_tokens_on_model_attempts": round(statistics.mean(
            row["prompt_tokens"] for row in attempted_rows), 1) if attempted_rows else None,
        "mean_output_tokens_on_model_attempts": round(statistics.mean(
            row["output_tokens"] for row in attempted_rows), 1) if attempted_rows else None,
        "monetary_api_cost_usd": 0,
        "cost_note": "Local Ollama inference; electricity and hardware amortization were not measured.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="research/.external_data/MLDebugging.jsonl")
    parser.add_argument("--preflight", default="results/test_preflight.jsonl")
    parser.add_argument("--config", default="experiments/diagnostic_config.json")
    parser.add_argument("--output-dir", default="results/repairs")
    parser.add_argument("--model", default="qwen2.5-coder:0.5b")
    parser.add_argument("--mode", choices=(*MODES, "all"), default="all")
    parser.add_argument("--limit", type=int, default=0,
                        help="Fixed hash-ordered eligible prefix for pilots; 0 traces all held-out cases")
    parser.add_argument("--attempts", type=int, default=2)
    args = parser.parse_args()
    if args.attempts < 1 or args.attempts > 3 or args.limit < 0:
        parser.error("attempts must be 1..3 and limit cannot be negative")
    config = json.loads(Path(args.config).read_text())
    if config["dataset_sha256"] != EXPECTED_SHA256:
        raise ValueError("Diagnostic config does not match pinned dataset")
    cases = load_cases(args.data)
    dev = [case for case in cases if case.split == "development"]
    test = [case for case in cases if case.split == "test"]
    preflight = {row["case_id"]: row for line in Path(args.preflight).read_text().splitlines()
                 if (row := json.loads(line))}
    if set(preflight) != {case.case_id for case in test}:
        raise ValueError("Preflight IDs do not match frozen test manifest")
    eligible = [case for case in test if preflight[case.case_id]["status"] == "fail"]
    eligible.sort(key=lambda case: (hashlib.sha256(case.case_id.encode()).hexdigest(), case.case_id))
    selected = eligible[:args.limit] if args.limit else sorted(
        test, key=lambda case: (hashlib.sha256(case.case_id.encode()).hexdigest(), case.case_id))
    model = DiagnosticModel(dev)
    diagnoses = {case.case_id: model.diagnose(case, retrieval=True,
                                             alpha=config["selected"]["alpha"],
                                             threshold=config["selected"]["threshold"])
                 for case in selected}
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    modes = MODES if args.mode == "all" else {args.mode: MODES[args.mode]}
    for mode, switches in modes.items():
        path = output_dir / f"{mode}.jsonl"
        settings = AgentSettings(model=args.model, attempts=args.attempts,
                                 confidence_floor=config["selected_gate"]["confidence_floor"],
                                 **switches)
        client = OllamaClient(settings)
        model_digest = client.model_digest()
        existing = [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
        for row in existing:
            if (row.get("model_digest") != model_digest or row.get("configuration") != settings.__dict__
                    or row.get("prompt_version") != PROMPT_VERSION):
                raise ValueError(f"Existing {path} uses a different model or configuration")
        done = {row["case_id"] for row in existing if row["status"] != "provider_error"}
        for index, case in enumerate(selected, 1):
            if case.case_id in done:
                continue
            diagnosis = None if mode == "E2_repairagent_style" else diagnoses[case.case_id]
            row = run_agent(case, settings, client, diagnosis, preflight[case.case_id])
            row["mode"] = mode
            row["model_digest"] = model_digest
            with path.open("a") as handle:
                handle.write(json.dumps(row) + "\n")
            print(f"{mode} {index}/{len(selected)} {case.case_id}: {row['status']}", flush=True)
            if row["status"] == "provider_error":
                raise RuntimeError("Provider unavailable; restart Ollama and resume this command")
        summary = summarize(path, len(test), len(eligible))
        (output_dir / f"{mode}_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        print(json.dumps({"mode": mode, **summary}, indent=2), flush=True)


if __name__ == "__main__":
    main()
