"""UC-X Ask My Documents CLI.

Implements the RICE contract in `agents.md` and `skills.md`:
- Loads and indexes the three approved policy documents by section number.
- Answers from a single document with section citations for each factual claim.
- Returns an exact refusal template when coverage is missing or would require
  cross-document blending.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


REFUSAL_TEXT = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact [relevant team] "
    "for guidance."
)

REQUIRED_DOCS = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)

SECTION_RE = re.compile(r"^(\d+\.\d+)\s+(.*)\s*$")
MAJOR_HEADING_RE = re.compile(r"^\d+\.\s+[A-Z][A-Z\s\-()]+$")
TOKEN_RE = re.compile(r"[a-z0-9]+")
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "for",
    "from",
    "how",
    "i",
    "if",
    "in",
    "is",
    "it",
    "may",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "when",
    "who",
    "with",
    "work",
}

TOKEN_EXPANSIONS = {
    "lwp": ["leave", "without", "pay"],
    "da": ["daily", "allowance"],
    "wfh": ["work", "from", "home"],
    "laptop": ["device", "devices"],
    "phone": ["device", "devices"],
    "slack": ["software"],
}


@dataclass(frozen=True)
class Section:
    doc_name: str
    section: str
    text: str


def _tokenize(text: str) -> List[str]:
    tokens: List[str] = []
    for raw in TOKEN_RE.findall(text.lower()):
        parts = [raw]
        if raw in TOKEN_EXPANSIONS:
            parts.extend(TOKEN_EXPANSIONS[raw])

        for part in parts:
            tok = part
            for suffix in ("ing", "ed", "es", "s", "al", "e"):
                if len(tok) > 4 and tok.endswith(suffix):
                    tok = tok[: -len(suffix)]
                    break
            if tok and tok not in STOP_WORDS:
                tokens.append(tok)
    return tokens


def _parse_sections(doc_name: str, raw_text: str) -> List[Section]:
    sections: List[Section] = []
    current_section = ""
    current_lines: List[str] = []

    for raw_line in raw_text.splitlines():
        line = raw_line.rstrip()
        match = SECTION_RE.match(line)
        if match:
            if current_section and current_lines:
                sections.append(
                    Section(
                        doc_name=doc_name,
                        section=current_section,
                        text=" ".join(" ".join(current_lines).split()),
                    )
                )
            current_section = match.group(1)
            current_lines = [match.group(2).strip()]
            continue

        if not current_section:
            continue

        stripped = line.strip()
        if not stripped or set(stripped) <= {"=", "-", "_", "|", ".", " ", "*", "#", "\u2550"}:
            continue
        if MAJOR_HEADING_RE.match(stripped):
            continue
        current_lines.append(stripped)

    if current_section and current_lines:
        sections.append(
            Section(
                doc_name=doc_name,
                section=current_section,
                text=" ".join(" ".join(current_lines).split()),
            )
        )

    if not sections:
        raise ValueError(f"Unable to parse sections from {doc_name}")

    return sections


def retrieve_documents(file_paths: Iterable[Path]) -> Dict[str, List[Section]]:
    """Load and index all required policy documents.

    Returns a dict keyed by document file name with parsed `Section` entries.
    Raises on any missing/unreadable/unparseable file (no partial index).
    """
    file_path_map = {path.name: path for path in file_paths}
    missing = [name for name in REQUIRED_DOCS if name not in file_path_map]
    if missing:
        raise FileNotFoundError(f"Missing required policy files: {', '.join(missing)}")

    indexed: Dict[str, List[Section]] = {}
    for doc_name in REQUIRED_DOCS:
        doc_path = file_path_map[doc_name]
        if not doc_path.exists() or not doc_path.is_file():
            raise FileNotFoundError(f"Required policy file not found: {doc_path}")
        raw_text = doc_path.read_text(encoding="utf-8")
        indexed[doc_name] = _parse_sections(doc_name, raw_text)

    return indexed


def _score_section(question: str, question_tokens: List[str], section: Section) -> int:
    section_tokens = set(_tokenize(section.text))
    score = sum(1 for tok in question_tokens if tok in section_tokens)

    q_lower = question.lower()
    s_lower = section.text.lower()

    if "personal" in q_lower and ("phone" in q_lower or "device" in q_lower):
        if "personal devices" in s_lower or "personal device" in s_lower:
            score += 3
        if "corporate devices" in s_lower or "corporate device" in s_lower:
            score -= 1

    if "access" in q_lower and ("file" in q_lower or "data" in q_lower):
        if "access" in s_lower:
            score += 2
        if "only" in s_lower:
            score += 1

    return max(score, 0)


def _select_single_source(
    question: str, indexed_documents: Dict[str, List[Section]]
) -> Tuple[str, List[Tuple[Section, int]]]:
    question_tokens = _tokenize(question)
    if not question_tokens:
        return "", []

    doc_scores: Dict[str, int] = {}
    doc_ranked_sections: Dict[str, List[Tuple[Section, int]]] = {}

    for doc_name, sections in indexed_documents.items():
        ranked = sorted(
            ((section, _score_section(question, question_tokens, section)) for section in sections),
            key=lambda item: item[1],
            reverse=True,
        )
        doc_ranked_sections[doc_name] = ranked
        doc_scores[doc_name] = sum(score for _, score in ranked[:3]) if ranked else 0

    sorted_docs = sorted(doc_scores.items(), key=lambda item: item[1], reverse=True)
    best_doc, best_score = sorted_docs[0]
    second_score = sorted_docs[1][1] if len(sorted_docs) > 1 else 0

    if best_score <= 0:
        return "", []

    # Refuse when confidence is too close across documents to avoid blending.
    if second_score > 0 and (best_score - second_score) <= 1:
        return "", []

    top_section = doc_ranked_sections[best_doc][0]
    selected = [top_section] if top_section[1] >= 1 else []

    if not selected:
        return "", []

    return best_doc, selected


def answer_question(question: str, indexed_documents: Dict[str, List[Section]]) -> str:
    """Return single-source cited answer or the exact refusal template."""
    best_doc, sections = _select_single_source(question, indexed_documents)
    if not best_doc or not sections:
        return REFUSAL_TEXT

    lines = [f"Source: {best_doc}"]
    for section, _ in sections:
        lines.append(f"- {section.text} ({section.doc_name} section {section.section})")
    return "\n".join(lines)


def _default_policy_paths() -> List[Path]:
    base_dir = Path(__file__).resolve().parent
    data_dir = (base_dir / ".." / "data" / "policy-documents").resolve()
    return [data_dir / name for name in REQUIRED_DOCS]


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents CLI")
    parser.add_argument(
        "--question",
        type=str,
        help="Optional one-shot question. If omitted, starts interactive mode.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Optional override for policy document directory.",
    )
    args = parser.parse_args()

    if args.data_dir:
        paths = [args.data_dir / name for name in REQUIRED_DOCS]
    else:
        paths = _default_policy_paths()

    try:
        index = retrieve_documents(paths)
    except Exception as exc:
        print(f"Error loading policy files: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.question:
        print(answer_question(args.question.strip(), index))
        return

    print("UC-X Ask My Documents")
    print("Type a policy question. Type 'exit' or press Ctrl+C to quit.")
    while True:
        try:
            question = input("\nQuestion> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            print("Exiting.")
            break

        print(answer_question(question, index))


if __name__ == "__main__":
    main()
