import csv
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(module_name, path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestUCWorkflows(unittest.TestCase):
    def test_uc0a_classification(self):
        classifier = load_module("uc0a_classifier", ROOT / "uc-0a" / "classifier.py")
        result = classifier.classify_complaint({
            "complaint_id": "T1",
            "description": "Large pothole 60cm wide causing tyre damage.",
        })
        self.assertEqual(result["category"], "Pothole")
        self.assertIn(result["priority"], {"Urgent", "Standard"})
        self.assertTrue(result["reason"].endswith("."))

    def test_uc0b_policy_summary(self):
        app = load_module("uc0b_app", ROOT / "uc-0b" / "app.py")
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = ROOT / "data" / "policy-documents" / "policy_hr_leave.txt"
            output_path = Path(temp_dir) / "summary.txt"
            app.summarize_policy(str(input_path), str(output_path))
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("2.3", content)
            self.assertIn("5.2", content)
            self.assertIn("7.2", content)

    def test_uc0c_growth_output(self):
        app = load_module("uc0c_app", ROOT / "uc-0c" / "app.py")
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = ROOT / "data" / "budget" / "ward_budget.csv"
            output_path = Path(temp_dir) / "growth.csv"
            app.compute_growth(
                input_path=str(input_path),
                ward="Ward 1 – Kasba",
                category="Roads & Pothole Repair",
                growth_type="MoM",
                output_path=str(output_path),
            )
            self.assertTrue(output_path.exists())
            with output_path.open(newline="", encoding="utf-8") as fh:
                rows = list(csv.DictReader(fh))
            self.assertTrue(rows)
            self.assertIn("growth_pct", rows[0])
            self.assertIn("status", rows[0])

    def test_ucx_answer_question(self):
        app = load_module("ucx_app", ROOT / "uc-x" / "app.py")
        answer = app.answer_question("Can I install Slack on my work laptop?")
        self.assertIn("policy_it_acceptable_use.txt", answer)
        self.assertIn("section 2.3", answer)


if __name__ == "__main__":
    unittest.main()
