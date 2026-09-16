#!/usr/bin/env python3
"""
UC-X — Ask My Documents
========================
An AI policy retrieval assistant that answers employee questions strictly
based on three company policy documents (see agents.md / skills.md).

This module implements the two skills defined in skills.md:
    1. retrieve_documents  -- loads and indexes the 3 policy files
    2. answer_question     -- searches the index, returns a single-source
                               answer with a citation, or the exact
                               refusal template

and enforces the four rules in agents.md programmatically (not just via
prompting), so they cannot be bypassed by hedging or blended reasoning:
    1. Never combine claims from two different documents into one answer
    2. Never use hedging phrases
    3. Unanswerable questions get the refusal template, verbatim, no variations
    4. Every factual claim is cited with document name + section number

Run
---
    python app.py
    python app.py --files path/to/hr.txt path/to/it.txt path/to/finance.txt
    python app.py --log-file my_session.log

With no arguments, the three input files are read from the paths given in
the UC README:
    ../data/policy-documents/policy_hr_leave.txt
    ../data/policy-documents/policy_it_acceptable_use.txt
    ../data/policy-documents/policy_finance_reimbursement.txt

Output
------
The run command in the UC README is an interactive CLI with no explicit
output-file spec. To satisfy "produce the output file" while preserving
that interactive behavior, every Q&A turn is also written to a session
transcript file (default: qa_session_log.txt, override with --log-file).
"""

import argparse
import logging
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

# --------------------------------------------------------------------------
# agents.md — governance constants, enforced in code (not merely prompted).
# --------------------------------------------------------------------------

ALLOWED_DOCUMENTS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

# Exact refusal template from agents.md / UC README. Must be emitted
# verbatim, with no variations.
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# Hedging phrases that must never appear in a generated answer
# (agents.md enforcement rule 2).
FORBIDDEN_HEDGES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]

DEFAULT_FILE_PATHS = [
    os.path.join("..", "data", "policy-documents", name)
    for name in ALLOWED_DOCUMENTS
]

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "i", "my", "me", "can", "do", "does", "did", "to", "for", "of", "on",
    "in", "at", "and", "or", "if", "it", "its", "this", "that", "what",
    "who", "how", "when", "where", "which", "with", "from", "as", "about",
    "use", "used", "using", "have", "has", "had", "will", "would",
    "should", "am", "so", "please", "there", "their", "them", "you",
    "your",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("uc_x_ask_my_documents")


# --------------------------------------------------------------------------
# Data model
# --------------------------------------------------------------------------

@dataclass
class Section:
    number: str
    title: str
    text: str


@dataclass
class Document:
    name: str
    sections: List[Section] = field(default_factory=list)


IndexedDataset = Dict[str, Document]


# --------------------------------------------------------------------------
# Skill 1: retrieve_documents
#   input:  list of file path strings
#   output: IndexedDataset -- {document_name: Document(sections=[...])}
#   error_handling: missing/unreadable file -> FileNotFoundError, halt;
#                   ambiguous section formatting -> warn + default split
# --------------------------------------------------------------------------

# Matches headers like "2.6", "2.6 Carry Forward", "Section 2.6: Title"
SECTION_HEADER_RE = re.compile(
    r"^\s*(?:section\s+)?(\d+(?:\.\d+)+)\s*[-:.]?\s*(.*)$",
    re.IGNORECASE,
)


def retrieve_documents(file_paths: List[str]) -> IndexedDataset:
    """Loads all 3 policy files and indexes their content by document
    name and section number (skills.md: retrieve_documents)."""
    index: IndexedDataset = {}

    for path in file_paths:
        doc_name = os.path.basename(path)

        if doc_name not in ALLOWED_DOCUMENTS:
            logger.warning(
                "Skipping '%s': not one of the allowed documents %s",
                doc_name, ALLOWED_DOCUMENTS,
            )
            continue

        if not os.path.isfile(path):
            raise FileNotFoundError(
                f"retrieve_documents: required policy file not found or "
                f"unreadable: '{path}'"
            )

        try:
            with open(path, "r", encoding="utf-8") as f:
                raw_text = f.read()
        except OSError as e:
            raise FileNotFoundError(
                f"retrieve_documents: could not read '{path}': {e}"
            ) from e

        sections = _parse_sections(raw_text, doc_name)
        index[doc_name] = Document(name=doc_name, sections=sections)
        logger.info("Indexed '%s' -> %d section(s).", doc_name, len(sections))

    missing = set(ALLOWED_DOCUMENTS) - set(index.keys())
    if missing:
        raise FileNotFoundError(
            f"retrieve_documents: missing required policy document(s): "
            f"{sorted(missing)}"
        )

    return index


def _parse_sections(raw_text: str, doc_name: str) -> List[Section]:
    """Splits a document's text into sections keyed by section number.
    Falls back to default whole-document splitting and logs a warning
    if section formatting is ambiguous (no numbered headers found), per
    skills.md error_handling for retrieve_documents."""
    lines = raw_text.splitlines()
    matches = []  # (line_index, number, title)

    for i, line in enumerate(lines):
        m = SECTION_HEADER_RE.match(line)
        if m:
            matches.append((i, m.group(1).strip(), m.group(2).strip()))

    if not matches:
        logger.warning(
            "'%s': no numbered section headers detected -- section "
            "formatting is ambiguous. Falling back to default section "
            "splitting (entire document treated as one section).",
            doc_name,
        )
        body = raw_text.strip()
        return [Section(number="0", title="Document", text=body)] if body else []

    sections: List[Section] = []
    for idx, (line_no, number, title) in enumerate(matches):
        start = line_no + 1
        end = matches[idx + 1][0] if idx + 1 < len(matches) else len(lines)
        body = "\n".join(lines[start:end]).strip()
        sections.append(Section(number=number, title=title, text=body))

    return sections


# --------------------------------------------------------------------------
# Skill 2: answer_question
#   input:  user_query string
#   output: single-source answer + citation, OR the refusal template
#   error_handling: unanswerable / cross-document / ambiguous ->
#                   refusal template, verbatim, no hedging
# --------------------------------------------------------------------------

def _tokenize(text: str) -> List[str]:
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 1]


def _build_idf(index: IndexedDataset) -> Dict[str, float]:
    """Computes an inverse-document-frequency weight per term across all
    sections in the corpus. Terms that appear in many sections (e.g.
    generic words like "work") are down-weighted, so a question is routed
    to the document whose *specific* vocabulary it matches, rather than
    tying on filler words shared across policies. This is what keeps
    e.g. "install Slack on my laptop" from tying against an unrelated HR
    section that merely mentions "work"."""
    import math

    all_sections: List[Section] = [
        s for doc in index.values() for s in doc.sections
    ]
    n = max(len(all_sections), 1)
    df: Dict[str, int] = {}
    for section in all_sections:
        terms = set(_tokenize(section.title + " " + section.text))
        for t in terms:
            df[t] = df.get(t, 0) + 1

    idf: Dict[str, float] = {}
    for term, freq in df.items():
        idf[term] = math.log((n + 1) / (freq + 1)) + 1.0  # smoothed idf, always > 0
    return idf


def _score_section(
    query_tokens: List[str], section: Section, idf: Dict[str, float]
) -> "tuple[float, int]":
    """Returns (weighted_score, distinct_matched_token_count)."""
    haystack = _tokenize(section.title + " " + section.text)
    score = 0.0
    matched = 0
    for tok in set(query_tokens):
        tf = haystack.count(tok)
        if tf:
            score += tf * idf.get(tok, 1.0)
            matched += 1
    return score, matched


@dataclass
class _Match:
    doc_name: str
    section: Section
    score: float
    matched_tokens: int


def answer_question(query: str, index: IndexedDataset) -> str:
    """Searches the indexed policy documents and returns a single-source
    answer with citation, or the exact refusal template
    (skills.md: answer_question)."""
    query_tokens = _tokenize(query)
    if not query_tokens:
        return REFUSAL_TEMPLATE

    idf = _build_idf(index)
    distinct_query_tokens = set(query_tokens)

    # Best-scoring section per document -- never merge sections/documents.
    best_per_doc: Dict[str, _Match] = {}
    for doc_name, doc in index.items():
        best_section: Optional[Section] = None
        best_score = 0.0
        best_matched = 0
        for section in doc.sections:
            score, matched = _score_section(query_tokens, section, idf)
            if score > best_score:
                best_score = score
                best_section = section
                best_matched = matched
        if best_section is not None and best_score > 0:
            best_per_doc[doc_name] = _Match(
                doc_name, best_section, best_score, best_matched
            )

    if not best_per_doc:
        # Not covered in any document -> refuse.
        return REFUSAL_TEMPLATE

    ranked = sorted(best_per_doc.values(), key=lambda m: m.score, reverse=True)
    top = ranked[0]
    runner_up = ranked[1] if len(ranked) > 1 else None

    # Coverage check: a genuine, on-topic match should share a meaningful
    # portion of the question's vocabulary with the section, not just one
    # incidental word (e.g. a question about "flexible working culture"
    # merely sharing the word "working" with an unrelated HR section).
    # Too little overlap means the question is not actually covered, so
    # we refuse rather than force a low-confidence guess.
    min_matched = 2 if len(distinct_query_tokens) > 1 else 1
    coverage_ratio = top.matched_tokens / max(len(distinct_query_tokens), 1)
    if top.matched_tokens < min_matched or coverage_ratio < 0.5:
        logger.info(
            "Refusing (insufficient coverage): top match '%s' sec %s "
            "matched only %d/%d distinct query terms.",
            top.doc_name, top.section.number,
            top.matched_tokens, len(distinct_query_tokens),
        )
        return REFUSAL_TEMPLATE

    # agents.md rule 1: never combine claims from two different documents.
    # If a second document's best match is close in relevance to the top
    # one, a confident single-source answer cannot be guaranteed -- this
    # is exactly the cross-document blending trap (e.g. IT vs HR on
    # "personal phone for work files"). Refuse rather than blend.
    if runner_up is not None and runner_up.score >= 0.8 * top.score:
        logger.info(
            "Refusing (cross-document ambiguity): '%s' sec %s (score=%.2f) "
            "vs '%s' sec %s (score=%.2f).",
            top.doc_name, top.section.number, top.score,
            runner_up.doc_name, runner_up.section.number, runner_up.score,
        )
        return REFUSAL_TEMPLATE

    answer = _format_answer(top)
    _assert_no_hedging(answer)
    return answer


def _format_answer(match: _Match) -> str:
    section = match.section
    body = section.text.strip()
    if not body:
        return REFUSAL_TEMPLATE
    citation = f"[Source: {match.doc_name}, Section {section.number}"
    if section.title:
        citation += f" - {section.title}"
    citation += "]"
    return f"{body}\n\n{citation}"


def _assert_no_hedging(answer: str) -> None:
    """Hard stop (agents.md rule 2): a generated answer must never
    contain a forbidden hedging phrase."""
    lowered = answer.lower()
    for phrase in FORBIDDEN_HEDGES:
        if phrase in lowered:
            raise RuntimeError(
                f"Enforcement violation: forbidden hedging phrase "
                f"detected in answer: '{phrase}'"
            )


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _resolve_file_paths(args_files: Optional[List[str]]) -> List[str]:
    if args_files:
        return args_files
    return DEFAULT_FILE_PATHS


def main() -> int:
    parser = argparse.ArgumentParser(
        description="UC-X -- Ask My Documents: policy retrieval assistant."
    )
    parser.add_argument(
        "--files", nargs=3, metavar=("HR", "IT", "FINANCE"),
        help=(
            "Paths to the three policy files (any order). Defaults to "
            "../data/policy-documents/<name>.txt for each of: "
            + ", ".join(ALLOWED_DOCUMENTS)
        ),
    )
    parser.add_argument(
        "--log-file", default="qa_session_log.txt",
        help="Output transcript file for the Q&A session (default: %(default)s).",
    )
    args = parser.parse_args()

    file_paths = _resolve_file_paths(args.files)

    try:
        index = retrieve_documents(file_paths)
    except FileNotFoundError as e:
        logger.error(str(e))
        print(f"Fatal error: {e}", file=sys.stderr)
        return 1

    print("UC-X -- Ask My Documents")
    print(f"Loaded documents: {', '.join(sorted(index.keys()))}")
    print("Type a question and press Enter. Type 'exit' or 'quit' to stop.\n")

    session_lines = [
        f"UC-X Ask My Documents -- session started {datetime.now().isoformat()}",
        f"Documents loaded: {', '.join(sorted(index.keys()))}",
        "",
    ]

    try:
        while True:
            try:
                query = input("Q: ").strip()
            except EOFError:
                break

            if not query:
                continue
            if query.lower() in ("exit", "quit"):
                break

            answer = answer_question(query, index)
            print(f"A: {answer}\n")

            session_lines.append(f"Q: {query}")
            session_lines.append(f"A: {answer}")
            session_lines.append("")
    finally:
        try:
            with open(args.log_file, "w", encoding="utf-8") as f:
                f.write("\n".join(session_lines))
            logger.info("Session log written to '%s'.", args.log_file)
        except OSError as e:
            logger.error("Could not write session log: %s", e)

    return 0


if __name__ == "__main__":
    sys.exit(main())