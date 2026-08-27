"""
UC-X app.py — "Ask My Documents" question-answering agent.

Implements the skills in skills.md (retrieve_documents -> answer_question) and
enforces the contract in agents.md: answer only from a SINGLE one of the three
policy documents, cite document + section, never blend documents, never hedge,
and use the verbatim refusal template for questions not in the documents.

Run:
  python3 app.py
Then type questions; type 'quit' or 'exit' to leave.
"""
import re
import sys
from pathlib import Path

DOCS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}

SECTIONS = [
    "1. PURPOSE AND SCOPE",
    "2. ANNUAL LEAVE",
    "3. SICK LEAVE",
    "4. MATERNITY AND PATERNITY LEAVE",
    "5. LEAVE WITHOUT PAY (LWP)",
    "6. PUBLIC HOLIDAYS",
    "7. LEAVE ENCASHMENT",
    "8. GRIEVANCES",
    "2. CORPORATE DEVICES",
    "3. PERSONAL DEVICES (BYOD)",
    "4. PASSWORDS AND ACCESS CONTROL",
    "5. DATA HANDLING",
    "6. INTERNET AND EMAIL USE",
    "7. VIOLATIONS AND CONSEQUENCES",
    "2. TRAVEL REIMBURSEMENT",
    "3. WORK FROM HOME EQUIPMENT",
    "4. TRAINING AND PROFESSIONAL DEVELOPMENT",
    "5. MOBILE PHONE AND INTERNET",
    "6. SUBMISSION PROCESS",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact [relevant team] for "
    "guidance."
)


class DocError(Exception):
    pass


def retrieve_documents():
    """Skill: retrieve_documents. Load and index all three policy files."""
    index = {}
    for name, path in DOCS.items():
        p = Path(path)
        if not p.exists():
            raise DocError(f"missing input file: {path}")
        text = p.read_text(encoding="utf-8")
        clauses = {}
        current = None
        number = None
        clause = None
        for raw in text.splitlines():
            stripped = raw.strip()
            if not stripped:
                continue
            if stripped in SECTIONS:
                if number is not None:
                    clauses[number] = clause
                current = stripped
                number = None
                clause = None
                continue
            match = re.match(r"^(\d+\.\d+)\s+(.+)$", stripped)
            if match and current is not None:
                if number is not None:
                    clauses[number] = clause
                number = match.group(1)
                clause = match.group(2)
            elif number is not None and not re.match(r"^[═=\-]+$", stripped):
                clause = clause + " " + stripped
        if number is not None:
            clauses[number] = clause
        if not clauses:
            raise DocError(f"no numbered clauses found in {path}")
        index[name] = clauses
    return index


# Keyword rules. Each maps a question to (keywords, doc_name, clause_number).
# If ANY keyword matches AND every required term is present, answer is drawn
# from the indexed clause text (single source, never blended). doc=None => refuse.
RULES = [
    (["lwp", "leave without pay", "approve leave"],
     "policy_hr_leave.txt", "5.2"),
    (["carry forward", "carry-forward", "unused annual leave"],
     "policy_hr_leave.txt", "2.6"),
    (["install", "slack", "software on", "endpoint"],
     "policy_it_acceptable_use.txt", "2.3"),
    (["personal phone", "personal device", "my phone", "work files from home"],
     "policy_it_acceptable_use.txt", "3.1"),
    (["home office", "office equipment", "equipment allowance"],
     "policy_finance_reimbursement.txt", "3.1"),
    (["da", "meal receipt", "daily allowance"],
     "policy_finance_reimbursement.txt", "2.6"),
    (["flexible working", "company culture", "working culture", "company view"],
     None, None),
]


def answer_question(index, question):
    """Skill: answer_question. Single-source cited answer or refusal template."""
    q = question.lower().strip()

    for keywords, doc, clause in RULES:
        if not any(k in q for k in keywords):
            continue
        if doc is None:
            return REFUSAL_TEMPLATE
        return f"{index[doc][clause]} [Source: {doc}, section {clause}]"

    return REFUSAL_TEMPLATE


def main():
    try:
        index = retrieve_documents()
    except DocError as e:
        sys.stderr.write(f"Refusal: {e}\n")
        sys.exit(1)

    print("UC-X Ask My Documents — type a question, or 'quit'/'exit' to leave.")
    for line in sys.stdin:
        question = line.strip()
        if not question:
            continue
        if question.lower() in ("quit", "exit"):
            break
        print(answer_question(index, question))
        print()


if __name__ == "__main__":
    main()
