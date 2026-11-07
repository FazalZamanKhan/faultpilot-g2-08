"""Check frozen repair traces against the committed test manifest and protocol."""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from experiments.run_repairs import MODES
from faultpilot.agent import PROMPT_VERSION
from faultpilot.data import EXPECTED_SHA256


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="results/test_manifest.json")
    parser.add_argument("--preflight", default="results/test_preflight.jsonl")
    parser.add_argument("--environment", default="results/environment.json")
    parser.add_argument("--input-dir", default="results/repairs")
    parser.add_argument("--output", default="results/repair_validation.json")
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text())
    assert manifest["dataset_sha256"] == EXPECTED_SHA256
    ids = set(manifest["ids"])
    assert len(ids) == manifest["count"] == 234
    preflight = {row["case_id"]: row for row in read_jsonl(Path(args.preflight))}
    assert set(preflight) == ids
    eligible = {case_id for case_id, row in preflight.items() if row["status"] == "fail"}
    assert len(eligible) == 198

    report = {"test_cases": len(ids), "repair_eligible": len(eligible), "modes": {}}
    digests = set()
    for mode, switches in MODES.items():
        rows = read_jsonl(Path(args.input_dir) / f"{mode}.jsonl")
        attempts = defaultdict(list)
        for row in rows:
            attempts[row["case_id"]].append(row)
        assert set(attempts) == ids, f"{mode}: missing or unexpected case IDs"
        assert all(all(row["status"] == "provider_error" for row in group[:-1])
                   and group[-1]["status"] != "provider_error" for group in attempts.values()), \
            f"{mode}: duplicate result or unresolved provider error"
        final = [group[-1] for group in attempts.values()]
        assert all(row["mode"] == mode and row["prompt_version"] == PROMPT_VERSION for row in rows)
        assert all(row["configuration"][key] == value for row in rows
                   for key, value in switches.items()), f"{mode}: wrong switch configuration"
        assert all(row["configuration"]["attempts"] == 2 and
                   row["configuration"]["seed"] == 17 and
                   row["configuration"]["temperature"] == 0 for row in rows)
        assert all(row["trace"] and row["trace"][0]["step"] == "reproduce" for row in rows)
        assert all(row["trace"][0]["result"]["status"] == preflight[row["case_id"]]["status"]
                   for row in rows), f"{mode}: original outcome changed"
        assert all(row["case_id"] in eligible or row["status"] in
                   ("environment_blocked", "original_already_passes") for row in rows)
        assert all(row["status"] != "verified_by_supplied_tests" or any(
            step["step"] == "test" and step["result"]["status"] == "pass"
            for step in row["trace"]) for row in rows)
        digests.update(row["model_digest"] for row in rows)
        report["modes"][mode] = {"cases": len(final), "provider_retries": len(rows) - len(final),
                                 "statuses": dict(Counter(row["status"] for row in final)),
                                 "verified_passes": sum(row["status"] == "verified_by_supplied_tests"
                                                        for row in final)}
    assert len(digests) == 1, "Compared modes use different model digests"
    report["model_digest"] = next(iter(digests))
    environment = json.loads(Path(args.environment).read_text())
    assert report["model_digest"] == environment["installed_model_digests"]["qwen2.5-coder:0.5b"]
    report["status"] = "passed"
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "modes": len(report["modes"]),
                      "cases_per_mode": len(ids)}))


if __name__ == "__main__":
    main()
