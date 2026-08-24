"""
UC-X Validation Script
Runs all 7 test questions against app.py's answer_question() logic.
Checks: single-source enforcement, cross-document blending, refusal template.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'uc-x'))

# Import the logic directly
import importlib.util
spec = importlib.util.spec_from_file_location("app", r"c:\workspace\prompt-to-production\uc-x\app.py")
app_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_mod)

REFUSAL_MARKER = "This question is not covered"
HEDGING = ["while not explicitly covered","typically","generally understood",
           "it is common practice","generally","usually","may imply"]

TEST_CASES = [
    {
        "id": "Q1",
        "question": "Can I carry forward unused annual leave?",
        "expect_source": "policy_hr_leave.txt",
        "expect_refusal": False,
        "must_contain": ["5", "carry", "forfeit"],
    },
    {
        "id": "Q2",
        "question": "Can I install Slack on my work laptop?",
        "expect_source": "policy_it_acceptable_use.txt",
        "expect_refusal": False,
        "must_contain": ["approval", "written"],
    },
    {
        "id": "Q3",
        "question": "What is the home office equipment allowance?",
        "expect_source": "policy_finance_reimbursement.txt",
        "expect_refusal": False,
        "must_contain": ["8,000", "8000"],
    },
    {
        "id": "Q4 (CROSS-DOC TRAP)",
        "question": "Can I use my personal phone to access work files when working from home?",
        "expect_source": None,   # Must refuse or single-source IT only
        "expect_refusal": None,  # acceptable: refusal OR single-source (IT only)
        "must_contain": [],
        "must_not_blend": True,
    },
    {
        "id": "Q5",
        "question": "What is the company view on flexible working culture?",
        "expect_source": None,
        "expect_refusal": True,
        "must_contain": [],
    },
    {
        "id": "Q6",
        "question": "Can I claim DA and meal receipts on the same day?",
        "expect_source": "policy_finance_reimbursement.txt",
        "expect_refusal": False,
        "must_contain": ["no", "not", "prohibited", "cannot"],
    },
    {
        "id": "Q7",
        "question": "Who approves leave without pay?",
        "expect_source": "policy_hr_leave.txt",
        "expect_refusal": False,
        "must_contain": ["department head", "hr director"],
    },
]

docs = app_mod.load_documents()

violations = []
ambiguity_failures = []

print("=" * 70)
print("UC-X VALIDATION — 7 Test Questions")
print("=" * 70)

for tc in TEST_CASES:
    answer, source_doc, section = app_mod.answer_question(tc["question"], docs)
    is_refusal = (REFUSAL_MARKER in answer)
    answer_lower = answer.lower()

    status_parts = []
    failed = False

    # 1. Refusal check
    if tc["expect_refusal"] is True and not is_refusal:
        status_parts.append("❌ Should have refused but answered")
        violations.append(f"{tc['id']}: Should have refused")
        failed = True
    elif tc["expect_refusal"] is False and is_refusal:
        status_parts.append("❌ Should have answered but refused")
        violations.append(f"{tc['id']}: Incorrectly refused")
        failed = True

    # 2. Source check (when exact source expected)
    if tc.get("expect_source") and not is_refusal:
        if source_doc != tc["expect_source"]:
            status_parts.append(f"❌ Wrong source: got '{source_doc}' expected '{tc['expect_source']}'")
            violations.append(f"{tc['id']}: Wrong source doc")
            failed = True

    # 3. Content check
    if tc.get("must_contain") and not is_refusal:
        for keyword in tc["must_contain"]:
            if keyword.lower() not in answer_lower:
                status_parts.append(f"❌ Missing keyword: '{keyword}'")
                violations.append(f"{tc['id']}: Missing keyword '{keyword}'")
                failed = True

    # 4. Cross-document blend check (Q4)
    if tc.get("must_not_blend") and not is_refusal:
        # If it mentions content from multiple docs, it's a blend
        hr_signal = "annual leave" in answer_lower or "manager" in answer_lower
        it_signal = "personal device" in answer_lower or "email" in answer_lower or "portal" in answer_lower
        finance_signal = "reimbursement" in answer_lower or "allowance" in answer_lower
        signals = sum([hr_signal, it_signal, finance_signal])
        if signals > 1:
            status_parts.append("❌ CROSS-DOCUMENT BLEND DETECTED")
            ambiguity_failures.append(f"{tc['id']}: blend across {signals} docs")
            failed = True

    # 5. Hedging check
    for phrase in HEDGING:
        if phrase in answer_lower:
            status_parts.append(f"❌ Hedging phrase: '{phrase}'")
            violations.append(f"{tc['id']}: Hedging phrase '{phrase}'")
            failed = True

    result = "✅ PASS" if not failed else "FAIL"
    print(f"\n{tc['id']} — {result}")
    print(f"  Q: {tc['question']}")
    print(f"  Source: {source_doc or '(refusal)'}")
    print(f"  Refusal: {is_refusal}")
    if status_parts:
        for s in status_parts:
            print(f"  {s}")
    print(f"  Answer preview: {answer[:120].strip()!r}")

print("\n" + "=" * 70)
print("SUMMARY")
print(f"  Violations:        {violations or 'None'}")
print(f"  Ambiguity failures: {ambiguity_failures or 'None'}")
if not violations and not ambiguity_failures:
    print("  ✅ ALL TESTS PASSED")
else:
    print(f"  ❌ {len(violations) + len(ambiguity_failures)} total issues")
