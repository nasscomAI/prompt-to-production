import unittest
import os
import csv
from classifier import classify_complaint, batch_classify, ALLOWED_CATEGORIES

class TestComplaintClassifier(unittest.TestCase):
    def test_allowed_categories(self):
        """Test that every possible description is mapped to a permitted category."""
        rows = [
            {"complaint_id": "1", "description": "There is a massive pothole in the road.", "days_open": "1"},
            {"complaint_id": "2", "description": "The street is flooded and under water.", "days_open": "2"},
            {"complaint_id": "3", "description": "The streetlight is broken and dark.", "days_open": "3"},
            {"complaint_id": "4", "description": "Bins of trash and garbage are overflowing.", "days_open": "4"},
            {"complaint_id": "5", "description": "Very loud wedding music playing late.", "days_open": "5"},
            {"complaint_id": "6", "description": "Footpath paving and tiles are cracked.", "days_open": "6"},
            {"complaint_id": "7", "description": "Ancient step well and heritage site defaced.", "days_open": "7"},
            {"complaint_id": "8", "description": "Road melting under severe heatwave conditions.", "days_open": "8"},
            {"complaint_id": "9", "description": "Stormwater drain is completely blocked.", "days_open": "9"},
            {"complaint_id": "10", "description": "Some random complaint about trees.", "days_open": "2"}
        ]

        for row in rows:
            res = classify_complaint(row)
            self.assertIn(res["category"], ALLOWED_CATEGORIES)
            self.assertTrue(res["reason"])

    def test_priority_rules(self):
        """Test that priority rules (Urgent, Standard, Low) are applied deterministically."""
        # Urgent priority triggered by severity keywords
        row_urgent = {"complaint_id": "1", "description": "Child fell in a deep pothole and was injured near a school.", "days_open": "1"}
        res_urgent = classify_complaint(row_urgent)
        self.assertEqual(res_urgent["priority"], "Urgent")
        self.assertTrue(any(k in res_urgent["reason"] for k in ["child", "injury", "school"]))

        # Standard priority for standard categories
        row_standard = {"complaint_id": "2", "description": "Pothole on the street.", "days_open": "2"}
        res_standard = classify_complaint(row_standard)
        self.assertEqual(res_standard["priority"], "Standard")

        # Low priority for Noise category with few days_open
        row_low = {"complaint_id": "3", "description": "Loud music past midnight.", "days_open": "1"}
        res_low = classify_complaint(row_low)
        self.assertEqual(res_low["priority"], "Low")

    def test_flagging(self):
        """Test that hazardous or ambiguous rows are flagged as NEEDS_REVIEW."""
        # Hazard: gas leak
        row_gas = {"complaint_id": "1", "description": "Road subsided and there is a smell of gas leak.", "days_open": "1"}
        res_gas = classify_complaint(row_gas)
        self.assertEqual(res_gas["flag"], "NEEDS_REVIEW")

        # Ambiguous / Other category
        row_ambig = {"complaint_id": "2", "description": "Something strange happened.", "days_open": "1"}
        res_ambig = classify_complaint(row_ambig)
        self.assertEqual(res_ambig["flag"], "NEEDS_REVIEW")

    def test_batch_processing(self):
        """Test batch processing works and creates expected file output."""
        test_in = "test_temp_in.csv"
        test_out = "test_temp_out.csv"

        with open(test_in, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["complaint_id", "description", "days_open"])
            writer.writerow(["C1", "Pothole on F.C. road.", "5"])
            writer.writerow(["C2", "Unlit streetlight.", "15"])

        try:
            batch_classify(test_in, test_out)
            self.assertTrue(os.path.exists(test_out))

            with open(test_out, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                self.assertEqual(len(rows), 2)
                self.assertEqual(rows[0]["complaint_id"], "C1")
                self.assertEqual(rows[0]["category"], "Pothole")
                self.assertEqual(rows[1]["complaint_id"], "C2")
                self.assertEqual(rows[1]["category"], "Streetlight")
        finally:
            if os.path.exists(test_in):
                os.remove(test_in)
            if os.path.exists(test_out):
                os.remove(test_out)

if __name__ == "__main__":
    unittest.main()
