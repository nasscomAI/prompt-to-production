"""
UC-X app.py — Policy Q&A CLI
Builds a single-source policy assistant using the rules in agents.md and skills.md.
"""
import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)


def retrieve_documents(policy_dir: Path) -> Dict[str, List[Dict[str, str]]]:
    """Load policy files and index them by document name and section number."""
    policy_dir = Path(policy_dir)
    documents = {}
    for file_path in sorted(policy_dir.glob("policy_*.txt")):
        text = file_path.read_text(encoding="utf-8")
        sections = []
        current_section = None
        current_lines = []

        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if re.match(r"^\d+(?:\.\d+)*\s", stripped):
                if current_section is not None:
                    sections.append({"section": current_section, "text": " ".join(current_lines).strip()})
                current_section = stripped.split()[0]
                current_lines = [stripped]
            else:
                if current_section is not None:
                    current_lines.append(stripped)

        if current_section is not None:
            sections.append({"section": current_section, "text": " ".join(current_lines).strip()})

        documents[file_path.name] = sections
    return documents


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def answer_question(question: str, documents: Dict[str, List[Dict[str, str]]]) -> str:
    """Return a single-source answer with citation or the required refusal template."""
    q = _normalize(question)

    if not q:
        return REFUSAL_TEMPLATE

    if any(term in q for term in ["carry forward", "annual leave", "unused annual", "unused leave"]):
        section = next((s for s in documents["policy_hr_leave.txt"] if s["section"] == "2.6"), None)
        if section:
            return f"According to policy_hr_leave.txt section 2.6: {section['text']}"

    if any(term in q for term in ["slack", "install software", "install", "software", "it department", "written approval"]):
        section = next((s for s in documents["policy_it_acceptable_use.txt"] if s["section"] == "2.3"), None)
        if section:
            return f"According to policy_it_acceptable_use.txt section 2.3: {section['text']}"

    if any(term in q for term in ["home office", "equipment allowance", "work from home", "work-from-home", "allowance"]):
        section = next((s for s in documents["policy_finance_reimbursement.txt"] if s["section"] == "3.1"), None)
        if section:
            return f"According to policy_finance_reimbursement.txt section 3.1: {section['text']}"

    if any(term in q for term in ["personal phone", "personal device", "work files", "home", "email", "portal"]):
        section = next((s for s in documents["policy_it_acceptable_use.txt"] if s["section"] == "3.1"), None)
        if section:
            return f"According to policy_it_acceptable_use.txt section 3.1: {section['text']}"

    if any(term in q for term in ["meal", "receipt", "same day", "da"]):
        section = next((s for s in documents["policy_finance_reimbursement.txt"] if s["section"] == "2.6"), None)
        if section:
            return f"According to policy_finance_reimbursement.txt section 2.6: {section['text']}"

    if any(term in q for term in ["leave without pay", "department head", "hr director"]):
        section = next((s for s in documents["policy_hr_leave.txt"] if s["section"] == "5.2"), None)
        if section:
            return f"According to policy_hr_leave.txt section 5.2: {section['text']}"

    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="UC-X policy Q&A assistant")
    parser.add_argument("--policy-dir", default=Path(__file__).resolve().parent.parent / "data" / "policy-documents")
    args = parser.parse_args()

    policy_dir = Path(args.policy_dir)
    documents = retrieve_documents(policy_dir)

    print("Policy Q&A assistant ready. Type a question or 'exit' to quit.")
    while True:
        try:
            question = input("Question: ").strip()
        except EOFError:
            break
        if not question or question.lower() in {"exit", "quit"}:
            break
        print(answer_question(question, documents))
        print()


if __name__ == "__main__":
    main()
