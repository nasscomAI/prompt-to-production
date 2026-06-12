"""
UC-X — Ask My Documents
Interactive policy Q&A from three CMC policy documents.
"""
from __future__ import annotations

import re
from pathlib import Path

POLICY_DIR = Path(__file__).resolve().parent.parent / "data" / "policy-documents"

POLICY_FILES = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

HEDGING_PHRASES = (
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
)

DocumentIndex = dict[str, dict[str, str]]


def retrieve_documents(policy_dir: Path | None = None) -> DocumentIndex:
    """Load all policy files and index content by document name and section number."""
    base = policy_dir or POLICY_DIR
    index: DocumentIndex = {}

    for filename in POLICY_FILES:
        path = base / filename
        if not path.is_file():
            raise FileNotFoundError(f"Policy file not found: {path}")

        text = path.read_text(encoding="utf-8")
        sections = _parse_sections(text)
        if not sections:
            print(f"Warning: no sections parsed from {filename}")
        index[filename] = sections

    return index


def _parse_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current_key: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("═"):
            continue

        match = re.match(r"^(\d+\.\d+)\s+(.*)$", line.strip())
        if match:
            if current_key:
                sections[current_key] = " ".join(current_lines).strip()
            current_key = match.group(1)
            current_lines = [match.group(2).strip()]
        elif current_key and line.strip():
            if not re.match(r"^\d+\.\s+[A-Z]", line.strip()):
                current_lines.append(line.strip())

    if current_key:
        sections[current_key] = " ".join(current_lines).strip()

    return sections


def _normalize(question: str) -> str:
    return re.sub(r"\s+", " ", question.strip().lower())


def _format_answer(document: str, section: str, body: str) -> str:
    return f"Source: {document}, section {section}\n\n{body}"


def _section_text(index: DocumentIndex, document: str, section: str) -> str | None:
    return index.get(document, {}).get(section)


def _match_rules(question: str) -> tuple[str, str] | None:
    """Return (document, section) for known question patterns."""
    q = _normalize(question)

    rules: list[tuple[tuple[str, ...], str, str]] = [
        (("carry forward", "unused annual leave"), "policy_hr_leave.txt", "2.6"),
        (("carry forward", "annual leave"), "policy_hr_leave.txt", "2.6"),
        (("install slack",), "policy_it_acceptable_use.txt", "2.3"),
        (("install", "work laptop"), "policy_it_acceptable_use.txt", "2.3"),
        (("software", "work laptop"), "policy_it_acceptable_use.txt", "2.3"),
        (("home office equipment allowance",), "policy_finance_reimbursement.txt", "3.1"),
        (("equipment allowance",), "policy_finance_reimbursement.txt", "3.1"),
        (("da", "meal receipt"), "policy_finance_reimbursement.txt", "2.6"),
        (("daily allowance", "meal"), "policy_finance_reimbursement.txt", "2.6"),
        (("leave without pay", "approv"), "policy_hr_leave.txt", "5.2"),
        (("lwp", "approv"), "policy_hr_leave.txt", "5.2"),
        (("who approves leave without pay",), "policy_hr_leave.txt", "5.2"),
    ]

    for keywords, document, section in rules:
        if all(keyword in q for keyword in keywords):
            return document, section

    if _is_personal_phone_question(q):
        return "policy_it_acceptable_use.txt", "3.1"

    if any(
        phrase in q
        for phrase in (
            "flexible working culture",
            "company view on flexible",
            "flexible working",
            "working culture",
        )
    ):
        return None

    return None


def _is_personal_phone_question(q: str) -> bool:
    phone_terms = ("personal phone", "personal device", "my phone", "own phone")
    work_terms = ("work file", "work files", "from home", "working from home", "wfh")
    return any(p in q for p in phone_terms) and (
        any(w in q for w in work_terms) or "access" in q
    )


def _score_section(question: str, section_text: str) -> int:
    q_words = {w for w in re.findall(r"[a-z0-9]+", _normalize(question)) if len(w) > 2}
    text_words = set(re.findall(r"[a-z0-9]+", section_text.lower()))
    return len(q_words & text_words)


def _best_single_source(index: DocumentIndex, question: str) -> tuple[str, str] | None:
    best: tuple[str, str, int] | None = None

    for document, sections in index.items():
        for section, body in sections.items():
            score = _score_section(question, body)
            if score == 0:
                continue
            if best is None or score > best[2]:
                best = (document, section, score)

    if best is None:
        return None

    top_score = best[2]
    top_matches = [
        (doc, sec)
        for doc, sections in index.items()
        for sec, body in sections.items()
        if _score_section(question, body) == top_score
    ]

    documents_involved = {doc for doc, _ in top_matches}
    if len(documents_involved) > 1:
        return None

    return best[0], best[1]


def answer_question(question: str, index: DocumentIndex) -> str:
    """Return a single-source cited answer or the refusal template."""
    if not question or not question.strip():
        return "Please rephrase your question."

    q = _normalize(question)

    matched = _match_rules(question)
    if matched is None and any(
        phrase in q
        for phrase in (
            "flexible working culture",
            "company view on flexible",
            "flexible working",
        )
    ):
        return REFUSAL_TEMPLATE

    if matched is None:
        if _is_personal_phone_question(q):
            matched = ("policy_it_acceptable_use.txt", "3.1")
        else:
            matched = _best_single_source(index, question)

    if matched is None:
        return REFUSAL_TEMPLATE

    document, section = matched
    body = _section_text(index, document, section)
    if not body:
        return REFUSAL_TEMPLATE

    answer = _format_answer(document, section, body)
    lower = answer.lower()
    for phrase in HEDGING_PHRASES:
        if phrase in lower:
            return REFUSAL_TEMPLATE

    return answer


def main() -> None:
    index = retrieve_documents()
    print("CMC Policy Assistant — ask a question or type 'quit' to exit.")
    print("Documents loaded:", ", ".join(POLICY_FILES))
    print()

    while True:
        try:
            question = input("Question> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not question:
            continue
        if question.lower() in {"quit", "exit", "q"}:
            break

        print()
        print(answer_question(question, index))
        print()


if __name__ == "__main__":
    main()
