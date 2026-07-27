"""
UC-X app.py — Policy Q&A assistant.
Implements retrieve_documents and answer_question skills from skills.md
using the enforcement rules in agents.md.
"""
import argparse
import re
from pathlib import Path

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)


def retrieve_documents(doc_paths=None):
    """Load policy documents and index them by document name and section number."""
    if doc_paths is None:
        base_dir = Path(__file__).resolve().parent.parent
        doc_paths = [
            base_dir / "data" / "policy-documents" / "policy_hr_leave.txt",
            base_dir / "data" / "policy-documents" / "policy_it_acceptable_use.txt",
            base_dir / "data" / "policy-documents" / "policy_finance_reimbursement.txt",
        ]

    documents = {}
    for path in doc_paths:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Policy file not found: {path}")

        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        clauses = []
        current_id = None
        current_lines = []

        for line in lines:
            match = re.match(r"^\s*(\d+\.\d+)\s+(.*)$", line)
            if match:
                if current_id is not None:
                    clauses.append({"id": current_id, "text": " ".join(current_lines).strip()})
                current_id = match.group(1)
                current_lines = [match.group(2).strip()]
            elif current_id is not None and line.strip():
                current_lines.append(line.strip())

        if current_id is not None:
            clauses.append({"id": current_id, "text": " ".join(current_lines).strip()})

        documents[path.name] = {
            "path": str(path),
            "text": text,
            "clauses": clauses,
        }

    return documents


def _normalize(text):
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _find_best_clause(question, documents):
    """Return a single relevant clause or None when the question is unsupported."""
    q = _normalize(question)
    q_tokens = set(q.split())

    if not q_tokens:
        return None

    rules = [
        ("carry forward", "policy_hr_leave.txt", "2.6"),
        ("unused annual leave", "policy_hr_leave.txt", "2.6"),
        ("leave without pay", "policy_hr_leave.txt", "5.2"),
        ("approves leave without pay", "policy_hr_leave.txt", "5.2"),
        ("slack", "policy_it_acceptable_use.txt", "2.3"),
        ("work laptop", "policy_it_acceptable_use.txt", "2.3"),
        ("install software", "policy_it_acceptable_use.txt", "2.3"),
        ("personal phone", "policy_it_acceptable_use.txt", "3.1"),
        ("work files", "policy_it_acceptable_use.txt", "3.1"),
        ("email and self service portal", "policy_it_acceptable_use.txt", "3.1"),
        ("home office equipment", "policy_finance_reimbursement.txt", "3.1"),
        ("work from home allowance", "policy_finance_reimbursement.txt", "3.1"),
        ("da and meal", "policy_finance_reimbursement.txt", "2.6"),
        ("meal receipts", "policy_finance_reimbursement.txt", "2.6"),
        ("same day", "policy_finance_reimbursement.txt", "2.6"),
    ]

    for pattern, document_name, clause_id in rules:
        if pattern in q:
            doc = documents.get(document_name)
            if doc:
                for clause in doc["clauses"]:
                    if clause["id"] == clause_id:
                        return {
                            "document_name": document_name,
                            "clause_id": clause_id,
                            "text": clause["text"],
                        }

    best_match = None
    best_score = 0
    for document_name, doc in documents.items():
        for clause in doc["clauses"]:
            clause_text = _normalize(clause["text"])
            clause_tokens = set(clause_text.split())
            overlap = len(q_tokens & clause_tokens)
            if overlap > best_score:
                best_score = overlap
                best_match = {
                    "document_name": document_name,
                    "clause_id": clause["id"],
                    "text": clause["text"],
                }

    if best_score >= 4:
        return best_match
    return None


def answer_question(question, documents):
    """Return a single-source answer with citation or the required refusal template."""
    match = _find_best_clause(question, documents)
    if not match:
        return REFUSAL_TEMPLATE

    return (
        f"{match['text']} "
        f"Source: {match['document_name']} (Section {match['clause_id']})"
    )


def main():
    parser = argparse.ArgumentParser(description="UC-X: Ask questions about policy documents")
    parser.add_argument("--question", help="Ask a single policy question and exit")
    args = parser.parse_args()

    documents = retrieve_documents()

    if args.question:
        print(answer_question(args.question, documents))
        return

    print("UC-X Policy Assistant")
    print("Type a question about the policy documents. Type 'exit' to quit.\n")

    while True:
        user_input = input("Question: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            break
        print(answer_question(user_input, documents))
        print()


if __name__ == "__main__":
    main()
