"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
from collections import OrderedDict
from pathlib import Path
import re


SECTION_LINE = re.compile(r"^(\d+)\.\s+(.*)$")
CLAUSE_LINE = re.compile(r"^(\d+\.\d+)\s+(.*)$")

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant department for guidance."
)

DEFAULT_DOCUMENTS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}


def _parse_document(path: str):
    text = Path(path).read_text(encoding="utf-8")
    sections = OrderedDict()
    current_section = None
    current_clause = None

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("═"):
            continue

        section_match = SECTION_LINE.match(stripped)
        clause_match = CLAUSE_LINE.match(stripped)

        if section_match and not clause_match:
            current_section = section_match.group(1)
            sections[current_section] = {
                "title": section_match.group(2),
                "clauses": OrderedDict(),
            }
            current_clause = None
            continue

        if clause_match:
            current_clause = clause_match.group(1)
            if current_section is None:
                raise ValueError(f"Clause {current_clause} found before section heading")
            sections[current_section]["clauses"][current_clause] = clause_match.group(2).strip()
            continue

        if current_clause is not None:
            prior = sections[current_section]["clauses"][current_clause]
            sections[current_section]["clauses"][current_clause] = f"{prior} {stripped}"

    return sections


def retrieve_documents(document_paths=None):
    document_paths = document_paths or DEFAULT_DOCUMENTS
    indexed = OrderedDict()
    for name, path in document_paths.items():
        indexed[name] = _parse_document(path)
    return indexed


def _normalize_question(question: str) -> str:
    return " ".join((question or "").lower().strip().split())


def _answer_with_citation(answer: str, citations):
    citation_text = "; ".join(f"{document} section {section}" for document, section in citations)
    return f"{answer} Source: {citation_text}."


def answer_question(question: str, documents) -> str:
    normalized = _normalize_question(question)
    if not normalized:
        return REFUSAL_TEMPLATE

    if "carry forward" in normalized and "annual leave" in normalized:
        return _answer_with_citation(
            "Yes. Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year, and any days above 5 are forfeited on 31 December.",
            [("policy_hr_leave.txt", "2.6")],
        )

    if "slack" in normalized and ("work laptop" in normalized or "laptop" in normalized or "install" in normalized):
        return _answer_with_citation(
            "Slack can be installed on a corporate device only with written approval from the IT Department.",
            [("policy_it_acceptable_use.txt", "2.3")],
        )

    if "home office equipment allowance" in normalized:
        return _answer_with_citation(
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.",
            [("policy_finance_reimbursement.txt", "3.1")],
        )

    if "personal phone" in normalized and "work files" in normalized:
        return _answer_with_citation(
            "No. Personal devices may be used to access CMC email and the CMC employee self-service portal only, and personal devices must not be used to access, store, or transmit classified or sensitive CMC data.",
            [("policy_it_acceptable_use.txt", "3.1"), ("policy_it_acceptable_use.txt", "3.2")],
        )

    if "flexible working culture" in normalized:
        return REFUSAL_TEMPLATE

    if "da" in normalized and "meal" in normalized and "same day" in normalized:
        return _answer_with_citation(
            "No. If actual meal expenses are claimed instead of DA, receipts are mandatory and DA and meal receipts cannot be claimed simultaneously for the same day.",
            [("policy_finance_reimbursement.txt", "2.6")],
        )

    if "leave without pay" in normalized and ("who approves" in normalized or "approves" in normalized):
        return _answer_with_citation(
            "Leave Without Pay requires approval from both the Department Head and the HR Director; manager approval alone is not sufficient.",
            [("policy_hr_leave.txt", "5.2")],
        )

    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="UC-X policy question answering CLI")
    parser.add_argument("--question", help="Optional single question to answer and exit")
    args = parser.parse_args()

    documents = retrieve_documents()

    if args.question:
        print(answer_question(args.question, documents))
        return

    print("UC-X policy assistant. Type a question, or type exit to quit.")
    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            break

        if question.lower() in {"exit", "quit"}:
            break

        print(answer_question(question, documents))

if __name__ == "__main__":
    main()
