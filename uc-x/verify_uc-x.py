"""
Verification Script for UC-X — Ask My Documents (CRAFT Self-Test)
Asserts prevention of cross-document blending, hedged hallucination, and condition dropping.
"""
import sys
from app import answer_question, retrieve_documents, FORBIDDEN_HEDGING, get_refusal_template


def test_knowledge_base():
    """Verify all 3 policy documents load and parse into structured sections."""
    kb = retrieve_documents()
    assert len(kb) == 3, f"Expected 3 documents, loaded {len(kb)}"
    assert "policy_hr_leave.txt" in kb
    assert "policy_it_acceptable_use.txt" in kb
    assert "policy_finance_reimbursement.txt" in kb

    for doc_name, data in kb.items():
        assert len(data["sections"]) > 0, f"No sections parsed in {doc_name}"


def test_7_core_questions():
    """Test the 7 required test questions from the UC-X specification."""
    kb = retrieve_documents()

    # Q1: Carry forward annual leave
    q1 = "Can I carry forward unused annual leave?"
    a1 = answer_question(q1, kb)
    assert "5" in a1 and "31 December" in a1, "Q1 missing 5-day cap or 31 Dec deadline"
    assert "policy_hr_leave.txt" in a1 and "2.6" in a1, "Q1 missing proper HR citation"

    # Q2: Install Slack on work laptop
    q2 = "Can I install Slack on my work laptop?"
    a2 = answer_question(q2, kb)
    assert "written approval" in a2.lower() or "it department" in a2.lower(), "Q2 missing IT approval requirement"
    assert "policy_it_acceptable_use.txt" in a2 and "2.3" in a2, "Q2 missing proper IT citation"

    # Q3: Home office allowance
    q3 = "What is the home office equipment allowance?"
    a3 = answer_question(q3, kb)
    assert "8,000" in a3, "Q3 missing Rs 8,000 allowance figure"
    assert "permanent" in a3.lower(), "Q3 dropped permanent WFH condition"
    assert "policy_finance_reimbursement.txt" in a3 and "3.1" in a3, "Q3 missing proper Finance citation"

    # Q4: Personal phone for work files (CRITICAL TRAP QUESTION - ZERO BLENDING)
    q4 = "Can I use my personal phone for work files from home?"
    a4 = answer_question(q4, kb)
    assert "policy_it_acceptable_use.txt" in a4, "Q4 must cite IT policy"
    assert "policy_hr_leave.txt" not in a4, "Cross-Document Blending Failure: Q4 blended HR and IT policies!"
    assert "email" in a4.lower() and "portal" in a4.lower(), "Q4 missing email/portal restriction"
    assert ("not" in a4.lower() or "prohibited" in a4.lower()), "Q4 gave false permission for work files"

    # Q5: Flexible working culture (OUT OF SCOPE - EXACT REFUSAL)
    q5 = "What is the company view on flexible working culture?"
    a5 = answer_question(q5, kb)
    refusal_prefix = (
        "This question is not covered in the available policy documents "
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt)."
    )
    assert refusal_prefix in a5, f"Q5 did not use exact mandatory refusal template: '{a5}'"

    # Q6: DA and meal receipts simultaneous claim
    q6 = "Can I claim DA and meal receipts on the same day?"
    a6 = answer_question(q6, kb)
    assert ("cannot" in a6.lower() or "not" in a6.lower() or "prohibited" in a6.lower()), "Q6 allowed simultaneous DA + meal receipts"
    assert "policy_finance_reimbursement.txt" in a6 and "2.6" in a6, "Q6 missing proper Finance citation"

    # Q7: Leave without pay approvers
    q7 = "Who approves leave without pay?"
    a7 = answer_question(q7, kb)
    assert "Department Head" in a7 and "HR Director" in a7, "Condition Drop Failure in Q7: Dropped dual approver requirement"
    assert "policy_hr_leave.txt" in a7 and "5.2" in a7, "Q7 missing proper HR citation"


def test_zero_hedging_and_mandatory_citations():
    """Verify no response contains prohibited hedging phrases and factual answers have citations."""
    kb = retrieve_documents()
    test_queries = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone for work files from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?",
        "How much is travel allowance?",
        "What are the rules for sick leave certificate?",
    ]

    for q in test_queries:
        resp = answer_question(q, kb)
        resp_lower = resp.lower()

        # Check hedging
        for hedge in FORBIDDEN_HEDGING:
            assert hedge not in resp_lower, (
                f"Hedged Hallucination Failure: Query '{q}' returned prohibited hedging phrase '{hedge}'"
            )

        # Check citation if not refusal
        if "not covered in the available policy documents" not in resp:
            assert "[Source:" in resp and ".txt" in resp and "Section" in resp, (
                f"Missing Citation Failure: Response for '{q}' lacks valid [Source: doc, Section ...] citation: '{resp}'"
            )


def run_all_checks():
    print("=" * 60)
    print("RUNNING UC-X SELF-TEST SUITE (CRAFT)")
    print("=" * 60)

    try:
        print("[1/3] Testing policy document retrieval and indexing...")
        test_knowledge_base()
        print("  --> PASS: All 3 policy documents parsed and indexed successfully.")

        print("[2/3] Testing all 7 test questions (Checking Cross-Doc Blending & Refusals)...")
        test_7_core_questions()
        print("  --> PASS: All 7 test questions handled correctly (Zero blending on Q4, exact refusal on Q5, dual-approvers on Q7).")

        print("[3/3] Testing zero hedged hallucination and mandatory source citations...")
        test_zero_hedging_and_mandatory_citations()
        print("  --> PASS: Zero hedging phrases detected and all factual claims properly cited.")

        print("=" * 60)
        print("ALL UC-X VERIFICATION CHECKS PASSED SUCCESSFULLY! (100% PASS)")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n❌ ASSERTION FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        return False


if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)
