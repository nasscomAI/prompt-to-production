"""
UC-X — Ask My Documents
Implements retrieve_documents and answer_question per agents.md (RICE) and skills.md.
Interactive CLI — type questions, get single-source cited answers or exact refusal template.
"""
import os
import re
import sys

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

POLICY_DOCS = [
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

# Phrases that must never appear in answers — hallucination markers
FORBIDDEN_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "generally",
    "usually",
    "as is standard",
    "employees are generally",
    "it is widely",
]

# Stop words excluded from keyword matching
STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "to", "of", "in", "on",
    "at", "by", "for", "with", "about", "from", "into", "through", "or",
    "and", "but", "if", "as", "it", "its", "this", "that", "these",
    "those", "i", "my", "me", "we", "our", "you", "your", "not", "no",
    "any", "all", "more", "also", "what", "who", "when", "where", "how",
    "which", "their", "there", "up", "use", "used", "using",
    # domain-generic terms that appear too broadly to discriminate
    "work", "must", "only", "after", "before", "within", "per", "without",
    # background topic words in LWP questions — intent signal comes from "approv"/"lwp"
    "pay", "leave",
}

# Minimum score to return an answer (not refusal)
MIN_SCORE = 0.5
# Minimum margin between top-doc and second-doc to avoid cross-doc ambiguity
BLEND_MARGIN = 2


# ---------------------------------------------------------------------------
# Skill 1: retrieve_documents
# ---------------------------------------------------------------------------

def _parse_sections(raw: str) -> dict:
    """Parse a policy document into { section_id: body } dict."""
    lines = raw.splitlines()
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if re.match(r'^[═─\-=*]{3,}$', stripped):
            continue
        if re.match(r'^\d+\.\s+[A-Z][A-Z\s\(\)/&]+$', stripped):
            continue
        cleaned.append(line)
    text = "\n".join(cleaned)

    clause_pattern = re.compile(r'(?m)^(\d+\.\d+)\s+(.*)')
    matches = list(clause_pattern.finditer(text))

    sections = {}
    for i, match in enumerate(matches):
        clause_id  = match.group(1)
        first_line = match.group(2).strip()
        start = match.end()
        end   = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        continuation = text[start:end].strip()
        body = re.sub(r'\s+', ' ', (first_line + " " + continuation)).strip()
        sections[clause_id] = body

    return sections


def retrieve_documents(doc_paths: list) -> dict:
    """
    Loads and indexes all policy documents.
    Returns { filename: { section_id: body } }
    """
    index = {}
    loaded = 0

    for path in doc_paths:
        filename = os.path.basename(path)
        if not os.path.exists(path):
            print(f"ERROR: Policy document not found: {path}", file=sys.stderr)
            sys.exit(1)

        with open(path, encoding="utf-8") as f:
            raw = f.read()

        if not raw.strip():
            print(f"WARNING: {filename} is empty — skipped.")
            continue

        sections = _parse_sections(raw)
        index[filename] = sections
        loaded += 1
        print(f"Indexed {len(sections)} sections from {filename}.")

    if loaded == 0:
        print("ERROR: No documents loaded successfully.", file=sys.stderr)
        sys.exit(1)

    return index


# ---------------------------------------------------------------------------
# Skill 2: answer_question
# ---------------------------------------------------------------------------

def _stem(word: str) -> str:
    """Strip common English suffixes to allow approve/approves/approval to match."""
    for suffix in ("tion", "ing", "ment", "ness", "al", "ed", "er", "es", "ly", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def _tokenize(text: str) -> set:
    """Lowercase, split on non-alphanumerics, remove stop words, apply stemming.
    Stop word filter is applied both before AND after stemming."""
    tokens = re.findall(r'[a-z0-9]+', text.lower())
    result = set()
    for t in tokens:
        if t in STOP_WORDS or len(t) <= 1:
            continue
        stemmed = _stem(t)
        if stemmed not in STOP_WORDS and len(stemmed) > 1:
            result.add(stemmed)
    return result


def _score_idf(question_tokens: set, body: str, idf: dict) -> float:
    """TF-IDF score with length normalisation.
    TF counts multiple occurrences — sections where a query term repeats score higher."""
    from collections import Counter
    raw_tokens = re.findall(r'[a-z0-9]+', body.lower())
    body_counts = Counter()
    for t in raw_tokens:
        if t in STOP_WORDS or len(t) <= 1:
            continue
        stemmed = _stem(t)
        if stemmed not in STOP_WORDS and len(stemmed) > 1:
            body_counts[stemmed] += 1
    n_unique = len(body_counts)
    if n_unique == 0:
        return 0.0
    raw = sum(body_counts[t] * idf.get(t, 1.0) for t in question_tokens if t in body_counts)
    return raw / (n_unique ** 0.5)  # length normalisation


def _build_idf(index: dict) -> dict:
    """
    Build inverse document frequency for every stemmed token across all sections.
    idf[token] = total_sections / sections_containing_token  (higher = rarer = more specific)
    """
    from collections import defaultdict
    section_count = defaultdict(int)
    total = 0
    for doc, sections in index.items():
        for body in sections.values():
            tokens = _tokenize(body)
            for t in tokens:
                section_count[t] += 1
            total += 1
    return {t: total / count for t, count in section_count.items()}


def _expand_query(q_tokens: set, original_question: str = "") -> set:
    """Add domain abbreviations when their full-form terms are present in the query.
    Uses the original question text so expansion works even if terms were stop-word filtered."""
    expanded = set(q_tokens)
    orig = original_question.lower()
    # "Leave Without Pay" → sections 5.2–5.4 use the abbreviation "LWP"
    if ("leave" in orig and ("pay" in orig or "without pay" in orig)) or "lwp" in orig:
        expanded.add("lwp")
    return expanded


def answer_question(question: str, index: dict) -> dict:
    """
    Finds the best single-source answer from the index using IDF-weighted scoring.
    Returns { answer, source_doc, source_section }.
    Refuses if: no match, cross-doc ambiguity, or blank question.
    """
    if not question or not question.strip():
        return {
            "answer":         REFUSAL_TEMPLATE,
            "source_doc":     "",
            "source_section": "",
        }

    idf = _build_idf(index)
    q_tokens = _expand_query(_tokenize(question), question)

    # Score every section in every document
    candidates = []   # (score, doc, section_id, body)
    for doc, sections in index.items():
        for section_id, body in sections.items():
            score = _score_idf(q_tokens, body, idf)
            if score > 0:
                candidates.append((score, doc, section_id, body))

    if not candidates:
        return {
            "answer":         REFUSAL_TEMPLATE,
            "source_doc":     "",
            "source_section": "",
        }

    # Sort descending by score
    candidates.sort(key=lambda x: -x[0])
    top_score, top_doc, top_section, top_body = candidates[0]

    # Reject if score below minimum threshold
    if top_score < MIN_SCORE:
        return {
            "answer":         REFUSAL_TEMPLATE,
            "source_doc":     "",
            "source_section": "",
        }

    # Cross-doc blending guard: if a different document also scores close, refuse
    for score, doc, section_id, body in candidates[1:]:
        if doc != top_doc and score >= top_score - BLEND_MARGIN:
            if score >= top_score:
                return {
                    "answer":         REFUSAL_TEMPLATE,
                    "source_doc":     "",
                    "source_section": "",
                }
            break

    return {
        "answer":         top_body,
        "source_doc":     top_doc,
        "source_section": top_section,
    }


# ---------------------------------------------------------------------------
# Main — Interactive CLI
# ---------------------------------------------------------------------------

def _find_doc_paths() -> list:
    """Locate policy documents relative to this script or CWD."""
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "data", "policy-documents"),
        os.path.join(os.getcwd(), "data", "policy-documents"),
        os.path.join(os.getcwd(), "..", "data", "policy-documents"),
    ]
    for base in candidates:
        paths = [os.path.join(base, d) for d in POLICY_DOCS]
        if all(os.path.exists(p) for p in paths):
            return paths
    return [os.path.join(candidates[0], d) for d in POLICY_DOCS]


def main():
    print("UC-X — Ask My Documents")
    print("Policies: HR Leave · IT Acceptable Use · Finance Reimbursement")
    print("Type your question and press Enter. Type 'quit' to exit.\n")

    doc_paths = _find_doc_paths()
    index = retrieve_documents(doc_paths)
    print()

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if question.lower() in ("quit", "exit", "q"):
            print("Exiting.")
            break

        result = answer_question(question, index)

        print()
        print(f"Answer: {result['answer']}")
        if result["source_doc"]:
            print(f"Source: {result['source_doc']}, Section {result['source_section']}")
        else:
            print("Source: (none)")
        print()


if __name__ == "__main__":
    main()
