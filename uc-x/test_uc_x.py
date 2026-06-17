from pathlib import Path
import uc_x.app as app


DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "policy-documents"


def setup_index():
    files = [
        DATA_DIR / "policy_hr_leave.txt",
        DATA_DIR / "policy_it_acceptable_use.txt",
        DATA_DIR / "policy_finance_reimbursement.txt",
    ]
    return app.retrieve_documents([str(p) for p in files])


def test_carry_forward_leave():
    idx = setup_index()
    resp = app.answer_question("Can I carry forward unused annual leave?", idx)
    assert resp["citation"]["document"] == "policy_hr_leave.txt"
    assert resp["citation"]["section"] == "2.6"
    assert "carry forward a maximum of 5" in resp["answer_text"]


def test_install_slack():
    idx = setup_index()
    resp = app.answer_question("Can I install Slack on my work laptop?", idx)
    assert resp["citation"]["document"] == "policy_it_acceptable_use.txt"
    assert resp["citation"]["section"] == "2.3"
    assert "must not install software on corporate devices without written approval" in resp["answer_text"] or "must not install software" in resp["answer_text"]


def test_home_office_allowance():
    idx = setup_index()
    resp = app.answer_question("What is the home office equipment allowance?", idx)
    assert resp["citation"]["document"] == "policy_finance_reimbursement.txt"
    assert resp["citation"]["section"] == "3.1"
    assert "Rs 8,000" in resp["answer_text"]


def test_personal_phone_question_single_source_or_refusal():
    idx = setup_index()
    resp = app.answer_question("Can I use my personal phone for work files from home?", idx)
    # Must be single-source IT (3.1) or refusal template
    if resp["citation"]:
        assert resp["citation"]["document"] == "policy_it_acceptable_use.txt"
        assert resp["citation"]["section"] == "3.1"
        assert "email" in resp["answer_text"].lower() or "employee self-service" in resp["answer_text"].lower()
    else:
        assert resp["answer_text"] == app.REFUSAL_TEMPLATE


def test_flexible_working_refusal():
    idx = setup_index()
    resp = app.answer_question("What is the company view on flexible working culture?", idx)
    assert resp["answer_text"] == app.REFUSAL_TEMPLATE


def test_da_and_meal_receipts():
    idx = setup_index()
    resp = app.answer_question("Can I claim DA and meal receipts on the same day?", idx)
    assert resp["citation"]["document"] == "policy_finance_reimbursement.txt"
    assert resp["citation"]["section"] == "2.6"
    assert "DA and meal receipts cannot be claimed simultaneously" in resp["answer_text"] or "cannot be claimed simultaneously" in resp["answer_text"]


def test_who_approves_lwp():
    idx = setup_index()
    resp = app.answer_question("Who approves leave without pay?", idx)
    assert resp["citation"]["document"] == "policy_hr_leave.txt"
    assert resp["citation"]["section"] == "5.2"
    assert "Department Head" in resp["answer_text"] and "HR Director" in resp["answer_text"]
import os
from uc_x import app as uc_app


ROOT = os.path.join(os.path.dirname(__file__), "..")
DOCS = [
    os.path.join(ROOT, "data", "policy-documents", "policy_hr_leave.txt"),
    os.path.join(ROOT, "data", "policy-documents", "policy_it_acceptable_use.txt"),
    os.path.join(ROOT, "data", "policy-documents", "policy_finance_reimbursement.txt"),
]

REFUSAL = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)


def setup_index():
    # use file paths relative to repo root
    return uc_app.retrieve_documents(DOCS)


def test_annual_leave_carry_forward():
    idx = setup_index()
    out = uc_app.answer_question("Can I carry forward unused annual leave?", idx, REFUSAL)
    assert out["citation"]["document"].endswith("policy_hr_leave.txt")
    assert out["citation"]["section"] == "2.6"
    assert "5" in out["answer_text"] and "31 December" in out["answer_text"] or "forfeited" in out["answer_text"]


def test_install_slack_on_work_laptop():
    idx = setup_index()
    out = uc_app.answer_question("Can I install Slack on my work laptop?", idx, REFUSAL)
    assert out["citation"]["document"].endswith("policy_it_acceptable_use.txt")
    assert out["citation"]["section"] == "2.3"
    assert "written approval" in out["answer_text"] or "approval from the IT Department" in out["answer_text"]


def test_home_office_equipment_allowance():
    idx = setup_index()
    out = uc_app.answer_question("What is the home office equipment allowance?", idx, REFUSAL)
    assert out["citation"]["document"].endswith("policy_finance_reimbursement.txt")
    assert out["citation"]["section"] == "3.1"
    assert "Rs 8,000" in out["answer_text"] or "8000" in out["answer_text"]


def test_personal_phone_for_work_files():
    idx = setup_index()
    out = uc_app.answer_question("Can I use my personal phone for work files from home?", idx, REFUSAL)
    # Must be single-source IT (3.1) OR refusal. Here we expect IT 3.1 which restricts to email + portal only
    if out["answer_text"] == REFUSAL:
        assert out["citation"]["document"] is None
    else:
        assert out["citation"]["document"].endswith("policy_it_acceptable_use.txt")
        assert out["citation"]["section"] == "3.1"
        assert "email" in out["answer_text"].lower() and "self-service portal" in out["answer_text"].lower()


def test_flexible_working_view_refusal():
    idx = setup_index()
    out = uc_app.answer_question("What is the company view on flexible working culture?", idx, REFUSAL)
    assert out["answer_text"] == REFUSAL


def test_da_and_meal_receipts():
    idx = setup_index()
    out = uc_app.answer_question("Can I claim DA and meal receipts on the same day?", idx, REFUSAL)
    assert out["citation"]["document"].endswith("policy_finance_reimbursement.txt")
    assert out["citation"]["section"] == "2.6"
    assert "cannot be claimed" in out["answer_text"] or "cannot be claimed simultaneously" in out["answer_text"] or "cannot" in out["answer_text"].lower()


def test_who_approves_lwp():
    idx = setup_index()
    out = uc_app.answer_question("Who approves leave without pay?", idx, REFUSAL)
    assert out["citation"]["document"].endswith("policy_hr_leave.txt")
    assert out["citation"]["section"] == "5.2"
    assert "Department Head" in out["answer_text"] and "HR Director" in out["answer_text"]
