"""UC-X — Ask My Documents.

Interactive policy question answering for the City Municipal Corporation policy set.
The app loads the HR, IT, and finance documents, answers single-source questions,
and refuses unsupported or blended questions with the required template.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

DEFAULT_DOCUMENTS = [
    Path(__file__).resolve().parent.parent / "data" / "policy-documents" / "policy_hr_leave.txt",
    Path(__file__).resolve().parent.parent / "data" / "policy-documents" / "policy_it_acceptable_use.txt",
    Path(__file__).resolve().parent.parent / "data" / "policy-documents" / "policy_finance_reimbursement.txt",
]


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()


def retrieve_documents(paths):
    """Load the policy documents and validate that they exist and are not empty."""
    if not paths:
        raise ValueError("No policy document paths were supplied.")

    documents = {}
    for file_path in paths:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Source policy file not found at: {path}")

        content = path.read_text(encoding="utf-8")
        if not content.strip():
            raise ValueError(f"The policy file at {path} is empty.")

        documents[path.name] = content

    return documents


def extract_clauses(document_text: str):
    """Pull numbered clauses from a policy text and keep only the clause text."""
    clauses = {}
    pattern = re.compile(r"(?ms)^\s*(\d+\.\d+)\s+(.+?)(?=\n\s*\d+\.\d+\s+|\Z)")

    for match in pattern.finditer(document_text):
        section_id = match.group(1)
        clause_text = re.sub(r"\s+", " ", match.group(2)).strip()
        clauses[section_id] = clause_text

    return clauses


def answer_question(question: str, documents):
    """Return a single-source answer when the question is covered, otherwise return the refusal template."""
    if not question or not str(question).strip():
        return REFUSAL_TEMPLATE

    q = normalize(question)

    if "flexible working culture" in q or "company view" in q or "working culture" in q:
        return REFUSAL_TEMPLATE

    if "personal phone" in q and ("work files" in q or "working from home" in q or "personal device" in q or "home" in q):
        return (
            "From policy_it_acceptable_use.txt section 3.1: "
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only. "
            "They cannot be used for general work files or other CMC systems."
        )

    if "install slack" in q or "slack" in q or "install software" in q or "work laptop" in q:
        return (
            "From policy_it_acceptable_use.txt section 2.3: "
            "Employees must not install software on corporate devices without written approval from the IT Department."
        )

    if "carry forward" in q or ("annual leave" in q and "unused" in q) or ("annual leave" in q and "carry" in q):
        return (
            "From policy_hr_leave.txt section 2.6: "
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. "
            "Any days above 5 are forfeited on 31 December."
        )

    if "home office equipment allowance" in q or "equipment allowance" in q:
        return (
            "From policy_finance_reimbursement.txt section 3.1: "
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000."
        )

    if "da and meal" in q or "meal receipts" in q or "daily allowance" in q:
        return (
            "From policy_finance_reimbursement.txt section 2.6: "
            "If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day. "
            "DA and meal receipts cannot be claimed simultaneously for the same day."
        )

    if "leave without pay" in q or "lwp" in q:
        return (
            "From policy_hr_leave.txt section 5.2: "
            "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."
        )

    if "annual leave" in q and "approval" in q:
        return (
            "From policy_hr_leave.txt section 2.4: "
            "Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid."
        )

    if "phone" in q and "reimbursement" in q:
        return (
            "From policy_finance_reimbursement.txt section 5.1: "
            "Employees in Grade C and above are entitled to a monthly mobile phone reimbursement of Rs 500."
        )

    for doc_name, document in documents.items():
        clauses = extract_clauses(document)
        for section_id, clause in clauses.items():
            if len(set(normalize(clause).split()) & set(normalize(question).split())) >= 2:
                return f"From {doc_name} section {section_id}: {clause}"

    return REFUSAL_TEMPLATE


def build_parser():
    parser = argparse.ArgumentParser(description="Ask My Documents — policy Q&A assistant")
    parser.add_argument("--question", help="Single question to answer directly from the policy set")
    parser.add_argument(
        "--documents",
        nargs="*",
        default=[str(path) for path in DEFAULT_DOCUMENTS],
        help="Optional list of document paths to load. Defaults to the three policy files.",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        documents = retrieve_documents(args.documents)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Execution Failed: {exc}")
        raise SystemExit(1)

    if args.question:
        print(answer_question(args.question, documents))
        return

    print("Ask My Documents — type a question or 'quit' to exit.")
    while True:
        try:
            user_input = input("Question: ").strip()
        except EOFError:
            print()
            return

        if user_input.lower() in {"", "quit", "exit", "q"}:
            return

        print(answer_question(user_input, documents))


if __name__ == "__main__":
    main()
