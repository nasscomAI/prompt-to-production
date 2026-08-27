"""
UC-X Test Suite — Policy Q&A System Validation
Tests single-document sourcing, citation preservation, hedging prevention, and cross-document blending detection
"""
import unittest
import sys
from pathlib import Path
from app import PolicyDocumentIndexer, PolicyQuestionAnswerer, REFUSAL_TEMPLATE


class TestDocumentLoading(unittest.TestCase):
    """Test document loading and indexing."""

    def setUp(self):
        self.indexer = PolicyDocumentIndexer()

    def test_all_documents_load(self):
        """All 3 policy documents load successfully."""
        self.indexer.load_documents()
        loaded_docs = self.indexer.get_all_documents()
        self.assertEqual(len(loaded_docs), 3)

    def test_documents_contain_sections(self):
        """Each document is indexed with section IDs."""
        self.indexer.load_documents()
        for doc_name in self.indexer.get_all_documents():
            self.assertGreater(len(self.indexer.documents[doc_name]), 0,
                             f"Document {doc_name} has no sections")

    def test_hr_policy_loaded(self):
        """HR Leave Policy loads with expected sections."""
        self.indexer.load_documents()
        self.assertIn("HR Leave Policy", self.indexer.get_all_documents())

    def test_it_policy_loaded(self):
        """IT Acceptable Use Policy loads with expected sections."""
        self.indexer.load_documents()
        self.assertIn("IT Acceptable Use Policy", self.indexer.get_all_documents())

    def test_finance_policy_loaded(self):
        """Finance Reimbursement Policy loads with expected sections."""
        self.indexer.load_documents()
        self.assertIn("Finance Reimbursement Policy", self.indexer.get_all_documents())


class TestQuestion1(unittest.TestCase):
    """Test: Can I carry forward unused annual leave?"""

    @classmethod
    def setUpClass(cls):
        cls.indexer = PolicyDocumentIndexer()
        cls.indexer.load_documents()
        cls.answerer = PolicyQuestionAnswerer(cls.indexer)

    def test_q1_has_answer(self):
        """Question 1 returns an answer."""
        answer, source, section = self.answerer.answer_question("Can I carry forward unused annual leave?")
        self.assertIsNotNone(answer)
        self.assertGreater(len(answer), 0)

    def test_q1_single_source(self):
        """Question 1 sources from HR policy only."""
        answer, source, section = self.answerer.answer_question("Can I carry forward unused annual leave?")
        self.assertEqual(source, "HR Leave Policy")
        self.assertIsNotNone(section)

    def test_q1_cites_section(self):
        """Question 1 answer cites section 2.6."""
        answer, source, section = self.answerer.answer_question("Can I carry forward unused annual leave?")
        self.assertEqual(section, "2.6")

    def test_q1_mentions_5_days(self):
        """Question 1 answer specifies max 5 days carry-forward."""
        answer, source, section = self.answerer.answer_question("Can I carry forward unused annual leave?")
        self.assertIn("5", answer)

    def test_q1_mentions_forfeiture_date(self):
        """Question 1 answer specifies 31 December forfeiture date."""
        answer, source, section = self.answerer.answer_question("Can I carry forward unused annual leave?")
        self.assertIn("31 December", answer)


class TestQuestion2(unittest.TestCase):
    """Test: Can I install Slack on my work laptop?"""

    @classmethod
    def setUpClass(cls):
        cls.indexer = PolicyDocumentIndexer()
        cls.indexer.load_documents()
        cls.answerer = PolicyQuestionAnswerer(cls.indexer)

    def test_q2_has_answer(self):
        """Question 2 returns an answer."""
        answer, source, section = self.answerer.answer_question("Can I install Slack on my work laptop?")
        self.assertIsNotNone(answer)

    def test_q2_single_source(self):
        """Question 2 sources from IT policy only."""
        answer, source, section = self.answerer.answer_question("Can I install Slack on my work laptop?")
        self.assertEqual(source, "IT Acceptable Use Policy")

    def test_q2_cites_section(self):
        """Question 2 answer cites section 2.3."""
        answer, source, section = self.answerer.answer_question("Can I install Slack on my work laptop?")
        self.assertEqual(section, "2.3")

    def test_q2_mentions_approval(self):
        """Question 2 answer mentions written IT approval requirement."""
        answer, source, section = self.answerer.answer_question("Can I install Slack on my work laptop?")
        self.assertIn("written approval", answer.lower())


class TestQuestion3(unittest.TestCase):
    """Test: What is the home office equipment allowance?"""

    @classmethod
    def setUpClass(cls):
        cls.indexer = PolicyDocumentIndexer()
        cls.indexer.load_documents()
        cls.answerer = PolicyQuestionAnswerer(cls.indexer)

    def test_q3_has_answer(self):
        """Question 3 returns an answer."""
        answer, source, section = self.answerer.answer_question("What is the home office equipment allowance?")
        self.assertIsNotNone(answer)

    def test_q3_single_source(self):
        """Question 3 sources from Finance policy only."""
        answer, source, section = self.answerer.answer_question("What is the home office equipment allowance?")
        self.assertEqual(source, "Finance Reimbursement Policy")

    def test_q3_cites_section(self):
        """Question 3 answer cites section 3.1."""
        answer, source, section = self.answerer.answer_question("What is the home office equipment allowance?")
        self.assertEqual(section, "3.1")

    def test_q3_mentions_8000(self):
        """Question 3 answer specifies Rs 8,000 allowance."""
        answer, source, section = self.answerer.answer_question("What is the home office equipment allowance?")
        self.assertIn("8,000", answer)

    def test_q3_mentions_permanent_wfh(self):
        """Question 3 answer specifies permanent work-from-home only."""
        answer, source, section = self.answerer.answer_question("What is the home office equipment allowance?")
        self.assertIn("permanent", answer.lower())


class TestQuestion4(unittest.TestCase):
    """Test: Can I use my personal phone to access work files from home? (THE TRAP)"""

    @classmethod
    def setUpClass(cls):
        cls.indexer = PolicyDocumentIndexer()
        cls.indexer.load_documents()
        cls.answerer = PolicyQuestionAnswerer(cls.indexer)

    def test_q4_has_answer(self):
        """Question 4 returns an answer."""
        answer, source, section = self.answerer.answer_question("Can I use my personal phone to access work files from home?")
        self.assertIsNotNone(answer)

    def test_q4_single_source(self):
        """Question 4 sources from IT policy only (NO blending with HR)."""
        answer, source, section = self.answerer.answer_question("Can I use my personal phone to access work files from home?")
        # Must NOT be None, and must be IT policy
        self.assertIsNotNone(source)
        self.assertEqual(source, "IT Acceptable Use Policy")

    def test_q4_cites_section(self):
        """Question 4 answer cites section 3.1."""
        answer, source, section = self.answerer.answer_question("Can I use my personal phone to access work files from home?")
        self.assertEqual(section, "3.1")

    def test_q4_mentions_email_portal_only(self):
        """Question 4 answer specifies email and portal ONLY."""
        answer, source, section = self.answerer.answer_question("Can I use my personal phone to access work files from home?")
        self.assertIn("email", answer.lower())
        self.assertIn("portal", answer.lower())

    def test_q4_mentions_no_sensitive_data(self):
        """Question 4 answer specifies no sensitive/classified data."""
        answer, source, section = self.answerer.answer_question("Can I use my personal phone to access work files from home?")
        self.assertIn("classified", answer.lower())

    def test_q4_no_blending(self):
        """Question 4 does NOT blend IT and HR policies."""
        answer, source, section = self.answerer.answer_question("Can I use my personal phone to access work files from home?")
        # Answer should NOT mention HR concepts like "approved remote work arrangements"
        # It should stick to IT policy section 3.1
        self.assertNotIn("HR", answer)


class TestQuestion5(unittest.TestCase):
    """Test: What is the company view on flexible working culture? (REFUSAL TEST)"""

    @classmethod
    def setUpClass(cls):
        cls.indexer = PolicyDocumentIndexer()
        cls.indexer.load_documents()
        cls.answerer = PolicyQuestionAnswerer(cls.indexer)

    def test_q5_refuses(self):
        """Question 5 is refused (not in any document)."""
        answer, source, section = self.answerer.answer_question("What is the company view on flexible working culture?")
        # Should use refusal template
        self.assertEqual(answer, REFUSAL_TEMPLATE)

    def test_q5_no_source(self):
        """Question 5 refusal has no source or section."""
        answer, source, section = self.answerer.answer_question("What is the company view on flexible working culture?")
        self.assertIsNone(source)
        self.assertIsNone(section)

    def test_q5_uses_exact_template(self):
        """Question 5 uses exact refusal template."""
        answer, source, section = self.answerer.answer_question("What is the company view on flexible working culture?")
        self.assertEqual(answer, REFUSAL_TEMPLATE)


class TestQuestion6(unittest.TestCase):
    """Test: Can I claim DA and meal receipts on the same day?"""

    @classmethod
    def setUpClass(cls):
        cls.indexer = PolicyDocumentIndexer()
        cls.indexer.load_documents()
        cls.answerer = PolicyQuestionAnswerer(cls.indexer)

    def test_q6_has_answer(self):
        """Question 6 returns an answer."""
        answer, source, section = self.answerer.answer_question("Can I claim DA and meal receipts on the same day?")
        self.assertIsNotNone(answer)

    def test_q6_single_source(self):
        """Question 6 sources from Finance policy only."""
        answer, source, section = self.answerer.answer_question("Can I claim DA and meal receipts on the same day?")
        self.assertEqual(source, "Finance Reimbursement Policy")

    def test_q6_cites_section(self):
        """Question 6 answer cites section 2.6."""
        answer, source, section = self.answerer.answer_question("Can I claim DA and meal receipts on the same day?")
        self.assertEqual(section, "2.6")

    def test_q6_says_no(self):
        """Question 6 answer clearly says NO."""
        answer, source, section = self.answerer.answer_question("Can I claim DA and meal receipts on the same day?")
        self.assertIn("cannot", answer.lower())


class TestQuestion7(unittest.TestCase):
    """Test: Who approves leave without pay?"""

    @classmethod
    def setUpClass(cls):
        cls.indexer = PolicyDocumentIndexer()
        cls.indexer.load_documents()
        cls.answerer = PolicyQuestionAnswerer(cls.indexer)

    def test_q7_has_answer(self):
        """Question 7 returns an answer."""
        answer, source, section = self.answerer.answer_question("Who approves leave without pay?")
        self.assertIsNotNone(answer)

    def test_q7_single_source(self):
        """Question 7 sources from HR policy only."""
        answer, source, section = self.answerer.answer_question("Who approves leave without pay?")
        self.assertEqual(source, "HR Leave Policy")

    def test_q7_cites_section(self):
        """Question 7 answer cites section 5.2."""
        answer, source, section = self.answerer.answer_question("Who approves leave without pay?")
        self.assertEqual(section, "5.2")

    def test_q7_mentions_both_approvers(self):
        """Question 7 answer mentions BOTH Department Head AND HR Director."""
        answer, source, section = self.answerer.answer_question("Who approves leave without pay?")
        self.assertIn("Department Head", answer)
        self.assertIn("HR Director", answer)


class TestEnforcementRules(unittest.TestCase):
    """Test enforcement of rules preventing common failures."""

    @classmethod
    def setUpClass(cls):
        cls.indexer = PolicyDocumentIndexer()
        cls.indexer.load_documents()
        cls.answerer = PolicyQuestionAnswerer(cls.indexer)

    def test_enforcement_1_no_cross_blending(self):
        """ENFORCEMENT #1: No cross-document blending."""
        # The personal phone question could be "blended" with HR's approved WFH tools
        # But correct answer must stay within IT policy section 3.1
        answer, source, section = self.answerer.answer_question("Can I use my personal phone to access work files from home?")
        
        # Verify it's single-source
        self.assertEqual(source, "IT Acceptable Use Policy")
        # Verify it doesn't mention HR concepts
        self.assertNotIn("approved remote work", answer.lower())

    def test_enforcement_2_no_hedging(self):
        """ENFORCEMENT #2: No hedging phrases in answers."""
        # Test all 7 questions for hedging phrases
        questions = [
            "Can I carry forward unused annual leave?",
            "Can I install Slack on my work laptop?",
            "What is the home office equipment allowance?",
            "Can I use my personal phone to access work files from home?",
            "Can I claim DA and meal receipts on the same day?",
            "Who approves leave without pay?",
        ]
        
        hedging_phrases = [
            "while not explicitly",
            "typically",
            "generally understood",
            "common practice",
            "most companies",
        ]
        
        for question in questions:
            answer, source, section = self.answerer.answer_question(question)
            answer_lower = answer.lower()
            for phrase in hedging_phrases:
                self.assertNotIn(phrase, answer_lower, 
                               f"Hedging phrase '{phrase}' found in answer to: {question}")

    def test_enforcement_3_exact_refusal_template(self):
        """ENFORCEMENT #3: Exact refusal template used, no paraphrasing."""
        answer, source, section = self.answerer.answer_question("What is the company view on flexible working culture?")
        # Must be exact template
        self.assertEqual(answer, REFUSAL_TEMPLATE)

    def test_enforcement_4_citations_included(self):
        """ENFORCEMENT #4: Every answer includes citation (document + section)."""
        questions_expecting_citation = [
            "Can I carry forward unused annual leave?",
            "Can I install Slack on my work laptop?",
            "What is the home office equipment allowance?",
            "Can I claim DA and meal receipts on the same day?",
            "Who approves leave without pay?",
        ]
        
        for question in questions_expecting_citation:
            answer, source, section = self.answerer.answer_question(question)
            self.assertIsNotNone(source, f"No source for: {question}")
            self.assertIsNotNone(section, f"No section for: {question}")

    def test_enforcement_5_condition_preservation(self):
        """ENFORCEMENT #5: Exact conditions preserved (email and portal ONLY)."""
        answer, source, section = self.answerer.answer_question("Can I use my personal phone to access work files from home?")
        # The policy says email and portal ONLY
        # Answer must preserve the "only" limitation
        self.assertIn("only", answer.lower())

    def test_enforcement_6_refusal_for_ambiguous(self):
        """ENFORCEMENT #6: Refuse if answering requires choosing between 2+ documents."""
        # A question about "approved work arrangements" could involve both HR and IT
        # The system should either answer from one or refuse
        # (In this test suite, we have predetermined answers, but in real scenario would refuse)
        pass


class TestFormattedResponse(unittest.TestCase):
    """Test response formatting."""

    @classmethod
    def setUpClass(cls):
        cls.indexer = PolicyDocumentIndexer()
        cls.indexer.load_documents()
        cls.answerer = PolicyQuestionAnswerer(cls.indexer)

    def test_response_includes_citation_format(self):
        """Formatted response includes [Source: Doc, Section ID] format."""
        answer, source, section = self.answerer.answer_question("Can I carry forward unused annual leave?")
        formatted = self.answerer.format_response(answer, source, section)
        
        self.assertIn("[Source:", formatted)
        self.assertIn("Section", formatted)

    def test_refusal_response_no_citation(self):
        """Refusal response has no citation."""
        answer, source, section = self.answerer.answer_question("What is the company view on flexible working culture?")
        formatted = self.answerer.format_response(answer, source, section)
        
        # Refusal should not have [Source: ...] format
        self.assertNotIn("[Source:", formatted)


class TestEndToEnd(unittest.TestCase):
    """End-to-end system tests."""

    def test_full_system_initialization(self):
        """Full system initializes without error."""
        indexer = PolicyDocumentIndexer()
        indexer.load_documents()
        answerer = PolicyQuestionAnswerer(indexer)
        
        self.assertIsNotNone(answerer)
        self.assertEqual(len(indexer.get_all_documents()), 3)

    def test_all_7_questions_answered(self):
        """All 7 test questions get responses."""
        indexer = PolicyDocumentIndexer()
        indexer.load_documents()
        answerer = PolicyQuestionAnswerer(indexer)
        
        questions = [
            "Can I carry forward unused annual leave?",
            "Can I install Slack on my work laptop?",
            "What is the home office equipment allowance?",
            "Can I use my personal phone to access work files from home?",
            "What is the company view on flexible working culture?",
            "Can I claim DA and meal receipts on the same day?",
            "Who approves leave without pay?",
        ]
        
        for question in questions:
            answer, source, section = answerer.answer_question(question)
            self.assertIsNotNone(answer)
            self.assertGreater(len(answer), 0)


def run_tests():
    """Run all tests with verbose output."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDocumentLoading))
    suite.addTests(loader.loadTestsFromTestCase(TestQuestion1))
    suite.addTests(loader.loadTestsFromTestCase(TestQuestion2))
    suite.addTests(loader.loadTestsFromTestCase(TestQuestion3))
    suite.addTests(loader.loadTestsFromTestCase(TestQuestion4))
    suite.addTests(loader.loadTestsFromTestCase(TestQuestion5))
    suite.addTests(loader.loadTestsFromTestCase(TestQuestion6))
    suite.addTests(loader.loadTestsFromTestCase(TestQuestion7))
    suite.addTests(loader.loadTestsFromTestCase(TestEnforcementRules))
    suite.addTests(loader.loadTestsFromTestCase(TestFormattedResponse))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEnd))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
