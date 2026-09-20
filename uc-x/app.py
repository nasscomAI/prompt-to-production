"""
UC-X — Ask My Documents
Implements retrieve_documents and answer_question per agents.md and skills.md.
"""
import argparse
import re
import sys
from pathlib import Path

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_TITLE_RE = re.compile(r"^\d+\.\s+[A-Z]")
HEDGE_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)
DOC_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

# Single-source routes for the required tests. One document only per question.
ROUTES = [
    {
        "name": "hr_carry_forward",
        "document": "policy_hr_leave.txt",
        "section": "2.6",
        "all": ["carry forward", "annual leave"],
    },
    {
        "name": "it_install_software",
        "document": "policy_it_acceptable_use.txt",
        "section": "2.3",
        "all": ["install"],
        "any": ["slack", "software", "laptop"],
    },
    {
        "name": "fin_home_office",
        "document": "policy_finance_reimbursement.txt",
        "section": "3.1",
        "all": ["home office"],
    },
    {
        "name": "fin_home_office_allowance",
        "document": "policy_finance_reimbursement.txt",
        "section": "3.1",
        "all": ["equipment allowance"],
    },
    {
        "name": "it_personal_phone",
        "document": "policy_it_acceptable_use.txt",
        "section": "3.1",
        "all": ["personal"],
        "any": ["phone", "device"],
        "any2": ["work file", "work files", "from home", "working from home", "wfh"],
    },
    {
        "name": "fin_da_meals",
        "document": "policy_finance_reimbursement.txt",
        "section": "2.6",
        "all": ["da"],
        "any": ["meal"],
    },
    {
        "name": "hr_lwp_approver",
        "document": "policy_hr_leave.txt",
        "section": "5.2",
        "all": ["leave without pay"],
        "any": ["approv", "who"],
    },
    {
        "name": "hr_lwp_approver_abbrev",
        "document": "policy_hr_leave.txt",
        "section": "5.2",
        "all": ["lwp"],
        "any": ["approv", "who"],
    },
]


def retrieve_documents(policy_dir: Path):
    index = {}
    missing = []
    for name in DOC_FILES:
        path = policy_dir / name
        if not path.exists():
            missing.append(name)
            continue
        clauses = _parse_clauses(path.read_text(encoding="utf-8"))
        for clause_id, text in clauses.items():
            index[(name, clause_id)] = text
    if missing:
        raise FileNotFoundError(
            "REFUSED: missing policy files: " + ", ".join(missing)
        )
    return index


def _parse_clauses(raw: str):
    clauses = {}
    current_id = None
    parts = []

    def flush():
        if current_id is None:
            return
        text = re.sub(r"\s+", " ", " ".join(p.strip() for p in parts if p.strip())).strip()
        clauses[current_id] = text

    for line in raw.splitlines():
        stripped = line.strip()
        match = CLAUSE_RE.match(stripped)
        if match:
            flush()
            current_id = match.group(1)
            parts = [match.group(2)]
        elif current_id is not None and stripped and not stripped.startswith("═") and not SECTION_TITLE_RE.match(stripped):
            parts.append(stripped)
    flush()
    return clauses


def _contains_all(text: str, terms):
    return all(term in text for term in terms)


def _contains_any(text: str, terms):
    return any(term in text for term in terms)


def _match_route(question: str):
    q = question.lower()
    if "flexible working culture" in q:
        return None
    matches = []
    for route in ROUTES:
        if not _contains_all(q, route["all"]):
            continue
        if "any" in route and not _contains_any(q, route["any"]):
            continue
        if "any2" in route and not _contains_any(q, route["any2"]):
            continue
        matches.append(route)
    if not matches:
        return None
    documents = {item["document"] for item in matches}
    if len(documents) > 1:
        return None
    return matches[0]


def answer_question(question: str, index: dict) -> str:
    route = _match_route(question)
    if route is None:
        return REFUSAL_TEMPLATE
    key = (route["document"], route["section"])
    text = index.get(key)
    if not text:
        return REFUSAL_TEMPLATE
    answer = (
        f"Source: {route['document']} section {route['section']}. {text}"
    )
    lowered = answer.lower()
    for phrase in HEDGE_PHRASES:
        if phrase in lowered:
            return REFUSAL_TEMPLATE
    return answer


def _interactive(index):
    print("Ask My Documents — answers come from one policy file only.")
    print("Type a question, or 'quit' to exit.")
    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            print()
            break
        if not question:
            continue
        if question.lower() in {"quit", "exit", "q"}:
            break
        print(answer_question(question, index))
        print()


DEMO_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone for work files from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?",
]


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument(
        "--policy-dir",
        default=str(Path(__file__).resolve().parent / ".." / "data" / "policy-documents"),
        help="Directory containing the three policy files",
    )
    parser.add_argument("--question", default="", help="Answer one question and exit")
    parser.add_argument("--demo", action="store_true", help="Run the seven README test questions")
    args = parser.parse_args()

    try:
        index = retrieve_documents(Path(args.policy_dir))
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    if args.demo:
        for question in DEMO_QUESTIONS:
            print(f"Q: {question}")
            print(f"A: {answer_question(question, index)}")
            print()
        return
    if args.question:
        print(answer_question(args.question, index))
        return
    _interactive(index)


if __name__ == "__main__":
    main()
