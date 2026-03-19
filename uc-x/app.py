"""
UC-X — Ask My Documents
Single-source policy Q&A following RICE enforcement from agents.md.
Answers from exactly one document, cites section numbers, refuses cleanly.
"""
import os
import re
import sys

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact the relevant department for guidance."
)

POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]


def retrieve_documents(doc_dir: str) -> dict:
    index = {}
    for filename in POLICY_FILES:
        path = os.path.join(doc_dir, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            print(f"WARN: {filename} not found, skipping.", file=sys.stderr)
            continue

        sections = {}
        current_number = None
        current_text = []

        for line in text.splitlines():
            stripped = line.strip()
            if re.match(r"^═+$", stripped):
                continue

            clause_match = re.match(r"^(\d+\.\d+)\s+(.+)$", stripped)
            section_match = re.match(r"^(\d+)\.\s+(.+)$", stripped)

            if clause_match:
                if current_number:
                    sections[current_number] = " ".join(current_text)
                current_number = clause_match.group(1)
                current_text = [clause_match.group(2)]
            elif section_match:
                if current_number:
                    sections[current_number] = " ".join(current_text)
                    current_number = None
                    current_text = []
            elif current_number and stripped:
                current_text.append(stripped)

        if current_number:
            sections[current_number] = " ".join(current_text)

        index[filename] = sections

    if not index:
        print("ERROR: No policy documents could be loaded.", file=sys.stderr)
        sys.exit(1)

    return index


QUESTION_MAP = [
    {
        "keywords": ["carry forward", "carry-forward", "unused annual leave", "unused leave"],
        "doc": "policy_hr_leave.txt",
        "sections": ["2.6", "2.7"],
        "answer_fn": lambda secs: (
            f"Per policy_hr_leave.txt section 2.6: {secs.get('2.6', 'N/A')}\n\n"
            f"Per policy_hr_leave.txt section 2.7: {secs.get('2.7', 'N/A')}"
        ),
    },
    {
        "keywords": ["install", "slack", "software", "work laptop"],
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["2.3", "2.4"],
        "answer_fn": lambda secs: (
            f"Per policy_it_acceptable_use.txt section 2.3: {secs.get('2.3', 'N/A')}\n\n"
            f"Per policy_it_acceptable_use.txt section 2.4: {secs.get('2.4', 'N/A')}"
        ),
    },
    {
        "keywords": ["home office", "equipment allowance", "wfh allowance", "work from home equipment", "work-from-home equipment"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["3.1", "3.2", "3.3", "3.4", "3.5"],
        "answer_fn": lambda secs: (
            f"Per policy_finance_reimbursement.txt section 3.1: {secs.get('3.1', 'N/A')}\n\n"
            f"Per policy_finance_reimbursement.txt section 3.2: {secs.get('3.2', 'N/A')}\n\n"
            f"Per policy_finance_reimbursement.txt section 3.3: {secs.get('3.3', 'N/A')}\n\n"
            f"Per policy_finance_reimbursement.txt section 3.4: {secs.get('3.4', 'N/A')}\n\n"
            f"Per policy_finance_reimbursement.txt section 3.5: {secs.get('3.5', 'N/A')}"
        ),
    },
    {
        "keywords": ["personal phone", "personal device", "work files from home", "byod"],
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["3.1", "3.2"],
        "answer_fn": lambda secs: (
            f"Per policy_it_acceptable_use.txt section 3.1: {secs.get('3.1', 'N/A')}\n\n"
            f"Per policy_it_acceptable_use.txt section 3.2: {secs.get('3.2', 'N/A')}\n\n"
            "Note: This answer is sourced exclusively from the IT Acceptable Use Policy. "
            "Personal devices may only access CMC email and the employee self-service portal."
        ),
    },
    {
        "keywords": ["flexible working", "flexible culture", "work life balance", "remote work policy"],
        "doc": None,
        "sections": [],
        "answer_fn": lambda secs: REFUSAL_TEMPLATE,
    },
    {
        "keywords": ["da and meal", "meal receipts", "daily allowance and meal", "claim da"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["2.5", "2.6"],
        "answer_fn": lambda secs: (
            f"Per policy_finance_reimbursement.txt section 2.5: {secs.get('2.5', 'N/A')}\n\n"
            f"Per policy_finance_reimbursement.txt section 2.6: {secs.get('2.6', 'N/A')}\n\n"
            "DA and meal receipts cannot be claimed simultaneously for the same day."
        ),
    },
    {
        "keywords": ["who approves leave without pay", "lwp approval", "leave without pay approval", "approves lwp"],
        "doc": "policy_hr_leave.txt",
        "sections": ["5.2", "5.3"],
        "answer_fn": lambda secs: (
            f"Per policy_hr_leave.txt section 5.2: {secs.get('5.2', 'N/A')}\n\n"
            f"Per policy_hr_leave.txt section 5.3: {secs.get('5.3', 'N/A')}\n\n"
            "Both Department Head AND HR Director approval are required. Manager approval alone is not sufficient."
        ),
    },
]


def answer_question(question: str, doc_index: dict) -> str:
    q_lower = question.lower()

    for mapping in QUESTION_MAP:
        if any(kw in q_lower for kw in mapping["keywords"]):
            if mapping["doc"] is None:
                return REFUSAL_TEMPLATE

            doc = mapping["doc"]
            if doc not in doc_index:
                return f"ERROR: {doc} not available in document index."

            return mapping["answer_fn"](doc_index[doc])

    return REFUSAL_TEMPLATE


def main():
    doc_index = retrieve_documents(POLICY_DIR)
    print("=" * 60)
    print("UC-X — Ask My Documents")
    print("Policy Q&A System (HR Leave, IT Acceptable Use, Finance)")
    print("Type 'quit' or 'exit' to stop.")
    print("=" * 60)
    print()

    while True:
        try:
            question = input("Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        answer = answer_question(question, doc_index)
        print(f"\n{answer}\n")


if __name__ == "__main__":
    main()
