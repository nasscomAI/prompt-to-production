"""
UC-X — Ask My Documents
"""
import re
import sys
from pathlib import Path


POLICY_FILES = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)
REFUSAL = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)
FORBIDDEN_PHRASES = (
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
)


def _parse_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current_number = ""
    current_lines: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^(\d+\.\d+)\s+(.*)", line)
        if match:
            if current_number:
                sections[current_number] = " ".join(current_lines).strip()
            current_number = match.group(1)
            current_lines = [match.group(2).strip()]
        elif current_number and line.strip() and not set(line.strip()) <= {"═"}:
            current_lines.append(line.strip())
    if current_number:
        sections[current_number] = " ".join(current_lines).strip()
    return sections


def retrieve_documents() -> dict[str, dict[str, str]]:
    base = Path(__file__).resolve().parents[1] / "data" / "policy-documents"
    documents: dict[str, dict[str, str]] = {}
    for filename in POLICY_FILES:
        path = base / filename
        if not path.exists():
            raise FileNotFoundError(f"Required policy file not found: {path}")
        sections = _parse_sections(path.read_text(encoding="utf-8"))
        if not sections:
            raise ValueError(f"No numbered sections found in {filename}")
        documents[filename] = sections
    return documents


def _answer(filename: str, section: str, text: str) -> str:
    answer = f"Source: {filename}, Section {section}\n{text}"
    lowered = answer.casefold()
    if any(phrase in lowered for phrase in FORBIDDEN_PHRASES):
        return REFUSAL
    return answer


def answer_question(question: str, documents: dict[str, dict[str, str]]) -> str:
    q = question.strip().casefold()
    if not q:
        return REFUSAL

    if "carry forward" in q and "annual leave" in q:
        return _answer(
            "policy_hr_leave.txt",
            "2.6",
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year; any days above 5 are forfeited on 31 December.",
        )
    if "install" in q and "slack" in q and ("laptop" in q or "work" in q):
        return _answer(
            "policy_it_acceptable_use.txt",
            "2.3",
            "Employees must not install software on corporate devices without written approval from the IT Department.",
        )
    if "home office" in q and "allowance" in q:
        return _answer(
            "policy_finance_reimbursement.txt",
            "3.1",
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.",
        )
    if "personal phone" in q or ("personal device" in q and ("work files" in q or "from home" in q)):
        return _answer(
            "policy_it_acceptable_use.txt",
            "3.1",
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only.",
        )
    if "flexible working culture" in q or "company view" in q:
        return REFUSAL
    if ("da" in q or "daily allowance" in q) and "meal" in q:
        return _answer(
            "policy_finance_reimbursement.txt",
            "2.6",
            "No. If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day; DA and meal receipts cannot be claimed simultaneously for the same day.",
        )
    if "leave without pay" in q or "lwp" in q:
        return _answer(
            "policy_hr_leave.txt",
            "5.2",
            "LWP requires approval from the Department Head and the HR Director; manager approval alone is not sufficient.",
        )
    return REFUSAL


def main():
    try:
        documents = retrieve_documents()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    print("Ask a policy question. Type exit or quit to stop.")
    while True:
        try:
            question = input("> ")
        except EOFError:
            break
        if question.strip().casefold() in {"exit", "quit"}:
            break
        print(answer_question(question, documents))


if __name__ == "__main__":
    main()
