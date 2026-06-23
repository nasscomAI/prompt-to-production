"""
UC-0A — Test Suite
CRAFT Cycle: Test phase

Tests cover:
  - Normal classification (happy-path for each category)
  - Severity keyword enforcement (all 9 keywords)
  - Edge cases (empty, very short, non-string descriptions)
  - Invalid/adversarial inputs (mixed categories, negated keywords)
  - Batch function error handling
  - Schema validation guardrails

Run with: python -m pytest test_classifier.py -v
Or:       python test_classifier.py
"""

import csv
import os
import sys
import tempfile
import unittest

# Ensure classifier module is importable from this directory
sys.path.insert(0, os.path.dirname(__file__))
from classifier import (
    ALLOWED_CATEGORIES,
    ALLOWED_PRIORITIES,
    SEVERITY_KEYWORDS,
    batch_classify,
    classify_complaint,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def make_row(description, complaint_id="TEST-001"):
    return {"complaint_id": complaint_id, "description": description}


# ---------------------------------------------------------------------------
# 1. Normal / happy-path tests — one per category
# ---------------------------------------------------------------------------

class TestCategoryClassification(unittest.TestCase):

    def _check(self, description, expected_category):
        result = classify_complaint(make_row(description))
        self.assertEqual(
            result["category"], expected_category,
            f"Expected {expected_category!r}, got {result['category']!r} for: {description!r}"
        )
        self.assertIn(result["category"], ALLOWED_CATEGORIES)
        self.assertIn(result["priority"], ALLOWED_PRIORITIES)
        self.assertIsInstance(result["reason"], str)
        self.assertTrue(len(result["reason"]) > 0)
        self.assertIn(result["flag"], {"NEEDS_REVIEW", ""})

    def test_pothole(self):
        self._check("Large pothole on main road causing accidents.", "Pothole")

    def test_flooding(self):
        self._check("Street flooded after heavy rain, water knee-deep.", "Flooding")

    def test_drain_blockage(self):
        self._check("Main drain blocked by debris. Water not draining.", "Drain Blockage")

    def test_waste(self):
        self._check("Garbage not cleared for 5 days. Area smells.", "Waste")

    def test_noise(self):
        self._check("Loud drilling near school from 4am every day.", "Noise")

    def test_road_damage(self):
        self._check("Road collapsed near bus stop. Crater visible.", "Road Damage")

    def test_heritage_damage(self):
        self._check("Heritage wall near Charminar showing cracks.", "Heritage Damage")

    def test_streetlight(self):
        self._check("Streetlight not working for two weeks. Road dark at night.", "Streetlight")

    def test_heat_hazard(self):
        self._check("Extreme heat wave. No shade on main road. Heat stroke risk.", "Heat Hazard")

    def test_other(self):
        self._check("Something unusual happened at the corner shop.", "Other")


# ---------------------------------------------------------------------------
# 2. Severity keyword enforcement — all 9 keywords must trigger Urgent
# ---------------------------------------------------------------------------

class TestSeverityKeywords(unittest.TestCase):

    def _check_urgent(self, keyword):
        desc = f"The situation involves {keyword} on the main road."
        result = classify_complaint(make_row(desc))
        self.assertEqual(
            result["priority"], "Urgent",
            f"Keyword {keyword!r} should trigger Urgent but got {result['priority']!r}"
        )

    def test_injury(self):     self._check_urgent("injury")
    def test_child(self):      self._check_urgent("child")
    def test_school(self):     self._check_urgent("school")
    def test_hospital(self):   self._check_urgent("hospital")
    def test_ambulance(self):  self._check_urgent("ambulance")
    def test_fire(self):       self._check_urgent("fire")
    def test_hazard(self):     self._check_urgent("hazard")
    def test_fell(self):       self._check_urgent("fell")
    def test_collapse(self):   self._check_urgent("collapse")

    def test_keyword_case_insensitive(self):
        result = classify_complaint(make_row("AMBULANCE was blocked by flooding."))
        self.assertEqual(result["priority"], "Urgent")

    def test_keyword_in_longer_word(self):
        # 'hospital' appears inside 'hospitalised' — substring match should still trigger Urgent
        result = classify_complaint(make_row("Rider was hospitalised after pothole accident."))
        self.assertEqual(result["priority"], "Urgent")


# ---------------------------------------------------------------------------
# 3. Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases(unittest.TestCase):

    def test_empty_description(self):
        result = classify_complaint(make_row(""))
        self.assertEqual(result["category"], "Other")
        self.assertEqual(result["priority"], "Low")
        self.assertEqual(result["flag"], "NEEDS_REVIEW")
        self.assertIn("empty", result["reason"].lower())

    def test_whitespace_only_description(self):
        result = classify_complaint(make_row("   "))
        self.assertEqual(result["flag"], "NEEDS_REVIEW")

    def test_single_word_description(self):
        result = classify_complaint(make_row("Pothole"))
        # Single word — treated as too short
        self.assertEqual(result["flag"], "NEEDS_REVIEW")

    def test_none_description(self):
        result = classify_complaint({"complaint_id": "T1", "description": None})
        self.assertEqual(result["category"], "Other")
        self.assertEqual(result["flag"], "NEEDS_REVIEW")

    def test_numeric_description(self):
        result = classify_complaint({"complaint_id": "T2", "description": 12345})
        # Should coerce to string "12345" — single token, gets NEEDS_REVIEW
        self.assertIn(result["category"], ALLOWED_CATEGORIES)

    def test_missing_complaint_id(self):
        result = classify_complaint({"description": "Pothole on road."})
        self.assertEqual(result["complaint_id"], "UNKNOWN")

    def test_output_has_all_required_fields(self):
        result = classify_complaint(make_row("Pothole near school."))
        for field in ("complaint_id", "category", "priority", "reason", "flag"):
            self.assertIn(field, result, f"Missing field: {field}")

    def test_no_null_values_in_output(self):
        result = classify_complaint(make_row("Some random description text."))
        for key, val in result.items():
            self.assertNotIn(str(val).lower(), {"none", "nan", "null"},
                             f"Field {key!r} has null-like value: {val!r}")


# ---------------------------------------------------------------------------
# 4. Adversarial inputs
# ---------------------------------------------------------------------------

class TestAdversarialInputs(unittest.TestCase):

    def test_two_category_signals_sets_needs_review(self):
        # Heritage + Waste both present
        result = classify_complaint(make_row(
            "Heritage zone garbage overflow near old city monuments."
        ))
        self.assertEqual(result["flag"], "NEEDS_REVIEW")

    def test_severity_keyword_in_negated_context(self):
        # "no injury" — rule still triggers Urgent (substring match)
        # This is a known limitation; NEEDS_REVIEW flag surfaces it for human review
        result = classify_complaint(make_row("No injury reported but road is broken."))
        self.assertEqual(result["priority"], "Urgent")
        # category should not be empty
        self.assertIn(result["category"], ALLOWED_CATEGORIES)

    def test_very_long_description(self):
        long_desc = "Pothole on road. " * 500
        result = classify_complaint(make_row(long_desc))
        self.assertEqual(result["category"], "Pothole")

    def test_description_with_special_characters(self):
        result = classify_complaint(make_row("Drain blocked!! Water — everywhere. #flood @ward55"))
        self.assertIn(result["category"], ALLOWED_CATEGORIES)

    def test_description_in_mixed_case(self):
        result = classify_complaint(make_row("POTHOLE NEAR SCHOOL BUS STOP"))
        self.assertEqual(result["category"], "Pothole")
        self.assertEqual(result["priority"], "Urgent")

    def test_category_not_invented(self):
        # Description should never produce a category outside the allowed set
        odd_descriptions = [
            "UFO sighting near the reservoir",
            "Politician seen dumping waste",
            "Internet not working in the area",
            "Stray dog biting residents",
        ]
        for desc in odd_descriptions:
            result = classify_complaint(make_row(desc))
            self.assertIn(result["category"], ALLOWED_CATEGORIES,
                          f"Invalid category {result['category']!r} for: {desc!r}")


# ---------------------------------------------------------------------------
# 5. Batch function tests
# ---------------------------------------------------------------------------

class TestBatchClassify(unittest.TestCase):

    def _write_temp_csv(self, rows, fieldnames=None):
        """Write rows to a temp CSV and return path."""
        if fieldnames is None:
            fieldnames = ["complaint_id", "description"]
        f = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8", newline=""
        )
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        f.close()
        return f.name

    def test_full_batch_15_rows(self):
        """Integration test: all 15 Hyderabad rows produce 15 output rows."""
        input_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "city-test-files", "test_hyderabad.csv"
        )
        if not os.path.exists(input_path):
            self.skipTest("Hyderabad test file not available")
        out = tempfile.mktemp(suffix=".csv")
        total, errors = batch_classify(input_path, out)
        self.assertEqual(total, 15)
        self.assertEqual(errors, 0)
        # Verify output
        with open(out, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 15)
        for row in rows:
            self.assertIn(row["category"], ALLOWED_CATEGORIES)
            self.assertIn(row["priority"], ALLOWED_PRIORITIES)
        os.unlink(out)

    def test_batch_no_null_cells(self):
        """No output cell may contain None/nan/null strings.
        Note: flag='' is valid (means no flag needed) — only category/priority/reason must be non-empty.
        """
        input_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "city-test-files", "test_hyderabad.csv"
        )
        if not os.path.exists(input_path):
            self.skipTest("Hyderabad test file not available")
        out = tempfile.mktemp(suffix=".csv")
        batch_classify(input_path, out)
        with open(out, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cid = row.get("complaint_id")
                # These fields must never be empty or null-like
                for key in ("complaint_id", "category", "priority", "reason"):
                    val = row.get(key, "")
                    self.assertNotIn(val.lower(), {"none", "nan", "null"},
                                     f"Cell {key!r} has null-like value in row {cid}")
                    self.assertTrue(len(val.strip()) > 0,
                                    f"Cell {key!r} is empty in row {cid}")
                # flag may legitimately be empty string (means no flag)
                flag_val = row.get("flag", "")
                self.assertIn(flag_val, {"NEEDS_REVIEW", ""},
                              f"Cell 'flag' has invalid value {flag_val!r} in row {cid}")
        os.unlink(out)

    def test_batch_missing_input_file(self):
        with self.assertRaises(FileNotFoundError):
            batch_classify("/nonexistent/path/file.csv", "/tmp/out.csv")

    def test_batch_missing_description_column(self):
        path = self._write_temp_csv(
            [{"complaint_id": "X1", "notes": "something"}],
            fieldnames=["complaint_id", "notes"]
        )
        try:
            with self.assertRaises(ValueError):
                batch_classify(path, tempfile.mktemp(suffix=".csv"))
        finally:
            os.unlink(path)

    def test_batch_with_blank_row(self):
        path = self._write_temp_csv([
            {"complaint_id": "A1", "description": "Pothole near the bus stop"},
            {"complaint_id": "",   "description": ""},
            {"complaint_id": "A2", "description": "Flooding after rain"},
        ])
        out = tempfile.mktemp(suffix=".csv")
        try:
            total, _ = batch_classify(path, out)
            # Blank row should be skipped; 2 real rows
            self.assertEqual(total, 2)
        finally:
            os.unlink(path)
            if os.path.exists(out):
                os.unlink(out)

    def test_batch_deterministic(self):
        """Same input must produce identical output on two runs."""
        input_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "city-test-files", "test_hyderabad.csv"
        )
        if not os.path.exists(input_path):
            self.skipTest("Hyderabad test file not available")
        out1 = tempfile.mktemp(suffix=".csv")
        out2 = tempfile.mktemp(suffix=".csv")
        batch_classify(input_path, out1)
        batch_classify(input_path, out2)
        with open(out1) as f1, open(out2) as f2:
            self.assertEqual(f1.read(), f2.read())
        os.unlink(out1)
        os.unlink(out2)


# ---------------------------------------------------------------------------
# 6. Hyderabad-specific spot checks (audit the actual output)
# ---------------------------------------------------------------------------

class TestHyderabadSpotChecks(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        input_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "city-test-files", "test_hyderabad.csv"
        )
        if not os.path.exists(input_path):
            cls.rows = {}
            return
        out = tempfile.mktemp(suffix=".csv")
        batch_classify(input_path, out)
        cls.rows = {}
        with open(out, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                cls.rows[row["complaint_id"]] = row
        os.unlink(out)

    def _get(self, cid):
        if cid not in self.rows:
            self.skipTest(f"Row {cid} not in output")
        return self.rows[cid]

    def test_GH202401_ambulance_is_urgent(self):
        row = self._get("GH-202401")
        self.assertEqual(row["priority"], "Urgent",
                         "GH-202401 contains 'ambulance' — must be Urgent")

    def test_GH202411_hospitalised_is_urgent(self):
        row = self._get("GH-202411")
        self.assertEqual(row["priority"], "Urgent",
                         "GH-202411 contains 'hospitalised' ('hospital' substring) — must be Urgent")

    def test_GH202412_school_bus_is_urgent(self):
        row = self._get("GH-202412")
        self.assertEqual(row["priority"], "Urgent",
                         "GH-202412 contains 'school' — must be Urgent")

    def test_GH202422_road_collapse_is_urgent(self):
        row = self._get("GH-202422")
        self.assertEqual(row["priority"], "Urgent",
                         "GH-202422 contains 'collapse' — must be Urgent")

    def test_GH202417_heritage_category(self):
        row = self._get("GH-202417")
        self.assertEqual(row["category"], "Heritage Damage",
                         "GH-202417 is in heritage zone — should be Heritage Damage")

    def test_GH202438_no_hallucinated_category(self):
        row = self._get("GH-202438")
        self.assertIn(row["category"], ALLOWED_CATEGORIES,
                      "GH-202438 category must be in allowed taxonomy")

    def test_all_reasons_non_empty(self):
        for cid, row in self.rows.items():
            self.assertTrue(
                len(row["reason"].strip()) > 5,
                f"Row {cid} has insufficient reason: {row['reason']!r}"
            )


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)
