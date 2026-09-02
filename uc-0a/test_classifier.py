"""
Unit tests for classifier.py
"""
import csv
import os
import subprocess
import tempfile
import unittest
from classifier import classify_complaint, batch_classify, ALLOWED_CATEGORIES

class TestComplaintClassifier(unittest.TestCase):

    def test_allowed_categories(self):
        self.assertEqual(len(ALLOWED_CATEGORIES), 10)
        self.assertIn("Pothole", ALLOWED_CATEGORIES)
        self.assertIn("Flooding", ALLOWED_CATEGORIES)
        self.assertIn("Streetlight", ALLOWED_CATEGORIES)
        self.assertIn("Waste", ALLOWED_CATEGORIES)
        self.assertIn("Noise", ALLOWED_CATEGORIES)
        self.assertIn("Road Damage", ALLOWED_CATEGORIES)
        self.assertIn("Heritage Damage", ALLOWED_CATEGORIES)
        self.assertIn("Heat Hazard", ALLOWED_CATEGORIES)
        self.assertIn("Drain Blockage", ALLOWED_CATEGORIES)
        self.assertIn("Other", ALLOWED_CATEGORIES)

    def test_urgent_keywords_override(self):
        # Case 1: school & child
        row1 = {"complaint_id": "T1", "description": "Deep pothole near bus stop. School children at risk during morning hours."}
        res1 = classify_complaint(row1)
        self.assertEqual(res1["category"], "Pothole")
        self.assertEqual(res1["priority"], "Urgent")
        self.assertIn("School", res1["reason"])

        # Case 2: hospital / hospitalised
        row2 = {"complaint_id": "T2", "description": "Pothole swallowed entire motorcycle wheel. Rider hospitalised."}
        res2 = classify_complaint(row2)
        self.assertEqual(res2["category"], "Pothole")
        self.assertEqual(res2["priority"], "Urgent")

        # Case 3: fell
        row3 = {"complaint_id": "T3", "description": "Footpath tiles broken and upturned. Elderly resident fell last week."}
        res3 = classify_complaint(row3)
        self.assertEqual(res3["category"], "Road Damage")
        self.assertEqual(res3["priority"], "Urgent")

        # Case 4: ambulance
        row4 = {"complaint_id": "T4", "description": "Underpass flooded after 1hr rain. Ambulance diverted. Lives at risk."}
        res4 = classify_complaint(row4)
        self.assertEqual(res4["category"], "Flooding")
        self.assertEqual(res4["priority"], "Urgent")

        # Case 5: collapsed
        row5 = {"complaint_id": "T5", "description": "Road collapsed partially. Crater 1m deep near residential gate."}
        res5 = classify_complaint(row5)
        self.assertEqual(res5["priority"], "Urgent")

    def test_missing_or_empty_description(self):
        row_empty = {"complaint_id": "T_EMPTY", "description": ""}
        res_empty = classify_complaint(row_empty)
        self.assertEqual(res_empty["category"], "Other")
        self.assertEqual(res_empty["flag"], "NEEDS_REVIEW")

        row_none = {"complaint_id": "T_NONE"}
        res_none = classify_complaint(row_none)
        self.assertEqual(res_none["category"], "Other")
        self.assertEqual(res_none["flag"], "NEEDS_REVIEW")

    def test_ambiguous_description(self):
        row = {"complaint_id": "T_AMB", "description": "Something happened here yesterday."}
        res = classify_complaint(row)
        self.assertEqual(res["category"], "Other")
        self.assertEqual(res["flag"], "NEEDS_REVIEW")

    def test_batch_execution(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv", newline="", encoding="utf-8") as fin:
            writer = csv.DictWriter(fin, fieldnames=["complaint_id", "city", "description"])
            writer.writeheader()
            writer.writerow({"complaint_id": "B1", "city": "Pune", "description": "Large pothole 60cm wide causing tyre damage."})
            writer.writerow({"complaint_id": "B2", "city": "Pune", "description": "Wedding venue playing music past midnight."})
            in_file = fin.name

        out_file = in_file.replace(".csv", "_out.csv")
        try:
            batch_classify(in_file, out_file)
            with open(out_file, "r", encoding="utf-8") as fout:
                reader = csv.DictReader(fout)
                rows = list(reader)
                self.assertEqual(len(rows), 2)
                self.assertEqual(rows[0]["category"], "Pothole")
                self.assertEqual(rows[0]["priority"], "Standard")
                self.assertEqual(rows[1]["category"], "Noise")
                self.assertEqual(rows[1]["priority"], "Low")
        finally:
            if os.path.exists(in_file):
                os.remove(in_file)
            if os.path.exists(out_file):
                os.remove(out_file)

if __name__ == "__main__":
    unittest.main()
