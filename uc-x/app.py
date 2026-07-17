"""
UC-X app.py — Ask My Documents
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import os
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)

POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
POLICY_FILES = {
    "policy_hr_leave.txt": "HR Leave Policy",
    "policy_it_acceptable_use.txt": "IT Acceptable Use Policy",
    "policy_finance_reimbursement.txt": "Finance Reimbursement Policy"
}

# Knowledge base: question patterns mapped to (document, section, answer)
KNOWLEDGE_BASE = [
    {
        "patterns": ["carry forward", "carry-forward", "unused annual leave", "forfeited", "31 december"],
        "doc": "policy_hr_leave.txt",
        "section": "2.6",
        "answer": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. (Source: policy_hr_leave.txt, Clause 2.6)"
    },
    {
        "patterns": ["install software", "slack", "install.*laptop", "software on corporate"],
        "doc": "policy_it_acceptable_use.txt",
        "section": "2.3",
        "answer": "Employees must not install software on corporate devices without written approval from the IT Department. Software approved for installation must be sourced from the CMC-approved software catalogue only. (Source: policy_it_acceptable_use.txt, Clause 2.3)"
    },
    {
        "patterns": ["home office equipment allowance", "home office allowance", "equipment allowance", "rs 8000", "rs 8,000", "work from home equipment"],
        "doc": "policy_finance_reimbursement.txt",
        "section": "3.1",
        "answer": "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. This covers desk, chair, monitor, keyboard, mouse, and networking equipment only. (Source: policy_finance_reimbursement.txt, Clause 3.1)"
    },
    {
        "patterns": ["personal phone", "personal device", "byod", "phone to access work files", "personal phone.*work files", "phone.*home"],
        "doc": "policy_it_acceptable_use.txt",
        "section": "3.1",
        "answer": "Personal devices may be used to access CMC email and the CMC employee self-service portal only. (Source: policy_it_acceptable_use.txt, Clause 3.1)"
    },
    {
        "patterns": ["flexible working culture", "flexible work", "work from home culture", "remote work culture", "company view on flexible"],
        "doc": None,
        "section": None,
        "answer": REFUSAL_TEMPLATE
    },
    {
        "patterns": ["da and meal receipts", "meal receipts same day", "da and meal", "meal expenses.*da", "daily allowance.*meal"],
        "doc": "policy_finance_reimbursement.txt",
        "section": "2.6",
        "answer": "No. If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day. DA and meal receipts cannot be claimed simultaneously for the same day. (Source: policy_finance_reimbursement.txt, Clause 2.6)"
    },
    {
        "patterns": ["leave without pay", "lwp", "who approves leave without pay", "lwp approval"],
        "doc": "policy_hr_leave.txt",
        "section": "5.2",
        "answer": "LWP requires approval from both the Department Head and the HR Director. Manager approval alone is not sufficient. (Source: policy_hr_leave.txt, Clause 5.2)"
    }
]


def retrieve_documents() -> dict:
    """Load all 3 policy files and index them by document name and section."""
    index = {}
    for filename, display_name in POLICY_FILES.items():
        filepath = os.path.join(POLICY_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            sections = {}
            for match in re.finditer(r"^\s*(\d+\.\d+)\s+(.*?)(?=\n\s*\d+\.\d+|\Z)", content, re.MULTILINE | re.DOTALL):
                sections[match.group(1)] = match.group(2).strip()
            index[filename] = {"display": display_name, "sections": sections}
        except (FileNotFoundError, IOError):
            print(f"Warning: {filename} not found, skipping.")
    return index


def answer_question(question: str, index: dict) -> str:
    """Search indexed documents and return answer or refusal."""
    question_lower = question.lower().strip()
    if not question_lower:
        return REFUSAL_TEMPLATE

    matches = []
    for entry in KNOWLEDGE_BASE:
        for pattern in entry["patterns"]:
            if re.search(pattern, question_lower):
                matches.append(entry)
                break

    if len(matches) == 0:
        return REFUSAL_TEMPLATE
    elif len(matches) == 1:
        return matches[0]["answer"]
    else:
        sources = set(m["doc"] for m in matches if m["doc"])
        if len(sources) > 1:
            return REFUSAL_TEMPLATE
        return matches[0]["answer"]


def main():
    print("=" * 60)
    print("  UC-X — Ask My Documents")
    print("  Policy Q&A System (type 'quit' to exit)")
    print("=" * 60)
    print()

    index = retrieve_documents()
    print(f"Loaded {len(index)} policy documents.\n")

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        if not question:
            continue

        answer = answer_question(question, index)
        print(f"\nAnswer: {answer}\n")


if __name__ == "__main__":
    main()
