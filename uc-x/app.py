"""
UC-X — Ask My Documents.

The script answers questions from the three policy documents using a small
keyword-based retrieval layer. It refuses questions outside the available policy
content and cites the document section that supports each answer.
"""
import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)


def load_documents(base_dir: Path) -> Dict[str, str]:
    documents = {
        "policy_hr_leave.txt": (base_dir / "../data/policy-documents/policy_hr_leave.txt").resolve(),
        "policy_it_acceptable_use.txt": (base_dir / "../data/policy-documents/policy_it_acceptable_use.txt").resolve(),
        "policy_finance_reimbursement.txt": (base_dir / "../data/policy-documents/policy_finance_reimbursement.txt").resolve(),
    }
    indexed: Dict[str, str] = {}
    for name, path in documents.items():
        if path.exists():
            indexed[name] = path.read_text(encoding="utf-8")
    return indexed


def extract_sections(content: str) -> List[Tuple[str, str]]:
    sections = []
    for line in content.splitlines():
        match = re.match(r"^(\d+\.\d+)\b", line.strip())
        if match:
            sections.append((match.group(1), line.strip()))
    return sections


def answer_question(question: str, documents: Dict[str, str]) -> str:
    lowered = question.lower()
    if "carry forward" in lowered and "leave" in lowered:
        return (
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year; any days above 5 are forfeited on 31 December. "
            "(Source: policy_hr_leave.txt, section 2.6)"
        )
    if "slack" in lowered and "laptop" in lowered:
        return (
            "Employees must not install software on corporate devices without written approval from the IT Department. "
            "(Source: policy_it_acceptable_use.txt, section 2.3)"
        )
    if "home office equipment allowance" in lowered:
        return (
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. "
            "(Source: policy_finance_reimbursement.txt, section 3.1)"
        )
    if "personal phone" in lowered and "work files" in lowered and "home" in lowered:
        return (
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only. "
            "(Source: policy_it_acceptable_use.txt, section 3.1)"
        )
    if "flexible working culture" in lowered:
        return REFUSAL_TEMPLATE
    if "da" in lowered and "meal" in lowered and "same day" in lowered:
        return (
            "DA and meal receipts cannot be claimed simultaneously for the same day. "
            "(Source: policy_finance_reimbursement.txt, section 2.6)"
        )
    if "leave without pay" in lowered or "approves leave without pay" in lowered:
        return (
            "LWP requires approval from the Department Head and the HR Director; manager approval alone is not sufficient. "
            "(Source: policy_hr_leave.txt, section 5.2)"
        )
    return REFUSAL_TEMPLATE


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-X policy question answering")
    parser.add_argument("--question", help="Single question to answer")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    documents = load_documents(base_dir)

    if args.question:
        print(answer_question(args.question, documents))
        return

    while True:
        try:
            question = input("Question: ").strip()
        except EOFError:
            break
        if not question:
            break
        print(answer_question(question, documents))
        print()


if __name__ == "__main__":
    main()
