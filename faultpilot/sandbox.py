"""Execute benchmark tests with no network or access to the user home."""

import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

RUNNER = Path(__file__).with_name("_sandbox_runner.py")
SYSTEM_BINDS = ("/usr", "/bin", "/lib", "/lib64", "/etc/alternatives", "/etc/ld.so.cache",
                "/etc/matplotlibrc", "/etc/fonts")


def run_tests(code: str, test_code: str, timeout: float = 12.0) -> dict:
    if not shutil.which("bwrap"):
        raise RuntimeError("bubblewrap is required for untrusted benchmark execution")
    with tempfile.TemporaryDirectory(prefix="faultpilot_case_") as temp:
        work = Path(temp)
        (work / "case.json").write_text(json.dumps({"code": code, "test_code": test_code}))
        (work / "runner.py").write_bytes(RUNNER.read_bytes())
        command = ["bwrap", "--unshare-all", "--die-with-parent", "--clearenv"]
        for host_path in SYSTEM_BINDS:
            if Path(host_path).exists():
                command += ["--ro-bind", host_path, host_path]
        command += [
            "--tmpfs", "/tmp", "--proc", "/proc", "--dev", "/dev",
            "--bind", temp, "/work", "--chdir", "/work",
            "--setenv", "HOME", "/tmp", "--setenv", "PATH", "/usr/bin:/bin",
            "--setenv", "PYTHONNOUSERSITE", "1", "--setenv", "OMP_NUM_THREADS", "1",
            "--setenv", "OPENBLAS_NUM_THREADS", "1", "--setenv", "MPLBACKEND", "Agg",
            "/usr/bin/python3", "-I", "/work/runner.py",
        ]
        started = time.monotonic()
        try:
            process = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "tests_run": 0, "failures": 0, "errors": 0,
                    "details": {}, "duration_s": round(time.monotonic() - started, 3)}
        duration = round(time.monotonic() - started, 3)
        if process.returncode:
            return {"status": "sandbox_error", "tests_run": 0, "failures": 0, "errors": 1,
                    "details": {"ALL": process.stderr[-2000:]}, "duration_s": duration}
        try:
            result = json.loads(process.stdout.splitlines()[-1])
        except (IndexError, json.JSONDecodeError):
            result = {"status": "sandbox_error", "tests_run": 0, "failures": 0, "errors": 1,
                      "details": {"ALL": "Harness produced no JSON result"}}
        result["duration_s"] = duration
        return result
