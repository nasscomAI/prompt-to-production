"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import re
from pathlib import Path
from typing import Dict, List, Tuple

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

SECTION_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_HEADING_RE = re.compile(r"^\d+\.\s+")


def retrieve_documents() -> Dict[str, Dict[str, str]]:
    base_dir = Path(__file__).resolve().parent
    files = {
        "policy_hr_leave.txt": base_dir / "../data/policy-documents/policy_hr_leave.txt",
        "policy_it_acceptable_use.txt": base_dir / "../data/policy-documents/policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt": base_dir / "../data/policy-documents/policy_finance_reimbursement.txt",
    }
    indexed: Dict[str, Dict[str, str]] = {}
    for name, path in files.items():
        text = Path(path).resolve().read_text(encoding="utf-8")
        sections: Dict[str, str] = {}
        current_section = ""
        parts: List[str] = []
        for raw in text.splitlines():
            line = raw.strip()
            if not line:
                continue
            match = SECTION_RE.match(line)
            if match:
                if current_section:
                    sections[current_section] = " ".join(parts).strip()
                current_section = match.group(1)
                parts = [match.group(2).strip()]
            elif current_section and not set(line) <= {"═"} and not SECTION_HEADING_RE.match(line):
                parts.append(line)
        if current_section:
            sections[current_section] = " ".join(parts).strip()
        indexed[name] = sections
    return indexed


def _contains_all(question: str, terms: List[str]) -> bool:
    return all(term in question for term in terms)


def answer_question(question: str, docs: Dict[str, Dict[str, str]]) -> str:
    q = question.strip().lower()
    if not q:
        return "Please ask a policy question or type 'exit'."

    # HR leave policy
    if _contains_all(q, ["carry", "forward"]) and "leave" in q:
        text = docs["policy_hr_leave.txt"]["2.6"]
        return f"{text}\nSource: policy_hr_leave.txt Section 2.6"
    if "leave without pay" in q or ("approve" in q and "lwp" in q) or ("who approves leave" in q):
        text = docs["policy_hr_leave.txt"]["5.2"]
        return f"{text}\nSource: policy_hr_leave.txt Section 5.2"

    # IT policy
    if ("install" in q and "slack" in q) or ("install software" in q and "laptop" in q):
        text = docs["policy_it_acceptable_use.txt"]["2.3"]
        return f"{text}\nSource: policy_it_acceptable_use.txt Section 2.3"
    if "personal phone" in q and ("work files" in q or "home" in q):
        text = docs["policy_it_acceptable_use.txt"]["3.1"]
        return f"{text}\nSource: policy_it_acceptable_use.txt Section 3.1"

    # Finance policy
    if "home office equipment allowance" in q or (
        "home office" in q and "allowance" in q
    ):
        text = docs["policy_finance_reimbursement.txt"]["3.1"]
        return f"{text}\nSource: policy_finance_reimbursement.txt Section 3.1"
    if ("da" in q and "meal" in q) or ("daily allowance" in q and "meal" in q):
        text = docs["policy_finance_reimbursement.txt"]["2.6"]
        return f"{text}\nSource: policy_finance_reimbursement.txt Section 2.6"

    return REFUSAL_TEMPLATE


def main():
    docs = retrieve_documents()
    print("UC-X Ask My Documents")
    print("Type your question. Type 'exit' to quit.")
    while True:
        user_q = input("> ").strip()
        if user_q.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break
        print(answer_question(user_q, docs))
        print()

if __name__ == "__main__":
    main()
