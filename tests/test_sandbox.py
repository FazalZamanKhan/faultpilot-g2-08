import unittest

from faultpilot.sandbox import run_tests


class SandboxTests(unittest.TestCase):
    def test_passing_and_failing_code(self):
        tests = "import unittest\nclass TestCases(unittest.TestCase):\n def test_value(self): self.assertEqual(task_func(), 2)"
        self.assertEqual(run_tests("def task_func(): return 2", tests)["status"], "pass")
        result = run_tests("def task_func(): return 1", tests)
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["tests_run"], 1)

    def test_no_home_or_network(self):
        tests = "import unittest\nclass TestCases(unittest.TestCase):\n def test_hidden(self): self.assertFalse(__import__('os').path.exists('/home/fazalkhan'))"
        self.assertEqual(run_tests("", tests)["status"], "pass")
