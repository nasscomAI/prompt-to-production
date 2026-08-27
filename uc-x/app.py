"""UC-X — single-source question answering over CMC policy documents."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any, Iterable


REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact [relevant team] "
    "for guidance."
)

APP_DIR = Path(__file__).resolve().parent
DEFAULT_POLICY_PATHS = (
    APP_DIR.parent / "data/policy-documents/policy_hr_leave.txt",
    APP_DIR.parent / "data/policy-documents/policy_it_acceptable_use.txt",
    APP_DIR.parent / "data/policy-documents/policy_finance_reimbursement.txt",
)

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
HEADING_RE = re.compile(r"^(\d+)\.\s+(.+)$")
SEPARATOR_RE = re.compile(r"^═+$")
WORD_RE = re.compile(r"[a-z0-9]+")

# Explicit routes cover concepts where literal overlap is weak or where the
# wrong section could accidentally grant permission.
INTENT_ROUTES: tuple[tuple[re.Pattern[str], str, tuple[str, ...]], ...] = (
    (
        re.compile(r"\bcarry\b.*\bannual leave\b|\bannual leave\b.*\bcarry\b", re.I),
        "policy_hr_leave.txt",
        ("2.6",),
    ),
    (
        re.compile(
            r"\binstall\b.*\b(slack|software|app(?:lication)?)\b"
            r"|\b(slack|software|app(?:lication)?)\b.*\b(work|corporate)\b.*\b(laptop|device)\b",
            re.I,
        ),
        "policy_it_acceptable_use.txt",
        ("2.3",),
    ),
    (
        re.compile(
            r"\b(home office|work[- ]from[- ]home|wfh)\b.*\b(equipment )?allowance\b",
            re.I,
        ),
        "policy_finance_reimbursement.txt",
        ("3.1",),
    ),
    (
        re.compile(
            r"\bpersonal (phone|device)\b.*\bwork files?\b"
            r"|\bwork files?\b.*\bpersonal (phone|device)\b",
            re.I,
        ),
        "policy_it_acceptable_use.txt",
        ("3.1",),
    ),
    (
        re.compile(
            r"\b(da|daily allowance)\b.*\bmeal\b|\bmeal\b.*\b(da|daily allowance)\b",
            re.I,
        ),
        "policy_finance_reimbursement.txt",
        ("2.6",),
    ),
    (
        re.compile(
            r"\b(approv\w*|who)\b.*\b(leave without pay|lwp)\b"
            r"|\b(leave without pay|lwp)\b.*\bapprov\w*\b",
            re.I,
        ),
        "policy_hr_leave.txt",
        ("5.2",),
    ),
)

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "can", "company", "do",
    "does", "for", "from", "how", "i", "if", "in", "is", "it", "me",
    "my", "of", "on", "or", "our", "same", "the", "this", "to", "use",
    "what", "when", "where", "which", "who", "with", "work",
}


class PolicyError(ValueError):
    """Raised when policy documents cannot be indexed safely."""


def _collapse_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _read_document(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise PolicyError(f"Policy file not found: {path}")
    if not path.is_file():
        raise PolicyError(f"Policy path is not a file: {path}")

    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise PolicyError(f"Policy file is unreadable: {path}") from exc
    if not raw.strip():
        raise PolicyError(f"Policy file is empty: {path}")

    metadata: dict[str, str] = {"document_name": path.name}
    sections: list[dict[str, str]] = []
    current_heading = ""
    current_id: str | None = None
    current_parts: list[str] = []

    def flush_clause() -> None:
        nonlocal current_id, current_parts
        if current_id is not None:
            text = _collapse_whitespace(" ".join(current_parts))
            if not text:
                raise PolicyError(f"Empty section {current_id} in {path}")
            sections.append(
                {
                    "section_id": current_id,
                    "heading": current_heading,
                    "text": text,
                }
            )
        current_id = None
        current_parts = []

    for raw_line in raw.splitlines():
        line = raw_line.strip()
        if not line or SEPARATOR_RE.fullmatch(line):
            continue

        heading_match = HEADING_RE.fullmatch(line)
        if heading_match:
            flush_clause()
            current_heading = heading_match.group(2).strip()
            continue

        clause_match = CLAUSE_RE.match(line)
        if clause_match:
            flush_clause()
            current_id = clause_match.group(1)
            current_parts = [clause_match.group(2)]
            continue

        if current_id is not None:
            current_parts.append(line)
        elif line.lower().startswith("document reference:"):
            metadata["reference"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("version:"):
            metadata["version"] = line.split(":", 1)[1].strip()

    flush_clause()
    if not sections:
        raise PolicyError(
            f"No numbered sections (N.N) found in {path}; refusing to invent structure."
        )

    return {"metadata": metadata, "sections": sections}


def retrieve_documents(
    policy_paths: Iterable[str | Path] | None = None,
) -> dict[str, dict[str, Any]]:
    """Load policy files into separate document/section indexes."""
    paths = tuple(Path(path) for path in (policy_paths or DEFAULT_POLICY_PATHS))
    if not paths:
        raise PolicyError("No policy paths supplied.")

    index: dict[str, dict[str, Any]] = {}
    for path in paths:
        document = _read_document(path)
        name = document["metadata"]["document_name"]
        if name in index:
            raise PolicyError(f"Duplicate policy document name: {name}")
        index[name] = document
    return index


def _section_lookup(
    index: dict[str, dict[str, Any]], document_name: str, section_ids: Iterable[str]
) -> list[dict[str, str]]:
    document = index.get(document_name)
    if not document:
        raise PolicyError(f"Required indexed document is missing: {document_name}")

    by_id = {section["section_id"]: section for section in document.get("sections", [])}
    sections: list[dict[str, str]] = []
    for section_id in section_ids:
        if section_id not in by_id:
            raise PolicyError(
                f"Required section {section_id} is missing from {document_name}"
            )
        sections.append(by_id[section_id])
    return sections


def _stem(word: str) -> str:
    for suffix in ("ments", "ment", "ing", "ies", "ed", "es", "s"):
        if word.endswith(suffix) and len(word) > len(suffix) + 3:
            return word[: -len(suffix)]
    return word


def _tokens(text: str) -> set[str]:
    return {
        _stem(word)
        for word in WORD_RE.findall(text.lower())
        if word not in STOP_WORDS and len(word) > 2
    }


def _lexical_route(
    index: dict[str, dict[str, Any]], question: str
) -> tuple[str, tuple[str, ...]] | None:
    """Select one strong, unambiguous section without crossing documents."""
    query_tokens = _tokens(question)
    if not query_tokens:
        return None

    scored: list[tuple[int, str, str]] = []
    for document_name, document in index.items():
        for section in document.get("sections", []):
            searchable = f"{section.get('heading', '')} {section.get('text', '')}"
            score = len(query_tokens & _tokens(searchable))
            if score:
                scored.append((score, document_name, section["section_id"]))

    if not scored:
        return None
    scored.sort(reverse=True)
    best_score, best_document, best_section = scored[0]
    if best_score < 2:
        return None
    tied_documents = {
        document for score, document, _ in scored if score == best_score
    }
    if len(tied_documents) != 1:
        return None
    return best_document, (best_section,)


def _format_answer(document_name: str, sections: Iterable[dict[str, str]]) -> str:
    return "\n".join(
        f"{section['text']} "
        f"(Source: {document_name}, section {section['section_id']})"
        for section in sections
    )


def answer_question(index: dict[str, dict[str, Any]], question: str) -> str:
    """Return a cited answer from one document, or the exact refusal text."""
    if not isinstance(index, dict) or not index:
        raise PolicyError("Document index is empty or malformed.")
    if not isinstance(question, str) or not question.strip():
        return REFUSAL_TEMPLATE

    normalized_question = _collapse_whitespace(question)
    route: tuple[str, tuple[str, ...]] | None = None
    for pattern, document_name, section_ids in INTENT_ROUTES:
        if pattern.search(normalized_question):
            route = document_name, section_ids
            break

    if route is None:
        route = _lexical_route(index, normalized_question)
    if route is None:
        return REFUSAL_TEMPLATE

    document_name, section_ids = route
    sections = _section_lookup(index, document_name, section_ids)
    return _format_answer(document_name, sections)


def _interactive(index: dict[str, dict[str, Any]]) -> None:
    print("Ask a CMC policy question. Type 'quit' or 'exit' to stop.")
    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if question.lower() in {"quit", "exit"}:
            return
        if question:
            print(answer_question(index, question))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ask questions using the three local CMC policy documents."
    )
    parser.add_argument(
        "--question",
        "-q",
        help="Answer one question and exit; omit for interactive mode.",
    )
    parser.add_argument(
        "--policy",
        action="append",
        dest="policies",
        help="Policy path; repeat for multiple files (defaults to all three).",
    )
    args = parser.parse_args()

    try:
        index = retrieve_documents(args.policies)
        if args.question is not None:
            print(answer_question(index, args.question))
        else:
            _interactive(index)
    except PolicyError as exc:
        raise SystemExit(f"error: {exc}") from exc


if __name__ == "__main__":
    main()
