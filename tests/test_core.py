import json
import unittest
from pathlib import Path
from faultpilot.core import diagnose, evaluate
from faultpilot.evaluation import evaluate_directory

class FaultPilotTests(unittest.TestCase):
    def test_classification(self):
        self.assertEqual(diagnose({"case_id":"x", "traceback":"RuntimeError: shapes cannot be multiplied"})["category"], "shape_mismatch")
    def test_end_to_end(self):
        case=json.loads(Path("cases/shape_mismatch.json").read_text())
        result=evaluate(case)
        self.assertTrue(result["category_correct"])
        self.assertTrue(result["reproduction_failed"])
        self.assertEqual(result["status"], "diagnosis_only_no_repair_attempted")
    def test_smoke_evaluation(self):
        report = evaluate_directory("cases")
        self.assertEqual(report["cases"], 4)
        self.assertEqual(report["category_accuracy"], 1.0)
        self.assertTrue(all(row["reproduction_failed"] for row in report["results"]))
