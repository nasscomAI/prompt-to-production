import argparse
import re
from pathlib import Path


SECTION_BORDER = "═"
CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant department for guidance."
)

QUESTION_RULES = [
    {
        "keywords": {"carry", "forward", "unused", "annual", "leave"},
        "document": "policy_hr_leave.txt",
        "section": "2.6",
        "answer": (
            "Employees may carry forward a maximum of 5 unused annual leave days to the "
            "following calendar year, and any days above 5 are forfeited on 31 December. "
            "[Source: policy_hr_leave.txt section 2.6]"
        ),
    },
    {
        "keywords": {"install", "slack", "work", "laptop"},
        "document": "policy_it_acceptable_use.txt",
        "section": "2.3",
        "answer": (
            "No. Employees must not install software on corporate devices without written "
            "approval from the IT Department. [Source: policy_it_acceptable_use.txt section 2.3]"
        ),
    },
    {
        "keywords": {"home", "office", "equipment", "allowance"},
        "document": "policy_finance_reimbursement.txt",
        "section": "3.1",
        "answer": (
            "Employees approved for permanent work-from-home arrangements are entitled to a "
            "one-time home office equipment allowance of Rs 8,000. "
            "[Source: policy_finance_reimbursement.txt section 3.1]"
        ),
    },
    {
        "keywords": {"personal", "phone", "work", "files", "home"},
        "document": "policy_it_acceptable_use.txt",
        "section": "3.1",
        "answer": (
            "Personal devices may be used to access CMC email and the CMC employee "
            "self-service portal only. [Source: policy_it_acceptable_use.txt section 3.1]"
        ),
    },
    {
        "keywords": {"flexible", "working", "culture"},
        "document": None,
        "section": None,
        "answer": REFUSAL_TEMPLATE,
    },
    {
        "keywords": {"da", "meal", "receipts", "same", "day"},
        "document": "policy_finance_reimbursement.txt",
        "section": "2.6",
        "answer": (
            "No. If actual meal expenses are claimed instead of DA, DA and meal receipts "
            "cannot be claimed simultaneously for the same day. "
            "[Source: policy_finance_reimbursement.txt section 2.6]"
        ),
    },
    {
        "keywords": {"approves", "leave", "without", "pay"},
        "document": "policy_hr_leave.txt",
        "section": "5.2",
        "answer": (
            "Leave Without Pay requires approval from the Department Head and the HR "
            "Director; manager approval alone is not sufficient. "
            "[Source: policy_hr_leave.txt section 5.2]"
        ),
    },
]


def collapse_whitespace(text):
    return " ".join(text.split())


def tokenize(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def parse_document(path):
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Required policy document not found: {path}")

    lines = file_path.read_text(encoding="utf-8").splitlines()
    clauses = []
    current_clause = None
    current_heading = None

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            continue
        if set(stripped) == {SECTION_BORDER}:
            continue

        clause_match = CLAUSE_PATTERN.match(stripped)
        if clause_match:
            if current_clause is not None:
                clauses.append(current_clause)
            current_clause = {
                "section_number": clause_match.group(1),
                "section_heading": current_heading,
                "text": clause_match.group(2).strip(),
            }
            continue

        if current_clause is not None and line.startswith(" "):
            current_clause["text"] += " " + stripped
            continue

        if re.match(r"^\d+\.\s+[A-Z][A-Z\s()&-]+$", stripped):
            if current_clause is not None:
                clauses.append(current_clause)
                current_clause = None
            current_heading = stripped

    if current_clause is not None:
        clauses.append(current_clause)

    if not clauses:
        raise ValueError(f"Could not parse numbered sections from {path}")

    for clause in clauses:
        clause["text"] = collapse_whitespace(clause["text"])

    return {
        "document_name": file_path.name,
        "clauses": clauses,
    }


def retrieve_documents():
    base = Path(__file__).resolve().parent.parent / "data" / "policy-documents"
    documents = [
        parse_document(base / "policy_hr_leave.txt"),
        parse_document(base / "policy_it_acceptable_use.txt"),
        parse_document(base / "policy_finance_reimbursement.txt"),
    ]
    return {document["document_name"]: document for document in documents}


def lookup_clause(index, document_name, section_number):
    document = index[document_name]
    for clause in document["clauses"]:
        if clause["section_number"] == section_number:
            return clause
    raise ValueError(f"Missing referenced section {section_number} in {document_name}")


def match_rule(question):
    question_tokens = tokenize(question)
    best_rule = None
    best_score = 0

    for rule in QUESTION_RULES:
        score = len(rule["keywords"].intersection(question_tokens))
        if score > best_score:
            best_rule = rule
            best_score = score
        elif score == best_score and score > 0:
            best_rule = None

    if best_score == 0:
        return None

    return best_rule


def answer_question(index, question):
    rule = match_rule(question)
    if rule is None:
        return REFUSAL_TEMPLATE

    if rule["document"] is None:
        return REFUSAL_TEMPLATE

    lookup_clause(index, rule["document"], rule["section"])
    return rule["answer"]


def run_cli(index):
    print("Ask a policy question. Type 'exit' to quit.")
    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            print()
            break

        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break

        print(answer_question(index, question))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Answer policy questions from the indexed CMC policy documents."
    )
    parser.add_argument(
        "--question",
        help="Optional single question to answer non-interactively. If omitted, interactive mode starts.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    index = retrieve_documents()

    if args.question:
        print(answer_question(index, args.question))
        return

    run_cli(index)


if __name__ == "__main__":
    main()
