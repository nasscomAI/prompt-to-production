"""
UC-0A — Complaint Classifier tests.
Run with: python -m pytest test_classifier.py  (or unittest)
"""
import csv
import os
import tempfile
import unittest

import classifier


class CategoryTests(unittest.TestCase):
    def check(self, description, expected_category):
        row = {"complaint_id": "T1", "description": description}
        res = classifier.classify_complaint(row)
        self.assertEqual(res["category"], expected_category,
                         f"'{description}' -> {res['category']}, expected {expected_category}")
        return res

    def test_pothole(self):
        self.check("Large pothole 60cm wide causing tyre damage.", "Pothole")

    def test_flooding(self):
        self.check("Underpass flooded knee-deep after heavy rain.", "Flooding")

    def test_streetlight(self):
        self.check("Three consecutive streetlights out for 10 days.", "Streetlight")

    def test_waste(self):
        self.check("Overflowing garbage bins near the market.", "Waste")

    def test_noise(self):
        self.check("Wedding venue playing music past midnight.", "Noise")

    def test_road_damage(self):
        self.check("Road surface cracked and sinking near utility work.", "Road Damage")

    def test_heritage_damage(self):
        self.check("Heritage street, lights out. Safety concern.", "Heritage Damage")

    def test_heat_hazard(self):
        self.check("Extreme heat causing concern in the bus depot.", "Heat Hazard")

    def test_drain_blockage(self):
        self.check("Drain blocked and water not flowing away.", "Drain Blockage")

    def test_drain_blockage_stormwater(self):
        self.check("Main stormwater drain 100% blocked with debris.", "Drain Blockage")

    def test_heat_hazard_temperature(self):
        self.check("River walk surface temperature unbearable at 52C.", "Heat Hazard")

    def test_noise_drilling(self):
        self.check("Construction drilling from 5am daily near residential towers.", "Noise")

    def test_noise_band(self):
        self.check("Wedding band playing near the museum at 11pm.", "Noise")

    def test_road_collapse(self):
        res = self.check("Road collapsed partially. Crater 1m deep near residential gate.",
                         "Road Damage")
        self.assertEqual(res["priority"], "Urgent")

    def test_other(self):
        res = self.check("Unknown complaint about local administration.", "Other")
        self.assertEqual(res["flag"], "NEEDS_REVIEW")

    def test_case_insensitive(self):
        self.check("A POTHOLE on the main road.", "Pothole")


class PriorityTests(unittest.TestCase):
    def check_urgent(self, description):
        row = {"complaint_id": "T", "description": description}
        res = classifier.classify_complaint(row)
        self.assertEqual(res["priority"], "Urgent", f"'{description}' should be Urgent")
        return res

    def check_standard(self, description):
        row = {"complaint_id": "T", "description": description}
        res = classifier.classify_complaint(row)
        self.assertEqual(res["priority"], "Standard", f"'{description}' should be Standard")

    def test_injury(self):
        self.check_urgent("Risk of serious injury to cyclists.")

    def test_child(self):
        self.check_urgent("School children at risk during morning hours.")

    def test_school(self):
        self.check_urgent("Deep pothole near the school.")

    def test_hospital(self):
        self.check_urgent("Road blocked near the hospital entrance.")

    def test_ambulance(self):
        self.check_urgent("Ambulance cannot pass this flooded street.")

    def test_fire(self):
        self.check_urgent("Electrical fire reported near the market.")

    def test_hazard(self):
        self.check_urgent("Electrical hazard reported.")

    def test_fell(self):
        self.check_urgent("Elderly resident fell last week.")

    def test_collapse(self):
        self.check_urgent("Wall collapse reported on main road.")

    def test_no_severity_standard(self):
        self.check_standard("Garbage bins overflowing in the market.")

    def test_severity_case_insensitive(self):
        self.check_urgent("A CHILD is near the construction site.")


class NullDescriptionTests(unittest.TestCase):
    def test_none_description(self):
        res = classifier.classify_complaint({"complaint_id": "T", "description": None})
        self.assertEqual(res["category"], "Other")
        self.assertEqual(res["priority"], "Low")
        self.assertEqual(res["flag"], "NEEDS_REVIEW")

    def test_empty_description(self):
        res = classifier.classify_complaint({"complaint_id": "T", "description": ""})
        self.assertEqual(res["category"], "Other")
        self.assertEqual(res["priority"], "Low")
        self.assertEqual(res["flag"], "NEEDS_REVIEW")


class SchemaTests(unittest.TestCase):
    def test_output_schema(self):
        row = {"complaint_id": "X", "description": "Large pothole on the road."}
        res = classifier.classify_complaint(row)
        self.assertEqual(set(res.keys()),
                         {"complaint_id", "category", "priority", "reason", "flag"})

    def test_category_in_allowed_list(self):
        samples = [
            "Large pothole", "flooded street", "streetlight out",
            "garbage bins", "loud music", "road surface cracked",
            "heritage damage", "extreme heat", "drain blocked",
            "completely unknown thing here",
        ]
        for s in samples:
            res = classifier.classify_complaint({"complaint_id": "X", "description": s})
            self.assertIn(res["category"], classifier.ALLOWED_CATEGORIES, s)

    def test_reason_cites_word(self):
        samples = [
            "Large pothole 60cm wide causing damage.",
            "flooded street near the market.",
            "streetlight flickering at night.",
            "garbage bins overflowing.",
            "music playing past midnight.",
            "road surface cracked and sinking.",
        ]
        for s in samples:
            res = classifier.classify_complaint({"complaint_id": "X", "description": s})
            # Every cited keyword in the reason must appear in the description
            import re
            cited = re.findall(r"'(.*?)'", res["reason"])
            self.assertTrue(cited, f"no keyword cited in reason for '{s}'")
            desc = s.lower()
            for kw in cited:
                self.assertIn(kw, desc,
                              f"cited '{kw}' not present in description '{s}'")

    def test_reason_cites_specific_keyword(self):
        res = classifier.classify_complaint(
            {"complaint_id": "X", "description": "Large pothole on the main road."})
        self.assertIn("pothole", res["reason"].lower())

    def test_reproducibility(self):
        row = {"complaint_id": "X", "description": "Deep pothole near school, children at risk."}
        r1 = classifier.classify_complaint(row)
        r2 = classifier.classify_complaint(row)
        self.assertEqual(r1, r2)


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, rows):
        path = os.path.join(self.tmp.name, "in.csv")
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["complaint_id", "description"])
            writer.writeheader()
            for r in rows:
                writer.writerow(r)
        return path

    def test_batch_writes_output(self):
        inp = self._write([
            {"complaint_id": "A", "description": "Large pothole near the school."},
            {"complaint_id": "B", "description": "loud music at night."},
        ])
        out = os.path.join(self.tmp.name, "out.csv")
        classifier.batch_classify(inp, out)
        self.assertTrue(os.path.exists(out))
        with open(out, "r", encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["category"], "Pothole")
        self.assertEqual(rows[0]["priority"], "Urgent")

    def test_batch_handles_empty_description(self):
        inp = self._write([{"complaint_id": "A", "description": None}])
        out = os.path.join(self.tmp.name, "out.csv")
        classifier.batch_classify(inp, out)
        with open(out, "r", encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(rows[0]["category"], "Other")
        self.assertEqual(rows[0]["priority"], "Low")
        self.assertEqual(rows[0]["flag"], "NEEDS_REVIEW")


if __name__ == "__main__":
    unittest.main()
