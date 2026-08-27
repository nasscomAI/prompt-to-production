"""
Result validator for UC-X — tests all 7 questions from README.md.
"""
import sys
sys.path.insert(0, ".")

from app import DOC_PATHS, REFUSAL_TEMPLATE, parse_document, build_index, answer_question

QUESTIONS = [
    {
        "question": "Can I carry forward unused annual leave?",
        "expect": "answer",
        "doc": "policy_hr_leave.txt",
        "section": "2.6",
        "checks": ["5", "carry", "forfeit", "31 December"],
    },
    {
        "question": "Can I install Slack on my work laptop?",
        "expect": "answer",
        "doc": "policy_it_acceptable_use.txt",
        "section": "2.3",
        "checks": ["install", "software", "written approval", "IT Department"],
    },
    {
        "question": "What is the home office equipment allowance?",
        "expect": "answer",
        "doc": "policy_finance_reimbursement.txt",
        "section": "3.1",
        "checks": ["8,000", "one-time", "permanent"],
    },
    {
        "question": "Can I use my personal phone to access work files when working from home?",
        "expect": "answer",
        "single_source": True,
        "doc": "policy_it_acceptable_use.txt",
        "section": "3.1",
        "checks": ["email", "portal", "only"],
        "blend_check": True,
        "forbidden_doc": "policy_hr_leave.txt",
    },
    {
        "question": "What is the company view on flexible working culture?",
        "expect": "refusal",
        "checks": ["not covered", "contact [relevant team]"],
    },
    {
        "question": "Can I claim DA and meal receipts on the same day?",
        "expect": "answer",
        "doc": "policy_finance_reimbursement.txt",
        "section": "2.6",
        "checks": ["DA", "meal", "cannot", "same day"],
    },
    {
        "question": "Who approves leave without pay?",
        "expect": "answer",
        "doc": "policy_hr_leave.txt",
        "section": "5.2",
        "checks": ["Department Head", "HR Director"],
    },
]

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "while not explicitly stated",
]


def validate():
    print("Loading documents and building index...", file=sys.stderr)
    all_sections = []
    for p in DOC_PATHS:
        all_sections.extend(parse_document(p))
    sections, idf = build_index(all_sections)
    print(f"Index built: {len(sections)} sections.\n", file=sys.stderr)

    errors = 0
    total = len(QUESTIONS)

    for q in QUESTIONS:
        question = q["question"]
        answer = answer_question(question, sections, idf)
        label = f"[{q['question'][:50]}]"

        for phrase in HEDGING_PHRASES:
            if phrase in answer.lower():
                print(f"FAIL {label}: Contains hedging phrase '{phrase}'")
                errors += 1

        if q["expect"] == "refusal":
            if answer.strip() == REFUSAL_TEMPLATE.strip():
                print(f"PASS {label}: Correctly refused")
            else:
                print(f"FAIL {label}: Expected refusal template, got:\n  {answer[:120]}")
                errors += 1
        else:
            expected_doc = q["doc"]
            expected_section = q["section"]

            if expected_doc not in answer:
                print(f"FAIL {label}: Missing document '{expected_doc}'")
                errors += 1
            else:
                print(f"PASS {label}: Cites '{expected_doc}'")

            if expected_section not in answer:
                print(f"FAIL {label}: Missing section '{expected_section}'")
                errors += 1
            else:
                print(f"PASS {label}: Cites Section {expected_section}")

            for check in q.get("checks", []):
                if check.lower() not in answer.lower():
                    print(f"  FAIL {label}: Expected content '{check}' not found")
                    errors += 1

            if q.get("single_source"):
                forbidden = q.get("forbidden_doc")
                if forbidden and forbidden in answer:
                    print(f"FAIL {label}: Blended from {forbidden} — must be single-source")
                    errors += 1
                elif forbidden:
                    print(f"PASS {label}: Single-source (no blend from {forbidden})")

    print(f"\nResults: {total - errors}/{total} checks passed, {errors} failed.")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(validate())
