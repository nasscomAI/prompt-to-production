import unittest
import os
import sys

# Prevent python path shadowing collisions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if 'app' in sys.modules:
    del sys.modules['app']

from app import retrieve_documents, answer_question, REFUSAL_TEMPLATE

class TestPolicyRAG(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.indexed_docs = retrieve_documents()

    def test_document_indexing(self):
        """Test that all three documents are successfully parsed and indexed."""
        self.assertIn("policy_hr_leave.txt", self.indexed_docs)
        self.assertIn("policy_it_acceptable_use.txt", self.indexed_docs)
        self.assertIn("policy_finance_reimbursement.txt", self.indexed_docs)

        # Verify specific sections exist
        self.assertIn("2.3", self.indexed_docs["policy_hr_leave.txt"])
        self.assertIn("3.1", self.indexed_docs["policy_it_acceptable_use.txt"])
        self.assertIn("3.1", self.indexed_docs["policy_finance_reimbursement.txt"])

    def test_question_carry_forward(self):
        """Test: Can I carry forward unused annual leave?"""
        q = "Can I carry forward unused annual leave?"
        ans, citation = answer_question(q, self.indexed_docs)
        self.assertIn("policy_hr_leave.txt", citation)
        self.assertIn("5 days", ans)
        self.assertIn("forfeited", ans)

    def test_question_install_slack(self):
        """Test: Can I install Slack on my work laptop?"""
        q = "Can I install Slack on my work laptop?"
        ans, citation = answer_question(q, self.indexed_docs)
        self.assertIn("policy_it_acceptable_use.txt", citation)
        self.assertIn("written approval", ans)
        self.assertIn("IT Department", ans)

    def test_question_home_office(self):
        """Test: What is the home office equipment allowance?"""
        q = "What is the home office equipment allowance?"
        ans, citation = answer_question(q, self.indexed_docs)
        self.assertIn("policy_finance_reimbursement.txt", citation)
        self.assertIn("8,000", ans)
        self.assertIn("permanent", ans)

    def test_question_personal_phone_isolation(self):
        """Test: Can I use my personal phone to access work files when working from home?
        Ensure no cross-document blending occurs."""
        q = "Can I use my personal phone to access work files when working from home?"
        ans, citation = answer_question(q, self.indexed_docs)
        self.assertIn("policy_it_acceptable_use.txt", citation)
        # Answer must specify email/portal access only and forbid other files
        self.assertIn("email", ans)
        self.assertIn("self-service portal", ans)
        self.assertIn("strictly prohibited", ans)

    def test_question_refusal(self):
        """Test: What is the company view on flexible working culture?
        Must use refusal template."""
        q = "What is the company view on flexible working culture?"
        ans, citation = answer_question(q, self.indexed_docs)
        self.assertEqual(citation, "None")
        self.assertIn("This question is not covered in the available policy documents", ans)
        self.assertIn("the HR Department", ans) # dynamically matched category department

    def test_question_da_and_meal(self):
        """Test: Can I claim DA and meal receipts on the same day?"""
        q = "Can I claim DA and meal receipts on the same day?"
        ans, citation = answer_question(q, self.indexed_docs)
        self.assertIn("policy_finance_reimbursement.txt", citation)
        self.assertIn("cannot be claimed simultaneously", ans)
        self.assertIn("explicitly prohibited", ans)

    def test_question_lwp_approvers(self):
        """Test: Who approves leave without pay?"""
        q = "Who approves leave without pay?"
        ans, citation = answer_question(q, self.indexed_docs)
        self.assertIn("policy_hr_leave.txt", citation)
        self.assertIn("both", ans)
        self.assertIn("Department Head", ans)
        self.assertIn("HR Director", ans)

if __name__ == "__main__":
    unittest.main()
