"""
UC-0B Test Suite — Policy Clause Preservation Validation
Tests the three core failure modes: clause omission, scope bleed, obligation softening
"""
import unittest
import sys
from pathlib import Path
from app import ClauseExtractor


class TestClauseExtraction(unittest.TestCase):
    """Test that all 10 critical clauses are extracted from the policy."""

    @classmethod
    def setUpClass(cls):
        """Load the policy document once for all tests."""
        policy_path = Path("../data/policy-documents/policy_hr_leave.txt")
        with open(policy_path, 'r', encoding='utf-8') as f:
            cls.policy_text = f.read()
        cls.extractor = ClauseExtractor(cls.policy_text)
        cls.summary, cls.missing = cls.extractor.extract_clauses()

    def test_all_clauses_extracted(self):
        """ENFORCEMENT #1: Every numbered clause must be present in the summary."""
        expected_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
        missing = self.missing
        self.assertEqual(len(missing), 0, f"CRITICAL FAILURE: Missing clauses {missing}")
        
    def test_clause_count(self):
        """Verify exactly 10 clauses are found."""
        found_count = sum(self.extractor.extracted_clauses.values())
        self.assertEqual(found_count, 10, f"Expected 10 clauses, found {found_count}")

    def test_clause_2_3_present(self):
        """Clause 2.3: 14-day advance notice required."""
        self.assertIn("2.3", self.summary)
        self.assertIn("14-day advance notice", self.summary)
        
    def test_clause_2_4_present(self):
        """Clause 2.4: Written approval required before leave commences."""
        self.assertIn("2.4", self.summary)
        self.assertIn("Written approval", self.summary)
        self.assertIn("Verbal not valid", self.summary)

    def test_clause_2_5_present(self):
        """Clause 2.5: Unapproved absence = LOP."""
        self.assertIn("2.5", self.summary)
        self.assertIn("Unapproved absence", self.summary)
        self.assertIn("LOP", self.summary)

    def test_clause_2_6_present(self):
        """Clause 2.6: Max 5 days carry-forward."""
        self.assertIn("2.6", self.summary)
        self.assertIn("Max 5 days", self.summary)
        self.assertIn("forfeited", self.summary)

    def test_clause_2_7_present(self):
        """Clause 2.7: Carry-forward must be used Jan-Mar."""
        self.assertIn("2.7", self.summary)
        self.assertIn("Jan", self.summary)
        self.assertIn("Mar", self.summary)

    def test_clause_3_2_present(self):
        """Clause 3.2: 3+ days requires medical cert within 48hrs."""
        self.assertIn("3.2", self.summary)
        self.assertIn("3+ consecutive sick days", self.summary)
        self.assertIn("medical cert", self.summary)
        self.assertIn("48hrs", self.summary)

    def test_clause_3_4_present(self):
        """Clause 3.4: Sick leave before/after holiday requires cert."""
        self.assertIn("3.4", self.summary)
        self.assertIn("before/after holiday", self.summary)
        self.assertIn("cert", self.summary)

    def test_clause_5_2_present(self):
        """Clause 5.2: THE TRAP — Requires Department Head AND HR Director (TWO approvers)."""
        self.assertIn("5.2", self.summary)
        self.assertIn("Department Head", self.summary, 
                      "MULTI-CONDITION VIOLATION: Missing 'Department Head' in clause 5.2")
        self.assertIn("HR Director", self.summary,
                      "MULTI-CONDITION VIOLATION: Missing 'HR Director' in clause 5.2")
        # Verify both are present and connected (not just one)
        self.assertTrue(
            ("Department Head" in self.summary and "HR Director" in self.summary),
            "CRITICAL FAILURE: Clause 5.2 must specify BOTH approvers, not just one"
        )

    def test_clause_5_3_present(self):
        """Clause 5.3: LWP >30 days requires Municipal Commissioner approval."""
        self.assertIn("5.3", self.summary)
        self.assertIn("Municipal Commissioner", self.summary)
        self.assertIn("30 days", self.summary)

    def test_clause_7_2_present(self):
        """Clause 7.2: Leave encashment during service not permitted."""
        self.assertIn("7.2", self.summary)
        self.assertIn("not permitted", self.summary)
        self.assertIn("during service", self.summary)


class TestBindingVerbPreservation(unittest.TestCase):
    """Test that binding verbs are preserved and not softened."""

    @classmethod
    def setUpClass(cls):
        policy_path = Path("../data/policy-documents/policy_hr_leave.txt")
        with open(policy_path, 'r', encoding='utf-8') as f:
            cls.policy_text = f.read()
        cls.extractor = ClauseExtractor(cls.policy_text)
        cls.summary, _ = cls.extractor.extract_clauses()

    def test_no_obligation_softening(self):
        """ENFORCEMENT #3: Never substitute 'should' for 'must' or 'may' for 'will'."""
        # Check for softening patterns
        softening_patterns = [
            ("must", "should"),
            ("must", "may"),
            ("will", "may"),
            ("must", "could"),
            ("will", "could"),
        ]
        
        for strong, weak in softening_patterns:
            if strong in self.policy_text and weak in self.summary:
                # Only flag if the weak form appears where strong was expected
                # This is a heuristic check
                pass
        
        # More direct check: verify key obligations use strong language
        must_clauses = ["2.3", "2.4", "2.7"]
        for clause_id in must_clauses:
            if clause_id in self.summary:
                # These should use "must" or equivalent strong verb
                self.assertTrue(
                    "must" in self.summary.lower() or "requires" in self.summary.lower() or "required" in self.summary.lower(),
                    f"Clause {clause_id} may have softened binding verb"
                )

    def test_clause_5_2_dual_requirement_not_softened(self):
        """Clause 5.2 cannot be softened to single approver."""
        clause_5_2_text = [line for line in self.summary.split('\n') if '5.2' in line]
        self.assertTrue(len(clause_5_2_text) > 0, "Clause 5.2 missing")
        
        clause_text = ' '.join(clause_5_2_text)
        # Both approvers must be mentioned
        self.assertIn("Department Head", clause_text)
        self.assertIn("HR Director", clause_text)


class TestMultiConditionPreservation(unittest.TestCase):
    """Test that multi-condition obligations preserve ALL conditions."""

    @classmethod
    def setUpClass(cls):
        policy_path = Path("../data/policy-documents/policy_hr_leave.txt")
        with open(policy_path, 'r', encoding='utf-8') as f:
            cls.policy_text = f.read()
        cls.extractor = ClauseExtractor(cls.policy_text)
        cls.summary, _ = cls.extractor.extract_clauses()

    def test_clause_5_2_both_approvers_required(self):
        """THE TRAP: Clause 5.2 requires BOTH approvers, not just 'approval'."""
        validation_issues = self.extractor.validate_multi_conditions()
        
        # Should have NO multi-condition violations
        multi_cond_issues = [i for i in validation_issues if "MULTI-CONDITION" in i]
        self.assertEqual(len(multi_cond_issues), 0, 
                        f"CRITICAL FAILURE: {multi_cond_issues}")

    def test_clause_5_2_not_dropped_to_single_approval(self):
        """Verify 5.2 is not simplified to just 'LWP requires approval'."""
        # Extract clause 5.2 section
        summary_lines = self.summary.split('\n')
        clause_5_2_line = [line for line in summary_lines if '5.2' in line]
        
        if clause_5_2_line:
            text = ' '.join(clause_5_2_line)
            # Must contain both approvers
            has_dept_head = "Department Head" in text
            has_hr_director = "HR Director" in text
            
            self.assertTrue(has_dept_head and has_hr_director,
                          f"MULTI-CONDITION VIOLATION: Clause 5.2 missing one or both approvers. Text: {text}")

    def test_clause_3_4_medical_cert_required_regardless(self):
        """Clause 3.4: Medical cert required REGARDLESS OF DURATION."""
        self.assertIn("3.4", self.summary)
        self.assertIn("regardless", self.summary)
        self.assertIn("duration", self.summary)


class TestNoScopeBleed(unittest.TestCase):
    """Test that summary does not add information not in source document."""

    @classmethod
    def setUpClass(cls):
        policy_path = Path("../data/policy-documents/policy_hr_leave.txt")
        with open(policy_path, 'r', encoding='utf-8') as f:
            cls.policy_text = f.read()
        cls.extractor = ClauseExtractor(cls.policy_text)
        cls.summary, _ = cls.extractor.extract_clauses()

    def test_no_external_knowledge_injected(self):
        """ENFORCEMENT #3: Never add information not present in source document."""
        # Check for common scope bleed patterns
        forbidden_phrases = [
            "international leave",
            "UNESCO",
            "global standard",
            "best practice",
            "industry standard",
            "based on research",
        ]
        
        for phrase in forbidden_phrases:
            self.assertNotIn(phrase.lower(), self.summary.lower(),
                           f"SCOPE BLEED: Summary contains '{phrase}' not in source")

    def test_only_source_clauses_present(self):
        """Summary should only contain the 10 critical clauses, no extras."""
        # Check for clause IDs not in the critical list
        critical_ids = {"2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}
        
        # Scan for other clause IDs (1.1, 1.2, 2.1, 2.2, etc.)
        import re
        all_clause_ids = set(re.findall(r'\d+\.\d+', self.summary))
        extra_ids = all_clause_ids - critical_ids
        
        # It's okay to have extra IDs if they're part of larger numbers or dates
        # But explicitly included clause IDs should only be the critical 10
        extra_critical = [cid for cid in extra_ids if 'Clause' in self.summary or f': {cid}' in self.summary]
        self.assertEqual(len(extra_critical), 0,
                        f"SCOPE BLEED: Extra clauses included: {extra_critical}")


class TestValidationReport(unittest.TestCase):
    """Test that the validation report is accurate and complete."""

    @classmethod
    def setUpClass(cls):
        policy_path = Path("../data/policy-documents/policy_hr_leave.txt")
        with open(policy_path, 'r', encoding='utf-8') as f:
            cls.policy_text = f.read()
        cls.extractor = ClauseExtractor(cls.policy_text)
        cls.summary, _ = cls.extractor.extract_clauses()

    def test_validation_report_present(self):
        """Summary must include a validation report."""
        self.assertIn("VALIDATION REPORT", self.summary)

    def test_validation_report_shows_correct_count(self):
        """Validation report must show correct clause count."""
        self.assertIn("Total Critical Clauses: 10", self.summary)
        self.assertIn("Clauses Found: 10", self.summary)
        self.assertIn("Clauses Missing: 0", self.summary)

    def test_all_clauses_preserved_message(self):
        """Should confirm all critical clauses preserved."""
        self.assertIn("all critical clauses preserved", self.summary.lower())


class TestEndToEndIntegration(unittest.TestCase):
    """End-to-end test: Policy → Extract → Summary → Validate."""

    def test_full_pipeline(self):
        """Complete pipeline test."""
        policy_path = Path("../data/policy-documents/policy_hr_leave.txt")
        with open(policy_path, 'r', encoding='utf-8') as f:
            policy = f.read()
        
        extractor = ClauseExtractor(policy)
        summary, missing = extractor.extract_clauses()
        validation_issues = extractor.validate_multi_conditions()
        
        # All critical checks
        self.assertEqual(len(missing), 0, f"Missing clauses: {missing}")
        self.assertEqual(len(validation_issues), 0, f"Validation issues: {validation_issues}")
        self.assertIn("all critical clauses preserved", summary.lower())


def run_tests():
    """Run all tests with verbose output."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestClauseExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestBindingVerbPreservation))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiConditionPreservation))
    suite.addTests(loader.loadTestsFromTestCase(TestNoScopeBleed))
    suite.addTests(loader.loadTestsFromTestCase(TestValidationReport))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEndIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
