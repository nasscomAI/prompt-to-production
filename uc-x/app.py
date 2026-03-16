"""
UC-X app.py — Ask My Documents (interactive CLI).

Run:
  python app.py
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

DISALLOWED_HEDGES = (
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
)


@dataclass(frozen=True)
class Section:
    section: str
    text: str


@dataclass(frozen=True)
class Document:
    document_name: str
    sections: List[Section]

    def sections_by_id(self) -> Dict[str, Section]:
        return {s.section: s for s in self.sections}

def _project_root() -> Path:
    # uc-x/ lives under prompt-to-production/; policy docs are in ../data/policy-documents/
    return Path(__file__).resolve().parent


def _default_policy_paths() -> List[Path]:
    base = _project_root().parent / "data" / "policy-documents"
    return [
        base / "policy_hr_leave.txt",
        base / "policy_it_acceptable_use.txt",
        base / "policy_finance_reimbursement.txt",
    ]


# Matches section lines like:
# - "2.6 Employees may carry forward..."
# - "3.1 Personal devices may be used..."
# and also major headings like:
# - "3. PERSONAL DEVICES (BYOD)"
SECTION_RE = re.compile(r"^\s*(\d+(?:\.\d+)*)\.?\s+(.*\S)?\s*$")


def retrieve_documents(paths: List[str] | None = None) -> List[Document]:
    """
    Load the three policy documents and build an index keyed by document name and section number.
    """
    resolved_paths = [Path(p) for p in paths] if paths else _default_policy_paths()
    documents: List[Document] = []
    for p in resolved_paths:
        text = p.read_text(encoding="utf-8")
        documents.append(_parse_document(p.name, text))
    return documents


def _parse_document(document_name: str, raw: str) -> Document:
    sections: List[Section] = []
    current_id: str | None = None
    current_lines: List[str] = []
    current_major_heading: str | None = None

    def flush() -> None:
        nonlocal current_id, current_lines
        if current_id is None:
            return
        body = "\n".join(_normalize_lines(current_lines)).strip()
        if body:
            sections.append(Section(section=current_id, text=body))
        current_id = None
        current_lines = []

    for line in raw.splitlines():
        m = SECTION_RE.match(line)
        if m:
            sec_id = m.group(1)
            rest = (m.group(2) or "").rstrip()
            flush()
            current_id = sec_id
            rendered = f"{sec_id} {rest}".rstrip()
            # If this is a major heading (e.g., "3." / "5.") remember it so subsections
            # can inherit key phrasing (e.g., "LEAVE WITHOUT PAY").
            if "." not in sec_id:
                current_major_heading = rendered
                current_lines = [rendered]
            else:
                # Prepend the major heading (if any) to improve retrieval without blending docs.
                current_lines = [current_major_heading] if current_major_heading else []
                current_lines.append(rendered)
        else:
            if current_id is not None:
                current_lines.append(line.rstrip("\n"))

    flush()
    return Document(document_name=document_name, sections=sections)


def _normalize_lines(lines: Iterable[str]) -> List[str]:
    # Keep policy wording, just trim right whitespace and collapse excessive blank lines.
    out: List[str] = []
    blank_streak = 0
    for ln in lines:
        stripped = ln.rstrip()
        if not stripped:
            blank_streak += 1
            if blank_streak <= 1:
                out.append("")
            continue
        blank_streak = 0
        out.append(stripped)
    return out


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "do",
    "for",
    "from",
    "how",
    "i",
    "if",
    "in",
    "is",
    "it",
    "me",
    "my",
    "of",
    "on",
    "or",
    "our",
    "same",
    "the",
    "to",
    "what",
    "when",
    "where",
    "who",
    "with",
    "within",
    "work",
    "working",
    "wfh",
}


TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokens(s: str) -> List[str]:
    toks = TOKEN_RE.findall(s.lower())
    return [t for t in toks if t and t not in STOPWORDS]


def answer_question(question: str, documents: List[Document]) -> Tuple[str, List[Dict[str, str]]]:
    """
    Return (answer_text, citations). Answer must be single-source (exactly one document) or refusal.
    """
    q_tokens = set(_tokens(question))
    if not q_tokens:
        return REFUSAL_TEMPLATE, []

    doc_best: List[Tuple[Document, int, List[str]]] = []
    for doc in documents:
        best_score = 0
        best_sections: List[str] = []
        for sec in doc.sections:
            score = _score_section(q_tokens, sec.text)
            if score > best_score:
                best_score = score
                best_sections = [sec.section]
            elif score == best_score and score > 0:
                best_sections.append(sec.section)
        if best_score > 0:
            doc_best.append((doc, best_score, best_sections))

    if not doc_best:
        return REFUSAL_TEMPLATE, []

    doc_best.sort(key=lambda t: t[1], reverse=True)

    # Enforce "Never combine claims from two different documents into a single answer".
    # We only answer when ONE document clearly dominates; otherwise we refuse rather than blend.
    #
    # Rationale: different policies share generic words (e.g., "employee", "approved") which can create
    # weak incidental matches. We refuse only when there is genuine competition between documents.
    top_doc, top_score, top_sections = doc_best[0]
    if len(doc_best) > 1:
        _second_score = doc_best[1][1]
        # If the top doc doesn't beat the runner-up by a safe margin, fail closed.
        # For low-signal queries (score==1), require strict uniqueness (runner-up must be 0).
        if (top_score == 1 and _second_score > 0) or (top_score >= 2 and top_score < _second_score + 2):
            return REFUSAL_TEMPLATE, []
    # Also fail closed on extremely weak matches.
    # Some questions (e.g., "install Slack") have only one overlapping token ("install")
    # with the relevant policy section; allow score==1 only when the winner is unambiguous.
    if top_score < 1:
        return REFUSAL_TEMPLATE, []

    doc, _score, sections = top_doc, top_score, top_sections

    # Build answer as direct excerpts from the chosen document only.
    by_id = doc.sections_by_id()
    chosen = _select_top_sections(question, sections, by_id)
    excerpts: List[str] = []
    citations: List[Dict[str, str]] = []
    for sec_id in chosen:
        sec = by_id.get(sec_id)
        if not sec:
            continue
        excerpts.append(sec.text)
        citations.append({"document_name": doc.document_name, "section": sec.section})

    if not excerpts:
        return REFUSAL_TEMPLATE, []

    answer_text = "\n\n".join(excerpts).strip()
    answer_text = _ensure_no_hedging(answer_text)
    return answer_text, citations


def _score_section(q_tokens: set[str], section_text: str) -> int:
    sec_tokens = set(_tokens(section_text))
    return len(q_tokens & sec_tokens)


def _select_top_sections(
    question: str, candidates: List[str], by_id: Dict[str, Section], max_sections: int = 2
) -> List[str]:
    q_tokens = set(_tokens(question))
    scored: List[Tuple[str, int]] = []
    for sec_id in candidates:
        sec = by_id.get(sec_id)
        if not sec:
            continue
        scored.append((sec_id, _score_section(q_tokens, sec.text)))
    scored.sort(key=lambda t: t[1], reverse=True)
    return [sec_id for sec_id, _ in scored[:max_sections] if _ > 0]


def _ensure_no_hedging(answer_text: str) -> str:
    lowered = answer_text.lower()
    for phrase in DISALLOWED_HEDGES:
        if phrase in lowered:
            # Fail closed: if our output accidentally contains disallowed language, refuse.
            return REFUSAL_TEMPLATE
    return answer_text


def _print_answer(answer: str, citations: List[Dict[str, str]]) -> None:
    print("\n" + answer)
    if citations:
        print("\nSources:")
        for c in citations:
            print(f"- {c['document_name']} section {c['section']}")


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="UC-X — Ask My Documents (policy Q&A CLI)")
    parser.add_argument(
        "--paths",
        nargs="*",
        default=None,
        help="Optional explicit policy document paths (defaults to the 3 standard policy files).",
    )
    args = parser.parse_args(argv)

    documents = retrieve_documents(paths=args.paths)

    print("UC-X — Ask My Documents")
    print("Type a question and press Enter. Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            q = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not q:
            continue
        if q.lower() in {"exit", "quit"}:
            break

        answer, citations = answer_question(q, documents)
        _print_answer(answer, citations)


if __name__ == "__main__":
    main()
