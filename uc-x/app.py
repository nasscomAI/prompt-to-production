#!/usr/bin/env python3
"""UC-X — Ask My Documents: fail-closed interactive policy Q&A CLI."""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_POLICY_DIR = BASE_DIR.parent / "data" / "policy-documents"

POLICY_FILES = {
    "policy_hr_leave.txt": "HR Leave Policy",
    "policy_it_acceptable_use.txt": "IT Acceptable Use Policy",
    "policy_finance_reimbursement.txt": "Finance Reimbursement Policy",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact [relevant team] "
    "for guidance."
)

FORBIDDEN_HEDGING_PHRASES = (
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
)

STOPWORDS = {
    "a", "an", "and", "are", "be", "can", "could", "do", "does", "for",
    "from", "how", "i", "in", "is", "it", "may", "me", "my", "of", "on",
    "or", "please", "the", "their", "this", "to", "use", "what", "when",
    "where", "who", "with", "would", "you", "your", "company", "policy",
    "tell", "about", "allowed", "allow", "get", "have", "has", "work",
}

@dataclass(frozen=True)
class Section:
    document: str
    title: str
    number: str
    text: str


def retrieve_documents(policy_dir: Path) -> Dict[str, Dict[str, Section]]:
    """Skill: load all three documents and index complete numbered sections."""
    if not policy_dir.exists() or not policy_dir.is_dir():
        raise RuntimeError(f"Policy directory does not exist or is not a directory: {policy_dir}")

    indexed: Dict[str, Dict[str, Section]] = {}
    for filename in POLICY_FILES:
        path = policy_dir / filename
        if not path.exists() or not path.is_file():
            raise RuntimeError(f"Required policy file is missing: {path}")
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise RuntimeError(f"Unable to read policy file {path}: {exc}") from exc
        if not text.strip():
            raise RuntimeError(f"Required policy file is empty: {path}")

        sections = _parse_sections(text, filename)
        if not sections:
            raise RuntimeError(f"Could not index any numbered sections in policy file: {filename}")
        indexed[filename] = {s.number: s for s in sections}

    if set(indexed) != set(POLICY_FILES):
        missing = set(POLICY_FILES) - set(indexed)
        raise RuntimeError("Document indexing incomplete; missing: " + ", ".join(sorted(missing)))
    return indexed


def _parse_sections(text: str, document: str) -> List[Section]:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    patterns = (
        re.compile(r"^\s*(\d+(?:\.\d+)+)\s*[-:.)]?\s*(.*\S)?\s*$"),
        re.compile(r"^\s*section\s+(\d+(?:\.\d+)+)\s*[-:.)]?\s*(.*\S)?\s*$", re.I),
    )
    matches: List[Tuple[int, str, str]] = []
    for i, line in enumerate(lines):
        for pattern in patterns:
            m = pattern.match(line)
            if m:
                matches.append((i, m.group(1), (m.group(2) or "").strip()))
                break

    sections: List[Section] = []
    for pos, (start, number, title) in enumerate(matches):
        end = matches[pos + 1][0] if pos + 1 < len(matches) else len(lines)
        body = "\n".join(lines[start + 1:end]).strip()
        full_text = f"{number} {title}".strip()
        if body:
            full_text += "\n" + body
        if not full_text.strip():
            raise RuntimeError(f"Empty indexed section {number} in {document}")
        sections.append(Section(document, title, number, full_text))
    return sections


def answer_question(question: str, documents: Dict[str, Dict[str, Section]]) -> str:
    """Skill: return one-source answer with citation, or exact refusal."""
    if not isinstance(question, str) or not question.strip() or not _valid_index(documents):
        return REFUSAL_TEMPLATE

    q = _normalize(question)

    # UC-X critical trap: personal-phone questions are restricted to IT 3.1.
    if _is_personal_phone_question(q):
        section = documents.get("policy_it_acceptable_use.txt", {}).get("3.1")
        if section is None:
            return REFUSAL_TEMPLATE
        answer = _answer_from_section(question, section)
        return answer if _valid_answer(answer, section) else REFUSAL_TEMPLATE

    candidates = _rank_sections(question, documents)
    if not candidates or candidates[0][0] < 2:
        return REFUSAL_TEMPLATE

    best_score = candidates[0][0]
    top = [x for x in candidates if x[0] == best_score]
    if len({x[1].document for x in top}) > 1:
        return REFUSAL_TEMPLATE

    section = top[0][1]
    if len(top) > 1:
        section = _break_tie(question, top)
        if section is None:
            return REFUSAL_TEMPLATE

    answer = _answer_from_section(question, section)
    return answer if _valid_answer(answer, section) else REFUSAL_TEMPLATE


def _valid_index(documents: object) -> bool:
    if not isinstance(documents, dict) or set(documents) != set(POLICY_FILES):
        return False
    for filename in POLICY_FILES:
        sections = documents.get(filename)
        if not isinstance(sections, dict) or not sections:
            return False
        for number, section in sections.items():
            if not isinstance(section, Section) or section.document != filename or section.number != number or not section.text.strip():
                return False
    return True


def _rank_sections(question: str, documents: Dict[str, Dict[str, Section]]) -> List[Tuple[int, Section]]:
    q = _normalize(question)
    qterms = _question_terms(question)
    if not qterms:
        return []
    ranked: List[Tuple[int, Section]] = []
    explicit_sections = re.findall(r"\b(?:section\s*)?(\d+(?:\.\d+)+)\b", q)

    for filename in POLICY_FILES:
        for section in documents[filename].values():
            s = _normalize(section.text)
            score = len(qterms & set(_question_terms(section.text)))
            if "carry forward" in q and "carry forward" in s: score += 4
            if "slack" in q and "slack" in s: score += 4
            if "home office" in q and "home office" in s: score += 4
            if "equipment allowance" in q and ("allowance" in s or "equipment" in s): score += 2
            if "da" in q and "meal" in q and "receipt" in q and "da" in s and "meal" in s: score += 5
            if "leave without pay" in q and "leave without pay" in s: score += 5
            if section.number in explicit_sections: score += 10
            if score > 0: ranked.append((score, section))

    ranked.sort(key=lambda x: (-x[0], x[1].document, _section_key(x[1].number)))
    return ranked


def _break_tie(question: str, candidates: List[Tuple[int, Section]]) -> Optional[Section]:
    q = _normalize(question)
    phrases = (
        "carry forward", "annual leave", "install slack", "work laptop",
        "home office equipment", "permanent wfh", "personal phone", "personal device",
        "work files", "leave without pay", "department head", "hr director",
        "meal receipts", "flexible working culture",
    )
    scored = []
    for _, section in candidates:
        s = _normalize(section.text)
        bonus = sum(len(p.split()) + 1 for p in phrases if p in q and p in s)
        scored.append((bonus, section))
    scored.sort(key=lambda x: (-x[0], _section_key(x[1].number)))
    if not scored or scored[0][0] == 0 or (len(scored) > 1 and scored[0][0] == scored[1][0]):
        return None
    return scored[0][1]


def _answer_from_section(question: str, section: Section) -> str:
    sentences = _split_sentences(section.text)
    qterms = _question_terms(question)
    scored: List[Tuple[int, int, str]] = []
    q = _normalize(question)
    phrases = (
        "carry forward", "annual leave", "written it approval", "home office",
        "one-time", "permanent wfh", "personal devices", "employee self-service portal",
        "cmc email", "da", "meal receipts", "leave without pay", "department head", "hr director",
    )
    for i, sentence in enumerate(sentences):
        s = _normalize(sentence)
        score = len(qterms & set(_question_terms(sentence)))
        score += sum(3 for p in phrases if p in q and p in s)
        if score > 0: scored.append((score, i, sentence.strip()))
    if not scored:
        return ""
    scored.sort(key=lambda x: (-x[0], x[1]))
    best = scored[0][0]
    chosen = {sentence for score, _, sentence in scored if score >= max(1, best - 1)}
    ordered = [s for s in sentences if s.strip() in chosen]
    if not ordered: return ""
    return " ".join(ordered).strip() + f" Source: {section.document}, Section {section.number}."


def _valid_answer(answer: str, section: Section) -> bool:
    if not answer.strip(): return False
    lower = _normalize(answer)
    if any(p in lower for p in FORBIDDEN_HEDGING_PHRASES): return False
    citation = f"source: {section.document.lower()}, section {section.number.lower()}."
    if citation not in lower: return False
    body = re.sub(r"\s*Source:\s*[^.]+\.\s*$", "", answer, flags=re.I).strip()
    if not body: return False
    source_terms = set(_question_terms(section.text))
    return all(len(set(_question_terms(s)) & source_terms) >= 2 for s in _split_sentences(body) if _question_terms(s))


def _is_personal_phone_question(q: str) -> bool:
    return (
        any(x in q for x in ("personal phone", "personal device", "personal mobile", "own phone"))
        and any(x in q for x in ("work files", "work file", "company files", "company file", "work documents", "work document"))
        and any(x in q for x in ("from home", "working from home", "at home", "home", "remote"))
    )


def _question_terms(text: str) -> set[str]:
    normalized = _normalize(text)
    terms = {t for t in re.findall(r"[a-z0-9]+", normalized) if len(t) > 1 and t not in STOPWORDS}
    if "annual leave" in normalized: terms.update({"annual", "leave"})
    if "leave without pay" in normalized: terms.update({"leave", "without", "pay"})
    if "meal receipts" in normalized: terms.update({"meal", "receipts"})
    if "department head" in normalized: terms.update({"department", "head"})
    if "hr director" in normalized: terms.update({"hr", "director"})
    return terms


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def _split_sentences(text: str) -> List[str]:
    pieces = re.split(r"(?<=[.!?])\s+|\n+", text.replace("\r\n", "\n").replace("\r", "\n"))
    return [p.strip(" \t-•") for p in pieces if p.strip(" \t-•")]


def _section_key(number: str) -> Tuple[int, ...]:
    try: return tuple(int(x) for x in number.split("."))
    except ValueError: return (999999,)


def run_cli(policy_dir: Path, output_path: Path) -> int:
    try:
        documents = retrieve_documents(policy_dir)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("UC-X — Ask My Documents")
    print("Loaded all three policy documents.")
    print("Type questions. Type 'exit' or 'quit' to stop.")
    print()
    answers: List[str] = []

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.lower() in {"exit", "quit"}:
            break
        answer = answer_question(question, documents)
        answers.append(f"Q: {question}\nA: {answer}")
        print("Answer: " + answer)
        print()

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n\n".join(answers) + ("\n" if answers else ""), encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: Could not write output file {output_path}: {exc}", file=sys.stderr)
        return 1
    print(f"Answers written to: {output_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="UC-X — Ask My Documents")
    parser.add_argument("--policy-dir", type=Path, default=DEFAULT_POLICY_DIR)
    parser.add_argument("--output", type=Path, default=BASE_DIR / "answers.txt")
    args = parser.parse_args()
    return run_cli(args.policy_dir, args.output)


if __name__ == "__main__":
    raise SystemExit(main())

