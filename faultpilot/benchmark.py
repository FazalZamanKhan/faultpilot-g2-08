"""Pinned MLDebugging records and the frozen source-task split."""

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from .data import CATEGORIES, EXPECTED_SHA256, extract_categories


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    task_id: str
    bug_code: str
    golden_code: str
    test_code: str
    runtime_feedback: str
    labels: tuple[str, ...]
    raw_category: str
    split: str


def split_for_task(task_id: str) -> str:
    digest = int(hashlib.sha256(task_id.encode("utf-8")).hexdigest(), 16)
    return "test" if digest % 5 == 0 else "development"


def load_cases(path: str | Path) -> list[BenchmarkCase]:
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_SHA256:
        raise ValueError("MLDebugging checksum mismatch")
    cases = []
    ids = set()
    for number, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            continue
        item = json.loads(line)
        case_id = item["ID"]
        if case_id in ids:
            raise ValueError(f"Duplicate ID at line {number}: {case_id}")
        ids.add(case_id)
        labels = tuple(extract_categories(item["category"]))
        if not labels or not set(labels) <= set(CATEGORIES):
            raise ValueError(f"Unrecognized category in {case_id}")
        cases.append(BenchmarkCase(
            case_id=case_id,
            task_id=item["task_id"],
            bug_code=item["bug_code"],
            golden_code=item["golden_code"],
            test_code=item["test_case"],
            runtime_feedback=item["runtime_feedback"],
            labels=labels,
            raw_category=item["category"],
            split=split_for_task(item["task_id"]),
        ))
    return cases


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="research/.external_data/MLDebugging.jsonl")
    parser.add_argument("--split", choices=("development", "test", "all"), default="all")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    cases = [c for c in load_cases(args.data) if args.split == "all" or c.split == args.split]
    manifest = {
        "dataset_sha256": EXPECTED_SHA256,
        "split": args.split,
        "count": len(cases),
        "ids": [c.case_id for c in cases],
        "multi_label_count": sum(len(c.labels) > 1 for c in cases),
    }
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote {len(cases)} case IDs to {destination}")


if __name__ == "__main__":
    main()
