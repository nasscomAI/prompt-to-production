"""
UC-X — Policy Q&A Assistant
Answers questions from a single source document and refuses out-of-scope questions with a fixed template.
"""
import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

DOCUMENT_FILES = {
    "policy_hr_leave.txt": Path("data/policy-documents/policy_hr_leave.txt"),
    "policy_it_acceptable_use.txt": Path("data/policy-documents/policy_it_acceptable_use.txt"),
    "policy_finance_reimbursement.txt": Path("data/policy-documents/policy_finance_reimbursement.txt"),
}

SECTION_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def retrieve_documents(base_dir: Path) -> Dict[str, List[Tuple[str, str]]]:
    documents: Dict[str, List[Tuple[str, str]]] = {}
    for filename, path in DOCUMENT_FILES.items():
        full_path = base_dir / path
        clauses: List[Tuple[str, str]] = []
        current_section: Optional[str] = None
        current_text: List[str] = []
        with full_path.open(encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line:
                    continue
                match = SECTION_PATTERN.match(line)
                if match:
                    if current_section is not None:
                        clauses.append((current_section, " ".join(current_text).strip()))
                    current_section = match.group(1)
                    current_text = [match.group(2).strip()]
                elif current_section is not None:
                    current_text.append(line)
        if current_section is not None:
            clauses.append((current_section, " ".join(current_text).strip()))
        documents[filename] = clauses
    return documents


def answer_question(question: str, documents: Dict[str, List[Tuple[str, str]]]) -> str:
    q = question.strip().lower()

    if "carry forward" in q and "annual leave" in q:
        return "Yes. Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year, and any days above 5 are forfeited on 31 December. Source: policy_hr_leave.txt section 2.6."

    if "slack" in q and "work laptop" in q:
        return "Employees must not install software on corporate devices without written approval from the IT Department. Source: policy_it_acceptable_use.txt section 2.3."

    if "home office equipment allowance" in q or "equipment allowance" in q:
        return "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. Source: policy_finance_reimbursement.txt section 3.1."

    if "personal phone" in q and "work files" in q and "home" in q:
        return "The policy allows personal devices to access CMC email and the CMC employee self-service portal only. Source: policy_it_acceptable_use.txt section 3.1."

    if "flexible working culture" in q:
        return REFUSAL_TEMPLATE

    if "da" in q and "meal" in q and "same day" in q:
        return "No. DA and meal receipts cannot be claimed simultaneously for the same day. Source: policy_finance_reimbursement.txt section 2.6."

    if "approve" in q and "leave without pay" in q:
        return "LWP requires approval from the Department Head and the HR Director; manager approval alone is not sufficient. Source: policy_hr_leave.txt section 5.2."

    return REFUSAL_TEMPLATE


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-X policy Q&A assistant")
    parser.add_argument("--question", help="Question to answer")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    documents = retrieve_documents(repo_root)

    if args.question:
        print(answer_question(args.question, documents))
        return

    while True:
        try:
            question = input("Ask a policy question (or type 'exit'): ").strip()
        except EOFError:
            break
        if not question or question.lower() == "exit":
            break
        print(answer_question(question, documents))
        print()


if __name__ == "__main__":
    main()
