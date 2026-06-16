"""
UC-X — Ask My Documents
Implements retrieve_documents and answer_question skills per agents.md RICE rules.
Interactive CLI: type questions, read single-source answers with citations.
"""
import os
import re
import sys

# ── Constants ─────────────────────────────────────────────────────────────────
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

# Phrases banned from all responses (enforcement rule 2)
BANNED_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "generally speaking",
    "it is generally",
    "in most organisations",
]

# Minimum keyword overlap score to return an answer instead of refusing
CONFIDENCE_THRESHOLD = 2

# Abbreviations to expand in document text during indexing
# Ensures acronym-only sections still match natural-language questions
ABBREVIATIONS = {
    r"\bLWP\b": "Leave Without Pay",
    r"\bDA\b":  "Daily Allowance",
    r"\bLOP\b": "Loss of Pay",
    r"\bMFA\b": "Multi-Factor Authentication",
    r"\bBYOD\b": "Bring Your Own Device personal device",
}

# Question-side synonym expansion — maps a question token to additional
# tokens to search for, preventing vocabulary mismatch with policy text
SYNONYM_EXPANSIONS: dict[str, set[str]] = {
    "laptop":   {"device", "devices"},
    "laptops":  {"device", "devices"},
    "phone":    {"device", "devices"},
    "phones":   {"device", "devices"},
    "files":    {"data", "documents", "information"},
    "approves": {"approval"},
    "approve":  {"approval"},
    "approved": {"approval"},
    "install":  {"installation", "software"},
    "slack":    {"software", "application"},
}


# ── Skill: retrieve_documents ─────────────────────────────────────────────────
def retrieve_documents(data_dir: str) -> dict:
    """
    Load all three policy files from data_dir, parse into:
      {doc_filename: {section_number: section_text}}
    Expands known abbreviations before indexing.
    Aborts if any file is missing. Warns if a doc has no section numbers.
    """
    index: dict[str, dict[str, str]] = {}

    for filename in POLICY_FILES:
        path = os.path.join(data_dir, filename)
        if not os.path.exists(path):
            sys.exit(f"ERROR: Required policy file not found: '{path}'")

        with open(path, encoding="utf-8") as f:
            raw = f.read()

        # Expand abbreviations so acronym-only sections match natural questions
        for pattern, expansion in ABBREVIATIONS.items():
            raw = re.sub(pattern, expansion, raw)

        sections: dict[str, str] = {}
        current_num = None
        current_lines: list[str] = []

        for line in raw.splitlines():
            match = re.match(r"^\s*(\d+\.\d+)\s+(.*)", line)
            if match:
                if current_num:
                    sections[current_num] = " ".join(current_lines).strip()
                current_num = match.group(1)
                current_lines = [match.group(2).strip()]
            elif current_num and line.strip() and not re.match(r"^[=\-\s\u2550\u2500]+$", line):
                current_lines.append(line.strip())
            elif re.match(r"^[=\-\s\u2550\u2500]+$", line) or re.match(r"^\d+\.\s+[A-Z]", line):
                if current_num:
                    sections[current_num] = " ".join(current_lines).strip()
                    current_num = None
                    current_lines = []

        if current_num:
            sections[current_num] = " ".join(current_lines).strip()

        if not sections:
            print(f"WARNING: No section numbers detected in '{filename}' — loaded as body.",
                  file=sys.stderr)
            sections["body"] = raw.strip()

        index[filename] = sections

    if len(index) < 3:
        sys.exit(f"ERROR: Only {len(index)} of 3 required documents loaded.")

    total = sum(len(s) for s in index.values())
    print(f"Loaded {len(index)} documents, {total} sections total.")
    for doc, secs in index.items():
        print(f"  {doc}: {len(secs)} sections")

    return index


# ── Skill: answer_question ─────────────────────────────────────────────────────
def answer_question(index: dict, question: str) -> dict:
    """
    Search index for a single-source answer. Returns:
      {"answer": str, "source": str|None, "answered": bool}
    Never blends across documents. Uses refusal template if not covered.
    """
    if len(index) < 3:
        raise ValueError(
            f"Index contains only {len(index)} documents — all 3 required before answering."
        )

    q_tokens = _expand_tokens(_tokenize(question))

    best_score = 0
    best_doc = None
    best_section = None
    best_text = None

    # Score every (doc, section) pair — pick single highest scorer (enforcement rule 1)
    for doc, sections in index.items():
        for sec_num, sec_text in sections.items():
            score = _score(q_tokens, sec_text)
            if score > best_score:
                best_score = score
                best_doc = doc
                best_section = sec_num
                best_text = sec_text

    # Below threshold → refusal (enforcement rule 3)
    if best_score < CONFIDENCE_THRESHOLD:
        return {
            "answer":   REFUSAL_TEMPLATE,
            "source":   None,
            "answered": False,
        }

    # Enforce: answer must come from exactly one source (enforcement rule 1)
    answer = best_text.strip()

    # Enforce: strip any banned hedging phrases (enforcement rule 2)
    for phrase in BANNED_PHRASES:
        if phrase.lower() in answer.lower():
            answer = re.sub(re.escape(phrase), "", answer, flags=re.IGNORECASE).strip()

    return {
        "answer":   answer,
        "source":   f"{best_doc} § {best_section}",
        "answered": True,
    }


def _tokenize(text: str) -> set[str]:
    """Lowercase word tokens, remove stopwords."""
    stopwords = {
        "i", "can", "the", "a", "an", "is", "are", "was", "be", "my", "for",
        "to", "of", "in", "on", "at", "do", "does", "what", "when", "how",
        "who", "which", "and", "or", "if", "it", "this", "that", "with",
        "from", "me", "we", "you", "they", "use", "used", "using", "work",
    }
    tokens = re.findall(r"[a-z]+", text.lower())
    return {t for t in tokens if t not in stopwords and len(t) > 2}


def _expand_tokens(tokens: set[str]) -> set[str]:
    """Expand question tokens with domain synonyms to bridge vocabulary gaps."""
    expanded = set(tokens)
    for token in tokens:
        if token in SYNONYM_EXPANSIONS:
            expanded.update(SYNONYM_EXPANSIONS[token])
    return expanded


def _score(q_tokens: set[str], section_text: str) -> int:
    """Count overlapping meaningful tokens between question and section."""
    sec_tokens = _tokenize(section_text)
    return len(q_tokens & sec_tokens)


# ── Interactive CLI ────────────────────────────────────────────────────────────
def main():
    # Locate policy documents relative to this file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir   = os.path.join(script_dir, "..", "data", "policy-documents")

    print("=" * 60)
    print("UC-X — Ask My Documents")
    print("Policy Q&A — single-source answers with citations only")
    print("Type 'quit' or 'exit' to stop.")
    print("=" * 60)
    print()

    index = retrieve_documents(data_dir)
    print()

    while True:
        try:
            question = input("Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        result = answer_question(index, question)

        print()
        if result["answered"]:
            print(f"Source  : {result['source']}")
            print(f"Answer  : {result['answer']}")
        else:
            print(f"Refused : {result['answer']}")
        print()


if __name__ == "__main__":
    main()
