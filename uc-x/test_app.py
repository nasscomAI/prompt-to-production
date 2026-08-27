from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import REFUSAL_TEMPLATE, answer_question


def test_install_question_uses_it_policy():
    answer = answer_question("Can I install Slack on my work laptop?")
    assert "policy_it_acceptable_use.txt" in answer
    assert "section 2.3" in answer


def test_unknown_question_uses_refusal_template():
    answer = answer_question("What is the company view on flexible working culture?")
    assert answer == REFUSAL_TEMPLATE


def test_leave_without_pay_question_uses_hr_policy():
    answer = answer_question("Who approves leave without pay?")
    assert "policy_hr_leave.txt" in answer
    assert "section 5.2" in answer
