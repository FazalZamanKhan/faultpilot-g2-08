import json
import subprocess
import sys
from pathlib import Path

TAXONOMY = {
    "shape_mismatch": {"tokens": ["shapes cannot be multiplied", "size mismatch", "dimension mismatch"], "hint": "Inspect tensor dimensions and the expected layer input width."},
    "device_mismatch": {"tokens": ["same device", "cuda", "cpu"], "hint": "Check model and tensor device placement."},
    "missing_dependency": {"tokens": ["modulenotfounderror", "no module named"], "hint": "Verify the package is installed in the active environment."},
}

def diagnose(case):
    traceback = case.get("traceback", "").lower()
    category = next((k for k, v in TAXONOMY.items() if any(t in traceback for t in v["tokens"])), "unknown")
    hint = TAXONOMY.get(category, {}).get("hint", "Insufficient taxonomy evidence; investigate manually.")
    return {"case_id": case["case_id"], "category": category, "diagnosis": hint, "repair_hint": hint, "confidence_proxy": "rule_match" if category != "unknown" else "no_match"}

def run_reproducer(case):
    cmd = case.get("reproducer", [])
    if not (isinstance(cmd, list) and len(cmd) == 3 and cmd[:2] == ["python", "-c"]):
        raise ValueError("Demo runner only accepts a Python -c reproducer")
    # Cases are local, trusted fixtures. Never pass model-generated commands here.
    proc = subprocess.run([sys.executable, "-c", cmd[2]], capture_output=True, text=True, timeout=5)
    return {"exit_code": proc.returncode, "reproduction_failed": proc.returncode != 0, "stdout": proc.stdout[-2000:], "stderr": proc.stderr[-2000:]}

def evaluate(case):
    result = diagnose(case)
    result.update(run_reproducer(case))
    result["category_correct"] = result["category"] == case.get("expected_category")
    result["status"] = "diagnosis_only_no_repair_attempted"
    return result
