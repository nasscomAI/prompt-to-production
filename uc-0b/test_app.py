import unittest
import importlib.util
import os


def load_module():
    here = os.path.dirname(__file__)
    path = os.path.join(here, "app.py")
    spec = importlib.util.spec_from_file_location("uc0b_app", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestPolicyPreservation(unittest.TestCase):
    def setUp(self):
        # path relative to repo
        self.path = os.path.join("data", "policy-documents", "policy_hr_leave.txt")

    def test_critical_clauses_present_and_exact(self):
        app_mod = load_module()
        clauses = app_mod.retrieve_policy(self.path)
        expected = {
            "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
            "2.4": "Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.",
            "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
            "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
            "2.7": "Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.",
            "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
            "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
            "5.2": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.",
            "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
            "7.2": "Leave encashment during service is not permitted under any circumstances.",
        }

        missing = [k for k in expected.keys() if k not in clauses]
        self.assertEqual(missing, [], f"Missing expected clauses: {missing}")
        for k, v in expected.items():
            self.assertEqual(clauses[k], v)


if __name__ == "__main__":
    unittest.main()
