"""Development-only pilot for repair model and prompt contract checks."""

import argparse
import hashlib
import json
from pathlib import Path

from faultpilot.agent import AgentSettings, OllamaClient, run_agent
from faultpilot.benchmark import load_cases
from faultpilot.diagnostics import DiagnosticModel
from faultpilot.sandbox import run_tests


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="research/.external_data/MLDebugging.jsonl")
    parser.add_argument("--config", default="experiments/diagnostic_config.json")
    parser.add_argument("--model", default="qwen2.5-coder:0.5b")
    parser.add_argument("--preflight-count", type=int, default=30)
    parser.add_argument("--repair-limit", type=int, default=10)
    parser.add_argument("--output", default="results/development_pilot.jsonl")
    args = parser.parse_args()
    if args.preflight_count < 1 or args.repair_limit < 1:
        parser.error("counts must be positive")
    cases = load_cases(args.data)
    def fold(case):
        return int(hashlib.sha256(case.task_id.encode()).hexdigest(), 16) % 5
    train = [case for case in cases if fold(case) in (2, 3, 4)]
    validation = [case for case in cases if fold(case) == 1]
    validation.sort(key=lambda case: (hashlib.sha256(case.case_id.encode()).hexdigest(), case.case_id))
    model = DiagnosticModel(train)
    config = json.loads(Path(args.config).read_text())
    settings = AgentSettings(model=args.model,
                             confidence_floor=config["selected_gate"]["confidence_floor"])
    client = OllamaClient(settings)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    done = {json.loads(line)["case_id"] for line in output.read_text().splitlines()} if output.exists() else set()
    repairs = 0
    for case in validation[:args.preflight_count]:
        if case.case_id in done:
            repairs += 1
            continue
        preflight = run_tests(case.bug_code, case.test_code, timeout=settings.timeout_s)
        if preflight["status"] != "fail":
            print(f"{case.case_id}: {preflight['status']} (ineligible)", flush=True)
            continue
        diagnosis = model.diagnose(case, retrieval=True, alpha=config["selected"]["alpha"],
                                   threshold=config["selected"]["threshold"])
        result = run_agent(case, settings, client, diagnosis, preflight)
        result["split"] = "development_validation"
        with output.open("a") as file:
            file.write(json.dumps(result) + "\n")
        repairs += 1
        print(f"{case.case_id}: {result['status']} ({repairs}/{args.repair_limit})", flush=True)
        if repairs >= args.repair_limit:
            break


if __name__ == "__main__":
    main()
