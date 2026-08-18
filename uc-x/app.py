"""
UC-X — Ask My Documents
Usage:
    python app.py

Interactive CLI — type questions about company policy, get answers citing
the exact source document and section number.

Rules enforced:
  - Never blend answers from two different documents
  - No hedging phrases (typically, generally, while not explicitly covered...)
  - Exact refusal template when question is not in any document
  - Every answer cites document name + section number
"""

import re
import sys
import os

# ── Document paths ─────────────────────────────────────────────────────────────

POLICY_FILES = {
    "policy_hr_leave.txt":           "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt":  "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "generally expected",
    "as is standard",
    "usually",
]


# ── Skill: retrieve_documents ─────────────────────────────────────────────────

def retrieve_documents() -> dict:
    """
    Loads all three policy files, indexes them by document name and section.
    Returns: { "policy_hr_leave.txt": [{"section": "2.3", "text": "..."},...], ... }
    """
    index = {}
    for doc_name, filepath in POLICY_FILES.items():
        # Try relative to script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        abs_path = os.path.join(script_dir, filepath)
        if not os.path.isfile(abs_path):
            # Try current working directory
            abs_path = filepath
        if not os.path.isfile(abs_path):
            print(f"ERROR: Policy file not found: {filepath}", file=sys.stderr)
            sys.exit(1)

        with open(abs_path, "r", encoding="utf-8") as f:
            raw = f.read()

        sections = []
        pattern = re.compile(
            r'(?m)^[ \t]*(\d+\.\d+)[ \t]+(.*?)(?=\n[ \t]*\d+\.\d+|\n[ \t]*[═=─-]{5}|\Z)',
            re.DOTALL
        )
        for match in pattern.finditer(raw):
            sec_num = match.group(1).strip()
            text = re.sub(r'\n[ \t]+', ' ', match.group(2)).strip()
            sections.append({"section": sec_num, "text": text, "doc": doc_name})

        index[doc_name] = sections
        print(f"  ✔ Loaded {doc_name} ({len(sections)} sections)")

    return index


# ── Skill: answer_question ────────────────────────────────────────────────────

def answer_question(question: str, index: dict) -> str:
    """
    Searches indexed documents for relevant sections.
    Returns a single-source answer with citation, or the refusal template.
    """
    q_lower = question.lower()

    # Score each section by keyword overlap
    scored = []
    for doc_name, sections in index.items():
        for entry in sections:
            text_lower = entry["text"].lower()
            # Simple token overlap score
            q_tokens = set(re.findall(r'\w+', q_lower))
            t_tokens = set(re.findall(r'\w+', text_lower))
            overlap = len(q_tokens & t_tokens)
            if overlap > 0:
                scored.append({
                    "doc":     doc_name,
                    "section": entry["section"],
                    "text":    entry["text"],
                    "score":   overlap,
                })

    if not scored:
        return REFUSAL_TEMPLATE

    # Sort by score descending
    scored.sort(key=lambda x: x["score"], reverse=True)

    # Check if top results come from multiple different documents
    top_score = scored[0]["score"]
    top_results = [s for s in scored if s["score"] == top_score]
    top_docs = {s["doc"] for s in top_results}

    if len(top_docs) > 1:
        # Cross-document ambiguity — refuse rather than blend
        return REFUSAL_TEMPLATE

    best = scored[0]
    answer = (
        f"{best['text']}\n\n"
        f"Source: {best['doc']}, Section {best['section']}"
    )
    return answer


# ── Main interactive loop ──────────────────────────────────────────────────────

def main():
    print("\n" + "═" * 60)
    print(" UC-X — Ask My Documents")
    print(" Policy Q&A — single-source, citation-required")
    print("═" * 60)
    print("\nLoading policy documents...")

    index = retrieve_documents()

    print(f"\nReady. {sum(len(v) for v in index.values())} sections indexed across 3 documents.")
    print("Type your question and press Enter. Type 'quit' to exit.\n")

    while True:
        try:
            question = input("Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        answer = answer_question(question, index)

        # Safety check — ensure no hedging slipped through
        for phrase in HEDGING_PHRASES:
            if phrase in answer.lower():
                answer = REFUSAL_TEMPLATE
                break

        print(f"\n{'─'*60}")
        print(f"Answer:\n{answer}")
        print(f"{'─'*60}\n")


if __name__ == "__main__":
    main()
