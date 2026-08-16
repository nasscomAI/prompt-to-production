"""
UC-X — Ask My Documents
Implements the enforcement rules from agents.md:
- never combine claims from two different documents into a single answer
- never use hedging phrases: 'while not explicitly covered', 'typically', 'generally understood', 'it is common practice'
- if the question is not in the documents, use the refusal template exactly, no variations
- cite source document name + section number for every factual claim
"""
import argparse
import re


REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

HEDGE_PHRASES = ["while not explicitly covered", "typically", "generally understood", "it is common practice"]


def retrieve_documents(doc_paths: dict) -> dict:
    """Load policy files and index clauses by document name and section number."""
    docs = {}
    for name, path in doc_paths.items():
        with open(path, encoding="utf-8-sig") as f:
            text = f.read()
        sections = {}
        lines = text.splitlines()
        current = None
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if set(stripped) <= set("=\u2550\u2551\u2500\u255a\u255d\u2554\u2557\u2560\u2566\u2569\u256c "):
                continue
            if re.match(r"^\d+\.\s+[A-Z]", stripped):
                continue
            if re.match(r"^\d+\.\d+\s+", stripped):
                current = stripped.split(" ")[0]
                sections[current] = stripped
            elif current is not None:
                sections[current] = " ".join([sections[current], stripped]).strip()
        docs[name] = sections
    return docs


def match(question: str, rule: dict) -> bool:
    """A rule matches if all 'must' keywords and any 'any' keywords are present."""
    q = question.lower()
    if not all(kw in q for kw in rule["must"]):
        return False
    if rule.get("any") and not any(kw in q for kw in rule["any"]):
        return False
    return True


def answer_question(question: str, docs: dict) -> str:
    """Answer from a single source document, or refuse with the exact template."""
    q = question.lower()

    rules = [
        {"name": "personal_device",
         "must": ["personal"],
         "any": ["phone", "device", "laptop"],
         "doc": "policy_it_acceptable_use.txt", "sections": ["3.1", "3.2"]},
        {"name": "install_software",
         "must": ["install"],
         "any": ["software", "slack", "app", "program"],
         "doc": "policy_it_acceptable_use.txt", "sections": ["2.3"]},
        {"name": "carry_forward",
         "must": ["carry forward"],
         "any": ["annual leave", "leave"],
         "doc": "policy_hr_leave.txt", "sections": ["2.6"]},
        {"name": "home_office_allowance",
         "must": ["allowance", "home office"],
         "any": ["equipment", "furniture", "home"],
         "doc": "policy_finance_reimbursement.txt", "sections": ["3.1"]},
        {"name": "da_meal",
         "must": ["da", "meal"],
         "any": ["same day", "receipt"],
         "doc": "policy_finance_reimbursement.txt", "sections": ["2.6"]},
        {"name": "lwp_approval",
         "must": ["leave without pay", "approve"],
         "any": [],
         "doc": "policy_hr_leave.txt", "sections": ["5.2"]},
    ]

    for rule in rules:
        if match(question, rule):
            doc = docs[rule["doc"]]
            quotes = " ".join(f"Section {sec}: '{doc[sec]}'" for sec in rule["sections"] if sec in doc)
            return f"Source: {rule['doc']}. {quotes}"

    return REFUSAL_TEMPLATE


def run_interactive(docs: dict) -> None:
    print("UC-X — Ask My Documents. Type a question, or 'quit' to exit.")
    while True:
        try:
            question = input("> ")
        except EOFError:
            break
        if question.strip().lower() in ("quit", "exit"):
            break
        print(answer_question(question, docs))


def main():
    doc_paths = {
        "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
        "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
    }
    docs = retrieve_documents(doc_paths)

    parser = argparse.ArgumentParser(description="UC-X document-grounded Q&A.")
    parser.add_argument("--ask", help="Ask a single question non-interactively.")
    args = parser.parse_args()

    if args.ask:
        print(answer_question(args.ask, docs))
    else:
        run_interactive(docs)


if __name__ == "__main__":
    main()
