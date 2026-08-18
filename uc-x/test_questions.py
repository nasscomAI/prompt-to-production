"""
UC-X test harness - feeds the 7 README test questions to app.py's
answer_question and prints each question with its full answer, then
runs hedge/single-source/refusal compliance checks.

Usage:
    python test_questions.py
"""

from app import REFUSAL_TEMPLATE, answer_question, retrieve_documents

HEDGE_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]

DOC_NAMES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

TEST_QUESTIONS = [
    ("Can I carry forward unused annual leave?", "HR policy section 2.6"),
    ("Can I install Slack on my work laptop?", "IT policy section 2.3"),
    ("What is the home office equipment allowance?", "Finance section 3.1"),
    (
        "Can I use my personal phone for work files from home?",
        "Single-source IT answer OR clean refusal - must NOT blend",
    ),
    ("What is the company view on flexible working culture?", "Refusal template"),
    (
        "Can I claim DA and meal receipts on the same day?",
        "Finance section 2.6 - NO, explicitly prohibited",
    ),
    (
        "Who approves leave without pay?",
        "HR section 5.2 - Department Head AND HR Director, both required",
    ),
]


def main():
    index = retrieve_documents()
    answers = []
    for question, _expected in TEST_QUESTIONS:
        answer = answer_question(question, index)
        answers.append(answer)
        print(f"Q: {question}")
        print(f"A: {answer}")
        print("-" * 72)

    print()
    print("Compliance checks:")
    for i, (question, _expected) in enumerate(TEST_QUESTIONS):
        answer = answers[i]
        low = answer.lower()
        hedges = [h for h in HEDGE_PHRASES if h in low]
        status = "PASS" if not hedges else "FAIL"
        print(f"  [{status}] no hedging: {question}")

    for i, (question, _expected) in enumerate(TEST_QUESTIONS):
        answer = answers[i]
        if answer == REFUSAL_TEMPLATE:
            print(f"  [N/A ] refusal (template, no claim): {question}")
            continue
        cited = [d for d in DOC_NAMES if d in answer]
        status = "PASS" if len(cited) == 1 else "FAIL"
        print(f"  [{status}] single-source citation ({len(cited)} doc(s)): {question}")

    refusal = answers[4]
    exact = refusal == REFUSAL_TEMPLATE
    print(f"  [{'PASS' if exact else 'FAIL'}] refusal template used verbatim for Q5")


if __name__ == "__main__":
    main()
