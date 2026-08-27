"""
UC-X app.py — Ask My Documents (Interactive Policy Q&A)
Implements skills: retrieve_documents + answer_question
Enforcement from agents.md (RICE):
  - Single-source answers only — no cross-document blending
  - Exact refusal template when question not covered
  - Every answer cites document name + section number
  - Hedging phrases prohibited
"""
import re
import sys

POLICY_FILES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "it is implied",
    "generally",
    "usually",
]


# ── Skill: retrieve_documents ─────────────────────────────────────────────────

def retrieve_documents(file_paths: list) -> dict:
    """
    Load all policy files and return index keyed by filename.
    Each value is a list of { section_id, heading, body }.
    Exits if any file fails to load.
    """
    index = {}

    for path in file_paths:
        filename = path.split("/")[-1]
        try:
            with open(path, encoding="utf-8") as f:
                raw = f.read()
        except FileNotFoundError:
            print(
                f"LOAD_FAILED: '{filename}' could not be read. All documents required.",
                file=sys.stderr,
            )
            sys.exit(1)
        except OSError as e:
            print(f"LOAD_FAILED: {e}", file=sys.stderr)
            sys.exit(1)

        sections = _parse_sections(raw)
        index[filename] = sections

    return index


def _parse_sections(raw: str) -> list:
    """Parse numbered sub-clauses from a policy text file."""
    # Strip divider lines
    raw = re.sub(r"═+", "", raw)

    sections = []
    clause_pattern = re.compile(
        r"^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    for m in clause_pattern.finditer(raw):
        section_id = m.group(1)
        raw_body = m.group(2)
        raw_body = re.sub(r"^\d+\.\s+[A-Z ()&]+$", "", raw_body, flags=re.MULTILINE)
        body = re.sub(r"\s+", " ", raw_body).strip()
        sections.append({
            "section_id": section_id,
            "heading":    "",
            "body":       body,
        })
    return sections


# ── Skill: answer_question ────────────────────────────────────────────────────

def answer_question(question: str, index: dict) -> str:
    """
    Search index for a single-source answer. Returns cited answer or refusal.
    Never blends two documents. Never uses hedging phrases.
    """
    if len(question.strip().split()) < 3:
        return "Please enter a complete question."

    if not index:
        return REFUSAL_TEMPLATE

    q_lower = question.lower()

    # Score each section in each document
    matches: list[dict] = []
    for filename, sections in index.items():
        for sec in sections:
            score = _score_section(q_lower, sec["body"].lower())
            if score > 0:
                matches.append({
                    "score":      score,
                    "filename":   filename,
                    "section_id": sec["section_id"],
                    "body":       sec["body"],
                })

    if not matches:
        return REFUSAL_TEMPLATE

    # Sort by score descending
    matches.sort(key=lambda x: x["score"], reverse=True)

    # Cross-document blending check: if top two matches are from different
    # documents with close scores, use refusal to avoid blending
    if len(matches) >= 2:
        top, second = matches[0], matches[1]
        if top["filename"] != second["filename"] and second["score"] >= top["score"] * 0.75:
            return REFUSAL_TEMPLATE

    best = matches[0]
    answer_text = best["body"]

    return (
        f"{answer_text}\n\n"
        f"Source: {best['filename']}, section {best['section_id']}"
    )


def _score_section(question: str, body: str) -> int:
    """Simple keyword overlap score."""
    # Remove stop words
    stop = {"the", "a", "an", "is", "are", "can", "i", "my", "to", "for",
            "of", "in", "on", "and", "or", "what", "when", "how", "do", "does"}
    q_words = {w.strip("?.,") for w in question.split() if w not in stop and len(w) > 2}
    score = sum(1 for w in q_words if w in body)
    return score


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    print("UC-X — Ask My Documents")
    print("Loading policy documents...")

    index = retrieve_documents(POLICY_FILES)

    doc_counts = {f: len(s) for f, s in index.items()}
    for fname, count in doc_counts.items():
        print(f"  Loaded {fname}: {count} sections")

    print("\nType your question (or 'quit' to exit).\n")

    while True:
        try:
            question = input("Q: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if question.lower() in ("quit", "exit", "q"):
            print("Exiting.")
            break

        if not question:
            continue

        answer = answer_question(question, index)
        print(f"\nA: {answer}\n")
        print("-" * 60)


if __name__ == "__main__":
    main()
