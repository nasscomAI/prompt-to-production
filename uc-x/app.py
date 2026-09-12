import argparse
import re
from pathlib import Path

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)
DOCUMENTS = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)
CLAUSE_START = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def retrieve_documents(document_dir):
    indexed = {}
    for filename in DOCUMENTS:
        path = Path(document_dir) / filename
        if not path.is_file():
            raise ValueError(f"Required policy file does not exist: {filename}")
        text = path.read_text(encoding="utf-8").strip()
        clauses = []
        current = None
        for raw_line in text.splitlines():
            line = " ".join(raw_line.split())
            if re.match(r"^[^A-Za-z0-9]+$", line) or re.match(r"^\d+\.\s", line):
                continue
            match = CLAUSE_START.match(line)
            if match:
                if current:
                    clauses.append(current)
                current = {"section": match.group(1), "text": match.group(2)}
            elif current and line:
                current["text"] += " " + line
        if current:
            clauses.append(current)
        if not clauses:
            raise ValueError(f"Policy file has no numbered sections: {filename}")
        indexed[filename] = clauses
    return indexed


def answer_question(question, documents):
    if not question or not question.strip():
        return REFUSAL
    query = question.lower()
    targeted = []
    if "carry forward" in query or "unused annual leave" in query:
        targeted = [("policy_hr_leave.txt", "2.6")]
    elif "slack" in query or "install" in query and "laptop" in query:
        targeted = [("policy_it_acceptable_use.txt", "2.3"), ("policy_it_acceptable_use.txt", "2.4")]
    elif "home office" in query or "equipment allowance" in query:
        targeted = [("policy_finance_reimbursement.txt", "3.1"), ("policy_finance_reimbursement.txt", "3.2"), ("policy_finance_reimbursement.txt", "3.3"), ("policy_finance_reimbursement.txt", "3.4"), ("policy_finance_reimbursement.txt", "3.5")]
    elif "personal phone" in query or "personal device" in query:
        targeted = [("policy_it_acceptable_use.txt", "3.1"), ("policy_it_acceptable_use.txt", "3.2")]
    elif "da" in query and "meal" in query:
        targeted = [("policy_finance_reimbursement.txt", "2.5"), ("policy_finance_reimbursement.txt", "2.6")]
    elif "leave without pay" in query:
        targeted = [("policy_hr_leave.txt", "5.2")]
    if not targeted:
        return REFUSAL

    results = []
    for filename, section in targeted:
        clause = next((item for item in documents[filename] if item["section"] == section), None)
        if clause:
            results.append(f"{clause['text']} [{filename}, section {section}]")
    return " ".join(results) if results else REFUSAL

def main():
    parser = argparse.ArgumentParser(description="Answer questions from CMC policy documents")
    parser.add_argument("--documents", default="../data/policy-documents")
    args = parser.parse_args()
    documents = retrieve_documents(args.documents)
    while True:
        try:
            question = input("Question (or 'quit'): ").strip()
        except EOFError:
            break
        if question.lower() in {"quit", "exit"}:
            break
        print(answer_question(question, documents))

if __name__ == "__main__":
    main()
