import unittest

from classifier import classify_complaint


class ClassifierTests(unittest.TestCase):
    def test_pothole_with_school_children_is_urgent(self):
        row = {
            "complaint_id": "PM-202402",
            "description": "Deep pothole near bus stop. School children at risk during morning hours.",
        }
        result = classify_complaint(row)
        self.assertEqual(result["category"], "Pothole")
        self.assertEqual(result["priority"], "Urgent")
        self.assertIn("school", result["reason"].lower())

    def test_streetlight_with_hazard_is_urgent(self):
        row = {
            "complaint_id": "PM-202411",
            "description": "Streetlight flickering and sparking. Electrical hazard reported.",
        }
        result = classify_complaint(row)
        self.assertEqual(result["category"], "Streetlight")
        self.assertEqual(result["priority"], "Urgent")

    def test_unknown_issue_falls_back_to_other(self):
        row = {
            "complaint_id": "PM-999999",
            "description": "Dead animal not removed for 36 hours. Health concern.",
        }
        result = classify_complaint(row)
        self.assertEqual(result["category"], "Other")
        self.assertEqual(result["priority"], "Standard")


if __name__ == "__main__":
    unittest.main()
