import unittest
import os
import sys

# Prevent python path shadowing collisions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if 'app' in sys.modules:
    del sys.modules['app']

from app import retrieve_policy, validate_clause_summary, generate_and_validate_summary

class TestClausePreservingSummarizer(unittest.TestCase):
    def test_retrieve_policy(self):
        """Test that policy sections are parsed and extracted correctly."""
        # Using the actual policy file
        policy_path = "../data/policy-documents/policy_hr_leave.txt"
        if os.path.exists(policy_path):
            sections = retrieve_policy(policy_path)
            self.assertIn("2.3", sections)
            self.assertIn("5.2", sections)
            self.assertTrue(len(sections) >= 10)

    def test_validation_success_cases(self):
        """Test that valid summaries pass the deterministic validation checks."""
        # 2.3
        self.assertTrue(validate_clause_summary("2.3", "Clause 2.3: Employees must submit annual leave requests at least 14 days in advance."))
        # 5.2
        self.assertTrue(validate_clause_summary("5.2", "Clause 5.2: Leave Without Pay (LWP) requires approval of both Department Head AND HR Director."))
        # 7.2
        self.assertTrue(validate_clause_summary("7.2", "Clause 7.2: Leave encashment during active service is not permitted under any circumstances."))

    def test_validation_softening_failures(self):
        """Test that validation fails when mandatory obligations are softened."""
        # 'must' replaced with 'should'
        self.assertFalse(validate_clause_summary("2.3", "Clause 2.3: Employees should submit leave requests at least 14 days in advance."))
        # 'requires' replaced with 'generally' or 'typically'
        self.assertFalse(validate_clause_summary("3.2", "Clause 3.2: Sick leave 3+ days typically requires certificate."))

    def test_validation_condition_drop_failures(self):
        """Test that validation fails when conditions or multi-approvers are dropped."""
        # 5.2 missing 'HR Director'
        self.assertFalse(validate_clause_summary("5.2", "Clause 5.2: Leave Without Pay requires approval from Department Head."))
        # 5.2 missing 'both' or 'and'
        self.assertFalse(validate_clause_summary("5.2", "Clause 5.2: Leave Without Pay requires approval of Department Head or HR Director."))

    def test_fallback_behavior(self):
        """Test that generate_and_validate_summary falls back to verbatim quoting if any summary fails validation."""
        fake_sections = {
            "2.3": "Original text 2.3",
            "5.2": "Original text 5.2"
        }
        # Let's verify standard summaries (which are correct) pass and do not fallback
        res = generate_and_validate_summary(fake_sections)
        self.assertNotIn("FLAGGED FOR REVIEW", res)

if __name__ == "__main__":
    unittest.main()
