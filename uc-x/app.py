"""
UC-X — Ask My Documents (Interactive Policy Q&A Agent)
Generated from agents.md and skills.md.

Agent contract (agents.md):
  role      : Answer questions from 3 CMC policy documents only. No blending.
              No general knowledge. No hedging.
  intent    : Single-source answer + citation OR exact refusal template.
  refusal   : "This question is not covered in the available policy documents
               (policy_hr_leave.txt, policy_it_acceptable_use.txt,
               policy_finance_reimbursement.txt).
               Please contact [relevant team] for guidance."
  enforcement:
    1. Never combine claims from two different documents.
    2. Forbidden hedging phrases: 'while not explicitly covered', 'typically',
       'generally understood', 'it is common practice', 'it is standard to',
       'employees are generally expected'.
    3. Question not in docs → exact refusal template, no partial answers.
    4. Every factual claim: [Source: <filename>, Section <X.Y>].

Skills (skills.md):
  retrieve_documents(file_paths)       → {index, flat_list}
  answer_question(question, index)     → {answer, source_doc, source_section, is_refusal}
"""
import os
import re
import string

# ── Policy document paths (relative to this file's location) ─────────────────
POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

# ── Refusal template (agents.md — exact wording, no variations) ───────────────
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# ── Forbidden hedging phrases (agents.md enforcement rule 2) ─────────────────
FORBIDDEN_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "it is standard to",
    "employees are generally expected",
]

# ── Common stop words for relevance scoring ───────────────────────────────────
STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "i", "my", "me", "we", "our",
    "you", "your", "it", "its", "this", "that", "these", "those", "to",
    "of", "in", "on", "at", "for", "with", "by", "from", "up", "and",
    "or", "not", "if", "what", "how", "when", "where", "who", "which",
    "there", "about", "any", "also", "so", "but", "no", "yes", "get",
    "use", "used", "using", "need", "want",
}


# ─────────────────────────────────────────────────────────────────────────────
# Skill: retrieve_documents  (skills.md)
# ─────────────────────────────────────────────────────────────────────────────
def retrieve_documents(file_paths: list) -> dict:
    """
    Load all policy .txt files and index their content by document name
    and section number.

    Returns:
      {
        "index": { "<doc_filename>": { "<section_id>": "<text>", ... }, ... },
        "flat":  [ (doc_name, section_id, text), ... ]   # for search
      }

    Error handling (skills.md):
      - FileNotFoundError if any file cannot be read.
      - Unparseable content → stored under "UNSTRUCTURED", never lost.
      - Warning printed if a file yields zero numbered sections.
    """
    section_pat = re.compile(r"^(\d+\.\d+)\s+(.*)")
    index = {}
    flat  = []

    for path in file_paths:
        doc_name = os.path.basename(path)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Policy file not found: {path}")

        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()

        sections      = {}
        current_id    = None
        current_lines = []

        def _flush():
            if current_id and current_lines:
                text = " ".join(current_lines)
                sections[current_id] = text
                flat.append((doc_name, current_id, text))

        for line in lines:
            stripped = line.strip()
            m = section_pat.match(stripped)
            if m:
                _flush()
                current_id    = m.group(1)
                current_lines = [m.group(2).strip()]
            elif current_id and stripped and not re.match(r"^[═]{3,}", stripped):
                current_lines.append(stripped)

        _flush()

        if not sections:
            print(f"  WARNING: No numbered sections found in {doc_name}")
            sections["UNSTRUCTURED"] = "\n".join(lines)
            flat.append((doc_name, "UNSTRUCTURED", sections["UNSTRUCTURED"]))

        index[doc_name] = sections

    return {"index": index, "flat": flat}


# ─────────────────────────────────────────────────────────────────────────────
# Skill: answer_question  (skills.md)
# ─────────────────────────────────────────────────────────────────────────────
def answer_question(question: str, index: dict, flat: list) -> dict:
    """
    Search indexed documents for sections relevant to the question and return
    a single-source answer with citation, or the exact refusal template.

    Enforcement (agents.md):
      Rule 1: If top matches span 2+ documents — refuse, never blend.
      Rule 2: Forbidden hedging phrases never appear in output.
      Rule 3: Not found → exact refusal template, no partial answer.
      Rule 4: Answer always ends with [Source: <filename>, Section <X.Y>].

    Error handling (skills.md):
      - ValueError if index is empty or None.
      - Cross-document ambiguity → is_refusal=True.
    """
    if not index:
        raise ValueError("Document index is empty - run retrieve_documents first.")

    tokens = set(
        w.lower().strip(string.punctuation)
        for w in question.split()
        if w.lower().strip(string.punctuation) not in STOP_WORDS
        and len(w.strip(string.punctuation)) > 2
    )

    if not tokens:
        return {"answer": REFUSAL_TEMPLATE, "source_doc": None,
                "source_section": None, "is_refusal": True}

    # Score every section by keyword overlap
    scored = []
    for doc_name, section_id, text in flat:
        hits = sum(1 for t in tokens if t in text.lower())
        if hits > 0:
            scored.append((hits, doc_name, section_id, text))

    scored.sort(key=lambda x: x[0], reverse=True)

    if not scored:
        return {"answer": REFUSAL_TEMPLATE, "source_doc": None,
                "source_section": None, "is_refusal": True}

    top_score   = scored[0][0]
    top_matches = [s for s in scored if s[0] == top_score]
    top_docs    = {m[1] for m in top_matches}

    # Enforcement rule 1: tie across multiple documents → refuse
    if len(top_docs) > 1:
        return {"answer": REFUSAL_TEMPLATE, "source_doc": None,
                "source_section": None, "is_refusal": True}

    _, doc_name, section_id, section_text = scored[0]

    # Enforcement rule 2: strip forbidden phrases (safety guard)
    answer_text = section_text
    for phrase in FORBIDDEN_PHRASES:
        answer_text = re.sub(re.escape(phrase), "[REDACTED]", answer_text,
                             flags=re.IGNORECASE)

    # Enforcement rule 4: append citation
    full_answer = answer_text + f"\n\n[Source: {doc_name}, Section {section_id}]"

    return {"answer": full_answer, "source_doc": doc_name,
            "source_section": section_id, "is_refusal": False}


# ─────────────────────────────────────────────────────────────────────────────
# Interactive CLI
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  UC-X — Ask My Documents  (CMC Policy Q&A Agent)")
    print("=" * 60)
    print("Loading policy documents...")

    file_paths = [os.path.join(POLICY_DIR, f) for f in POLICY_FILES]

    try:
        result = retrieve_documents(file_paths)
    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
        raise SystemExit(1)

    index = result["index"]
    flat  = result["flat"]

    total_sections = sum(len(v) for v in index.values())
    print(f"Loaded {len(index)} documents · {total_sections} sections indexed")
    for doc_name, sections in index.items():
        print(f"  {doc_name}: {len(sections)} sections")

    print("\nType your question and press Enter. Type 'quit' or 'exit' to stop.\n")

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        result = answer_question(question, index, flat)

        print()
        if result["is_refusal"]:
            print("Agent [REFUSAL]:")
        else:
            print(f"Agent [Source: {result['source_doc']}, Section {result['source_section']}]:")
        print(result["answer"])
        print()


if __name__ == "__main__":
    main()
