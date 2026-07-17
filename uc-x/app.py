"""
UC-X — Ask My Documents
Interactive policy Q&A with single-source answering and refusal template.
"""
import os
import re


REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)


def retrieve_documents(data_dir: str) -> dict:
    """Load all 3 policy files, index by document name and section number."""
    indexed = {}
    files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]
    for fname in files:
        path = os.path.join(data_dir, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            current_section = None
            current_text = []
            for line in content.split("\n"):
                match = re.match(r"^\s*(\d+\.\d+)\s", line)
                if match:
                    if current_section:
                        indexed[(fname, current_section)] = "\n".join(current_text).strip()
                    current_section = match.group(1)
                    current_text = [line.strip()]
                elif current_section:
                    current_text.append(line.strip())
            if current_section:
                indexed[(fname, current_section)] = "\n".join(current_text).strip()
        except Exception as e:
            print(f"Error reading {fname}: {e}")
    return indexed


def answer_question(question: str, indexed: dict) -> dict:
    """Search indexed documents, return single-source answer or refusal."""
    q_lower = question.lower()

    keyword_map = {
        "carry forward": ("policy_hr_leave.txt", "2.6"),
        "unused annual leave": ("policy_hr_leave.txt", "2.6"),
        "install slack": ("policy_it_acceptable_use.txt", "2.3"),
        "install software": ("policy_it_acceptable_use.txt", "2.3"),
        "home office equipment allowance": ("policy_finance_reimbursement.txt", "3.1"),
        "home office": ("policy_finance_reimbursement.txt", "3.1"),
        "personal phone": ("policy_it_acceptable_use.txt", "3.1"),
        "personal device": ("policy_it_acceptable_use.txt", "3.1"),
        "flexible working": None,
        "flexible culture": None,
        "company view": None,
        "claim da and meal": ("policy_finance_reimbursement.txt", "2.6"),
        "da and meal receipts": ("policy_finance_reimbursement.txt", "2.6"),
        "da meal receipts same day": ("policy_finance_reimbursement.txt", "2.6"),
        "leave without pay": ("policy_hr_leave.txt", "5.2"),
        "who approves lwp": ("policy_hr_leave.txt", "5.2"),
        "approves leave without pay": ("policy_hr_leave.txt", "5.2"),
    }

    matched_doc = None
    matched_section = None
    for keyword, target in keyword_map.items():
        if keyword in q_lower:
            if target is None:
                return {"answer": REFUSAL_TEMPLATE, "source_doc": "N/A", "section_num": "N/A", "refusal": True}
            matched_doc, matched_section = target
            break

    if matched_doc and matched_section:
        section_text = indexed.get((matched_doc, matched_section), "")
        return {
            "answer": f"According to {matched_doc} section {matched_section}: {section_text}",
            "source_doc": matched_doc,
            "section_num": matched_section,
            "refusal": False
        }

    return {"answer": REFUSAL_TEMPLATE, "source_doc": "N/A", "section_num": "N/A", "refusal": True}


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "data", "policy-documents")
    indexed = retrieve_documents(data_dir)
    print(f"Loaded {len(indexed)} sections from 3 policy documents")
    print("Type your question (or 'quit' to exit):\n")

    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not question or question.lower() == "quit":
            break
        result = answer_question(question, indexed)
        print(f"\n{result['answer']}\n")
        if not result.get("refusal"):
            print(f"[Source: {result['source_doc']}, Section {result['section_num']}]\n")


if __name__ == "__main__":
    main()
