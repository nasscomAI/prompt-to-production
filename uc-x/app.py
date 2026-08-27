"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "can", "do", "for", "from", "i",
    "in", "is", "it", "my", "of", "on", "or", "same", "the", "to", "what", "when",
    "who", "with", "without", "you", "your", "work", "working",
}


@dataclass
class SectionEntry:
    document: str
    section: str
    text: str


def _tokenize(text: str) -> List[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return [tok for tok in tokens if tok not in STOPWORDS and len(tok) > 1]


def _is_divider_or_heading(line: str) -> bool:
    # Ignore visual dividers and top-level section headers (e.g., "5. LEAVE WITHOUT PAY").
    if set(line) == {"═"}:
        return True
    if re.match(r"^\d+\.\s+[A-Z][A-Z\s&()\-/]+$", line):
        return True
    return False


def retrieve_documents(base_dir: Path) -> List[SectionEntry]:
    """
    Load policy documents and index by document + section number (x.y clauses).
    """
    indexed: List[SectionEntry] = []
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)$")

    for filename in POLICY_FILES:
        file_path = base_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Missing policy file: {file_path}")

        with file_path.open("r", encoding="utf-8") as infile:
            active_section = None
            active_text_parts: List[str] = []

            for raw_line in infile:
                line = raw_line.rstrip("\n")
                stripped = line.strip()
                if not stripped:
                    continue

                m = clause_pattern.match(stripped)
                if m:
                    if active_section and active_text_parts:
                        indexed.append(
                            SectionEntry(
                                document=filename,
                                section=active_section,
                                text=" ".join(active_text_parts).strip(),
                            )
                        )
                    active_section = m.group(1)
                    active_text_parts = [m.group(2).strip()]
                    continue

                if active_section:
                    if _is_divider_or_heading(stripped):
                        continue
                    # Append continuation lines to the active clause only.
                    active_text_parts.append(stripped)

            if active_section and active_text_parts:
                indexed.append(
                    SectionEntry(
                        document=filename,
                        section=active_section,
                        text=" ".join(active_text_parts).strip(),
                    )
                )

    if not indexed:
        raise ValueError("No policy sections were indexed from the provided documents.")

    return indexed


def _score_question(question: str, entry: SectionEntry) -> int:
    q_tokens = _tokenize(question)
    entry_tokens = set(_tokenize(entry.text))
    score = sum(1 for tok in q_tokens if tok in entry_tokens)

    q = question.lower()
    t = entry.text.lower()

    # Lightweight phrase bonuses to improve deterministic retrieval for policy phrasing.
    phrase_pairs = [
        ("carry forward", "carry forward"),
        ("annual leave", "annual leave"),
        ("slack", "install software"),
        ("home office", "home office equipment allowance"),
        ("personal phone", "personal devices"),
        ("work files", "cmc email"),
        ("meal receipts", "meal receipts"),
        ("leave without pay", "leave without pay"),
        ("approves", "requires approval"),
    ]
    for q_phrase, t_phrase in phrase_pairs:
        if q_phrase in q and t_phrase.replace("\n", "") in t:
            score += 3

    if "approv" in q and "approval" in t:
        score += 4
    if "who" in q and ("department head" in t or "hr director" in t):
        score += 4

    return score


def _top_matches(question: str, indexed: List[SectionEntry]) -> List[Tuple[int, SectionEntry]]:
    scored = [(_score_question(question, entry), entry) for entry in indexed]
    scored.sort(key=lambda item: item[0], reverse=True)
    return scored


def answer_question(question: str, indexed: List[SectionEntry]) -> str:
    """
    Return single-source, citation-backed answer OR exact refusal template.
    """
    matches = _top_matches(question, indexed)
    if not matches or matches[0][0] <= 0:
        return REFUSAL_TEMPLATE

    best_score, best = matches[0]
    second_score, second = matches[1] if len(matches) > 1 else (0, None)

    # Refuse if top evidence is too weak.
    if best_score < 2:
        return REFUSAL_TEMPLATE

    # Refuse if two different documents compete closely (cross-document ambiguity).
    if second is not None and second_score >= 3 and best.document != second.document:
        if best_score - second_score <= 1:
            return REFUSAL_TEMPLATE

    # Single-source answer with mandatory citation.
    return f"{best.text} (Source: {best.document} section {best.section})"


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.parse_args()

    base_dir = (Path(__file__).resolve().parent / "../data/policy-documents").resolve()
    indexed = retrieve_documents(base_dir)

    print("UC-X Ask My Documents")
    print("Type your question and press Enter. Type 'exit' to quit.")

    while True:
        try:
            question = input("\nQuestion: ").strip()
        except EOFError:
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            print("Exiting.")
            break

        answer = answer_question(question, indexed)
        print(f"Answer: {answer}")


if __name__ == "__main__":
    main()
