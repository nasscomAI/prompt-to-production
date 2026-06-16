"""
UC-X — Ask My Documents
Implements retrieve_documents and answer_question per agents.md (RICE) and skills.md.

Core failure modes guarded against:
  - Cross-document blending  : single-source answers only; ambiguous cross-doc → refusal
  - Hedged hallucination     : no "typically", "generally", "while not explicitly covered"
  - Condition dropping       : verbatim section body preserved in answer
  - Citation omission        : every answer includes document name + section number
"""
import os
import re
import sys
from math import log

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

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
    "generally expected",
    "as standard practice",
]

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "can", "will", "would",
    "could", "should", "may", "might", "shall", "its", "if", "then",
    "than", "so", "such", "i", "we", "you", "he", "she", "they", "it",
    "me", "us", "him", "her", "this", "that", "these", "those", "what",
    "who", "how", "when", "where", "why", "which", "for", "on", "at",
    "by", "from", "to", "of", "in", "and", "or", "but", "not", "with",
    "my", "your", "our", "their", "any", "all", "some", "each", "no",
    "as", "also", "only", "just", "after", "before", "about", "per", "up",
}

# Minimum IDF-weighted score for a section to count as a match
MIN_SCORE = 0.8

# Ratio by which the top-scoring document must exceed the second
# to be returned as a single-source answer (below this → refusal)
AMBIGUITY_RATIO = 1.5

# Keywords that indicate a "who approves/authorizes" answer
WHO_ANSWER_KEYWORDS = {
    "approval", "requires", "required", "authorized", "authorize",
    "director", "commissioner", "head", "manager",
}
WHO_BOOST = 2.5  # Added to section score for each matching WHO keyword found

# Heading weight relative to body (headings help route but are less specific)
HEADING_WEIGHT = 0.25


# ---------------------------------------------------------------------------
# Skill 1: retrieve_documents
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> list:
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 2]


def _parse_document(file_path: str) -> dict:
    fname = os.path.basename(file_path)
    with open(file_path, encoding="utf-8", errors="replace") as f:
        raw_text = f.read()
    if not raw_text.strip():
        raise ValueError(f"Policy file is empty: {fname}")

    heading_map = {}
    for m in re.finditer(r'^(\d+)\.\s+([A-Z][A-Z\s\(\)\-&]+)$', raw_text, re.MULTILINE):
        heading_map[m.group(1)] = m.group(2).strip()

    clause_pattern = re.compile(
        r'^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+\s|^\d+\.\s+[A-Z]|\Z)',
        re.MULTILINE | re.DOTALL
    )

    sections = {}
    for match in clause_pattern.finditer(raw_text):
        sid  = match.group(1)
        body = match.group(2).strip()
        body = re.sub(r'[ \t]*\n[ \t]*', ' ', body).strip()
        body = re.sub(r'[\u2550\u2500\u2502\u251c\u2514\u2510\u250c\u2518\u2524]+', '', body).strip()
        body = re.sub(r'\s{2,}', ' ', body).strip()
        parent  = sid.split(".")[0]
        heading = heading_map.get(parent, "")
        sections[sid] = {"display": body, "heading": heading}

    if not sections:
        raise ValueError(
            f"No numbered sections found in {fname} — "
            "verify document format before indexing."
        )
    sections["_raw"] = {"display": raw_text, "heading": ""}
    return sections


def _compute_idf(index: dict) -> dict:
    """Compute IDF over all non-metadata sections across all documents."""
    word_section_count: dict = {}
    total = 0
    for fname, sections in index.items():
        for sid, content in sections.items():
            if sid.startswith("_"):
                continue
            total += 1
            words = set(_tokenize(content["display"] + " " + content["heading"]))
            for w in words:
                word_section_count[w] = word_section_count.get(w, 0) + 1
    idf = {}
    for w, df in word_section_count.items():
        idf[w] = log(max(total, 1) / (1 + df)) + 1.0
    return idf


def retrieve_documents(file_paths: list) -> dict:
    fnames = {os.path.basename(p) for p in file_paths}
    missing = set(POLICY_FILES) - fnames
    if missing:
        raise ValueError(f"Missing required policy files: {sorted(missing)}")

    index = {}
    for path in file_paths:
        fname = os.path.basename(path)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Policy file not found: {path}")
        index[fname] = _parse_document(path)

    index["_idf"] = _compute_idf(index)
    return index


# ---------------------------------------------------------------------------
# Skill 2: answer_question
# ---------------------------------------------------------------------------

def _score_section(keywords: list, section: dict, idf: dict) -> float:
    """
    IDF-weighted score for a section.
    Body text gets full weight; heading text gets HEADING_WEIGHT.
    Exact match: 1.0 × idf; prefix match (len≥5): 0.5 × idf.
    """
    body_words  = set(re.findall(r'\b[a-zA-Z]+\b', section["display"].lower()))
    head_words  = set(re.findall(r'\b[a-zA-Z]+\b', section["heading"].lower()))

    score = 0.0
    for kw in keywords:
        kw_idf = idf.get(kw, 1.0)
        if kw in body_words:
            score += 1.0 * kw_idf
            continue
        if kw in head_words:
            score += HEADING_WEIGHT * kw_idf
            continue
        if len(kw) >= 5:
            prefix = kw[:5]
            # Check body first
            match = next(
                (bw for bw in body_words if len(bw) >= 5 and
                 (bw.startswith(prefix) or kw.startswith(bw[:5]))), None
            )
            if match:
                score += 0.5 * max(kw_idf, idf.get(match, 1.0))
                continue
            # Check heading with reduced weight
            match_h = next(
                (bw for bw in head_words if len(bw) >= 5 and
                 (bw.startswith(prefix) or kw.startswith(bw[:5]))), None
            )
            if match_h:
                score += HEADING_WEIGHT * 0.5 * max(kw_idf, idf.get(match_h, 1.0))
    return score


def _best_section_in_doc(doc_sections: dict, keywords: list,
                         idf: dict, who_intent: bool) -> tuple:
    """
    Return (best_score, best_sid, best_display) for one document.
    For 'who' questions, applies WHO_BOOST so authorization-related sections win.
    For other questions, uses total IDF score for document-level ranking, then
    re-selects the answer section by the rarest matched keyword (highest IDF).
    """
    scored = []
    for sid, content in doc_sections.items():
        if sid.startswith("_"):
            continue
        s = _score_section(keywords, content, idf)
        if who_intent:
            body_words = set(re.findall(r'\b[a-zA-Z]+\b', content["display"].lower()))
            s += sum(WHO_BOOST for wk in WHO_ANSWER_KEYWORDS if wk in body_words)
        scored.append((s, sid, content))

    if not scored:
        return 0.0, None, None

    scored.sort(reverse=True)
    top_score, top_sid, top_content = scored[0]
    if top_score == 0.0:
        return 0.0, None, None

    # For 'who' questions the boost already picks the right section
    if who_intent:
        return top_score, top_sid, top_content["display"]

    # Rarest-keyword refinement: find the highest-IDF keyword that appears
    # in this document, and prefer the section that best matches it.
    # This ensures the section whose explicit topic matches the query action
    # wins even when a broader section accumulates higher total IDF score.
    rarest_kw  = None
    rarest_idf = 0.0
    for kw in keywords:
        kw_idf = idf.get(kw, 1.0)
        if kw_idf <= rarest_idf:
            continue
        # Check if kw (exact or prefix) appears in any section of this doc
        for sk, content in doc_sections.items():
            if sk.startswith("_"):
                continue
            bwords = set(re.findall(r'\b[a-zA-Z]+\b', content["display"].lower()))
            prefix = kw[:5] if len(kw) >= 5 else kw
            found = kw in bwords or (
                len(kw) >= 5 and
                any(len(bw) >= 5 and (bw.startswith(prefix) or kw.startswith(bw[:5]))
                    for bw in bwords)
            )
            if found:
                rarest_kw  = kw
                rarest_idf = kw_idf
                break

    # Only refine if we found a truly distinctive keyword (IDF above threshold)
    IDF_DISTINCTIVE = 3.5
    if rarest_kw and rarest_idf >= IDF_DISTINCTIVE:
        best_r = 0.0
        best_sid_r = top_sid
        best_body_r = top_content["display"]
        for _, sid, content in scored:
            s_r = _score_section([rarest_kw], content, idf)
            if s_r > best_r:
                best_r = s_r
                best_sid_r = sid
                best_body_r = content["display"]
        return top_score, best_sid_r, best_body_r

    return top_score, top_sid, top_content["display"]


def answer_question(index: dict, question: str) -> str:
    loaded = {k for k in index if not k.startswith("_")}
    missing = set(POLICY_FILES) - loaded
    if missing:
        return (
            "Document index is incomplete — retrieve_documents must be called "
            f"successfully with all three policy files. Missing: {sorted(missing)}"
        )

    if not question or not question.strip():
        return REFUSAL_TEMPLATE

    keywords = _tokenize(question)
    if not keywords:
        return REFUSAL_TEMPLATE

    idf = index.get("_idf", {})
    who_intent = question.strip().lower().startswith("who ")

    # Score best section per document
    doc_results = {}
    for fname in POLICY_FILES:
        if fname not in index:
            continue
        score, sid, body = _best_section_in_doc(index[fname], keywords, idf, who_intent)
        if score >= MIN_SCORE:
            doc_results[fname] = (score, sid, body)

    if not doc_results:
        return REFUSAL_TEMPLATE

    ranked = sorted(doc_results.items(), key=lambda x: x[1][0], reverse=True)
    top_fname, (top_score, top_sid, top_body) = ranked[0]

    if len(ranked) == 1:
        return _format_answer(top_body, top_fname, top_sid)

    _, (second_score, _, _) = ranked[1]
    ratio = top_score / second_score if second_score > 0 else float("inf")

    if ratio < AMBIGUITY_RATIO:
        return REFUSAL_TEMPLATE

    return _format_answer(top_body, top_fname, top_sid)


def _format_answer(body: str, fname: str, sid: str) -> str:
    lower = body.lower()
    for phrase in HEDGING_PHRASES:
        if phrase in lower:
            return REFUSAL_TEMPLATE
    return f"{body}\n\nSource: {fname}, section {sid}"


# ---------------------------------------------------------------------------
# Interactive CLI
# ---------------------------------------------------------------------------

def load_index(data_dir: str) -> dict:
    paths = [os.path.join(data_dir, fname) for fname in POLICY_FILES]
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        raise FileNotFoundError(
            f"Policy file(s) not found: {missing}\nSearched in: {data_dir}"
        )
    return retrieve_documents(paths)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir   = os.path.join(script_dir, "..", "data", "policy-documents")

    print("UC-X -- Ask My Documents")
    print("=" * 60)
    print(f"Loading policy documents from: {os.path.normpath(data_dir)}")

    try:
        index = load_index(data_dir)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    for fname in POLICY_FILES:
        sc = sum(1 for k in index[fname] if not k.startswith("_"))
        print(f"  {fname} ({sc} sections)")

    print()
    print("Rules: single-source answers with citation. Not covered = refusal.")
    print("Type 'quit' or 'exit' to stop.\n")

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Exiting.")
            break
        print()
        print(answer_question(index, question))
        print()


if __name__ == "__main__":
    main()
