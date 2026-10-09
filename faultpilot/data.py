"""Reproducible ingestion and profiling of the published MLDebugging data."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from urllib.request import Request, urlopen

SOURCE_URL = (
    "https://raw.githubusercontent.com/hjyTsuki/MLDebugging/"
    "0fd4dec184721ffaa71584d7df7c015244f9ff6a/data/MLDebugging.jsonl"
)
EXPECTED_SHA256 = "52b076ad3230911208483df7af95543ed81b92ffec077db792315f680490df07"
CATEGORIES = (
    "Type Mismatch",
    "Data Transfer Issues",
    "Function Parameter Errors",
    "Parameter Configuration Errors",
    "Function Misuse",
    "Requirement Misunderstanding",
    "Import Errors",
)
REQUIRED_FIELDS = {"ID", "task_id", "bug_code", "golden_code", "test_case", "runtime_feedback", "category"}


def download(destination):
    request = Request(SOURCE_URL, headers={"User-Agent": "FaultPilot-Phase1"})
    with urlopen(request, timeout=30) as response:
        data = response.read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError(f"Dataset checksum mismatch: {digest}")
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    return destination


def extract_categories(raw_label):
    """Extract published category names, preserving multi-label examples."""
    text = raw_label.lower()
    labels = [category for category in CATEGORIES if category.lower() in text]
    if "misuse of function" in text and "Function Misuse" not in labels:
        labels.append("Function Misuse")
    return labels


def profile(path):
    path = Path(path)
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != EXPECTED_SHA256:
        raise ValueError("Dataset checksum mismatch")
    counts = Counter()
    total = multi_label = missing_feedback = 0
    split_counts = Counter()
    for line_number, line in enumerate(data.splitlines(), 1):
        if not line.strip():
            continue
        item = json.loads(line)
        missing = REQUIRED_FIELDS - item.keys()
        if missing:
            raise ValueError(f"Line {line_number} missing fields: {sorted(missing)}")
        total += 1
        # Related variants share task_id; keep them on the same side of the split.
        group_hash = int(hashlib.sha256(item["task_id"].encode()).hexdigest(), 16)
        split_counts["test" if group_hash % 5 == 0 else "development"] += 1
        labels = extract_categories(item["category"])
        counts.update(labels)
        multi_label += len(labels) > 1
        missing_feedback += not bool(item["runtime_feedback"])
    return {
        "source": SOURCE_URL,
        "sha256": EXPECTED_SHA256,
        "records": total,
        "category_mentions": dict(sorted(counts.items())),
        "records_with_multiple_category_mentions": multi_label,
        "records_without_runtime_feedback": missing_feedback,
        "split_rule": "sha256(task_id) modulo 5 == 0 => test; otherwise development",
        "split_counts": dict(sorted(split_counts.items())),
        "note": "Data profile only; no model or diagnosis accuracy was measured.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Fetch the pinned source dataset")
    parser.add_argument("--data", default="research/.external_data/MLDebugging.jsonl")
    parser.add_argument("--output", default="outputs/mldebugging_profile.json")
    args = parser.parse_args()
    path = download(args.data) if args.download else Path(args.data)
    result = profile(path)
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
