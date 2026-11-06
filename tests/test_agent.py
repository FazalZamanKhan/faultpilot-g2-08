import unittest

from faultpilot.agent import AgentSettings, apply_edit, run_agent
from faultpilot.benchmark import BenchmarkCase
from faultpilot.diagnostics import Diagnosis


class FakeClient:
    def propose(self, prompt):
        return {"line": 2, "new": "return x + 2"}, {"prompt_tokens": 10, "output_tokens": 8}


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.case = BenchmarkCase(
            "fixture", "task", "def add_two(x):\n    return x + 1\n", "return x + 2",
            "import unittest\nclass TestCases(unittest.TestCase):\n"
            "    def test_add(self):\n        self.assertEqual(add_two(2), 4)\n",
            "AssertionError: 3 != 4", ("Function Misuse",), "Function Misuse", "test")
        self.diagnosis = Diagnosis(("Function Misuse",), 0.8, {},
                                   [{"line": 2, "text": "return x + 1"}], [])

    def test_exact_edit_contract(self):
        self.assertEqual(apply_edit("a a", {"old": "a", "new": "b"})[1], "old_text_not_unique")
        self.assertEqual(apply_edit("a", {"old": "a", "new": "b"}), ("b", "applied"))
        self.assertEqual(apply_edit("a\n", {"line": 1, "new": "b"}), ("b\n", "applied"))
        self.assertEqual(apply_edit("a\n", {"line": 0, "new": "b"})[1], "invalid_line_number")

    def test_repair_is_verified(self):
        result = run_agent(self.case, AgentSettings(), FakeClient(), self.diagnosis)
        self.assertEqual(result["status"], "verified_by_supplied_tests")
        self.assertEqual(result["trace"][-1]["result"]["status"], "pass")

    def test_evidence_gate(self):
        result = run_agent(self.case, AgentSettings(), FakeClient(), None)
        self.assertEqual(result["status"], "abstained_insufficient_evidence")


if __name__ == "__main__":
    unittest.main()
