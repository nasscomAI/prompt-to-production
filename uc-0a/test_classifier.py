import csv
import os
import tempfile
import unittest

from classifier import batch_classify, classify_complaint


class ComplaintClassifierTests(unittest.TestCase):
    def test_classify_complaint_marks_urgent_for_severity_keywords(self):
        row = {
            "complaint_id": "PM-1001",
            "description": "School children at risk near a deep pothole.",
        }

        result = classify_complaint(row)

        self.assertEqual(result["category"], "Pothole")
        self.assertEqual(result["priority"], "Urgent")
        self.assertIn("school", result["reason"].lower())
        self.assertIn("pothole", result["reason"].lower())

    def test_batch_classify_writes_csv_and_handles_bad_rows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input.csv")
            output_path = os.path.join(tmpdir, "output.csv")

            with open(input_path, "w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["complaint_id", "description"])
                writer.writeheader()
                writer.writerow({"complaint_id": "PM-1", "description": "Large pothole near school."})
                writer.writerow({"complaint_id": "PM-2", "description": ""})

            batch_classify(input_path, output_path)

            with open(output_path, "r", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))

            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["category"], "Pothole")
            self.assertEqual(rows[0]["priority"], "Urgent")
            self.assertEqual(rows[1]["category"], "Other")
            self.assertEqual(rows[1]["flag"], "NEEDS_REVIEW")


if __name__ == "__main__":
    unittest.main()
