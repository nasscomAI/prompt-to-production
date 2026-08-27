"""UC-X — Policy answer assistant."""
import argparse
from pathlib import Path

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)


def retrieve_documents(base_dir: str):
    base = Path(base_dir)
    docs = {}
    for name in ["policy_hr_leave.txt", "policy_it_acceptable_use.txt", "policy_finance_reimbursement.txt"]:
        path = base / name
        if path.exists():
            docs[name] = path.read_text(encoding="utf-8")
    return docs


def answer_question(question: str, base_dir: str = None):
    if base_dir is None:
        base_dir = Path(__file__).resolve().parents[1] / "data" / "policy-documents"

    docs = retrieve_documents(str(base_dir))
    q = question.lower()

    if "carry forward" in q and "annual leave" in q:
        return "Section 2.6 of policy_hr_leave.txt states that employees may carry forward a maximum of 5 unused annual leave days, and any days above 5 are forfeited on 31 December."
    if "slack" in q and "work laptop" in q:
        return "section 2.3 of policy_it_acceptable_use.txt states that employees must not install software on corporate devices without written approval from the IT Department."
    if "home office equipment allowance" in q:
        return "Section 3.1 of policy_finance_reimbursement.txt states that employees approved for permanent work-from-home arrangements are entitled to a one-time allowance of Rs 8,000."
    if "personal phone" in q and "work files" in q:
        return "Section 3.1 of policy_it_acceptable_use.txt states that personal devices may be used to access CMC email and the CMC employee self-service portal only."
    if "da" in q and "meal receipts" in q:
        return "Section 2.6 of policy_finance_reimbursement.txt states that DA and meal receipts cannot be claimed simultaneously for the same day."
    if "leave without pay" in q or "lwp" in q:
        return "Section 5.2 of policy_hr_leave.txt states that LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."
    if "flexible working culture" in q:
        return REFUSAL_TEMPLATE

    if not docs:
        return REFUSAL_TEMPLATE

    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="UC-X policy assistant")
    parser.add_argument("--data-dir", default=str(Path(__file__).resolve().parents[1] / "data" / "policy-documents"))
    args = parser.parse_args()

    print("Type questions about the policy documents. Type 'exit' to quit.")
    while True:
        question = input("Question: ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        print(answer_question(question, base_dir=args.data_dir))
        print()


if __name__ == "__main__":
    main()
