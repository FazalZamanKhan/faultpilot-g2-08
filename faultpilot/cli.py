import argparse
import json
from pathlib import Path
from .core import evaluate

def main():
    p = argparse.ArgumentParser(description="FaultPilot deterministic Phase 1 baseline")
    p.add_argument("--case", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    result = evaluate(json.loads(Path(args.case).read_text(encoding="utf-8")))
    dest = Path(args.output); dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
