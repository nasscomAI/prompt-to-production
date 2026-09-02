"""
Unit tests for UC-0C app.py (Ward Budget Growth Analytics)
"""
import csv
import io
import os
import subprocess
import sys
import tempfile
import unittest
from app import load_dataset, compute_growth, normalize_dash

class TestWardBudgetApp(unittest.TestCase):

    def setUp(self):
        self.csv_path = "data/budget/ward_budget.csv"

    def test_load_dataset_null_detection(self):
        dataset, null_rows = load_dataset(self.csv_path)
        self.assertEqual(len(dataset), 300)
        self.assertEqual(len(null_rows), 5)
        null_periods = [r["period"] for r in null_rows]
        self.assertIn("2024-03", null_periods)
        self.assertIn("2024-05", null_periods)
        self.assertIn("2024-07", null_periods)
        self.assertIn("2024-08", null_periods)
        self.assertIn("2024-11", null_periods)

    def test_compute_growth_mom_reference_values(self):
        dataset, _ = load_dataset(self.csv_path)
        results = compute_growth(dataset, "Ward 1 – Kasba", "Roads & Pothole Repair", "MoM")
        self.assertEqual(len(results), 12)

        # 2024-07 should be +33.1%
        row_07 = next(r for r in results if r["period"] == "2024-07")
        self.assertEqual(row_07["actual_spend"], "19.7")
        self.assertEqual(row_07["growth"], "+33.1%")
        self.assertIn("(19.7 - 14.8) / 14.8", row_07["formula_used"])

        # 2024-10 should be -34.8%
        row_10 = next(r for r in results if r["period"] == "2024-10")
        self.assertEqual(row_10["actual_spend"], "13.1")
        self.assertEqual(row_10["growth"], "-34.8%")
        self.assertIn("(13.1 - 20.1) / 20.1", row_10["formula_used"])

    def test_null_row_handling(self):
        dataset, _ = load_dataset(self.csv_path)
        results = compute_growth(dataset, "Ward 2 – Shivajinagar", "Drainage & Flooding", "MoM")
        self.assertEqual(len(results), 12)

        row_03 = next(r for r in results if r["period"] == "2024-03")
        self.assertEqual(row_03["actual_spend"], "NULL")
        self.assertEqual(row_03["growth"], "NULL_FLAGGED")
        self.assertEqual(row_03["flag"], "NULL_ACTUAL_SPEND")
        self.assertIn("Data not submitted by ward office", row_03["formula_used"])

        row_04 = next(r for r in results if r["period"] == "2024-04")
        self.assertEqual(row_04["actual_spend"], "10.0")
        self.assertEqual(row_04["growth"], "NULL_FLAGGED")
        self.assertEqual(row_04["flag"], "NULL_PRIOR_PERIOD")
        self.assertIn("Data not submitted by ward office", row_04["formula_used"])

    def test_yoy_insufficient_data(self):
        dataset, _ = load_dataset(self.csv_path)
        results = compute_growth(dataset, "Ward 1 – Kasba", "Roads & Pothole Repair", "YoY")
        for r in results:
            self.assertEqual(r["growth"], "INSUFFICIENT_DATA")
            self.assertEqual(r["flag"], "NO_PRIOR_YEAR_DATA")

    def test_cli_missing_growth_type_refusal(self):
        cmd = [
            sys.executable, "uc-0c/app.py",
            "--input", self.csv_path,
            "--ward", "Ward 1 – Kasba",
            "--category", "Roads & Pothole Repair",
            "--output", "uc-0c/temp_should_not_exist.csv"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("--growth-type must be explicitly specified", res.stderr)
        self.assertFalse(os.path.exists("uc-0c/temp_should_not_exist.csv"))

    def test_cli_invalid_ward_refusal(self):
        cmd = [
            sys.executable, "uc-0c/app.py",
            "--input", self.csv_path,
            "--ward", "Nonexistent Ward",
            "--category", "Roads & Pothole Repair",
            "--growth-type", "MoM",
            "--output", "uc-0c/temp_should_not_exist.csv"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("Refusal — No rows found matching Ward", res.stderr)
        self.assertFalse(os.path.exists("uc-0c/temp_should_not_exist.csv"))

if __name__ == "__main__":
    unittest.main()
