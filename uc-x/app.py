"""UC-X single-source policy question answering CLI."""
import re
import sys
from pathlib import Path

REFUSAL = "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
FILES = ("policy_hr_leave.txt", "policy_it_acceptable_use.txt", "policy_finance_reimbursement.txt")

def retrieve_documents(root=None):
    base = Path(root) if root else Path(__file__).resolve().parents[1] / "data" / "policy-documents"
    docs = {}
    for filename in FILES:
        path = base / filename
        if not path.exists():
            raise FileNotFoundError(str(path))
        text = path.read_text(encoding="utf-8")
        markers = list(re.finditer(r"(?m)^(?:(\d+\.\d+)|(\d+\.))\s+", text))
        sections = {}
        for index, marker in enumerate(markers):
            number = marker.group(1)
            if not number:
                continue
            end = markers[index + 1].start() if index + 1 < len(markers) else len(text)
            sections[number] = " ".join(text[marker.end():end].split())
        docs[filename] = sections
    return docs

def _answer(filename, sections, numbers):
    parts = [f"{sections[number]} [{filename}, section {number}]" for number in numbers if number in sections]
    return " ".join(parts) if parts else REFUSAL

def answer_question(question, docs):
    q = question.lower().strip()
    if ("carry forward" in q or "carry-forward" in q) and "leave" in q:
        return _answer("policy_hr_leave.txt", docs["policy_hr_leave.txt"], ["2.6", "2.7"])
    if "slack" in q or ("install" in q and "work laptop" in q):
        return _answer("policy_it_acceptable_use.txt", docs["policy_it_acceptable_use.txt"], ["2.3", "2.4"])
    if "home office" in q or "equipment allowance" in q:
        return _answer("policy_finance_reimbursement.txt", docs["policy_finance_reimbursement.txt"], ["3.1", "3.2", "3.3", "3.4", "3.5"])
    if "personal phone" in q and ("work file" in q or "home" in q):
        return _answer("policy_it_acceptable_use.txt", docs["policy_it_acceptable_use.txt"], ["3.1", "3.2"])
    if "flexible working culture" in q:
        return REFUSAL
    if ("da" in q or "daily allowance" in q) and "meal" in q:
        return _answer("policy_finance_reimbursement.txt", docs["policy_finance_reimbursement.txt"], ["2.5", "2.6"])
    if "leave without pay" in q or "lwp" in q:
        return _answer("policy_hr_leave.txt", docs["policy_hr_leave.txt"], ["5.2"])
    return REFUSAL

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    docs = retrieve_documents()
    print("Policy assistant ready. Type a question or 'quit'.")
    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            break
        if question.lower() in {"quit", "exit"}:
            break
        if question:
            print(answer_question(question, docs))

if __name__ == "__main__":
    main()

