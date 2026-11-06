"""Run FaultPilot on one pinned MLDebugging case and save its complete trace."""

import argparse
import json
from pathlib import Path

from .agent import AgentSettings, OllamaClient, run_agent
from .benchmark import load_cases
from .data import EXPECTED_SHA256
from .diagnostics import DiagnosticModel


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--data", default="research/.external_data/MLDebugging.jsonl")
    parser.add_argument("--config", default="experiments/diagnostic_config.json")
    parser.add_argument("--model", default="qwen2.5-coder:0.5b")
    parser.add_argument("--output", required=True)
    parser.add_argument("--no-retrieval", action="store_true")
    parser.add_argument("--no-verification", action="store_true")
    parser.add_argument("--no-gate", action="store_true")
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    if config["dataset_sha256"] != EXPECTED_SHA256:
        raise ValueError("Diagnostic configuration is from a different dataset")
    cases = load_cases(args.data)
    matches = [case for case in cases if case.case_id == args.case_id]
    if len(matches) != 1:
        parser.error("case ID not found")
    case = matches[0]
    model = DiagnosticModel([row for row in cases if row.split == "development"])
    diagnosis = model.diagnose(case, retrieval=not args.no_retrieval,
                               alpha=config["selected"]["alpha"],
                               threshold=config["selected"]["threshold"])
    settings = AgentSettings(model=args.model, retrieval=not args.no_retrieval,
                             verification=not args.no_verification, evidence_gate=not args.no_gate,
                             confidence_floor=config["selected_gate"]["confidence_floor"])
    result = run_agent(case, settings, OllamaClient(settings), diagnosis)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"case_id": case.case_id, "status": result["status"],
                      "wall_s": result["wall_s"], "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()
