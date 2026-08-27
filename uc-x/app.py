#!/usr/bin/env python3
"""
UC-X Ask My Documents

A policy document question-answering CLI that follows the agent and skill
definitions in uc-x/agents.md and uc-x/skills.md.
"""

from __future__ import annotations

import pathlib
import re
import sys
from collections import defaultdict
from typing import Dict, List, Set, Tuple

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

SECTION_HEADER_RE = re.compile(r"^(\d+\.\d+)\s+(.*)")
TOKEN_RE = re.compile(r"\b\w+\b")

STOP_WORDS: Set[str] = {
    "the",
    "is",
    "are",
    "a",
    "an",
    "and",
    "or",
    "of",
    "to",
    "for",
    "in",
    "on",
    "with",
    "that",
    "this",
    "by",
    "from",
    "be",
    "as",
    "at",
    "all",
    "any",
    "not",
    "only",
    "must",
    "may",
    "can",
    "will",
    "if",
    "their",
    "which",
}

PHRASE_SYNONYM_MAP: Dict[str, str] = {
    r"\bleave without pay\b": "lwp",
    r"\bwithout pay\b": "lwp",
    r"\bpersonal phone\b": "personal device",
}

SYNONYM_MAP: Dict[str, Set[str]] = {
    "phone": {"device"},
    "phones": {"device"},
    "laptop": {"device"},
    "laptops": {"device"},
    "slack": {"software"},
    "files": {"data", "document", "documents"},
    "file": {"data", "document", "documents"},
    "workfromhome": {"home"},
    "work-from-home": {"home"},
    "wfh": {"home"},
    "approve": {"approval"},
    "approves": {"approval"},
}

IMPORTANT_WORDS: Set[str] = {
    "approval", "require", "must", "director", "head", "rs", "day", "month", "year",
    "forfeit", "exhaust", "entitlement", "compensatory", "retirement", "resignation",
    "excessive", "bandwidth", "remote", "wipe", "lock", "biometric",
    "carry", "forward", "install", "home", "office", "da", "meal", "lwp",
    "annual", "sick", "maternity", "paternity", "encash", "travel", "reimbursement",
    "allowance", "training", "mobile", "internet", "slack", "phone",
    "personal", "corporate", "software", "email",
    "portal", "access", "use", "claim", "receipt", "paid", "unpaid", "leave",
}

NEGATIVE_RESTRICTION_WORDS: Set[str] = {"classified", "restricted", "confidential", "sensitive"}
PERSONAL_DEVICE_QUERY: Set[str] = {"personal"}
SECURITY_ISSUE_WORDS: Set[str] = {"lost", "stolen", "wipe", "report"}


def normalize_token(token: str) -> str:
    token = token.lower().strip()
    if token.endswith("s") and len(token) > 3:
        token = token[:-1]
    return token


def tokenize_text(text: str) -> List[str]:
    tokens: List[str] = []
    normalized_text = text.lower()
    for pattern, replacement in PHRASE_SYNONYM_MAP.items():
        normalized_text = re.sub(pattern, replacement, normalized_text)

    for raw in TOKEN_RE.findall(normalized_text):
        normalized = normalize_token(raw)
        if not normalized or normalized in STOP_WORDS:
            continue
        tokens.append(normalized)
        for synonym in SYNONYM_MAP.get(raw.lower(), set()):
            tokens.append(normalize_token(synonym))
    return tokens


def retrieve_documents(base_dir: pathlib.Path) -> Tuple[Dict[str, Dict[str, List[str]]], Dict[str, Set[Tuple[str, str]]]]:
    """Load the policy files and index them by document name and section number."""
    docs: Dict[str, Dict[str, List[str]]] = {}
    index: Dict[str, Set[Tuple[str, str]]] = defaultdict(set)

    for file_name in POLICY_FILES:
        path = base_dir / file_name
        if not path.is_file():
            raise FileNotFoundError(f"Policy file not found: {path}")

        current_section: str | None = None
        current_lines: List[str] = []
        sections: Dict[str, List[str]] = {}

        with path.open(encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("═"):
                    continue

                match = SECTION_HEADER_RE.match(stripped)
                if match:
                    if current_section is not None:
                        sections[current_section] = current_lines[:]
                    current_section = match.group(1)
                    current_lines = [match.group(2).strip()]
                elif current_section is not None:
                    current_lines.append(stripped)

        if current_section is not None:
            sections[current_section] = current_lines[:]

        if not sections:
            raise ValueError(f"No numbered sections found in {file_name}")

        docs[file_name] = sections
        for section_id, section_lines in sections.items():
            section_text = " ".join(section_lines)
            for token in set(tokenize_text(section_text)):
                index[token].add((file_name, section_id))

    return docs, index


def score_section(section_lines: List[str], query_tokens: Set[str]) -> int:
    section_text = " ".join(section_lines)
    section_tokens = set(tokenize_text(section_text))
    score = sum(3 if token in IMPORTANT_WORDS else 1 for token in section_tokens & query_tokens)

    if "personal" in query_tokens and query_tokens & {"phone", "device"}:
        if "corporate" in section_tokens:
            score -= 4
        if "personal" in section_tokens and "device" in section_tokens:
            score += 2
        if "email" in section_tokens and "portal" in section_tokens:
            score += 3

    if (query_tokens & NEGATIVE_RESTRICTION_WORDS) == set() and section_tokens & NEGATIVE_RESTRICTION_WORDS:
        score -= 3

    if (query_tokens & SECURITY_ISSUE_WORDS) == set() and section_tokens & SECURITY_ISSUE_WORDS:
        score -= 2

    return score


def score_sentence(sentence: str, query_tokens: Set[str]) -> int:
    sentence_tokens = set(tokenize_text(sentence))
    return len(sentence_tokens & query_tokens)


def answer_question(query: str, docs: Dict[str, Dict[str, List[str]]], index: Dict[str, Set[Tuple[str, str]]]) -> str:
    """Answer the question from a single source document or return the refusal template."""
    query_tokens = set(tokenize_text(query))
    if not query_tokens:
        return REFUSAL_TEMPLATE

    doc_candidates: Set[str] = set()
    for token in query_tokens:
        doc_candidates.update(doc for doc, _ in index.get(token, set()))

    if not doc_candidates:
        return REFUSAL_TEMPLATE

    scored_docs: List[Tuple[int, str, str, List[str]]] = []
    for doc_name, sections in docs.items():
        best_section_id = ""
        best_section_score = 0
        best_section_lines: List[str] = []

        for section_id, section_lines in sections.items():
            score = score_section(section_lines, query_tokens)
            if score > best_section_score or (score == best_section_score and section_id < best_section_id):
                best_section_score = score
                best_section_id = section_id
                best_section_lines = section_lines

        if best_section_score > 0:
            scored_docs.append((best_section_score, doc_name, best_section_id, best_section_lines))

    if not scored_docs:
        return REFUSAL_TEMPLATE

    scored_docs.sort(reverse=True)
    top_score, top_doc, top_section_id, top_lines = scored_docs[0]
    second_score = scored_docs[1][0] if len(scored_docs) > 1 else 0

    if second_score >= top_score:
        return REFUSAL_TEMPLATE

    # Find the best line in the top section
    lines = [line.strip() for line in top_lines if line.strip()]
    if not lines:
        citation = f"{top_doc}, section {top_section_id}"
        return f"{' '.join(top_lines)} [{citation}]"

    best_line = max(lines, key=lambda l: score_sentence(l, query_tokens))
    citation = f"{top_doc}, section {top_section_id}"
    return f"{best_line} [{citation}]"


def main() -> None:
    base_dir = pathlib.Path(__file__).resolve().parent.parent / "data" / "policy-documents"
    try:
        docs, index = retrieve_documents(base_dir)
    except Exception as exc:
        sys.exit(f"Failed to load policy documents: {exc}")

    print("UC-X Ask My Documents – type a question or 'exit' to quit.")
    while True:
        try:
            query = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not query:
            continue
        if query.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        response = answer_question(query, docs, index)
        print(response)


if __name__ == "__main__":
    main()
