import unittest
from dataclasses import replace

from faultpilot.benchmark import BenchmarkCase, split_for_task
from faultpilot.diagnostics import local_evidence, phase1_labels


def sample_case():
    return BenchmarkCase(
        case_id="demo", task_id="task", bug_code="def task_func(x):\n    return x.reshape(2, 3)",
        golden_code="", test_code="", runtime_feedback="RuntimeError: size mismatch in reshape",
        labels=("Type Mismatch",), raw_category="Type Mismatch", split="development",
    )


class DiagnosticTests(unittest.TestCase):
    def test_phase1_mapping(self):
        self.assertEqual(phase1_labels(sample_case()), ("Type Mismatch",))

    def test_evidence_is_from_case_code(self):
        evidence = local_evidence(sample_case())
        self.assertEqual(evidence[0]["line"], 2)
        self.assertIn("reshape", evidence[0]["text"])

    def test_split_is_stable(self):
        self.assertEqual(split_for_task("BigCodeBench/56"), split_for_task("BigCodeBench/56"))
