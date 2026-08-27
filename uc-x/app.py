"""
UC-X app.py — Policy Document Q&A Agent
Built using RICE (agents.md) + skills.md + CRAFT workflow.

CRAFT breakdown embedded in this implementation:
  C (Context)  — Three indexed policy documents; no external knowledge.
  R (Role)     — Single-source Policy Q&A Agent with strict refusal.
  A (Action)   — Load docs → parse sections → match question → cite or refuse.
  F (Format)   — Factual answer + [document_name, Section X.Y] OR refusal template.
  T (Tone)     — Neutral, factual, zero speculation.
"""
import os
import re
import sys

# ─────────────────────────────────────────────────────────────────────
# Constants — from agents.md enforcement rules
# ─────────────────────────────────────────────────────────────────────

POLICY_FILES = [
    os.path.join("..", "data", "policy-documents", "policy_hr_leave.txt"),
    os.path.join("..", "data", "policy-documents", "policy_it_acceptable_use.txt"),
    os.path.join("..", "data", "policy-documents", "policy_finance_reimbursement.txt"),
]

DOCUMENT_NAMES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact the relevant team "
    "for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "usually",
    "in most cases",
    "it is likely",
]

# Abbreviation expansions used in policy documents
ABBREVIATIONS = {
    "lwp": "leave without pay",
    "lop": "loss of pay",
    "da": "daily allowance",
    "cmc": "city municipal corporation",
    "mfa": "multi factor authentication",
    "byod": "bring your own device",
    "wfh": "work from home",
}


# ─────────────────────────────────────────────────────────────────────
# Skill 1: retrieve_documents
# (skills.md — loads all 3 policy files, parses into sections,
#  builds in-memory index keyed by document name + section number)
# ─────────────────────────────────────────────────────────────────────

def retrieve_documents(file_paths: list, doc_names: list) -> dict:
    """
    Loads all three policy documents, parses them into sections,
    and returns a structured index:
      { "policy_hr_leave.txt": { "2.6": "full section text..." }, ... }

    Error handling (from skills.md):
      - If any file is missing or unreadable, raises an error naming
        the missing file. All three must load successfully.
    """
    if len(file_paths) != 3:
        raise ValueError(
            f"Expected exactly 3 policy file paths, got {len(file_paths)}."
        )

    # Resolve paths relative to this script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    document_index = {}

    for file_path, doc_name in zip(file_paths, doc_names):
        abs_path = os.path.join(script_dir, file_path)

        if not os.path.isfile(abs_path):
            raise FileNotFoundError(
                f"Policy file missing or unreadable: '{doc_name}' "
                f"(looked at: {abs_path})"
            )

        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            raise IOError(
                f"Failed to read policy file '{doc_name}': {e}"
            )

        sections = _parse_sections(lines)

        if not sections:
            raise ValueError(
                f"Policy file '{doc_name}' contains no numbered sections. "
                "Cannot build index."
            )

        document_index[doc_name] = sections

    return document_index


def _parse_sections(lines: list) -> dict:
    """
    Parses raw lines from a policy document into a dict of
    { section_number: full_section_text }.
    Section numbers are X.Y format (e.g. "2.6", "3.1").
    """
    sections = {}
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)")
    current_id = None
    current_text_parts = []

    for line in lines:
        stripped = line.strip()

        # Skip headers, decorative separators, and empty lines
        if (
            not stripped
            or stripped.startswith("═")
            or stripped.isupper()
            or stripped.startswith("Document ")
            or stripped.startswith("Version:")
        ):
            continue

        match = clause_pattern.match(stripped)
        if match:
            # Save previous section
            if current_id:
                sections[current_id] = " ".join(current_text_parts)
            current_id = match.group(1)
            current_text_parts = [match.group(2)]
        elif current_id:
            # Continuation line of the current section
            current_text_parts.append(stripped)

    # Save the last section
    if current_id:
        sections[current_id] = " ".join(current_text_parts)

    return sections


# ─────────────────────────────────────────────────────────────────────
# Skill 2: answer_question
# (skills.md — searches indexed documents, returns single-source
#  answer + citation OR the refusal template)
# ─────────────────────────────────────────────────────────────────────

def answer_question(question: str, document_index: dict) -> str:
    """
    Accepts a user question and the document index, searches for
    matching sections, and returns:
      (a) A single-source answer with citation [doc_name, Section X.Y], OR
      (b) The refusal template verbatim.

    Enforcement rules (from agents.md):
      - Never combine claims from two different documents.
      - Never use hedging phrases.
      - Every factual claim includes a citation.
      - If ambiguous across documents, prefer the single most relevant
        document; if genuine ambiguity, refuse.
      - Never fabricate section numbers or details.
    """
    # Guard: empty or nonsensical question
    if not question or not question.strip():
        return REFUSAL_TEMPLATE

    question_lower = question.lower().strip()

    # Build a list of (doc_name, section_id, section_text, relevance_score)
    matches = []

    for doc_name, sections in document_index.items():
        for section_id, section_text in sections.items():
            score = _compute_relevance(question_lower, section_text.lower())
            if score > 0:
                matches.append((doc_name, section_id, section_text, score))

    if not matches:
        return REFUSAL_TEMPLATE

    # Sort by relevance descending
    matches.sort(key=lambda m: m[3], reverse=True)

    # Minimum relevance threshold — if the best match is too weak,
    # the question is not covered in the documents. This prevents
    # false positives from incidental word overlap.
    top_score = matches[0][3]
    if top_score < 2.0:
        return REFUSAL_TEMPLATE

    # Enforcement: single-source only.
    # Group matches by document.
    doc_scores = {}
    for doc_name, section_id, section_text, score in matches:
        if doc_name not in doc_scores:
            doc_scores[doc_name] = []
        doc_scores[doc_name].append((section_id, section_text, score))

    # Pick the document with the highest single-section score (not total),
    # to favor precision over breadth.
    best_doc = max(
        doc_scores.keys(),
        key=lambda d: max(m[2] for m in doc_scores[d]),
    )

    # Get the best matching sections from that single document
    best_sections = sorted(
        doc_scores[best_doc], key=lambda m: m[2], reverse=True
    )

    # Build the answer: include the top section, plus any additional
    # sections that are at least 30% as relevant as the top one.
    # This ensures closely related sections (e.g. 5.1 + 5.2 for LWP)
    # are included together while filtering out marginal matches.
    answer_parts = []
    used_sections = []
    top_section_score = best_sections[0][2]

    for section_id, section_text, score in best_sections:
        if score >= top_section_score * 0.3:
            answer_parts.append(section_text)
            used_sections.append(section_id)

    # Format the answer with citation(s)
    answer_text = " ".join(answer_parts)

    # Build citation string
    if len(used_sections) == 1:
        citation = f"[{best_doc}, Section {used_sections[0]}]"
    else:
        section_refs = ", ".join(f"Section {s}" for s in used_sections)
        citation = f"[{best_doc}, {section_refs}]"

    return f"{answer_text}\n\n{citation}"


def _expand_abbreviations(text: str) -> str:
    """
    Expands known abbreviations in the text so that e.g. 'LWP'
    becomes 'leave without pay', allowing keyword matching to work
    across abbreviation boundaries.
    """
    result = text
    for abbr, expansion in ABBREVIATIONS.items():
        # Match whole-word abbreviations only (case-insensitive)
        result = re.sub(
            r'\b' + re.escape(abbr) + r'\b',
            expansion,
            result,
            flags=re.IGNORECASE,
        )
    return result


def _stem(word: str) -> str:
    """
    Naive suffix-stripping stemmer. Reduces simple morphological
    variants so 'install'/'installed', 'approve'/'approval'/'approves'
    match each other. Not a full Porter stemmer — just enough for
    policy document vocabulary.
    """
    # Order matters: try longer suffixes first
    for suffix in ("ation", "ment", "ness", "able", "ible", "tion",
                   "sion", "ence", "ance", "ious", "eous", "ling",
                   "ally", "ful", "ous", "ive", "ing", "ies",
                   "ity", "ual", "ary", "ory",
                   "ed", "ly", "er", "es", "al", "en"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    if word.endswith("s") and len(word) > 3:
        return word[:-1]
    return word


def _compute_relevance(question: str, section_text: str) -> float:
    """
    Computes a relevance score between a question and a section's text.
    Uses stemmed keyword overlap + bigram (phrase) matching for precision.
    Returns a float score >= 0.

    Scoring:
      - Each matching stemmed keyword:  1 point
      - Each matching stemmed bigram:   2 bonus points (phrase proximity)
    """
    stopwords = {
        "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "shall",
        "should", "may", "might", "can", "could", "i", "my", "me", "we",
        "our", "you", "your", "he", "she", "it", "they", "them", "their",
        "this", "that", "these", "those", "what", "which", "who", "whom",
        "how", "when", "where", "why", "if", "or", "and", "but", "not",
        "no", "nor", "so", "too", "very", "just", "about", "of", "in",
        "on", "at", "to", "for", "with", "by", "from", "up", "out",
        "off", "over", "under", "into", "through", "during", "before",
        "after", "above", "below", "between", "same", "any", "each",
        "all", "both", "few", "more", "most", "other", "some", "such",
        "than", "also", "as", "get", "use", "used",
        # Domain-specific common words that add noise
        "employee", "employees", "must", "day", "days",
        "required", "within", "department", "upon", "per",
    }

    # Expand abbreviations in both question and section text
    expanded_q = _expand_abbreviations(question)
    expanded_s = _expand_abbreviations(section_text)

    # Tokenize into words
    q_tokens = re.findall(r"[a-z]+", expanded_q)
    s_tokens = re.findall(r"[a-z]+", expanded_s)

    # Remove stopwords and stem
    q_words = [_stem(w) for w in q_tokens if w not in stopwords]
    s_words_set = set(_stem(w) for w in s_tokens if w not in stopwords)

    if not q_words:
        return 0.0

    # Keyword overlap score (stemmed)
    overlap = set(q_words) & s_words_set
    keyword_score = len(overlap)

    if keyword_score == 0:
        return 0.0

    # Bigram matching on stemmed tokens — rewards phrase proximity
    q_bigrams = set()
    for i in range(len(q_words) - 1):
        q_bigrams.add((q_words[i], q_words[i + 1]))

    s_filtered = [_stem(w) for w in s_tokens if w not in stopwords]
    s_bigrams = set()
    for i in range(len(s_filtered) - 1):
        s_bigrams.add((s_filtered[i], s_filtered[i + 1]))

    bigram_overlap = q_bigrams & s_bigrams
    bigram_score = len(bigram_overlap) * 2

    total = keyword_score + bigram_score
    return total


# ─────────────────────────────────────────────────────────────────────
# Main — Interactive CLI (CRAFT Action: load → loop → answer/refuse)
# ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  UC-X — Policy Document Q&A Agent")
    print("  Ask questions about HR Leave, IT Acceptable Use,")
    print("  or Finance Reimbursement policies.")
    print("  Type 'quit' or 'exit' to stop.")
    print("=" * 60)
    print()

    # Step 1: Load and index all policy documents (retrieve_documents skill)
    try:
        document_index = retrieve_documents(POLICY_FILES, DOCUMENT_NAMES)
        doc_count = sum(len(secs) for secs in document_index.values())
        print(f"[System] Loaded {len(document_index)} documents "
              f"({doc_count} total sections indexed).\n")
    except (FileNotFoundError, IOError, ValueError) as e:
        print(f"[Fatal] {e}", file=sys.stderr)
        sys.exit(1)

    # Step 2: Interactive Q&A loop (answer_question skill)
    while True:
        try:
            question = input("Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[System] Goodbye.")
            break

        if question.lower() in ("quit", "exit", "q"):
            print("[System] Goodbye.")
            break

        if not question:
            print("[System] Please enter a question.\n")
            continue

        # Get the answer (single-source + citation OR refusal)
        answer = answer_question(question, document_index)
        print(f"\n{answer}\n")


if __name__ == "__main__":
    main()
