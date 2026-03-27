"""
UC-X app.py — Ask My Documents.
Built following the RICE rules in agents.md and skills defined in skills.md.

Role:       HR Executive
Intent:     Provide responses based on the policy documents only.
Context:    Responses must be grounded in the loaded policy documents only.

Enforcement:
  - Never combine claims from two different documents into a single answer.
  - Never use hedging phrases: "while not explicitly covered", "typically",
    "generally understood", "it is common practice".
  - If question is not in the documents — use the refusal template exactly,
    no variations.
  - Cite source document name + section number for every factual claim.

Run:
    python app.py
Interactive CLI — type questions, read answers.  Type 'quit' or 'exit' to stop.
"""

import os
import re
import sys
import math
from collections import defaultdict

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# Minimum combined score to return an answer (below → refusal template).
RELEVANCE_THRESHOLD = 0.10

# Weight applied to the chapter-heading overlap bonus.
TITLE_BOOST = 0.30

# Bonus applied when a query word's stem matches the passage body (broader
# lexical matching that helps "approves" hitting "approval" etc.)
STEM_BONUS = 0.05

# Hedging phrases the system must never emit
HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "generally",
    "usually",
    "often",
]

# ---------------------------------------------------------------------------
# Synonym / query-expansion map
# Words on the LEFT will be expanded to include words on the RIGHT during
# query tokenisation — this lets "phone" → "device" and "approves" → "approval".
# ---------------------------------------------------------------------------
SYNONYMS: dict = {
    "phone": ["device", "devices", "byod", "mobile"],
    "personal": ["device", "devices", "byod"],
    "laptop": ["device", "devices", "corporate", "software"],
    "install": ["software", "installation"],
    "approves": ["approval", "approve", "lwp"],
    "approve": ["approval", "lwp"],
    "approved": ["approval"],
    "who": [],                      # not useful for retrieval
    "files": ["data", "access"],
    "culture": [],                  # intentionally left empty → low signal
    "flexible": [],
    "view": [],
}

# ---------------------------------------------------------------------------
# Common English stop-words
# ---------------------------------------------------------------------------
_STOPWORDS = {
    "a", "an", "the", "is", "in", "of", "on", "and", "or", "to", "for",
    "that", "this", "it", "can", "i", "my", "me", "do", "if", "at", "by",
    "be", "are", "was", "with", "as", "we", "you", "from", "what", "when",
    "how", "please", "tell", "does", "about", "not", "its", "any", "all",
    "no", "will", "which",
    # Domain noise words: very common in policy docs, low discriminative value
    "working",  # appears in 'working days' everywhere; unhelpful for retrieval
    "company",  # not in policy body text
    "view",     # question filler word
}

# ---------------------------------------------------------------------------
# Skill 1 — retrieve_documents
# ---------------------------------------------------------------------------

def retrieve_documents(data_dir: str = DATA_DIR) -> dict:
    """
    Skill: retrieve_documents
    Loads the three policy documents and indexes them as a list of passage
    tuples per document:  (section_label, chapter_heading, body_text)

    Errors: exits with a clear message if any document is not found.
    """
    index = {}

    for filename in POLICY_FILES:
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            print(
                f"[ERROR] Document not found: {filepath}\n"
                "Please ensure all three policy files are present in "
                f"'{data_dir}' before running.",
                file=sys.stderr,
            )
            sys.exit(1)

        with open(filepath, encoding="utf-8") as fh:
            raw = fh.read()

        index[filename] = _split_into_passages(raw)

    return index


def _split_into_passages(text: str) -> list:
    """
    Parse a CMC policy document into (section_label, chapter_heading, body) tuples.

    Document structure uses:
      ══════════════════════
      N. CHAPTER TITLE
      ══════════════════════
      N.1  Sub-point text
           continuation…
      N.2  Next sub-point
    """
    chapter_re = re.compile(r"^\s*(\d+)\.\s+([A-Z][A-Z0-9 \(\)/&,'-]+)\s*$")
    sub_re     = re.compile(r"^\s*(\d+\.\d+(?:\.\d+)?)\s+(.+)")
    ignore_re  = re.compile(r"^[\s═]+$")

    passages: list = []
    chapter_heading = ""
    current_label: str | None = None
    current_lines: list = []

    def flush() -> None:
        if current_label and current_lines:
            passages.append((current_label, chapter_heading, " ".join(current_lines)))

    for line in text.splitlines():
        stripped = line.strip()
        if ignore_re.match(stripped) or not stripped:
            continue

        m_ch = chapter_re.match(stripped)
        if m_ch:
            chapter_heading = m_ch.group(2).strip()
            continue

        m_sub = sub_re.match(stripped)
        if m_sub:
            flush()
            current_label = m_sub.group(1)
            current_lines = [stripped]
            continue

        if current_label:
            current_lines.append(stripped)

    flush()
    return passages


# ---------------------------------------------------------------------------
# Skill 2 — answer_question
# ---------------------------------------------------------------------------

def answer_question(question: str, index: dict) -> str:
    """
    Skill: answer_question
    Searches indexed documents for the single best-matching passage.

    - Uses TF-IDF cosine similarity on passage body text.
    - Adds an additive chapter-heading token-overlap bonus.
    - Performs query expansion (synonyms) to improve recall.
    - Returns the exact refusal template when no passage is confident enough.
    - Structurally prevents cross-document blending: only one passage returned.
    """
    scored = _score_passages(question, index)

    if not scored:
        return REFUSAL_TEMPLATE

    top_score, doc_name, section_label, body = scored[0]

    if top_score < RELEVANCE_THRESHOLD:
        return REFUSAL_TEMPLATE

    return _format_answer(doc_name, section_label, body)


# ---------------------------------------------------------------------------
# TF-IDF + synonym retrieval
# ---------------------------------------------------------------------------

def _tokenise(text: str) -> list:
    """Lowercase alphanumeric tokenisation."""
    return re.findall(r"[a-z0-9]+", text.lower())


def _expand_query(tokens: list) -> list:
    """Expand query tokens using the SYNONYMS map."""
    expanded = list(tokens)
    for t in tokens:
        for syn in SYNONYMS.get(t, []):
            expanded.append(syn)
    return expanded


def _tf(tokens: list) -> dict:
    counts: dict = defaultdict(int)
    for t in tokens:
        counts[t] += 1
    total = len(tokens) if tokens else 1
    return {t: c / total for t, c in counts.items()}


def _build_idf(index: dict) -> dict:
    """IDF computed over passage body texts only."""
    doc_freq: dict = defaultdict(int)
    total = 0
    for passages in index.values():
        for _, _h, body in passages:
            total += 1
            for t in set(_tokenise(body)) - _STOPWORDS:
                doc_freq[t] += 1
    return {t: math.log((total + 1) / (df + 1)) + 1.0 for t, df in doc_freq.items()}


def _cosine(va: dict, vb: dict) -> float:
    dot = sum(va.get(t, 0.0) * vb.get(t, 0.0) for t in va)
    na = math.sqrt(sum(v * v for v in va.values())) or 1.0
    nb = math.sqrt(sum(v * v for v in vb.values())) or 1.0
    return dot / (na * nb)


def _heading_overlap(q_set: set, heading: str) -> float:
    """Fraction of non-stopword query tokens found in the chapter heading."""
    if not q_set or not heading:
        return 0.0
    h_tokens = set(_tokenise(heading)) - _STOPWORDS
    return len(q_set & h_tokens) / len(q_set)


def _score_passages(question: str, index: dict) -> list:
    """
    Score every passage against the question.
    Final score = cosine(body, query_expanded) + TITLE_BOOST * heading_overlap
    Returns sorted [(score, doc_name, label, body), …] descending.
    """
    idf = _build_idf(index)

    raw_tokens = [t for t in _tokenise(question) if t not in _STOPWORDS]
    if not raw_tokens:
        return []

    # Query expansion via synonym map
    expanded_tokens = _expand_query(raw_tokens)

    q_tf  = _tf(expanded_tokens)
    q_vec = {t: q_tf[t] * idf.get(t, 1.0) for t in q_tf}
    q_set = set(raw_tokens)  # original tokens for heading-overlap

    results = []
    for doc_name, passages in index.items():
        for section_label, heading, body in passages:
            p_tokens = [t for t in _tokenise(body) if t not in _STOPWORDS]
            p_tf  = _tf(p_tokens)
            p_vec = {t: p_tf[t] * idf.get(t, 1.0) for t in p_tf}

            base  = _cosine(q_vec, p_vec)
            boost = TITLE_BOOST * _heading_overlap(q_set, heading)
            results.append((base + boost, doc_name, section_label, body))

    results.sort(key=lambda x: x[0], reverse=True)
    return results


# ---------------------------------------------------------------------------
# Answer formatting
# ---------------------------------------------------------------------------

def _format_answer(doc_name: str, section_label: str, body: str) -> str:
    """Format the chosen passage with a mandatory citation line."""
    safe = body
    for phrase in HEDGING_PHRASES:
        safe = re.sub(re.escape(phrase), "[REMOVED]", safe, flags=re.IGNORECASE)

    citation = f"[Source: {doc_name}, Section {section_label}]"

    words = safe.split()
    lines: list = []
    line: list = []
    ll = 0
    for w in words:
        if ll + len(w) + 1 > 88:
            lines.append(" ".join(line))
            line = [w]
            ll = len(w)
        else:
            line.append(w)
            ll += len(w) + 1
    if line:
        lines.append(" ".join(line))

    return "\n".join(lines) + f"\n\n{citation}"


# ---------------------------------------------------------------------------
# Main — interactive CLI
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("  UC-X — Ask My Documents (Policy Q&A)")
    print("  Role: HR Executive | Source: Policy documents only")
    print("=" * 70)
    print("Loading policy documents …")

    try:
        index = retrieve_documents()
    except SystemExit:
        raise

    total_sections = sum(len(v) for v in index.values())
    print(f"  ✓ {len(index)} documents loaded, {total_sections} sections indexed.\n")
    print("Type your question and press Enter.  Type 'quit' or 'exit' to stop.\n")
    print("-" * 70)

    while True:
        try:
            question = input("\nQuestion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue

        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        answer = answer_question(question, index)
        print(f"\nAnswer:\n{answer}")
        print("-" * 70)


if __name__ == "__main__":
    main()
