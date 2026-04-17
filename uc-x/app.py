"""
UC-X — Ask My Documents
RAG pipeline: loads 3 CMC policy documents, indexes by section,
retrieves via TF-IDF, enforces single-source answers, refuses anything
not found in the documents.

Run modes:
  python app.py                          → interactive CLI
  python app.py --question "..."         → single question
  python app.py --input questions.txt    → batch from file
"""

import argparse
import math
import os
import re
import sys
from collections import defaultdict
from typing import Dict, List, Tuple

# ─────────────────────────────────────────────────────────
# CONFIGURATION  (from agents.md + skills.md + README.md)
# ─────────────────────────────────────────────────────────

DOCUMENT_PATHS = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "../data/policy-documents/policy_hr_leave.txt"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "../data/policy-documents/policy_it_acceptable_use.txt"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "../data/policy-documents/policy_finance_reimbursement.txt"),
]

DOC_NAMES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

# Exact refusal template from README.md / agents.md — used verbatim
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# Forbidden hedging phrases (agents.md enforcement)
FORBIDDEN_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
]

# If the top-2 results are from different documents AND the second score
# is >= this fraction of the top score → cross-doc ambiguity → refuse.
CROSS_DOC_AMBIGUITY_RATIO = 0.75

# Absolute minimum score to return any answer.
MIN_SCORE_THRESHOLD = 0.04

# Boost factor when all query tokens appear in the same section text (phrase match).
PHRASE_BOOST = 1.5

TITLE_BOOST = 1.2
# ─────────────────────────────────────────────────────────
# SKILL: retrieve_documents
# ─────────────────────────────────────────────────────────

def _tokenise(text: str) -> List[str]:
    """Lowercase, remove non-alphanumeric, split. Skip 1-char tokens."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return [w for w in text.split() if len(w) > 1]


def _parse_sections(raw_text: str, doc_name: str) -> List[Dict]:
    """
    Parse a CMC policy document into section-level chunks.

    Document format:
        [file header]
        ════════ (ruler)
        N. SECTION HEADING
        ════════ (ruler)
        body text for section N (all sub-clauses N.1, N.2 …)
        ════════ (ruler)
        N+1. SECTION HEADING
        ════════ (ruler)
        body text …

    Parts after splitting on ═{10,} alternate: heading / body / heading / body …
    Part 0 is always the file header (before the first ruler).
    """
    parts = re.split(r"═{10,}", raw_text)
    sections = []

    # Part 0: document header — kept for keyword matching but skipped as answers
    header_text = parts[0].strip()
    sections.append({
        "doc_name": doc_name,
        "section_id": "header",
        "section_title": "Document Header",
        "text": header_text,
        "tokens": _tokenise(header_text),
        "is_header": True,
    })

    # Parts 1,2 are heading/body; 3,4 are next heading/body; etc.
    i = 1
    while i < len(parts) - 1:
        heading_part = parts[i].strip()
        body_part = parts[i + 1].strip() if (i + 1) < len(parts) else ""
        i += 2

        if not heading_part:
            continue

        # Extract the section number (e.g. "2", "3.1")
        num_match = re.match(r"(\d+(?:\.\d+)?)", heading_part)
        section_id = num_match.group(1) if num_match else heading_part[:20]
        section_title = heading_part.splitlines()[0].strip()

        # Combine heading + body for retrieval so sub-clauses are searchable
        full_text = section_title + ("\n" + body_part if body_part else "")

        sections.append({
            "doc_name": doc_name,
            "section_id": section_id,
            "section_title": section_title,
            "title_tokens": _tokenise(section_title),
            "text": full_text,
            "tokens": _tokenise(full_text),
            "is_header": False,
        })

    return sections


def retrieve_documents(paths: List[str], names: List[str]) -> List[Dict]:
    """
    SKILL: retrieve_documents
    Loads all 3 policy files, parses them into section chunks, returns list.
    Stops execution if any file is missing or unreadable.
    """
    all_sections = []
    for path, name in zip(paths, names):
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            print(f"[ERROR] Policy file not found: {abs_path}", file=sys.stderr)
            sys.exit(1)
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                raw = f.read()
        except OSError as exc:
            print(f"[ERROR] Cannot read {abs_path}: {exc}", file=sys.stderr)
            sys.exit(1)

        sections = _parse_sections(raw, name)
        all_sections.extend(sections)

    return all_sections


# ─────────────────────────────────────────────────────────
# TF-IDF INDEX
# ─────────────────────────────────────────────────────────

def _build_tfidf_index(sections: List[Dict]) -> Dict:
    """
    Build smoothed TF-IDF vectors for every section.
    Returns: {'idf': {term: float}, 'vectors': [{section, vec, mag}]}
    """
    N = len(sections)
    df: Dict[str, int] = defaultdict(int)
    tf_per_section = []

    for sec in sections:
        tokens = sec["tokens"]
        if not tokens:
            tf_per_section.append({})
            continue
        freq: Dict[str, int] = defaultdict(int)
        for t in tokens:
            freq[t] += 1
        tf = {t: c / len(tokens) for t, c in freq.items()}
        tf_per_section.append(tf)
        for t in freq:
            df[t] += 1

    # Smoothed IDF
    idf = {t: math.log((N + 1) / (cnt + 1)) + 1.0 for t, cnt in df.items()}

    vectors = []
    for sec, tf in zip(sections, tf_per_section):
        vec = {t: tf_val * idf.get(t, 0.0) for t, tf_val in tf.items()}
        mag = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        vectors.append({"section": sec, "vec": vec, "mag": mag})

    return {"idf": idf, "vectors": vectors}


def _query_vector(query_tokens: List[str], idf: Dict[str, float]) -> Tuple[Dict, float]:
    """Compute sparse TF-IDF vector for the query."""
    if not query_tokens:
        return {}, 1.0
    freq: Dict[str, int] = defaultdict(int)
    for t in query_tokens:
        freq[t] += 1
    tf = {t: c / len(query_tokens) for t, c in freq.items()}
    vec = {t: tf_val * idf.get(t, 0.0) for t, tf_val in tf.items()}
    mag = math.sqrt(sum(v * v for v in vec.values())) or 1.0
    return vec, mag


def _cosine(vec_a: Dict, mag_a: float, vec_b: Dict, mag_b: float) -> float:
    """Cosine similarity between two sparse vectors."""
    dot = sum(vec_a.get(t, 0.0) * vec_b.get(t, 0.0) for t in vec_a)
    return dot / (mag_a * mag_b) if (mag_a * mag_b) > 0 else 0.0


# ─────────────────────────────────────────────────────────
# SKILL: answer_question
# ─────────────────────────────────────────────────────────

def detect_domains(query: str) -> List[str]:
    query_lower = query.lower()
    domains = set()
    if "leave" in query_lower:
        domains.add("hr")
    if "reimbursement" in query_lower or "finance" in query_lower:
        domains.add("finance")
    if "it" in query_lower or "acceptable use" in query_lower:
        domains.add("it")
    return list(domains)


def answer_question(query: str, index: Dict) -> str:
    """
    SKILL: answer_question
    Searches indexed documents for the most relevant single-source section.

    Enforcement (agents.md):
      1. Never combine claims from two different documents.
      2. Never use hedging phrases (FORBIDDEN_PHRASES).
      3. If question is not in any document → exact REFUSAL_TEMPLATE, no variations.
      4. Cite source document name + section number for every factual claim.

    Returns the section's verbatim text followed by a citation line,
    or REFUSAL_TEMPLATE when no confident single-source answer exists.
    """
    domains = detect_domains(query)
    if len(domains) != 1:
        return REFUSAL_TEMPLATE

    query_tokens = _tokenise(query)
    if not query_tokens:
        return REFUSAL_TEMPLATE

    q_vec, q_mag = _query_vector(query_tokens, index["idf"])

    # Score every section
    scored = []
    query_token_set = set(query_tokens)
    for entry in index["vectors"]:
        sec = entry["section"]
        if sec["is_header"]:
            continue  # headers never serve as answers

        score = _cosine(q_vec, q_mag, entry["vec"], entry["mag"])
        if score <= 0:
            continue

        # Boost when all query tokens appear in the section text (completeness)
        sec_token_set = set(sec["tokens"])
        overlap = query_token_set & sec_token_set
        if len(overlap) == len(query_token_set):
            score *= PHRASE_BOOST

        # Boost for title matches
        title_token_set = set(sec.get("title_tokens", []))
        if query_token_set & title_token_set:
            score *= TITLE_BOOST

        scored.append((score, sec))

    if not scored:
        return REFUSAL_TEMPLATE

    scored.sort(key=lambda x: x[0], reverse=True)

    best_score, best_sec = scored[0]

    # Threshold check — must be confident
    if best_score < MIN_SCORE_THRESHOLD:
        return REFUSAL_TEMPLATE

    # ── Cross-document blending check (agents.md rule 1) ─────────────
    # If a second result from a *different* document scores within
    # CROSS_DOC_AMBIGUITY_RATIO of the top, question spans multiple
    # sources → refuse rather than blend.
    for second_score, second_sec in scored[1:]:
        if second_sec["doc_name"] != best_sec["doc_name"]:
            if second_score >= best_score * CROSS_DOC_AMBIGUITY_RATIO:
                return REFUSAL_TEMPLATE
            break  # only check the first cross-doc competitor

    # ── Build answer ─────────────────────────────────────────────────
    citation = (
        f"[Source: {best_sec['doc_name']} "
        f"— Section {best_sec['section_id']}: {best_sec['section_title']}]"
    )
    answer_text = best_sec["text"].strip()

    return f"{answer_text}\n\n{citation}"


# ─────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────

def run_interactive(index: Dict) -> None:
    """Interactive REPL: type questions, get answers. 'quit' to exit."""
    print("\n" + "═" * 62)
    print("  CMC Policy Q&A  |  UC-X — Ask My Documents")
    print("  Documents: HR Leave · IT Acceptable Use · Finance Reimbursement")
    print("  Type your question and press Enter. Type 'quit' to exit.")
    print("═" * 62 + "\n")

    while True:
        try:
            query = input("❓ Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not query:
            continue
        if query.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        answer = answer_question(query, index)
        print(f"\n📄 Answer:\n{answer}\n")
        print("─" * 62 + "\n")


def run_single(question: str, index: Dict) -> None:
    """Answer a single question from --question flag."""
    print(answer_question(question, index))


def run_from_file(input_file: str, index: Dict) -> None:
    """Read questions one-per-line from a file and print each answer."""
    if not os.path.exists(input_file):
        print(f"[ERROR] Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)
    with open(input_file, "r", encoding="utf-8") as f:
        questions = [line.strip() for line in f if line.strip()]

    for q in questions:
        print(f"❓ {q}")
        print(f"📄 {answer_question(q, index)}")
        print("─" * 62 + "\n")


# ─────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="UC-X — Ask My Documents: single-source RAG over CMC policy docs."
    )
    parser.add_argument(
        "--input", metavar="FILE",
        help="Path to a text file with one question per line (batch mode).",
    )
    parser.add_argument(
        "--question", metavar="TEXT",
        help="Ask a single question from the command line.",
    )
    args = parser.parse_args()

    # SKILL: retrieve_documents
    print("[INFO] Loading policy documents...", file=sys.stderr)
    sections = retrieve_documents(DOCUMENT_PATHS, DOC_NAMES)
    index = _build_tfidf_index(sections)
    print(
        f"[INFO] Indexed {len(sections)} sections across {len(DOC_NAMES)} documents.\n",
        file=sys.stderr,
    )

    if args.question:
        run_single(args.question, index)
    elif args.input:
        run_from_file(args.input, index)
    else:
        run_interactive(index)


if __name__ == "__main__":
    main()
