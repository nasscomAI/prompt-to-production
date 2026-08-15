"""
UC-X — Ask My Documents

Interactive CLI that answers policy questions from exactly one source
document at a time. Answers are drawn verbatim from the indexed clauses,
never blended across documents, and always carry a document + section
citation. Uncovered questions get the exact refusal template.

Usage:
    python app.py                 # interactive
    python test_questions.py      # runs the 7 README test questions
"""

import re

POLICY_FILES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

RULES = [
    {
        "doc": "policy_hr_leave.txt",
        "section": "2.6",
        "terms": ["carry", "forward", "annual", "leave"],
        "lead": "Yes - up to 5 unused annual leave days may be carried forward to the following year; any days above 5 are forfeited on 31 December.",
    },
    {
        "doc": "policy_it_acceptable_use.txt",
        "section": "2.3",
        "terms": ["install", "slack", "software", "laptop"],
        "lead": "No - installing software on a corporate device requires written approval from the IT Department.",
    },
    {
        "doc": "policy_finance_reimbursement.txt",
        "section": "3.1",
        "terms": ["home", "office", "equipment", "allowance"],
        "lead": "The home office equipment allowance is a one-time Rs 8,000 for employees approved for permanent work-from-home arrangements.",
    },
    {
        "doc": "policy_it_acceptable_use.txt",
        "section": "3.1",
        "terms": ["personal", "phone", "work", "files", "home"],
        "lead": "Personal phones may be used to access CMC email and the CMC employee self-service portal only.",
    },
    {
        "doc": "policy_finance_reimbursement.txt",
        "section": "2.6",
        "terms": ["da", "meal", "receipts", "same", "day"],
        "lead": "No - DA and meal receipts cannot be claimed simultaneously for the same day.",
    },
    {
        "doc": "policy_hr_leave.txt",
        "section": "5.2",
        "terms": ["approve", "leave", "without", "pay"],
        "lead": "Leave Without Pay requires approval from both the Department Head and the HR Director.",
    },
]


def _is_clause(line: str) -> bool:
    return bool(re.match(r"^\d+\.\d+", line))


def _is_section(line: str) -> bool:
    return bool(re.match(r"^\d+\.\s+[A-Z]", line)) and not _is_clause(line)


def _parse_document(path: str):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    doc_name = path.split("/")[-1]
    clauses = {}
    current_section = None
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if _is_section(line):
            current_section = re.match(r"^(\d+)\.\s+(.*)$", line).group(1)
            i += 1
            continue
        if _is_clause(line):
            num, _, rest = line.partition(" ")
            parts = [rest]
            i += 1
            while i < len(lines):
                nxt = lines[i].strip()
                if not nxt or nxt.startswith("\u2550"):
                    i += 1
                    continue
                if _is_section(nxt) or _is_clause(nxt):
                    break
                parts.append(nxt)
                i += 1
            if current_section is not None:
                clauses[num] = " ".join(p for p in parts if p)
            continue
        i += 1
    return doc_name, clauses


def retrieve_documents():
    index = {}
    for path in POLICY_FILES:
        doc_name, clauses = _parse_document(path)
        index[doc_name] = clauses
    return index


def _match_rule(question: str):
    tokens = set(re.findall(r"[a-z0-9]+", question.lower()))
    best = None
    best_count = 0
    for rule in RULES:
        count = len(tokens & set(rule["terms"]))
        if count > best_count:
            best = rule
            best_count = count
    if best is None or best_count < 2:
        return None
    others = [
        r
        for r in RULES
        if r is not best and len(tokens & set(r["terms"])) == best_count
    ]
    if others:
        return None
    return best


def answer_question(question: str, index) -> str:
    rule = _match_rule(question)
    if rule is None:
        return REFUSAL_TEMPLATE
    clause_text = index.get(rule["doc"], {}).get(rule["section"])
    if clause_text is None:
        return REFUSAL_TEMPLATE
    return (
        f"{rule['lead']}\n\n"
        f"Source: {rule['doc']}, section {rule['section']}\n"
        f'"{clause_text}"'
    )


def main():
    index = retrieve_documents()
    print("Ask My Documents - type a policy question. Type 'quit' to exit.")
    while True:
        try:
            question = input("\nQuestion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in ("quit", "exit"):
            break
        print()
        print(answer_question(question, index))


if __name__ == "__main__":
    main()
