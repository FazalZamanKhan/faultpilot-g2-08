"""Trusted harness run only inside the bubblewrap sandbox."""

import json
import sys
import types
import unittest
from pathlib import Path


def main() -> None:
    item = json.loads(Path("/work/case.json").read_text())
    module = types.ModuleType("__test__")
    module.__file__ = "/work/__test__.py"
    sys.modules["__test__"] = module
    try:
        source = item["code"] + "\n" + item["test_code"]
        exec(compile(source, module.__file__, "exec"), module.__dict__)
        test_class = getattr(module, "TestCases")
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        result = unittest.TestResult()
        suite.run(result)
        failures = result.failures + result.errors
        output = {
            "status": "pass" if result.testsRun and not failures else "fail",
            "tests_run": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "details": {test._testMethodName: trace[-2000:] for test, trace in failures},
        }
    except BaseException as error:
        output = {
            "status": "setup_error",
            "tests_run": 0,
            "failures": 0,
            "errors": 1,
            "details": {"ALL": f"{type(error).__name__}: {error}"[:2000]},
        }
    print(json.dumps(output))


if __name__ == "__main__":
    main()
