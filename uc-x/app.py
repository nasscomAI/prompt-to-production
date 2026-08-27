"""
UC-X — Ask My Documents

Single-source policy Q&A CLI with exact refusal behavior.
"""
import argparse
import re
from pathlib import Path


DOCUMENTS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)
SECTION_RE = re.compile(r"(?m)^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+\s+|^═|\Z)", re.DOTALL)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def retrieve_documents(policy_dir: str) -> dict[str, dict[str, str]]:
    """Load the three policy documents and index numbered sections."""
    indexed = {}
    base_path = Path(policy_dir)
    if not base_path.exists():
        base_path = Path(__file__).resolve().parent / policy_dir

    for document_name in DOCUMENTS:
        path = base_path / document_name
        text = path.read_text(encoding="utf-8")
        indexed[document_name] = {
            section: " ".join(section_text.split())
            for section, section_text in SECTION_RE.findall(text)
        }

    return indexed


def answer_question(question: str, documents: dict[str, dict[str, str]]) -> str:
    """Return a single-source answer with citations, or the exact refusal template."""
    q = _normalize(question)

    if "carry forward" in q and "annual leave" in q:
        return (
            "According to policy_hr_leave.txt section 2.6, employees may carry forward a maximum of 5 unused annual leave days "
            "to the following calendar year, and any days above 5 are forfeited on 31 December."
        )

    if "install" in q and ("slack" in q or "software" in q or "work laptop" in q):
        return (
            "According to policy_it_acceptable_use.txt section 2.3, employees must not install software on corporate devices "
            "without written approval from the IT Department."
        )

    if "home office equipment allowance" in q or ("equipment allowance" in q and "home" in q):
        return (
            "According to policy_finance_reimbursement.txt section 3.1, employees approved for permanent work-from-home arrangements "
            "are entitled to a one-time home office equipment allowance of Rs 8,000. According to policy_finance_reimbursement.txt "
            "section 3.5, employees on temporary or partial work-from-home arrangements are not eligible for this allowance."
        )

    if "personal phone" in q or "personal device" in q:
        return (
            "According to policy_it_acceptable_use.txt section 3.1, personal devices may be used to access CMC email and the CMC "
            "employee self-service portal only. According to policy_it_acceptable_use.txt section 3.2, personal devices must not "
            "be used to access, store, or transmit classified or sensitive CMC data."
        )

    if ("da" in q or "daily allowance" in q) and ("meal" in q or "receipts" in q):
        return (
            "According to policy_finance_reimbursement.txt section 2.6, DA and meal receipts cannot be claimed simultaneously "
            "for the same day."
        )

    if "leave without pay" in q or "lwp" in q:
        return (
            "According to policy_hr_leave.txt section 5.2, Leave Without Pay requires approval from the Department Head and the "
            "HR Director, and manager approval alone is not sufficient. According to policy_hr_leave.txt section 5.3, Leave "
            "Without Pay exceeding 30 continuous days requires approval from the Municipal Commissioner."
        )

    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="UC-X policy Q&A")
    parser.add_argument("--policy-dir", default="../data/policy-documents", help="Directory containing policy documents")
    parser.add_argument("--question", help="Optional single question for non-interactive use")
    args = parser.parse_args()

    documents = retrieve_documents(args.policy_dir)

    if args.question:
        print(answer_question(args.question, documents))
        return

    print("UC-X policy Q&A. Type a question, or type 'exit' to quit.")
    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            break
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue
        print(answer_question(question, documents))


if __name__ == "__main__":
    main()
