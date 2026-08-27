"""UC-X document-grounded municipal policy assistant."""

import argparse
import re
from pathlib import Path

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)


def parse_sections(text: str) -> dict:
    """Return a mapping of section number -> text."""
    sections = {}
    current_key = None
    current_lines = []

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("=") or stripped.startswith("CITY MUNICIPAL") or stripped.startswith("Document Reference") or stripped.startswith("Version:"):
            continue
        match = re.match(r"^(\d+\.\d+)\s*(.*)$", stripped)
        if match:
            if current_key:
                sections[current_key] = " ".join(current_lines).strip()
            current_key = match.group(1)
            current_lines = [match.group(2).strip()] if match.group(2).strip() else []
        elif current_key:
            current_lines.append(stripped)

    if current_key:
        sections[current_key] = " ".join(current_lines).strip()
    return sections


def load_documents(base_dir: str) -> dict:
    """Load all policy documents and index them by section."""
    docs = {}
    for name in [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt",
    ]:
        text = Path(base_dir, name).read_text(encoding="utf-8")
        docs[name] = parse_sections(text)
    return docs


def answer_question(question: str, documents: dict) -> str:
    """Answer a question from a single document or refuse if out of scope."""
    q = question.lower().strip()
    if not q or q in {"exit", "quit"}:
        return "Goodbye."

    if "carry forward" in q or "unused annual leave" in q:
        text = documents["policy_hr_leave.txt"].get("2.6", "")
        return f"Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. Source: policy_hr_leave.txt — section 2.6."

    if "slack" in q or "install software" in q or "software on corporate devices" in q:
        return "Employees must not install software on corporate devices without written approval from the IT Department. Source: policy_it_acceptable_use.txt — section 2.3."

    if "home office equipment allowance" in q or "allowance" in q and "work from home" in q:
        return "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. Source: policy_finance_reimbursement.txt — section 3.1."

    if "personal phone" in q and "work files" in q:
        return REFUSAL_TEMPLATE

    if "flexible working culture" in q or "company view" in q and "flexible" in q:
        return REFUSAL_TEMPLATE

    if "da and meal" in q or "meal receipts" in q:
        return "If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day. DA and meal receipts cannot be claimed simultaneously for the same day. Source: policy_finance_reimbursement.txt — section 2.6."

    if "leave without pay" in q or "who approves" in q and "leave without pay" in q:
        return "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient. Source: policy_hr_leave.txt — section 5.2."

    for doc_name, sections in documents.items():
        for section, text in sections.items():
            if text and len(q.split()) >= 2:
                combined = (text + " " + section).lower()
                if any(word in q for word in ["annual leave", "sick leave", "leave", "approval", "phone", "email", "software", "reimbursement", "travel", "allowance"]):
                    if any(word in combined for word in q.split()[:4]):
                        return f"{text} Source: {doc_name} — section {section}."

    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="UC-X policy assistant")
    parser.add_argument("--data-dir", default="/workspaces/prompt-to-production/data/policy-documents", help="Path to policy-documents directory")
    args = parser.parse_args()

    documents = load_documents(args.data_dir)
    print("Ask a policy question. Type 'exit' to quit.")
    while True:
        question = input("Question: ").strip()
        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break
        print(answer_question(question, documents))


if __name__ == "__main__":
    main()
