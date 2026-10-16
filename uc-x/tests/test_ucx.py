import os
import pytest
import importlib.util

# load uc-x/app.py as a module by path (hyphen in folder prevents normal import)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_PATH = os.path.join(ROOT_DIR, "app.py")
spec = importlib.util.spec_from_file_location("ucx_app", APP_PATH)
ucx_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ucx_app)


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(ROOT, "data", "policy-documents")


@pytest.fixture(scope="module")
def index():
    files = [
        os.path.join(DATA_DIR, "policy_hr_leave.txt"),
        os.path.join(DATA_DIR, "policy_it_acceptable_use.txt"),
        os.path.join(DATA_DIR, "policy_finance_reimbursement.txt"),
    ]
    index, errors = ucx_app.retrieve_documents(files)
    assert not errors
    return index


def test_retrieve_documents_contains_files(index):
    assert "policy_hr_leave.txt" in index
    assert "policy_it_acceptable_use.txt" in index
    assert "policy_finance_reimbursement.txt" in index


def test_answer_question_single_source(index):
    # This question should be answered from IT policy 2.3
    q = "Can I install software on my work laptop?"
    res = ucx_app.answer_question(index, q)
    assert "answer" in res
    assert "citation" in res
    assert res["citation"]["filename"] == "policy_it_acceptable_use.txt"
    # should reference install/corporate devices language from IT policy
    assert "install" in res["answer"].lower() or "corporate" in res["answer"].lower()


def test_answer_question_refusal(index):
    q = "Can I use my personal phone to access work files when working from home?"
    res = ucx_app.answer_question(index, q)
    assert "refusal" in res
    assert ucx_app.REFUSAL_TEMPLATE in res["refusal"]
