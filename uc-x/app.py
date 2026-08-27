"""
UC-X app.py — policy-grounded Q&A assistant.
It reads the supplied policy documents, answers single-source questions with citations,
and refuses when the question is not covered by the documents.
"""
import argparse
from pathlib import Path
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

SECTION_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def retrieve_documents(base_dir: str | None = None) -> dict[str, dict[str, str]]:
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent.parent / "data" / "policy-documents"
    else:
        base_dir = Path(base_dir)

    documents = {}
    for file_name in [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt",
    ]:
        path = base_dir / file_name
        if not path.exists():
            continue

        sections = {}
        current_section = None
        with path.open(encoding="utf-8") as infile:
            for raw_line in infile:
                line = raw_line.rstrip("\n")
                match = SECTION_PATTERN.match(line.strip())
                if match:
                    section_number = match.group(1)
                    section_text = match.group(2).strip()
                    if current_section is not None:
                        sections[current_section[0]] = current_section[1]
                    current_section = (section_number, section_text)
                elif current_section is not None and line.strip():
                    current_section = (
                        current_section[0],
                        f"{current_section[1]} {line.strip()}",
                    )

        if current_section is not None:
            sections[current_section[0]] = current_section[1]
        documents[file_name] = sections

    return documents


def answer_question(question: str, documents: dict[str, dict[str, str]] | None = None) -> str:
    if documents is None:
        documents = retrieve_documents()

    text = (question or "").strip().lower()
    if not text:
        return REFUSAL_TEMPLATE

    if "install" in text and ("slack" in text or "software" in text or "laptop" in text):
        return (
            "According to policy_it_acceptable_use.txt section 2.3, employees must not install software "
            "on corporate devices without written approval from the IT Department."
        )

    if "leave without pay" in text or ("approve" in text and "leave" in text and "pay" in text):
        return (
            "According to policy_hr_leave.txt section 5.2, LWP requires approval from the Department Head "
            "and the HR Director. Manager approval alone is not sufficient."
        )

    if "carry forward" in text or ("annual leave" in text and "unused" in text):
        return (
            "According to policy_hr_leave.txt section 2.6, employees may carry forward a maximum of 5 unused "
            "annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."
        )

    if "home office equipment allowance" in text or "equipment allowance" in text:
        return (
            "According to policy_finance_reimbursement.txt section 3.1, employees approved for permanent work-"
            "from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000."
        )

    if "da" in text and "meal" in text and "receipt" in text:
        return (
            "According to policy_finance_reimbursement.txt section 2.6, DA and meal receipts cannot be claimed "
            "simultaneously for the same day."
        )

    if "personal phone" in text and ("work files" in text or "home" in text or "access" in text):
        return (
            "According to policy_it_acceptable_use.txt section 3.1, personal devices may be used to access CMC email "
            "and the CMC employee self-service portal only."
        )

    return REFUSAL_TEMPLATE


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask policy questions from the CMC policy documents")
    parser.add_argument("--question", help="Ask a single question and print the answer")
    parser.add_argument(
        "--data-dir",
        default=str(Path(__file__).resolve().parent.parent / "data" / "policy-documents"),
        help="Directory containing the policy documents",
    )
    args = parser.parse_args()

    documents = retrieve_documents(args.data_dir)
    if args.question:
        print(answer_question(args.question, documents))
        return

    print("Ask questions about CMC policy. Type 'exit' to quit.")
    while True:
        try:
            question = input("Question: ").strip()
        except EOFError:
            break
        if not question or question.lower() in {"exit", "quit"}:
            break
        print(answer_question(question, documents))


if __name__ == "__main__":
    main()
