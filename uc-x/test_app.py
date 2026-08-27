import unittest
from pathlib import Path
import app


class PolicyQATests(unittest.TestCase):
    def setUp(self):
        self.docs = app.retrieve_documents(Path(__file__).resolve().parent.parent / "data" / "policy-documents")

    def test_refusal_for_unclear_topic(self):
        answer = app.answer_question("What is the company view on flexible working culture?", self.docs)
        self.assertIn("This question is not covered", answer)

    def test_single_source_answer_with_citation(self):
        answer = app.answer_question("Can I carry forward unused annual leave?", self.docs)
        self.assertIn("policy_hr_leave.txt", answer)
        self.assertIn("section 2.6", answer)

    def test_personal_phone_question_is_not_blended(self):
        answer = app.answer_question("Can I use my personal phone for work files from home?", self.docs)
        self.assertIn("policy_it_acceptable_use.txt", answer)
        self.assertIn("section 3.1", answer)
        self.assertNotIn("policy_hr_leave.txt", answer)


if __name__ == "__main__":
    unittest.main()
