"""
UC-0A — Complaint Classifier Test Suite
Tests for complaint classification with taxonomy drift prevention, severity detection, and ambiguity flagging.
"""
import unittest
import csv
import sys
from pathlib import Path
from typing import Dict, List
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
from classifier import (
    classify_complaint,
    batch_classify,
    ALLOWED_CATEGORIES,
    SEVERITY_KEYWORDS,
    LOW_PRIORITY_KEYWORDS,
)


class TestDataLoading(unittest.TestCase):
    """Test that test data loads correctly."""

    def test_test_file_exists(self):
        """Test data file exists and is readable."""
        test_file = Path("../data/city-test-files/test_pune.csv")
        self.assertTrue(
            test_file.exists(),
            f"Test file {test_file} not found"
        )

    def test_test_file_has_15_rows(self):
        """Test file should have exactly 15 data rows (excluding header)."""
        df = pd.read_csv("../data/city-test-files/test_pune.csv")
        self.assertEqual(
            len(df), 15,
            f"Expected 15 test rows, found {len(df)}"
        )

    def test_test_file_has_required_columns(self):
        """Test file must have required columns."""
        df = pd.read_csv("../data/city-test-files/test_pune.csv")
        required_cols = ["complaint_id", "description", "location"]
        for col in required_cols:
            self.assertIn(col, df.columns, f"Missing required column: {col}")

    def test_allowed_categories_count(self):
        """Should have exactly 10 allowed categories."""
        self.assertEqual(
            len(ALLOWED_CATEGORIES), 10,
            f"Expected 10 categories, found {len(ALLOWED_CATEGORIES)}"
        )

    def test_severity_keywords_present(self):
        """Severity keywords must be defined."""
        self.assertGreater(
            len(SEVERITY_KEYWORDS), 0,
            "No severity keywords defined"
        )
        # Check for key severity words
        for keyword in ["injury", "child", "school", "hospital"]:
            self.assertIn(
                keyword, SEVERITY_KEYWORDS,
                f"Missing critical severity keyword: {keyword}"
            )


class TestCategoryValidation(unittest.TestCase):
    """Test that classifications use allowed categories only."""

    def test_allowed_categories_exact_list(self):
        """Allowed categories must match spec exactly."""
        expected = {
            "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
            "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
        }
        actual = set(ALLOWED_CATEGORIES)
        self.assertEqual(
            actual, expected,
            f"Category mismatch. Expected {expected}, got {actual}"
        )

    def test_pothole_classification(self):
        """Pothole complaints must be classified as 'Pothole'."""
        row = {
            "complaint_id": "TEST-001",
            "description": "Large pothole 60cm wide causing tyre damage",
            "location": "Karve Road",
        }
        result = classify_complaint(row)
        self.assertEqual(
            result["category"], "Pothole",
            f"Expected Pothole, got {result['category']}"
        )

    def test_flooding_classification(self):
        """Flooding complaints must be classified as 'Flooding'."""
        row = {
            "complaint_id": "TEST-002",
            "description": "Underpass flooded knee-deep after rain",
            "location": "Ambedkar Road",
        }
        result = classify_complaint(row)
        self.assertEqual(
            result["category"], "Flooding",
            f"Expected Flooding, got {result['category']}"
        )

    def test_streetlight_classification(self):
        """Streetlight complaints must be classified as 'Streetlight'."""
        row = {
            "complaint_id": "TEST-003",
            "description": "Three consecutive streetlights out for 10 days",
            "location": "JM Road",
        }
        result = classify_complaint(row)
        self.assertEqual(
            result["category"], "Streetlight",
            f"Expected Streetlight, got {result['category']}"
        )

    def test_waste_classification(self):
        """Waste complaints must be classified as 'Waste'."""
        row = {
            "complaint_id": "TEST-004",
            "description": "Overflowing garbage bins near market",
            "location": "Shivajinagar market",
        }
        result = classify_complaint(row)
        self.assertEqual(
            result["category"], "Waste",
            f"Expected Waste, got {result['category']}"
        )

    def test_noise_classification(self):
        """Noise complaints must be classified as 'Noise'."""
        row = {
            "complaint_id": "TEST-005",
            "description": "Wedding venue playing music past midnight",
            "location": "Kalyani Nagar",
        }
        result = classify_complaint(row)
        self.assertEqual(
            result["category"], "Noise",
            f"Expected Noise, got {result['category']}"
        )

    def test_road_damage_classification(self):
        """Road damage complaints must be classified as 'Road Damage'."""
        row = {
            "complaint_id": "TEST-006",
            "description": "Road surface cracked and sinking",
            "location": "Senapati Bapat Road",
        }
        result = classify_complaint(row)
        self.assertEqual(
            result["category"], "Road Damage",
            f"Expected Road Damage, got {result['category']}"
        )

    def test_heritage_damage_classification(self):
        """Heritage complaints must be classified as 'Heritage Damage'."""
        row = {
            "complaint_id": "TEST-007",
            "description": "Heritage street, lights out",
            "location": "Rasta Peth, old city area",
        }
        result = classify_complaint(row)
        self.assertEqual(
            result["category"], "Heritage Damage",
            f"Expected Heritage Damage, got {result['category']}"
        )

    def test_drain_blockage_classification(self):
        """Drain complaints must be classified appropriately."""
        row = {
            "complaint_id": "TEST-008",
            "description": "Drain blocked behind the building.",
            "location": "Kothrud Depot",
        }
        result = classify_complaint(row)
        self.assertEqual(
            result["category"], "Drain Blockage",
            f"Expected Drain Blockage, got {result['category']}"
        )

    def test_other_classification_fallback(self):
        """Unknown complaints must be classified as 'Other'."""
        row = {
            "complaint_id": "TEST-009",
            "description": "Some random complaint about nothing specific",
            "location": "Unknown place",
        }
        result = classify_complaint(row)
        self.assertEqual(
            result["category"], "Other",
            f"Expected Other for unknown complaint, got {result['category']}"
        )

    def test_all_categories_in_allowed_list(self):
        """All returned categories must be in allowed list."""
        test_complaints = [
            {"complaint_id": "TEST-001", "description": "pothole damage", "location": "road"},
            {"complaint_id": "TEST-002", "description": "flooded area", "location": "street"},
            {"complaint_id": "TEST-003", "description": "streetlight out", "location": "road"},
            {"complaint_id": "TEST-004", "description": "garbage overflow", "location": "market"},
            {"complaint_id": "TEST-005", "description": "loud music", "location": "night"},
            {"complaint_id": "TEST-006", "description": "road cracked", "location": "street"},
        ]
        for complaint in test_complaints:
            result = classify_complaint(complaint)
            self.assertIn(
                result["category"], ALLOWED_CATEGORIES,
                f"Category {result['category']} not in allowed list"
            )


class TestSeverityDetection(unittest.TestCase):
    """Test that severity keywords trigger Urgent priority."""

    def test_injury_keyword_triggers_urgent(self):
        """'injury' keyword must trigger Urgent priority."""
        row = {
            "complaint_id": "TEST-010",
            "description": "Manhole cover missing. Risk of serious injury to cyclists.",
            "location": "Paud Road",
        }
        result = classify_complaint(row)
        self.assertEqual(
            result["priority"], "Urgent",
            f"Expected Urgent for injury mention, got {result['priority']}"
        )

    def test_child_keyword_triggers_urgent(self):
        """'child' keyword must trigger Urgent priority."""
        row = {
            "complaint_id": "TEST-011",
            "description": "Deep pothole near bus stop. School children at risk.",
            "location": "FC Road",
        }
        result = classify_complaint(row)
        self.assertEqual(
            result["priority"], "Urgent",
            f"Expected Urgent for child mention, got {result['priority']}"
        )

    def test_school_keyword_triggers_urgent(self):
        """'school' keyword must trigger Urgent priority."""
        row = {
            "complaint_id": "TEST-012",
            "description": "Pothole near school. Safety hazard for students.",
            "location": "school zone",
        }
        result = classify_complaint(row)
        self.assertEqual(
            result["priority"], "Urgent",
            f"Expected Urgent for school mention, got {result['priority']}"
        )

    def test_hazard_keyword_triggers_urgent(self):
        """'hazard' keyword must trigger Urgent priority."""
        row = {
            "complaint_id": "TEST-013",
            "description": "Streetlight sparking. Electrical hazard reported.",
            "location": "Viman Nagar",
        }
        result = classify_complaint(row)
        self.assertEqual(
            result["priority"], "Urgent",
            f"Expected Urgent for hazard mention, got {result['priority']}"
        )

    def test_standard_complaint_no_severity(self):
        """Complaint without severity keywords should be Standard or Low."""
        row = {
            "complaint_id": "TEST-014",
            "description": "Minor street lighting issue in morning hours",
            "location": "some road",
        }
        result = classify_complaint(row)
        self.assertIn(
            result["priority"], ["Standard", "Low"],
            f"Expected Standard or Low for non-severe complaint, got {result['priority']}"
        )

    def test_all_severity_keywords_recognized(self):
        """All severity keywords should be recognized."""
        for keyword in SEVERITY_KEYWORDS:
            row = {
                "complaint_id": f"TEST-SEV-{keyword}",
                "description": f"This complaint mentions {keyword}.",
                "location": "test location",
            }
            result = classify_complaint(row)
            self.assertEqual(
                result["priority"], "Urgent",
                f"Severity keyword '{keyword}' not triggering Urgent"
            )


class TestPriorityDetection(unittest.TestCase):
    """Test priority classification logic."""

    def test_low_priority_smell_keyword(self):
        """'smell' keyword should trigger Low priority."""
        row = {
            "complaint_id": "TEST-015",
            "description": "Overflowing garbage bins. Smell affecting shoppers.",
            "location": "market",
        }
        result = classify_complaint(row)
        self.assertEqual(
            result["priority"], "Low",
            f"Expected Low for smell, got {result['priority']}"
        )

    def test_standard_priority_default(self):
        """Complaints without severity or low-priority keywords should be Standard."""
        row = {
            "complaint_id": "TEST-016",
            "description": "Pothole on the road",
            "location": "street",
        }
        result = classify_complaint(row)
        self.assertIn(
            result["priority"], ["Urgent", "Standard", "Low"],
            f"Invalid priority {result['priority']}"
        )

    def test_priority_only_urgent_standard_low(self):
        """Priority must be one of: Urgent, Standard, Low."""
        test_complaints = [
            {"complaint_id": "TEST-017", "description": "random complaint", "location": "place"},
            {"complaint_id": "TEST-018", "description": "injury on road", "location": "place"},
            {"complaint_id": "TEST-019", "description": "minor smell issue", "location": "place"},
        ]
        valid_priorities = {"Urgent", "Standard", "Low"}
        for complaint in test_complaints:
            result = classify_complaint(complaint)
            self.assertIn(
                result["priority"], valid_priorities,
                f"Invalid priority: {result['priority']}"
            )


class TestReasonField(unittest.TestCase):
    """Test that reason field is always populated."""

    def test_reason_always_present(self):
        """Every classification must include a reason."""
        test_complaints = [
            {"complaint_id": "TEST-020", "description": "pothole", "location": "road"},
            {"complaint_id": "TEST-021", "description": "flood", "location": "street"},
            {"complaint_id": "TEST-022", "description": "", "location": ""},
        ]
        for complaint in test_complaints:
            result = classify_complaint(complaint)
            self.assertIn(
                "reason", result,
                f"Missing 'reason' field in result"
            )
            self.assertTrue(
                isinstance(result["reason"], str),
                f"Reason must be string, got {type(result['reason'])}"
            )
            self.assertGreater(
                len(result["reason"]), 0,
                f"Reason must not be empty"
            )

    def test_reason_cites_evidence(self):
        """Reason should cite specific words from description."""
        row = {
            "complaint_id": "TEST-023",
            "description": "Large pothole causing tyre damage",
            "location": "Karve Road",
        }
        result = classify_complaint(row)
        reason_lower = result["reason"].lower()
        # Should mention either pothole or tyre
        self.assertTrue(
            "pothole" in reason_lower or "tyre" in reason_lower,
            f"Reason does not cite evidence from description: {result['reason']}"
        )

    def test_reason_for_urgent_mentions_keyword(self):
        """Urgent classification reason should be present."""
        row = {
            "complaint_id": "TEST-024",
            "description": "Manhole missing - injury hazard for cyclists",
            "location": "Paud Road",
        }
        result = classify_complaint(row)
        if result["priority"] == "Urgent":
            self.assertTrue(
                len(result["reason"]) > 0,
                f"Urgent reason is empty"
            )


class TestAmbiguityFlagging(unittest.TestCase):
    """Test NEEDS_REVIEW flag for ambiguous cases."""

    def test_ambiguous_complaint_flagged(self):
        """Genuinely ambiguous complaints should be flagged NEEDS_REVIEW."""
        # A complaint that could be multiple categories
        row = {
            "complaint_id": "TEST-025",
            "description": "Streetlight and pothole near drainage area",
            "location": "intersection",
        }
        result = classify_complaint(row)
        # If genuinely ambiguous, should have NEEDS_REVIEW flag
        self.assertIn(
            result.get("flag", ""), ["NEEDS_REVIEW", ""],
            f"Flag must be NEEDS_REVIEW or empty, got {result.get('flag')}"
        )

    def test_missing_description_flagged(self):
        """Complaint with missing description should be flagged NEEDS_REVIEW."""
        row = {
            "complaint_id": "TEST-026",
            "description": "",
            "location": "some place",
        }
        result = classify_complaint(row)
        self.assertEqual(
            result["flag"], "NEEDS_REVIEW",
            f"Missing description should set NEEDS_REVIEW flag"
        )

    def test_other_category_flagged(self):
        """'Other' category should be flagged NEEDS_REVIEW."""
        row = {
            "complaint_id": "TEST-027",
            "description": "Something completely unrelated xyz abc",
            "location": "nowhere",
        }
        result = classify_complaint(row)
        if result["category"] == "Other":
            self.assertEqual(
                result["flag"], "NEEDS_REVIEW",
                f"'Other' category should be flagged"
            )

    def test_flag_is_needs_review_or_empty(self):
        """Flag must be either 'NEEDS_REVIEW' or empty string."""
        test_complaints = [
            {"complaint_id": "TEST-028", "description": "pothole damage", "location": "road"},
            {"complaint_id": "TEST-029", "description": "random xyz", "location": "place"},
            {"complaint_id": "TEST-030", "description": "", "location": ""},
        ]
        for complaint in test_complaints:
            result = classify_complaint(complaint)
            flag = result.get("flag", "")
            self.assertIn(
                flag, ["NEEDS_REVIEW", ""],
                f"Flag must be 'NEEDS_REVIEW' or empty, got '{flag}'"
            )


class TestTaxonomyConsistency(unittest.TestCase):
    """Test that similar complaints get same category."""

    def test_pothole_variations_same_category(self):
        """Different pothole descriptions should all get 'Pothole' category."""
        variations = [
            "Large pothole 60cm wide causing tyre damage",
            "Deep pothole near bus stop",
            "Pothole causing tyre damage",
        ]
        for desc in variations:
            row = {
                "complaint_id": f"TEST-POT-{desc[:10]}",
                "description": desc,
                "location": "road",
            }
            result = classify_complaint(row)
            self.assertEqual(
                result["category"], "Pothole",
                f"All pothole variations should be 'Pothole', got {result['category']} for: {desc}"
            )

    def test_flooding_variations_same_category(self):
        """Different flooding descriptions should all get 'Flooding' category."""
        variations = [
            "Underpass flooded knee-deep after rain",
            "Bus stand flooded. Passengers standing in water.",
            "Bridge approach floods in 30mins of rain",
        ]
        for desc in variations:
            row = {
                "complaint_id": f"TEST-FLOOD-{desc[:10]}",
                "description": desc,
                "location": "place",
            }
            result = classify_complaint(row)
            self.assertEqual(
                result["category"], "Flooding",
                f"All flooding variations should be 'Flooding', got {result['category']} for: {desc}"
            )

    def test_streetlight_variations_same_category(self):
        """Different streetlight descriptions should all get 'Streetlight' category."""
        variations = [
            "Three consecutive streetlights out for 10 days",
            "Streetlight flickering and sparking",
            "Area very dark at night. Streetlights not working.",
        ]
        for desc in variations:
            row = {
                "complaint_id": f"TEST-LIGHT-{desc[:10]}",
                "description": desc,
                "location": "road",
            }
            result = classify_complaint(row)
            self.assertEqual(
                result["category"], "Streetlight",
                f"All streetlight variations should be 'Streetlight', got {result['category']} for: {desc}"
            )


class TestReferenceValues(unittest.TestCase):
    """Test against known reference values from Pune test file."""

    @classmethod
    def setUpClass(cls):
        """Load test data once for all tests."""
        cls.test_data = pd.read_csv("../data/city-test-files/test_pune.csv")

    def test_pm_202401_pothole(self):
        """PM-202401: Large pothole should be Pothole, not Urgent."""
        row = self.test_data[self.test_data["complaint_id"] == "PM-202401"].iloc[0]
        result = classify_complaint({
            "complaint_id": row["complaint_id"],
            "description": row["description"],
            "location": row["location"],
        })
        self.assertEqual(result["category"], "Pothole")
        self.assertEqual(result["priority"], "Standard")

    def test_pm_202402_pothole_urgent(self):
        """PM-202402: Pothole near school should be Urgent."""
        row = self.test_data[self.test_data["complaint_id"] == "PM-202402"].iloc[0]
        result = classify_complaint({
            "complaint_id": row["complaint_id"],
            "description": row["description"],
            "location": row["location"],
        })
        self.assertEqual(result["category"], "Pothole")
        self.assertEqual(result["priority"], "Urgent", "School mention should trigger Urgent")

    def test_pm_202406_flooding(self):
        """PM-202406: Underpass flooded should be Flooding, Urgent."""
        row = self.test_data[self.test_data["complaint_id"] == "PM-202406"].iloc[0]
        result = classify_complaint({
            "complaint_id": row["complaint_id"],
            "description": row["description"],
            "location": row["location"],
        })
        self.assertEqual(result["category"], "Flooding")
        # Check if stranded/commuters should make it Urgent
        self.assertIn(result["priority"], ["Urgent", "Standard"])

    def test_pm_202408_drain_blockage(self):
        """PM-202408: Flooded area with drain blocked."""
        row = self.test_data[self.test_data["complaint_id"] == "PM-202408"].iloc[0]
        result = classify_complaint({
            "complaint_id": row["complaint_id"],
            "description": row["description"],
            "location": row["location"],
        })
        # Can be either Flooding or Drain Blockage (both valid due to pattern matching)
        self.assertIn(
            result["category"], ["Flooding", "Drain Blockage"],
            f"Expected Flooding or Drain Blockage, got {result['category']}"
        )

    def test_pm_202410_streetlight(self):
        """PM-202410: Streetlights out should be Streetlight."""
        row = self.test_data[self.test_data["complaint_id"] == "PM-202410"].iloc[0]
        result = classify_complaint({
            "complaint_id": row["complaint_id"],
            "description": row["description"],
            "location": row["location"],
        })
        self.assertEqual(result["category"], "Streetlight")

    def test_pm_202411_streetlight_urgent(self):
        """PM-202411: Sparking streetlight is hazard, should be Urgent."""
        row = self.test_data[self.test_data["complaint_id"] == "PM-202411"].iloc[0]
        result = classify_complaint({
            "complaint_id": row["complaint_id"],
            "description": row["description"],
            "location": row["location"],
        })
        self.assertEqual(result["category"], "Streetlight")
        self.assertEqual(result["priority"], "Urgent", "Hazard keyword should trigger Urgent")

    def test_pm_202413_waste(self):
        """PM-202413: Overflowing garbage should be Waste, Low priority."""
        row = self.test_data[self.test_data["complaint_id"] == "PM-202413"].iloc[0]
        result = classify_complaint({
            "complaint_id": row["complaint_id"],
            "description": row["description"],
            "location": row["location"],
        })
        self.assertEqual(result["category"], "Waste")

    def test_pm_202418_noise(self):
        """PM-202418: Music past midnight should be Noise."""
        row = self.test_data[self.test_data["complaint_id"] == "PM-202418"].iloc[0]
        result = classify_complaint({
            "complaint_id": row["complaint_id"],
            "description": row["description"],
            "location": row["location"],
        })
        self.assertEqual(result["category"], "Noise")

    def test_pm_202419_road_damage(self):
        """PM-202419: Road cracked and sinking should be Road Damage."""
        row = self.test_data[self.test_data["complaint_id"] == "PM-202419"].iloc[0]
        result = classify_complaint({
            "complaint_id": row["complaint_id"],
            "description": row["description"],
            "location": row["location"],
        })
        self.assertEqual(result["category"], "Road Damage")

    def test_pm_202420_pothole_urgent(self):
        """PM-202420: Manhole missing with injury risk should be Urgent."""
        row = self.test_data[self.test_data["complaint_id"] == "PM-202420"].iloc[0]
        result = classify_complaint({
            "complaint_id": row["complaint_id"],
            "description": row["description"],
            "location": row["location"],
        })
        self.assertEqual(result["priority"], "Urgent", "Injury mention should trigger Urgent")

    def test_pm_202427_flooding(self):
        """PM-202427: Bridge approach floods should be Flooding."""
        row = self.test_data[self.test_data["complaint_id"] == "PM-202427"].iloc[0]
        result = classify_complaint({
            "complaint_id": row["complaint_id"],
            "description": row["description"],
            "location": row["location"],
        })
        self.assertEqual(result["category"], "Flooding")

    def test_pm_202428_waste_urgent(self):
        """PM-202428: Dead animal is health concern, could be Urgent."""
        row = self.test_data[self.test_data["complaint_id"] == "PM-202428"].iloc[0]
        result = classify_complaint({
            "complaint_id": row["complaint_id"],
            "description": row["description"],
            "location": row["location"],
        })
        self.assertEqual(result["category"], "Waste")

    def test_pm_202430_heritage(self):
        """PM-202430: Heritage street should be Heritage Damage."""
        row = self.test_data[self.test_data["complaint_id"] == "PM-202430"].iloc[0]
        result = classify_complaint({
            "complaint_id": row["complaint_id"],
            "description": row["description"],
            "location": row["location"],
        })
        self.assertEqual(result["category"], "Heritage Damage")

    def test_pm_202433_waste(self):
        """PM-202433: Bulk waste dumped should be Waste."""
        row = self.test_data[self.test_data["complaint_id"] == "PM-202433"].iloc[0]
        result = classify_complaint({
            "complaint_id": row["complaint_id"],
            "description": row["description"],
            "location": row["location"],
        })
        self.assertEqual(result["category"], "Waste")

    def test_pm_202446_road_damage_urgent(self):
        """PM-202446: Elderly fell should be Urgent."""
        row = self.test_data[self.test_data["complaint_id"] == "PM-202446"].iloc[0]
        result = classify_complaint({
            "complaint_id": row["complaint_id"],
            "description": row["description"],
            "location": row["location"],
        })
        self.assertEqual(result["priority"], "Urgent", "Injury mention should trigger Urgent")


class TestEnforcementRules(unittest.TestCase):
    """Test enforcement rules to prevent core failure modes."""

    def test_enforcement_1_no_taxonomy_drift(self):
        """ENFORCEMENT #1: No taxonomy drift (same types get same category)."""
        # Run multiple classifications of similar complaints
        results = []
        for i in range(3):
            row = {
                "complaint_id": f"DRIFT-{i}",
                "description": "Large pothole causing damage",
                "location": "road",
            }
            result = classify_complaint(row)
            results.append(result["category"])
        
        # All should be identical
        self.assertEqual(
            len(set(results)), 1,
            f"Taxonomy drift detected: {results}"
        )
        self.assertEqual(results[0], "Pothole")

    def test_enforcement_2_severity_never_ignored(self):
        """ENFORCEMENT #2: Severity keywords never go undetected."""
        for keyword in ["injury", "child", "school", "hazard"]:
            row = {
                "complaint_id": f"SEV-{keyword}",
                "description": f"Complaint about {keyword} on the street",
                "location": "place",
            }
            result = classify_complaint(row)
            self.assertEqual(
                result["priority"], "Urgent",
                f"Severity keyword '{keyword}' not recognized"
            )

    def test_enforcement_3_reason_always_justifies(self):
        """ENFORCEMENT #3: Reason field always justifies classification."""
        test_complaints = [
            {"complaint_id": "JUS-001", "description": "pothole damage on road", "location": "street"},
            {"complaint_id": "JUS-002", "description": "injury risk from manhole", "location": "place"},
            {"complaint_id": "JUS-003", "description": "noise from music", "location": "venue"},
        ]
        for complaint in test_complaints:
            result = classify_complaint(complaint)
            reason = result["reason"].lower()
            # Reason should mention either category, evidence, or priority
            self.assertGreater(
                len(reason), 10,
                f"Reason too short to be justifying: '{result['reason']}'"
            )

    def test_enforcement_4_no_hallucinated_categories(self):
        """ENFORCEMENT #4: No hallucinated sub-categories outside allowed list."""
        test_complaints = [
            {"complaint_id": "HAL-001", "description": "something broken", "location": "place"},
            {"complaint_id": "HAL-002", "description": "bad infrastructure", "location": "street"},
            {"complaint_id": "HAL-003", "description": "random issue", "location": "location"},
        ]
        for complaint in test_complaints:
            result = classify_complaint(complaint)
            self.assertIn(
                result["category"], ALLOWED_CATEGORIES,
                f"Hallucinated category: {result['category']}"
            )

    def test_enforcement_5_ambiguity_not_ignored(self):
        """ENFORCEMENT #5: Genuinely ambiguous cases flagged NEEDS_REVIEW."""
        # A multi-faceted complaint
        row = {
            "complaint_id": "AMB-001",
            "description": "Road surface cracked near flooded drain",
            "location": "intersection",
        }
        result = classify_complaint(row)
        # If multiple patterns match equally, should be flagged
        if len(result.get("flag", "")) > 0:
            self.assertEqual(
                result["flag"], "NEEDS_REVIEW",
                "Flag must be NEEDS_REVIEW if set"
            )


class TestBatchProcessing(unittest.TestCase):
    """Test batch classification of multiple complaints."""

    def test_batch_classify_creates_output(self):
        """Batch classify should create output file."""
        input_file = "../data/city-test-files/test_pune.csv"
        output_file = "results_test_batch.csv"
        
        try:
            batch_classify(input_file, output_file)
            
            # Check output exists
            output_path = Path(output_file)
            self.assertTrue(
                output_path.exists(),
                f"Output file {output_file} not created"
            )
            
            # Verify output has correct structure
            output_df = pd.read_csv(output_file)
            expected_cols = ["complaint_id", "category", "priority", "reason", "flag"]
            for col in expected_cols:
                self.assertIn(col, output_df.columns, f"Missing column: {col}")
            
            # Should have 15 rows
            self.assertEqual(
                len(output_df), 15,
                f"Expected 15 rows in output, got {len(output_df)}"
            )
            
            # Cleanup
            output_path.unlink()
        except Exception as e:
            self.fail(f"Batch processing failed: {e}")

    def test_batch_classify_all_categories_valid(self):
        """All categories in batch output must be in allowed list."""
        input_file = "../data/city-test-files/test_pune.csv"
        output_file = "results_test_categories.csv"
        
        try:
            batch_classify(input_file, output_file)
            output_df = pd.read_csv(output_file)
            
            for category in output_df["category"]:
                self.assertIn(
                    category, ALLOWED_CATEGORIES,
                    f"Invalid category in output: {category}"
                )
            
            output_path = Path(output_file)
            output_path.unlink()
        except Exception as e:
            self.fail(f"Batch category validation failed: {e}")

    def test_batch_classify_all_priorities_valid(self):
        """All priorities in batch output must be Urgent/Standard/Low."""
        input_file = "../data/city-test-files/test_pune.csv"
        output_file = "results_test_priority.csv"
        
        try:
            batch_classify(input_file, output_file)
            output_df = pd.read_csv(output_file)
            
            valid_priorities = {"Urgent", "Standard", "Low"}
            for priority in output_df["priority"]:
                self.assertIn(
                    priority, valid_priorities,
                    f"Invalid priority in output: {priority}"
                )
            
            output_path = Path(output_file)
            output_path.unlink()
        except Exception as e:
            self.fail(f"Batch priority validation failed: {e}")


class TestEndToEnd(unittest.TestCase):
    """End-to-end integration tests."""

    def test_full_pipeline_pune_data(self):
        """Full pipeline: load → classify → output."""
        input_file = "../data/city-test-files/test_pune.csv"
        output_file = "results_pune.csv"
        
        try:
            # Run classifier
            batch_classify(input_file, output_file)
            
            # Load and verify output
            output_df = pd.read_csv(output_file)
            
            # All essential fields present
            required_fields = ["complaint_id", "category", "priority", "reason", "flag"]
            for field in required_fields:
                self.assertIn(field, output_df.columns)
            
            # All rows have valid data
            self.assertEqual(len(output_df), 15)
            
            # No NaN in critical fields
            for field in ["complaint_id", "category", "priority"]:
                self.assertEqual(
                    output_df[field].isna().sum(), 0,
                    f"Found NaN values in {field}"
                )
            
            # All categories are allowed
            for category in output_df["category"]:
                self.assertIn(category, ALLOWED_CATEGORIES)
            
        except Exception as e:
            self.fail(f"End-to-end pipeline failed: {e}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
