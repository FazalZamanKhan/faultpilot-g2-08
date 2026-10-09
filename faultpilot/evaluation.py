"""Small, transparent smoke evaluation for the deterministic baseline."""

import argparse
import json
from collections import Counter
from pathlib import Path

from .core import evaluate


def evaluate_directory(case_dir):
    rows = []
    for path in sorted(Path(case_dir).glob("*.json")):
        case = json.loads(path.read_text(encoding="utf-8"))
        result = evaluate(case)
        rows.append({
            "case_id": result["case_id"],
            "expected_category": case["expected_category"],
            "predicted_category": result["category"],
            "category_correct": result["category_correct"],
            "reproduction_failed": result["reproduction_failed"],
            "status": result["status"],
        })
    if not rows:
        raise ValueError(f"No JSON cases found in {case_dir}")
    by_category = Counter(row["expected_category"] for row in rows)
    return {
        "scope": "synthetic_smoke_cases_only_not_research_accuracy",
        "cases": len(rows),
        "category_accuracy": sum(row["category_correct"] for row in rows) / len(rows),
        "reproduction_rate": sum(row["reproduction_failed"] for row in rows) / len(rows),
        "class_counts": dict(sorted(by_category.items())),
        "results": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", default="cases")
    parser.add_argument("--output", default="outputs/smoke_evaluation.json")
    args = parser.parse_args()
    result = evaluate_directory(args.cases)
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
