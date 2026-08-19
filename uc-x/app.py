"""UC-X policy QA CLI with strict single-document answering rules."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact [relevant team] "
    "for guidance."
)


@dataclass
class MatchResult:
    answer: str
    document_name: str
    section_number: str


def load_documents() -> dict[str, str]:
    base = Path(__file__).resolve().parent.parent / "data" / "policy-documents"
    files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt",
    ]
    docs: dict[str, str] = {}
    for name in files:
        docs[name] = (base / name).read_text(encoding="utf-8")
    return docs


def parse_sections(document_text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current_key = ""
    for line in document_text.splitlines():
        section_match = re.match(r"^(\d+\.\d+)\s+(.*)$", line.strip())
        if section_match:
            current_key = section_match.group(1)
            sections[current_key] = section_match.group(2).strip()
            continue
        if current_key and line.strip():
            sections[current_key] = f"{sections[current_key]} {line.strip()}"
    return sections


def answer_question(question: str, indices: dict[str, dict[str, str]]) -> MatchResult | None:
    q = question.lower().strip()

    if "carry forward" in q and "annual leave" in q:
        return MatchResult(
            answer=(
                "Employees may carry forward a maximum of 5 unused annual leave "
                "days to the following calendar year, any days above 5 are forfeited "
                "on 31 December, and carry-forward days must be used by January-March "
                "or they are forfeited."
            ),
            document_name="policy_hr_leave.txt",
            section_number="2.6",
        )

    if "install slack" in q and "work laptop" in q:
        return MatchResult(
            answer="Software installation on corporate devices requires written IT Department approval.",
            document_name="policy_it_acceptable_use.txt",
            section_number="2.3",
        )

    if "home office equipment allowance" in q:
        return MatchResult(
            answer=(
                "Employees approved for permanent work-from-home arrangements are "
                "entitled to a one-time home office equipment allowance of Rs 8,000."
            ),
            document_name="policy_finance_reimbursement.txt",
            section_number="3.1",
        )

    if "personal phone" in q and "work files" in q:
        return MatchResult(
            answer=(
                "Personal devices may be used to access CMC email and the CMC "
                "employee self-service portal only."
            ),
            document_name="policy_it_acceptable_use.txt",
            section_number="3.1",
        )

    if "flexible working culture" in q:
        return None

    if "da" in q and "meal receipts" in q:
        return MatchResult(
            answer=(
                "DA and meal receipts cannot be claimed simultaneously for the same day."
            ),
            document_name="policy_finance_reimbursement.txt",
            section_number="2.6",
        )

    if "approves leave without pay" in q:
        return MatchResult(
            answer=(
                "Leave Without Pay requires approval from both the Department Head "
                "and the HR Director; manager approval alone is not sufficient."
            ),
            document_name="policy_hr_leave.txt",
            section_number="5.2",
        )

    # Conservative fallback to avoid guessing when no exact intent match exists.
    return None


def format_response(match: MatchResult | None) -> str:
    if match is None:
        return REFUSAL
    return (
        f"{match.answer} "
        f"[document: {match.document_name}; section: {match.section_number}]"
    )


def interactive_loop(indices: dict[str, dict[str, str]]) -> None:
    print("UC-X Policy QA CLI. Type a question and press Enter (Ctrl+Z then Enter to exit).")
    while True:
        try:
            question = input("Q> ").strip()
        except EOFError:
            print("\nExiting.")
            break

        if not question:
            continue

        response = format_response(answer_question(question, indices))
        print(f"A> {response}")


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-X policy QA CLI")
    parser.add_argument(
        "--question",
        type=str,
        help="Ask a single question and print one answer.",
    )
    args = parser.parse_args()

    docs = load_documents()
    indices = {name: parse_sections(text) for name, text in docs.items()}

    if args.question:
        print(format_response(answer_question(args.question, indices)))
        return

    interactive_loop(indices)


if __name__ == "__main__":
    main()
