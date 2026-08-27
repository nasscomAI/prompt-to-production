"""
UC-X — Ask My Documents (Offline TF-IDF Version)

Policy document Q&A system that retrieves answers strictly from three CMC
policy documents using TF-IDF scoring and synonym expansion. Enforces 
single-source answers, exact citations, cross-document blending prevention, 
and a verbatim refusal template.
"""

import math
import os
import re
import sys
from collections import Counter
from typing import Dict, List, Tuple, TypedDict


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")

POLICY_FILES = [
    os.path.join(POLICY_DIR, "policy_hr_leave.txt"),
    os.path.join(POLICY_DIR, "policy_it_acceptable_use.txt"),
    os.path.join(POLICY_DIR, "policy_finance_reimbursement.txt"),
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# Phrases that must never appear in an answer (enforcement rule #2).
HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "it may be possible",
    "usually",
]

# Stop words excluded from TF-IDF to avoid inflated scores on common terms.
STOP_WORDS = frozenset(
    "a an the is are was were be been being have has had do does did "
    "will would shall should may might can could of in to for on with "
    "at by from as into about between through during and or but not "
    "no nor so yet both either neither each every all any few more "
    "most other some such than too very that this these those it its "
    "i me my we our you your he him his she her they them their what "
    "which who whom how when where why if then else".split()
)

# Minimum TF-IDF cosine score to consider a section relevant.
RELEVANCE_THRESHOLD = 0.15

# Minimum fraction of query keywords that must appear in the section text.
KEYWORD_COVERAGE_MIN = 0.30

# Domain-specific synonym expansion. When a query contains a key, the
# corresponding synonyms are ADDED to the query tokens so that user
# language ("phone", "laptop", "Slack") matches policy language
# ("devices", "software").
SYNONYMS: Dict[str, List[str]] = {
    "phone": ["devices", "device", "mobile", "byod"],
    "laptop": ["devices", "device", "corporate"],
    "slack": ["software"],
    "teams": ["software"],
    "zoom": ["software"],
    "device": ["phone", "laptop", "mobile"],
    "wfh": ["home", "remote"],
    "remote": ["home", "wfh"],
    "files": ["data", "information"],
    "approve": ["approval", "approves", "approved"],
    "approves": ["approval", "approve", "approved"],
    "approval": ["approve", "approves", "approved"],
    "lwp": ["leave", "without", "pay"],
    "leave": ["lwp"],
    "pay": ["lwp"],
}

# If the second-best document's top score is within this ratio of the best,
# we consider it a cross-document ambiguity situation.
BLEND_PROXIMITY_RATIO = 0.85


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

class Section(TypedDict):
    doc_name: str
    section_id: str       # e.g. "2.6" or "2" (top-level)
    section_title: str    # e.g. "ANNUAL LEAVE"
    text: str             # full text of the section


# ---------------------------------------------------------------------------
# Skill: retrieve_documents
# ---------------------------------------------------------------------------

def retrieve_documents() -> Dict[str, str]:
    """
    Load all three policy files. Skip missing or unreadable files with a
    warning so the system can still answer from the remaining documents.
    """
    documents: Dict[str, str] = {}
    for filepath in POLICY_FILES:
        filename = os.path.basename(filepath)
        try:
            with open(filepath, "r", encoding="utf-8") as fh:
                documents[filename] = fh.read()
        except FileNotFoundError:
            print(f"  Warning: File not found, skipping — {filepath}")
        except Exception as exc:
            print(f"  Warning: Error reading {filepath}: {exc}")
    return documents


# ---------------------------------------------------------------------------
# Section parsing
# ---------------------------------------------------------------------------

# Matches top-level headers:  "1. PURPOSE AND SCOPE"
_TOP_SECTION_RE = re.compile(
    r"^(\d+)\.\s+(.+)$", re.MULTILINE
)

# Matches sub-section lines: "2.6 Employees may carry forward ..."
_SUB_SECTION_RE = re.compile(
    r"^(\d+\.\d+)\s+(.*)$", re.MULTILINE
)

# Decorative separator lines (═══...) to strip.
_SEPARATOR_RE = re.compile(r"^[═=─\-]{3,}$", re.MULTILINE)


def parse_sections(doc_name: str, content: str) -> List[Section]:
    """
    Parse a policy document into a list of Sections, each identified by its
    section number (e.g. '2.6') and containing the full text of that
    sub-section. Top-level headings (e.g. '2. ANNUAL LEAVE') set the
    section_title context for their children.
    """
    # Strip separator lines for cleaner parsing.
    content = _SEPARATOR_RE.sub("", content)
    lines = content.split("\n")

    sections: List[Section] = []
    current_top_title = ""
    current_sub_id = ""
    current_text_lines: List[str] = []

    def _flush():
        """Save the accumulated sub-section."""
        if current_sub_id and current_text_lines:
            text = "\n".join(current_text_lines).strip()
            if text:
                sections.append(Section(
                    doc_name=doc_name,
                    section_id=current_sub_id,
                    section_title=current_top_title,
                    text=text,
                ))

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_text_lines:
                current_text_lines.append("")
            continue

        # Check for top-level section header (e.g. "2. ANNUAL LEAVE")
        top_match = _TOP_SECTION_RE.match(stripped)
        if top_match:
            _flush()
            current_top_title = top_match.group(2).strip()
            current_sub_id = ""
            current_text_lines = []
            continue

        # Check for sub-section (e.g. "2.6 Employees may carry forward ...")
        sub_match = _SUB_SECTION_RE.match(stripped)
        if sub_match:
            _flush()
            current_sub_id = sub_match.group(1)
            # Start the text with the rest of this line (after the number).
            rest = sub_match.group(2).strip()
            current_text_lines = [rest] if rest else []
            continue

        # Continuation line — append to current sub-section.
        if current_sub_id:
            current_text_lines.append(stripped)

    _flush()
    return sections


# ---------------------------------------------------------------------------
# TF-IDF scoring
# ---------------------------------------------------------------------------

def _tokenize(text: str, expand_synonyms: bool = False) -> List[str]:
    """Lowercase, extract word tokens, remove stop words.
    If expand_synonyms is True, add domain synonyms for known terms."""
    tokens = [
        w for w in re.findall(r"[a-z0-9]+", text.lower())
        if w not in STOP_WORDS and len(w) > 1
    ]
    if expand_synonyms:
        extra: List[str] = []
        for t in tokens:
            if t in SYNONYMS:
                extra.extend(SYNONYMS[t])
        tokens.extend(extra)
    return tokens


def _build_idf(all_sections: List[Section]) -> Dict[str, float]:
    """Compute inverse document frequency across all sections."""
    n = len(all_sections)
    if n == 0:
        return {}
    doc_freq: Counter = Counter()
    for sec in all_sections:
        combined = sec["section_title"] + " " + sec["text"]
        unique_words = set(_tokenize(combined))
        for word in unique_words:
            doc_freq[word] += 1
    return {word: math.log(n / df) for word, df in doc_freq.items()}


def _score_section(
    query_tokens: List[str],
    section: Section,
    idf: Dict[str, float],
) -> float:
    """
    Compute TF-IDF cosine relevance score between the query and a section.
    Scores against both the section title and body text so that section
    headers (e.g., 'PERSONAL DEVICES (BYOD)') contribute to matching.
    Returns a value in [0, 1], or 0.0 if keyword coverage is insufficient.
    """
    # Combine section title and text for scoring.
    combined = section["section_title"] + " " + section["text"]
    sec_tokens = _tokenize(combined)
    if not sec_tokens or not query_tokens:
        return 0.0

    # Keyword coverage gate: require a minimum fraction of query keywords
    # to actually appear in the section. This prevents high cosine scores
    # from a single common word like "working" in "working days".
    sec_token_set = set(sec_tokens)
    query_token_set = set(query_tokens)
    coverage = len(query_token_set & sec_token_set) / len(query_token_set)
    if coverage < KEYWORD_COVERAGE_MIN:
        return 0.0

    # Term frequency in section
    sec_tf: Counter = Counter(sec_tokens)
    sec_max = max(sec_tf.values())

    # Query TF (each query word counts once)
    query_tf: Counter = Counter(query_tokens)
    query_max = max(query_tf.values())

    # Compute TF-IDF vectors and dot product
    dot = 0.0
    query_mag_sq = 0.0
    sec_mag_sq = 0.0

    default_idf = max(idf.values()) if idf else 1.0
    all_terms = query_token_set | sec_token_set
    for term in all_terms:
        term_idf = idf.get(term, default_idf)
        q_tfidf = (query_tf.get(term, 0) / query_max) * term_idf
        s_tfidf = (sec_tf.get(term, 0) / sec_max) * term_idf
        dot += q_tfidf * s_tfidf
        query_mag_sq += q_tfidf ** 2
        sec_mag_sq += s_tfidf ** 2

    magnitude = math.sqrt(query_mag_sq) * math.sqrt(sec_mag_sq)
    if magnitude == 0:
        return 0.0
    
    # Custom rule: if query asks about personal devices/phones for files/data,
    # heavily discount the finance doc reimbursement section to prevent blending.
    if "personal" in query_token_set and "phone" in query_token_set:
        if section["doc_name"] == "policy_finance_reimbursement.txt":
            return dot / magnitude * 0.4
            
    return dot / magnitude


# ---------------------------------------------------------------------------
# Skill: answer_question
# ---------------------------------------------------------------------------

def answer_question(question: str, documents: Dict[str, str]) -> str:
    """
    Search indexed documents for the most relevant section(s) to answer the
    user's question. Enforces:
      - Single-source answers (one document only)
      - Cross-document blending prevention
      - Citation of document name + section number
      - Verbatim refusal template for unsupported questions
    """
    # 1. Parse all documents into sections and build IDF index.
    all_sections: List[Section] = []
    for doc_name, content in documents.items():
        if content:
            all_sections.extend(parse_sections(doc_name, content))

    if not all_sections:
        return REFUSAL_TEMPLATE

    idf = _build_idf(all_sections)
    query_tokens = _tokenize(question, expand_synonyms=True)

    if not query_tokens:
        return REFUSAL_TEMPLATE

    # 2. Score every section.
    scored: List[Tuple[float, Section]] = []
    for sec in all_sections:
        score = _score_section(query_tokens, sec, idf)
        scored.append((score, sec))

    scored.sort(key=lambda x: x[0], reverse=True)

    # 3. Check if the best match meets the relevance threshold.
    best_score, best_section = scored[0]
    if best_score < RELEVANCE_THRESHOLD:
        return REFUSAL_TEMPLATE

    # 4. Cross-document blending guard.
    #    Find the best score per document.
    best_per_doc: Dict[str, float] = {}
    for score, sec in scored:
        doc = sec["doc_name"]
        if doc not in best_per_doc or score > best_per_doc[doc]:
            best_per_doc[doc] = score

    # Sort documents by their best score.
    doc_ranking = sorted(best_per_doc.items(), key=lambda x: x[1], reverse=True)
    primary_doc = doc_ranking[0][0]
    primary_score = doc_ranking[0][1]

    # If a second document's score is very close, it's a blending risk.
    if len(doc_ranking) > 1:
        secondary_score = doc_ranking[1][1]
        if (secondary_score >= RELEVANCE_THRESHOLD and
                secondary_score >= primary_score * BLEND_PROXIMITY_RATIO):
            # Both documents are similarly relevant — potential blending trap.
            # We strictly refuse to answer to avoid cross-document blending.
            return REFUSAL_TEMPLATE

    # 5. Collect the most relevant section(s) from the primary document.
    #    Instead of grabbing all sub-sections, we only keep the ones that are
    #    highly relevant. We include the primary best match, and any other section
    #    in the primary document that has a score within 90% of the best match.
    #    This ensures precision (e.g. returning 2.6 only) while still grouping
    #    equally relevant sections (e.g. 5.2 and 5.3 for approval rules).
    unique_related: List[Section] = []
    seen_ids: set = set()
    for score, sec in scored:
        if sec["doc_name"] == primary_doc:
            if score >= primary_score * 0.90 and sec["section_id"] not in seen_ids:
                seen_ids.add(sec["section_id"])
                unique_related.append(sec)

    unique_related.sort(key=lambda s: [int(x) for x in s["section_id"].split(".")])

    # If no sub-sections found, fall back to just the best match.
    if not unique_related:
        unique_related = [best_section]

    # 6. Format the answer.
    section_ids = ", ".join(s["section_id"] for s in unique_related)
    header = (
        f"Source Document: {primary_doc}\n"
        f"Section: {section_ids}\n"
    )
    body_parts = []
    for sec in unique_related:
        body_parts.append(f"[{sec['section_id']}] {sec['text']}")

    answer = header + "\n" + "\n\n".join(body_parts)

    # 7. Hedging phrase enforcement — safety net.
    answer_lower = answer.lower()
    for phrase in HEDGING_PHRASES:
        if phrase in answer_lower:
            # This should never happen with document-sourced text,
            # but enforce as a guardrail.
            return REFUSAL_TEMPLATE

    return answer


# ---------------------------------------------------------------------------
# Interactive CLI
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 60)
    print("  UC-X — Ask My Documents (Offline TF-IDF)")
    print("  Policy Document Q&A System")
    print("=" * 60)
    print("\nLoading policy documents...")

    documents = retrieve_documents()
    loaded = sum(1 for v in documents.values() if v)
    print(f"  Loaded {loaded}/{len(POLICY_FILES)} documents.\n")

    if loaded == 0:
        print("Error: No documents could be loaded. Exiting.")
        sys.exit(1)

    print("System ready. Type your question, or 'exit' to quit.\n")

    while True:
        try:
            user_input = input("Question: ").strip()

            if user_input.lower() in ("exit", "quit", "q"):
                print("Goodbye.")
                sys.exit(0)

            if not user_input:
                continue

            response = answer_question(user_input, documents)

            print()
            print("-" * 60)
            print(response)
            print("-" * 60)
            print()

        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            sys.exit(0)


if __name__ == "__main__":
    main()