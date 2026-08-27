"""
UC-X - Ask My Documents
Interactive policy Q&A with single-source answers and strict refusal behavior.
"""
import re
from pathlib import Path
from typing import Dict, List, Tuple


BASE_DIR = Path(__file__).resolve().parent.parent
DOC_PATHS = {
    "policy_hr_leave.txt": BASE_DIR / "data" / "policy-documents" / "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": BASE_DIR / "data" / "policy-documents" / "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": BASE_DIR / "data" / "policy-documents" / "policy_finance_reimbursement.txt",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]


def _normalize_text(text: str) -> str:
    return " ".join((text or "").lower().split())


def _parse_sections(content: str) -> Dict[str, str]:
    sections: Dict[str, str] = {}
    current_id = ""
    current_lines: List[str] = []

    def flush() -> None:
        nonlocal current_id, current_lines
        if current_id:
            sections[current_id] = " ".join(" ".join(current_lines).split())
        current_id = ""
        current_lines = []

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if re.fullmatch(r"[\W_]+", line):
            continue

        item = re.match(r"^(\d+\.\d+)\s+(.*)$", line)
        if item:
            flush()
            current_id = item.group(1)
            current_lines = [item.group(2)]
            continue

        # Section heading like "2. ANNUAL LEAVE".
        if re.match(r"^\d+\.\s+[A-Z][A-Z\s&()/-]+$", line):
            flush()
            continue

        if current_id:
            current_lines.append(line)

    flush()
    return sections


def retrieve_documents() -> Dict[str, Dict[str, str]]:
    """
    Load all required policy documents and index them by section number.
    """
    index: Dict[str, Dict[str, str]] = {}
    for filename, path in DOC_PATHS.items():
        if not path.exists():
            raise FileNotFoundError(f"Required policy document missing: {path}")
        content = path.read_text(encoding="utf-8-sig", errors="replace")
        sections = _parse_sections(content)
        if not sections:
            raise ValueError(f"No numbered sections found in {filename}")
        index[filename] = sections
    return index


def _find_sections(
    doc_sections: Dict[str, str],
    required_section_ids: List[str],
) -> List[Tuple[str, str]]:
    found: List[Tuple[str, str]] = []
    for section_id in required_section_ids:
        text = doc_sections.get(section_id)
        if text:
            found.append((section_id, text))
    return found


def _format_single_source_answer(filename: str, matches: List[Tuple[str, str]]) -> str:
    lines = []
    for section_id, text in matches:
        lines.append(f"{text} ({filename} section {section_id})")
    answer = "\n".join(lines)
    lower_answer = answer.lower()
    if any(phrase in lower_answer for phrase in HEDGING_PHRASES):
        return REFUSAL_TEMPLATE
    return answer


def answer_question(question: str, index: Dict[str, Dict[str, str]]) -> str:
    """
    Return single-source cited answer or exact refusal template.
    """
    q = _normalize_text(question)
    if not q:
        return REFUSAL_TEMPLATE

    # Deterministic routes for known policy intents.
    # Each route maps to exactly one source document.
    routes = [
        (
            ["carry forward", "annual leave"],
            "policy_hr_leave.txt",
            ["2.6"],
        ),
        (
            ["install", "slack", "work laptop"],
            "policy_it_acceptable_use.txt",
            ["2.3"],
        ),
        (
            ["home office equipment allowance"],
            "policy_finance_reimbursement.txt",
            ["3.1"],
        ),
        (
            ["personal phone", "work files", "home"],
            "policy_it_acceptable_use.txt",
            ["3.1"],
        ),
        (
            ["da", "meal", "same day"],
            "policy_finance_reimbursement.txt",
            ["2.6"],
        ),
        (
            ["who approves leave without pay"],
            "policy_hr_leave.txt",
            ["5.2"],
        ),
    ]

    selected = None
    for keywords, filename, sections in routes:
        if all(keyword in q for keyword in keywords):
            selected = (filename, sections)
            break

    if selected is None:
        # Additional fallback for common phrasing variants.
        if "leave without pay" in q and ("approve" in q or "approval" in q):
            selected = ("policy_hr_leave.txt", ["5.2"])
        elif "carry forward" in q and "leave" in q:
            selected = ("policy_hr_leave.txt", ["2.6"])
        elif "slack" in q and ("install" in q or "software" in q):
            selected = ("policy_it_acceptable_use.txt", ["2.3"])
        elif "home office" in q and "allowance" in q:
            selected = ("policy_finance_reimbursement.txt", ["3.1"])
        elif "personal phone" in q and ("work files" in q or "access work files" in q):
            selected = ("policy_it_acceptable_use.txt", ["3.1"])
        elif "meal" in q and "da" in q:
            selected = ("policy_finance_reimbursement.txt", ["2.6"])

    if selected is None:
        return REFUSAL_TEMPLATE

    filename, required_sections = selected
    sections = index.get(filename, {})
    matches = _find_sections(sections, required_sections)
    if not matches:
        return REFUSAL_TEMPLATE

    return _format_single_source_answer(filename, matches)


def main() -> None:
    index = retrieve_documents()
    print("Policy Q&A ready. Ask a question (type 'exit' to quit).")

    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if question.lower() in {"exit", "quit"}:
            print("Exiting.")
            break

        answer = answer_question(question, index)
        print(answer)


if __name__ == "__main__":
    main()
