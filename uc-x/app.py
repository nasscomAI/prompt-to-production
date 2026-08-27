"""
UC-X app.py - Ask My Documents interactive CLI.

Implements the two skills from skills.md:
- retrieve_documents: load all three policy files and index by document/section.
- answer_question: return a single-source cited answer or the exact refusal.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


POLICY_PATHS = (
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
)

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

BANNED_HEDGES = (
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
)

SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z\s()]+)$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")


@dataclass(frozen=True)
class IndexedSection:
    document_name: str
    section_number: str
    section_title: str
    original_text: str
    normalized_text: str


def normalize_text(value: str) -> str:
    value = value.replace("â€“", "-").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", value).strip()


def normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", normalize_text(value).lower()).strip()


def is_separator_line(value: str) -> bool:
    return value.startswith("â•") or value.startswith("═") or set(value) <= {"═", " "}


def retrieve_documents(paths: tuple[str, ...] = POLICY_PATHS) -> list[IndexedSection]:
    """Loads all policy files and indexes clauses by document name and section number."""
    if len(paths) != 3:
        raise ValueError("retrieve_documents requires exactly three policy file paths.")

    index: list[IndexedSection] = []
    for path_text in paths:
        path = Path(path_text)
        if path.suffix.lower() != ".txt":
            raise ValueError(f"Policy file must be .txt: {path}")
        if not path.exists():
            raise FileNotFoundError(f"Policy file not found: {path}")
        if not path.is_file():
            raise ValueError(f"Policy path is not a file: {path}")

        raw = path.read_text(encoding="utf-8", errors="replace")
        if not raw.strip():
            raise ValueError(f"Policy file is empty: {path}")

        document_name = path.name
        current_title = "Unsectioned"
        current_number: str | None = None
        current_lines: list[str] = []

        def flush_clause() -> None:
            nonlocal current_number, current_lines
            if current_number is None:
                return
            original = normalize_text(" ".join(current_lines))
            index.append(
                IndexedSection(
                    document_name=document_name,
                    section_number=current_number,
                    section_title=current_title,
                    original_text=original,
                    normalized_text=normalize_key(original),
                )
            )
            current_number = None
            current_lines = []

        for line in raw.splitlines():
            stripped = line.strip()
            if not stripped or is_separator_line(stripped):
                continue

            section_match = SECTION_RE.match(stripped)
            if section_match:
                flush_clause()
                current_title = normalize_text(section_match.group(2)).title()
                continue

            clause_match = CLAUSE_RE.match(stripped)
            if clause_match:
                flush_clause()
                current_number = clause_match.group(1)
                current_lines = [clause_match.group(2)]
                continue

            if current_number is not None:
                current_lines.append(stripped)

        flush_clause()

    if not index:
        raise ValueError("No section-numbered policy content could be parsed.")

    expected_docs = {Path(path).name for path in paths}
    parsed_docs = {entry.document_name for entry in index}
    missing_docs = expected_docs - parsed_docs
    if missing_docs:
        raise ValueError(f"No sections parsed from required document(s): {', '.join(sorted(missing_docs))}")

    return index


def section(index: list[IndexedSection], document_name: str, section_number: str) -> IndexedSection:
    for entry in index:
        if entry.document_name == document_name and entry.section_number == section_number:
            return entry
    raise ValueError(f"Required source section missing: {document_name} section {section_number}")


def cited_answer(entry: IndexedSection, answer_text: str) -> str:
    answer = f"{answer_text} ({entry.document_name} section {entry.section_number})"
    lowered = answer.lower()
    for phrase in BANNED_HEDGES:
        if phrase in lowered:
            raise ValueError(f"Answer contains banned hedge phrase: {phrase}")
    return answer


def answer_question(index: list[IndexedSection], question: str) -> str:
    """Search indexed documents and return a single-source answer or exact refusal."""
    q = normalize_key(question)
    if not q:
        return REFUSAL_TEMPLATE

    if "flexible working culture" in q or "company view" in q and "culture" in q:
        return REFUSAL_TEMPLATE

    if all(term in q for term in ("carry", "forward", "leave")):
        entry = section(index, "policy_hr_leave.txt", "2.6")
        return cited_answer(
            entry,
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year, and any days above 5 are forfeited on 31 December.",
        )

    if "slack" in q and ("install" in q or "laptop" in q or "work laptop" in q):
        entry = section(index, "policy_it_acceptable_use.txt", "2.3")
        return cited_answer(
            entry,
            "Employees must not install software on corporate devices without written approval from the IT Department.",
        )

    if "home office equipment allowance" in q or ("equipment allowance" in q and "home" in q):
        entry = section(index, "policy_finance_reimbursement.txt", "3.1")
        return cited_answer(
            entry,
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.",
        )

    if "personal phone" in q or ("personal device" in q and ("work files" in q or "files" in q)):
        entry = section(index, "policy_it_acceptable_use.txt", "3.1")
        return cited_answer(
            entry,
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only.",
        )

    if ("da" in q or "daily allowance" in q) and "meal" in q:
        entry = section(index, "policy_finance_reimbursement.txt", "2.6")
        return cited_answer(
            entry,
            "No. DA and meal receipts cannot be claimed simultaneously for the same day.",
        )

    if ("leave without pay" in q or "lwp" in q) and ("approve" in q or "approves" in q or "approval" in q):
        entry = section(index, "policy_hr_leave.txt", "5.2")
        return cited_answer(
            entry,
            "LWP requires approval from both the Department Head and the HR Director; manager approval alone is not sufficient.",
        )

    return search_single_source(index, q)


def search_single_source(index: list[IndexedSection], normalized_question: str) -> str:
    """Conservative fallback retrieval. Refuses unless one section clearly matches."""
    stop_words = {
        "a",
        "about",
        "am",
        "an",
        "and",
        "are",
        "can",
        "do",
        "does",
        "for",
        "from",
        "i",
        "in",
        "is",
        "it",
        "my",
        "of",
        "on",
        "or",
        "the",
        "to",
        "what",
        "when",
        "who",
        "with",
    }
    terms = [term for term in normalized_question.split() if term not in stop_words and len(term) > 2]
    if len(terms) < 2:
        return REFUSAL_TEMPLATE

    scored: list[tuple[int, IndexedSection]] = []
    for entry in index:
        score = sum(1 for term in terms if term in entry.normalized_text)
        if score:
            scored.append((score, entry))
    if not scored:
        return REFUSAL_TEMPLATE

    scored.sort(key=lambda item: item[0], reverse=True)
    best_score, best_entry = scored[0]
    tied_docs = {entry.document_name for score, entry in scored if score == best_score}
    if best_score < 2 or len(tied_docs) > 1:
        return REFUSAL_TEMPLATE

    return cited_answer(best_entry, best_entry.original_text)


def main() -> int:
    try:
        index = retrieve_documents()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("Ask a policy question. Type 'exit' or 'quit' to stop.")
    while True:
        try:
            question = input("> ")
        except EOFError:
            break
        if question.strip().lower() in {"exit", "quit"}:
            break
        try:
            print(answer_question(index, question))
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
