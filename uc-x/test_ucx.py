import unittest

from app import REFUSAL_TEMPLATE, answer_question, default_policy_dir, load_policy_sections


class TestUCXPolicyQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sections = load_policy_sections(default_policy_dir())

    def ask(self, question: str) -> str:
        return answer_question(question, self.sections)

    def test_q1_carry_forward(self):
        result = self.ask("Can I carry forward unused annual leave?")
        self.assertIn("policy_hr_leave.txt, section 2.6", result)
        self.assertIn("maximum of 5", result)
        self.assertIn("forfeited on 31 December", result)

    def test_q2_install_slack(self):
        result = self.ask("Can I install Slack on my work laptop?")
        self.assertIn("policy_it_acceptable_use.txt, section 2.3", result)
        self.assertIn("must not install software", result)
        self.assertIn("written approval", result)

    def test_q3_home_office_allowance(self):
        result = self.ask("What is the home office equipment allowance?")
        self.assertIn("policy_finance_reimbursement.txt, section 3.1", result)
        self.assertIn("one-time home office equipment allowance", result)
        self.assertIn("Rs 8,000", result)

    def test_q4_personal_phone_trap(self):
        result = self.ask("Can I use my personal phone for work files from home?")
        self.assertEqual(REFUSAL_TEMPLATE, result)

    def test_q5_flexible_working_culture(self):
        result = self.ask("What is the company view on flexible working culture?")
        self.assertEqual(REFUSAL_TEMPLATE, result)

    def test_q6_da_and_meal_same_day(self):
        result = self.ask("Can I claim DA and meal receipts on the same day?")
        self.assertIn("policy_finance_reimbursement.txt, section 2.6", result)
        self.assertIn("cannot be claimed simultaneously for the same day", result)

    def test_q7_lwp_approval(self):
        result = self.ask("Who approves leave without pay?")
        self.assertIn("policy_hr_leave.txt, section 5.2", result)
        self.assertIn("Department Head", result)
        self.assertIn("HR Director", result)


if __name__ == "__main__":
    unittest.main()
