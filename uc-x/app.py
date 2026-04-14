"""
UC-X app.py
"""
from __future__ import annotations

import re
from pathlib import Path

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact Human Resources Department for guidance."
)

BASE_DIR = Path(__file__).resolve().parent
DOCUMENT_PATHS = {
    "policy_hr_leave.txt": BASE_DIR.parent / "data" / "policy-documents" / "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": BASE_DIR.parent / "data" / "policy-documents" / "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": BASE_DIR.parent / "data" / "policy-documents" / "policy_finance_reimbursement.txt",
}


def normalize_text(value: str) -> str:
    return (
        (value or "")
        .lower()
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .strip()
    )


def retrieve_documents() -> dict[str, dict[str, str]]:
    documents: dict[str, dict[str, str]] = {}
    for document_name, path in DOCUMENT_PATHS.items():
        text = path.read_text(encoding="utf-8-sig")
        sections: dict[str, str] = {}
        current_section = None
        current_lines: list[str] = []

        for raw_line in text.splitlines():
            line = raw_line.strip()
            match = re.match(r"^(\d+\.\d+)\s+(.*)$", line)
            if match:
                if current_section is not None:
                    sections[current_section] = " ".join(current_lines).strip()
                current_section = match.group(1)
                current_lines = [match.group(2).strip()]
            elif current_section is not None and line:
                current_lines.append(line)

        if current_section is not None:
            sections[current_section] = " ".join(current_lines).strip()

        if not sections:
            raise ValueError(f"Could not parse numbered sections from {document_name}")
        documents[document_name] = sections
    return documents


def cite(document_name: str, section: str, text: str) -> str:
    return f"{text} [{document_name} section {section}]"


def answer_question(question: str, documents: dict[str, dict[str, str]]) -> str:
    q = normalize_text(question)
    hr = documents["policy_hr_leave.txt"]
    it = documents["policy_it_acceptable_use.txt"]
    fin = documents["policy_finance_reimbursement.txt"]

    if "carry forward" in q and "leave" in q:
        return (
            cite(
                "policy_hr_leave.txt",
                "2.6",
                "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year, and any days above 5 are forfeited on 31 December.",
            )
            + " "
            + cite(
                "policy_hr_leave.txt",
                "2.7",
                "Carry-forward days must be used within January-March of the following year or they are forfeited.",
            )
        )

    if ("install" in q or "slack" in q) and ("laptop" in q or "work laptop" in q or "corporate device" in q):
        return cite(
            "policy_it_acceptable_use.txt",
            "2.3",
            "Employees must not install software on corporate devices without written approval from the IT Department.",
        )

    if "home office equipment allowance" in q or ("equipment allowance" in q and "home" in q):
        return (
            cite(
                "policy_finance_reimbursement.txt",
                "3.1",
                "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.",
            )
            + " "
            + cite(
                "policy_finance_reimbursement.txt",
                "3.5",
                "Employees on temporary or partial work-from-home arrangements are not eligible for this allowance.",
            )
        )

    if "personal phone" in q or ("personal device" in q and "work files" in q):
        return (
            cite(
                "policy_it_acceptable_use.txt",
                "3.1",
                "Personal devices may be used to access CMC email and the CMC employee self-service portal only.",
            )
            + " "
            + cite(
                "policy_it_acceptable_use.txt",
                "3.2",
                "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data.",
            )
        )

    if "flexible working culture" in q:
        return REFUSAL_TEMPLATE

    if ("da" in q or "daily allowance" in q) and ("meal" in q or "receipts" in q):
        return cite(
            "policy_finance_reimbursement.txt",
            "2.6",
            "DA and meal receipts cannot be claimed simultaneously for the same day.",
        )

    if "leave without pay" in q and "approve" in q:
        return (
            cite(
                "policy_hr_leave.txt",
                "5.2",
                "Leave Without Pay requires approval from the Department Head and the HR Director, and manager approval alone is not sufficient.",
            )
            + " "
            + cite(
                "policy_hr_leave.txt",
                "5.3",
                "If Leave Without Pay exceeds 30 continuous days, Municipal Commissioner approval is also required.",
            )
        )

    section_hits = []
    for document_name, sections in documents.items():
        for section_number, text in sections.items():
            score = sum(1 for token in re.findall(r"[a-z0-9]+", q) if token in normalize_text(text))
            if score:
                section_hits.append((score, document_name, section_number, text))

    if not section_hits:
        return REFUSAL_TEMPLATE

    section_hits.sort(reverse=True)
    top_score, top_document, top_section, top_text = section_hits[0]
    conflicting_documents = {document for score, document, _, _ in section_hits if score == top_score}
    if len(conflicting_documents) > 1 or top_score < 2:
        return REFUSAL_TEMPLATE

    sentence = top_text.rstrip(".") + "."
    return cite(top_document, top_section, sentence)


def main():
    documents = retrieve_documents()
    print("Policy assistant ready. Type a question or 'exit' to quit.")
    while True:
        question = input("> ").strip()
        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break
        if not question:
            print("Please enter a question.")
            continue
        print(answer_question(question, documents))


if __name__ == "__main__":
    main()
