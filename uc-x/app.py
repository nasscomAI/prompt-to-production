"""
UC-X — Ask My Documents
Interactive CLI that answers questions strictly from indexed policy files.
Run: python app.py
"""

import os
import re
import sys

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data", "policy-documents")

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]

# Matches section headings like "2. ANNUAL LEAVE" or "3.1 Some heading"
SECTION_PATTERN = re.compile(
    r"^(?P<num>\d+(?:\.\d+)?)\s+[A-Z]", re.MULTILINE
)


# ---------------------------------------------------------------------------
# Skill: retrieve_documents
# ---------------------------------------------------------------------------

def retrieve_documents(file_paths: list[str]) -> dict[tuple[str, str], str]:
    """
    Load policy files and build an index keyed by (filename, section_number).
    Raises RuntimeError if any file cannot be read.
    Returns {(filename, section_num): section_text}.
    """
    index: dict[tuple[str, str], str] = {}

    for path in file_paths:
        filename = os.path.basename(path)
        try:
            with open(path, encoding="utf-8") as fh:
                content = fh.read()
        except OSError as exc:
            raise RuntimeError(
                f"retrieve_documents: cannot load '{filename}': {exc}"
            ) from exc

        matches = list(SECTION_PATTERN.finditer(content))

        if not matches:
            print(
                f"[WARNING] No parseable section markers found in '{filename}'. "
                "Storing entire file under section '0'.",
                file=sys.stderr,
            )
            index[(filename, "0")] = content.strip()
            continue

        for i, match in enumerate(matches):
            section_num = match.group("num")
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            section_text = content[start:end].strip()
            index[(filename, section_num)] = section_text

    return index


# ---------------------------------------------------------------------------
# Skill: answer_question
# ---------------------------------------------------------------------------

def _contains_hedging(text: str) -> bool:
    lower = text.lower()
    return any(phrase in lower for phrase in HEDGING_PHRASES)


def _keyword_score(question: str, text: str) -> int:
    """Simple word-overlap score between question and section text."""
    q_words = set(re.findall(r"\b\w{4,}\b", question.lower()))
    t_words = set(re.findall(r"\b\w{4,}\b", text.lower()))
    return len(q_words & t_words)


def answer_question(
    question: str,
    index: dict[tuple[str, str], str],
) -> str:
    """
    Search the index for the best single-source answer.
    Returns a cited answer string or the verbatim refusal template.
    """
    if not index:
        raise RuntimeError("answer_question: document index is empty or was not provided.")

    # Score every section
    scored: list[tuple[int, str, str]] = []  # (score, filename, section_num)
    for (filename, section_num), text in index.items():
        score = _keyword_score(question, text)
        if score > 0:
            scored.append((score, filename, section_num))

    if not scored:
        return REFUSAL_TEMPLATE 

    scored.sort(key=lambda x: x[0], reverse=True)
    top_score = scored[0][0]

    # Collect all sections that tie for top score
    top_hits = [(fn, sec) for s, fn, sec in scored if s == top_score]

    # More than one document in top hits → cross-document ambiguity → refuse
    top_docs = {fn for fn, _ in top_hits}
    if len(top_docs) > 1:
        return REFUSAL_TEMPLATE

    best_filename, best_section = top_hits[0]
    section_text = index[(best_filename, best_section)]

    # Guard: reject any hedging that somehow crept into source text
    if _contains_hedging(section_text):
        return REFUSAL_TEMPLATE

    # Build the cited answer
    answer = (
        f"{section_text}\n\n"
        f"(Source: {best_filename}, Section {best_section})"
    )
    return answer


# ---------------------------------------------------------------------------
# Main — interactive CLI
# ---------------------------------------------------------------------------

def main() -> None:
    file_paths = [os.path.join(DATA_DIR, f) for f in POLICY_FILES]

    try:
        index = retrieve_documents(file_paths)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    print("Policy Q&A — Ask My Documents")
    print(f"Loaded {len(index)} sections from {len(POLICY_FILES)} policy files.")
    print("Type your question and press Enter. Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            question = input("Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        result = answer_question(question, index)
        print(f"\n{result}\n")


if __name__ == "__main__":
    main()
