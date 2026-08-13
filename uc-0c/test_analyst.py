import unittest
import os
import csv
import sys

# Prevent python path shadowing collisions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if 'app' in sys.modules:
    del sys.modules['app']

from app import load_and_validate_dataset, compute_growth

class TestNumericalAnalyst(unittest.TestCase):
    def test_schema_validation(self):
        """Test that schema validation detects missing or invalid columns."""
        bad_csv_path = "test_bad_schema.csv"
        with open(bad_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["period", "ward", "budgeted_amount"]) # Missing category and actual_spend
            writer.writerow(["2024-01", "Ward 1", "100.0"])

        try:
            with self.assertRaises(ValueError):
                load_and_validate_dataset(bad_csv_path)
        finally:
            if os.path.exists(bad_csv_path):
                os.remove(bad_csv_path)

    def test_compute_growth_success(self):
        """Test standard MoM growth calculations with realistic values."""
        rows = [
            {"period": "2024-01", "ward": "W1", "category": "Cat1", "budgeted_amount": "10", "actual_spend": "10.0", "notes": ""},
            {"period": "2024-02", "ward": "W1", "category": "Cat1", "budgeted_amount": "10", "actual_spend": "15.0", "notes": ""},
            {"period": "2024-03", "ward": "W1", "category": "Cat1", "budgeted_amount": "10", "actual_spend": "12.0", "notes": ""}
        ]
        res = compute_growth(rows, "W1", "Cat1", "MoM")

        # Row 1 (first period)
        self.assertEqual(res[0]["mom_growth"], "N/A - first period")
        self.assertEqual(res[0]["formula"], "N/A")

        # Row 2 (increase: ((15 - 10)/10)*100 = +50.0%)
        self.assertEqual(res[1]["mom_growth"], "+50.0%")
        self.assertEqual(res[1]["formula"], "((15.0 - 10.0) / 10.0) * 100")

        # Row 3 (decrease: ((12 - 15)/15)*100 = -20.0%)
        self.assertEqual(res[2]["mom_growth"], "-20.0%")
        self.assertEqual(res[2]["formula"], "((12.0 - 15.0) / 15.0) * 100")

    def test_null_value_handling(self):
        """Test that NULL actual_spend rows are detected, preserved, and explain reason."""
        rows = [
            {"period": "2024-01", "ward": "W1", "category": "Cat1", "budgeted_amount": "10", "actual_spend": "10.0", "notes": ""},
            {"period": "2024-02", "ward": "W1", "category": "Cat1", "budgeted_amount": "10", "actual_spend": "NULL", "notes": "No invoices submitted"},
            {"period": "2024-03", "ward": "W1", "category": "Cat1", "budgeted_amount": "10", "actual_spend": "12.0", "notes": ""}
        ]
        res = compute_growth(rows, "W1", "Cat1", "MoM")

        # Row 2 should be flagged as current value NULL
        self.assertEqual(res[1]["actual_spend"], "NULL")
        self.assertIn("current value is NULL (No invoices submitted)", res[1]["mom_growth"])

        # Row 3 should be flagged because previous value was NULL
        self.assertIn("previous value is NULL (No invoices submitted)", res[2]["mom_growth"])

    def test_unsupported_growth_type(self):
        """Test that the system raises ValueError for unsupported growth types."""
        rows = [{"period": "2024-01", "ward": "W1", "category": "Cat1", "budgeted_amount": "10", "actual_spend": "10", "notes": ""}]
        with self.assertRaises(ValueError):
            compute_growth(rows, "W1", "Cat1", "YoY")

if __name__ == "__main__":
    unittest.main()
