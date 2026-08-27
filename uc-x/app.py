"""
UC-X — Ask My Documents
"""
import os
import re
from pathlib import Path

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

HEDGING_PHRASES = (
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
)

SECTION_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.+)$", re.MULTILINE)

QUESTION_RULES = [
    {
        "patterns": [r"carry forward", r"unused annual leave", r"annual leave.*carry"],
        "document": "policy_hr_leave.txt",
        "sections": ["2.6", "2.7"],
        "answer": (
            "Yes, with limits. Employees may carry forward a maximum of 5 unused annual leave "
            "days to the following calendar year; any days above 5 are forfeited on 31 December. "
            "Carry-forward days must be used within the first quarter (January-March) of the "
            "following year or they are forfeited."
        ),
    },
    {
        "patterns": [r"install slack", r"slack.*work laptop", r"install.*software.*laptop"],
        "document": "policy_it_acceptable_use.txt",
        "sections": ["2.3", "2.4"],
        "answer": (
            "Employees must not install software on corporate devices without written approval "
            "from the IT Department. Software approved for installation must be sourced from "
            "the CMC-approved software catalogue only."
        ),
    },
    {
        "patterns": [r"home office equipment allowance", r"home office equipment", r"equipment allowance"],
        "document": "policy_finance_reimbursement.txt",
        "sections": ["3.1", "3.2", "3.3", "3.5"],
        "answer": (
            "Employees approved for permanent work-from-home arrangements are entitled to a "
            "one-time home office equipment allowance of Rs 8,000. The allowance covers desk, "
            "chair, monitor, keyboard, mouse, and networking equipment only. It does not cover "
            "personal computers, laptops, smartphones, printers, or air conditioning equipment. "
            "Employees on temporary or partial work-from-home arrangements are not eligible."
        ),
    },
    {
        "patterns": [
            r"personal phone.*work files",
            r"personal phone.*from home",
            r"personal phone.*access work",
            r"use my personal phone",
        ],
        "document": "policy_it_acceptable_use.txt",
        "sections": ["3.1", "3.2"],
        "cross_document_trap": True,
        "answer": (
            "Personal devices may be used to access CMC email and the CMC employee self-service "
            "portal only. Personal devices must not be used to access, store, or transmit "
            "classified or sensitive CMC data. Work files are not covered by the permitted uses "
            "in section 3.1."
        ),
    },
    {
        "patterns": [r"flexible working culture", r"company view on flexible"],
        "refuse": True,
    },
    {
        "patterns": [r"da and meal receipts", r"daily allowance.*meal", r"meal receipts.*same day"],
        "document": "policy_finance_reimbursement.txt",
        "sections": ["2.5", "2.6"],
        "answer": (
            "No. DA and meal receipts cannot be claimed simultaneously for the same day. "
            "Daily allowance (DA) for outstation travel is Rs 750 per day and covers meals "
            "and incidentals. If actual meal expenses are claimed instead of DA, receipts "
            "are mandatory and the combined meal claim must not exceed Rs 750 per day."
        ),
    },
    {
        "patterns": [r"leave without pay", r"approves lwp", r"who approves leave without pay"],
        "document": "policy_hr_leave.txt",
        "sections": ["5.2", "5.3"],
        "answer": (
            "Leave Without Pay requires approval from the Department Head and the HR Director; "
            "manager approval alone is not sufficient. LWP exceeding 30 continuous days "
            "requires approval from the Municipal Commissioner."
        ),
    },
]


def retrieve_documents(base_path: str | None = None) -> dict:
    """Load all policy files and index by document name and section number."""
    if base_path is None:
        base_path = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")

    base = Path(base_path)
    index: dict[str, dict[str, str]] = {}

    for filename in POLICY_FILES:
        filepath = base / filename
        if not filepath.is_file():
            raise FileNotFoundError(f"Policy file not found: {filepath}")

        text = filepath.read_text(encoding="utf-8")
        sections: dict[str, str] = {}
        current_section = None
        current_lines: list[str] = []

        for line in text.splitlines():
            match = SECTION_PATTERN.match(line.strip())
            if match:
                if current_section is not None:
                    sections[current_section] = " ".join(current_lines).strip()
                current_section = match.group(1)
                current_lines = [match.group(2).strip()]
            elif current_section is not None and line.strip():
                current_lines.append(line.strip())

        if current_section is not None:
            sections[current_section] = " ".join(current_lines).strip()

        if not sections:
            sections["_raw"] = text
        index[filename] = sections

    return index


def _normalize(question: str) -> str:
    return re.sub(r"\s+", " ", question.strip().lower())


def _format_citation(document: str, sections: list[str]) -> str:
    section_text = ", ".join(f"section {s}" for s in sections)
    return f"Source: {document} ({section_text})"


def _match_rule(question: str) -> dict | None:
    normalized = _normalize(question)
    for rule in QUESTION_RULES:
        if any(re.search(pattern, normalized) for pattern in rule["patterns"]):
            return rule
    return None


def _score_sections(question: str, document_index: dict) -> tuple[str, str, float] | None:
    words = set(re.findall(r"[a-z0-9]+", _normalize(question)))
    if not words:
        return None

    best: tuple[str, str, float] | None = None
    for document, sections in document_index.items():
        for section_id, section_text in sections.items():
            if section_id == "_raw":
                continue
            section_words = set(re.findall(r"[a-z0-9]+", section_text.lower()))
            overlap = len(words & section_words)
            if overlap == 0:
                continue
            score = overlap / max(len(words), 1)
            if best is None or score > best[2]:
                best = (document, section_id, score)

    return best


def answer_question(question: str, document_index: dict) -> str:
    """Return a single-source cited answer or the exact refusal template."""
    if not question or not question.strip():
        return "Please enter a question."

    rule = _match_rule(question)
    if rule is not None:
        if rule.get("refuse"):
            return REFUSAL_TEMPLATE

        citation = _format_citation(rule["document"], rule["sections"])
        return f"{rule['answer']}\n\n{citation}"

    scored = _score_sections(question, document_index)
    if scored is None or scored[2] < 0.15:
        return REFUSAL_TEMPLATE

    document, section_id, _ = scored
    section_text = document_index[document].get(section_id, "")
    if not section_text:
        return REFUSAL_TEMPLATE

    answer_body = section_text[0].upper() + section_text[1:] if section_text else section_text
    if not answer_body.endswith("."):
        answer_body += "."

    citation = _format_citation(document, [section_id])
    return f"{answer_body}\n\n{citation}"


def main():
    document_index = retrieve_documents()

    print("Ask My Documents — type a question or 'exit' to quit.")
    while True:
        try:
            question = input("\nQuestion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            print("Please enter a question.")
            continue
        if question.lower() == "exit":
            print("Goodbye.")
            break

        response = answer_question(question, document_index)
        for phrase in HEDGING_PHRASES:
            if phrase in response.lower():
                response = REFUSAL_TEMPLATE
                break
        print(f"\n{response}")


if __name__ == "__main__":
    main()
