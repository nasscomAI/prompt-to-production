"""Adversarial retrieval cases derived directly from the three policy files."""
import unittest

import app


class AdversarialRetrievalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = app.retrieve_documents()

    def assert_section(self, question, section, document="policy_finance_reimbursement.txt"):
        answer = app.answer_question(question, self.index)
        self.assertIn(f"[{document}, section {section}]", answer, question)

    def assert_refusal(self, question):
        self.assertEqual(app.answer_question(question, self.index), app.REFUSAL, question)

    def test_meal_and_da_distinctions(self):
        clause_26 = (
            "Can I claim meals and DA together?",
            "Can I submit meal receipts if I already claimed DA?",
            "Can I claim DA and meal receipts on the same day?",
            "Can I claim Rs 750 for meals in addition to DA?",
            "What is the maximum meal reimbursement per day?",
            "Can I claim actual meals instead of DA?",
            "If I don't claim DA, can I claim meal expenses?",
            "Can I claim both DA and actual meal expenses?",
        )
        for question in clause_26:
            with self.subTest(question=question):
                self.assert_section(question, "2.6")
        self.assert_section("Does DA include meals?", "2.5")
        self.assert_section("Are meal receipts required when claiming DA?", "2.5")

    def test_deadline_processing_and_submission_method(self):
        for question in (
            "How late can I submit a reimbursement claim?",
            "How long do I have to submit a reimbursement?",
            "How many days do I have to submit an expense claim?",
            "What is the deadline for submitting an expense?",
        ):
            with self.subTest(question=question):
                self.assert_section(question, "1.3")
        self.assert_section("When must reimbursement claims be submitted?", "6.1")
        for question in (
            "When will my reimbursement be processed?",
            "How quickly will Finance process my reimbursement?",
            "How many working days does reimbursement processing take?",
            "How long does Finance take to process a claim?",
            "How quickly will Finance pay my reimbursement?",
            "How long does reimbursement processing normally take?",
            "How much time does Finance need to process an expense claim?",
            "What is the processing period for reimbursement?",
        ):
            with self.subTest(question=question):
                self.assert_section(question, "6.3")

    def test_wfh_allowance_status_and_documents(self):
        self.assert_section("What is the home office equipment allowance?", "3.1")
        self.assert_section("Is the Rs 8,000 allowance available for permanent WFH?", "3.1")
        for question in (
            "Can temporary WFH employees get the home office allowance?",
            "Can partial WFH employees receive the allowance?",
            "Can employees on temporary WFH claim Rs 8,000?",
            "Can employees on partial WFH claim Rs 8,000?",
        ):
            with self.subTest(question=question):
                self.assert_section(question, "3.5")
        self.assert_section("What documents are required for a home office equipment claim?", "3.4")
        self.assert_section("How long do I have to submit a WFH equipment claim?", "3.4")

    def test_installation_and_multi_topic_question(self):
        for question in (
            "Can I install Slack on my work laptop?",
            "Do I need IT approval before installing software?",
            "Can I install software on my company laptop?",
            "Is written approval required before installing software?",
            "Can I install an application on a corporate device?",
        ):
            with self.subTest(question=question):
                self.assert_section(question, "2.3", "policy_it_acceptable_use.txt")
        self.assert_refusal("Can I install Slack using my WFH equipment allowance?")

    def test_personal_devices_do_not_grant_general_wfh_permission(self):
        self.assert_refusal("Can I work from home using my personal laptop?")
        self.assert_section("Can I use my personal phone to access CMC email?", "3.1", "policy_it_acceptable_use.txt")
        self.assert_section("Can I use my personal laptop to access sensitive CMC data?", "3.2", "policy_it_acceptable_use.txt")
        self.assert_section("Can personal devices store classified CMC information?", "3.2", "policy_it_acceptable_use.txt")
        self.assert_section("Do personal devices need a PIN or biometric lock?", "3.4", "policy_it_acceptable_use.txt")

    def test_leave_subtopics(self):
        for question in (
            "Can I carry forward unused annual leave?",
            "Can annual leave be carried into next year?",
            "How many annual leave days can I carry forward?",
            "What happens to unused annual leave?",
            "Annual leave carry forward?",
        ):
            with self.subTest(question=question):
                self.assert_section(question, "2.6", "policy_hr_leave.txt")
        self.assert_section("When do carried-forward leave days expire?", "2.7", "policy_hr_leave.txt")
        self.assert_section("What is maternity leave for the first two live births?", "4.1", "policy_hr_leave.txt")
        self.assert_section("What is maternity leave for a third child?", "4.2", "policy_hr_leave.txt")
        self.assert_section("What is the paternity leave entitlement?", "4.3", "policy_hr_leave.txt")
        self.assert_section("Who approves leave without pay?", "5.2", "policy_hr_leave.txt")
        self.assert_refusal("Does the IT department approve leave without pay?")

    def test_out_of_scope_and_near_misses_refuse(self):
        for question in (
            "What is the company's dress code?",
            "What is the company view on flexible working culture?",
            "Can I get reimbursement for my annual leave?",
            "Can employees claim bonuses through the reimbursement system?",
            "What is the company's remote work culture?",
            "What is the company's promotion policy?",
            "What is the company's performance review policy?",
            "What is the company's medical insurance policy?",
            "What is the deadline for submitting a claim?",
            "What is the processing time for a claim?",
            "What documents do I need for reimbursement?",
            "Can temporary employees receive the allowance?",
            "Can I use a personal device for work?",
            "Can I install software?",
        ):
            with self.subTest(question=question):
                self.assert_refusal(question)


if __name__ == "__main__":
    unittest.main()
