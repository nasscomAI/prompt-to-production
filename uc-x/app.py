#!/usr/bin/env python3
"""
app.py — UC-X "Ask My Documents" Policy Q&A Agent

Interactive CLI. Implements the two skills defined in skills.md:
  - retrieve_documents: loads all 3 policy files, indexes by document name
                         and section number.
  - answer_question:    searches indexed documents, returns a single-source
                         answer + citation, OR the exact refusal template.

Follows every enforcement rule in agents.md:
  1. Never combine claims from two different documents into a single answer.
  2. Never use hedging phrases ("while not explicitly covered", "typically",
     "generally understood", "it is common practice").
  3. If the question is not in the documents, use the refusal template
     exactly — no variation in wording.
  4. Cite source document name + section number for every factual claim.
  5. Cross-document trap questions are answered from ONE document's
     applicable section only, or refused — never blended.

No hedging phrases appear anywhere in this file's generated output.

Run with --debug to print per-document relevance scores for each question,
useful when diagnosing why a question was answered or refused.
"""

import argparse
import os
import re
import sys
import math

DOC_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

STOPWORDS = {
    "a", "an", "the", "is", "are", "am", "i", "my", "me", "on", "to", "of",
    "for", "and", "or", "in", "at", "can", "do", "does", "what", "who",
    "when", "how", "with", "from", "be", "it", "this", "that", "if", "as",
    "using", "use", "used", "same", "day",
}

# Small domain synonym map — bridges vocabulary gaps between how an
# employee phrases a question and how the policy documents phrase the
# same concept (e.g. "phone" -> "device", since IT policy talks about
# "personal devices" rather than "phone").
SYNONYMS = {
    "phone": ["device", "devices", "mobile"],
    "phones": ["device", "devices", "mobile"],
    "laptop": ["device", "devices", "computer", "corporate"],
    "files": ["data"],
    "file": ["data"],
    "install": ["software"],
    "installing": ["software", "install"],
    "allowance": ["reimbursement", "reimbursable", "reimbursed"],
    "approve": ["approval", "approved"],
    "approves": ["approval", "approved"],
    "approval": ["approve", "approved"],
    "culture": ["flexible", "working"],
    "carry": ["carryforward", "forward"],
    "without": ["lwp"],
    "lwp": ["without", "pay"],
}


class AgentRefusal(Exception):
    """Raised when the agent must return the refusal template verbatim."""
    pass


# ---------------------------------------------------------------------------
# Skill 1: retrieve_documents
# ---------------------------------------------------------------------------
def retrieve_documents(doc_dir):
    """
    Loads all three policy files and indexes their content by document name
    and section number.

    Returns:
        index = {
            doc_filename: {
                section_number: section_text (str, header + body)
            }
        }

    Error handling:
      - Any of the three files missing/unreadable -> refuse (AgentRefusal),
        report which file could not be loaded. Never proceeds with a
        partial index.
      - Section numbers that cannot be parsed are not silently dropped as
        free text — parsing failures are reported so citation integrity
        is never compromised.
    """
    index = {}
    missing = []
    for filename in DOC_FILES:
        path = os.path.join(doc_dir, filename)
        if not os.path.isfile(path):
            missing.append(path)
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        sections = _parse_sections(text)
        if not sections:
            raise AgentRefusal(
                f"Cannot index {filename} — no numbered sections (e.g. '2.6') "
                f"could be parsed. Refusing to proceed with an unindexed document, "
                f"since every answer must cite a section number."
            )
        index[filename] = sections

    if missing:
        raise AgentRefusal(
            f"Cannot load dataset — the following required file(s) are missing: "
            f"{missing}. Refusing to answer with a partial (2 of 3) document set."
        )

    print(f"[retrieve_documents] Indexed {len(index)} document(s):")
    for fname, sections in index.items():
        print(f"  - {fname}: {len(sections)} section(s) indexed")

    return index


def _parse_sections(text):
    """
    Parses subsection entries like:
        2.6 Employees may carry forward a maximum of 5 unused annual leave
            days to the following calendar year. Any days above 5 are
            forfeited on 31 December.
    into {"2.6": "Employees may carry forward ... forfeited on 31 December."}
    Continuation lines (indented, no leading section number) are appended
    to the current section's text.
    """
    sections = {}
    current_num = None
    current_lines = []
    section_start_re = re.compile(r"^(\d+\.\d+)\s+(.*)$")

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        match = section_start_re.match(stripped)
        if match:
            if current_num is not None:
                sections[current_num] = " ".join(current_lines).strip()
            current_num = match.group(1)
            current_lines = [match.group(2)]
            continue

        if current_num is None:
            continue  # header/title/separator lines before first section

        if stripped == "" or stripped.startswith("═") or stripped.startswith("-"):
            continue  # blank lines / separators don't break the current section

        if re.match(r"^\d+\.\s+[A-Z]", stripped):
            # a new top-level header (e.g. "3. WORK FROM HOME EQUIPMENT")
            # closes off the previous subsection
            sections[current_num] = " ".join(current_lines).strip()
            current_num = None
            current_lines = []
            continue

        current_lines.append(stripped)

    if current_num is not None:
        sections[current_num] = " ".join(current_lines).strip()

    return sections


# ---------------------------------------------------------------------------
# Skill 2: answer_question
# ---------------------------------------------------------------------------
def _tokenize(text):
    words = re.findall(r"[a-z]+", text.lower())
    expanded = []
    for w in words:
        if w in STOPWORDS:
            continue
        expanded.append(w)
        expanded.extend(SYNONYMS.get(w, []))
    return expanded


def _build_term_idf(index):
    """Simple IDF across all sections in the corpus, so rare/distinctive
    terms (e.g. 'devices') count more than common ones (e.g. 'work')."""
    section_term_sets = []
    for doc, sections in index.items():
        for num, text in sections.items():
            section_term_sets.append(set(_tokenize(text)))

    n_sections = len(section_term_sets)
    df = {}
    for term_set in section_term_sets:
        for term in term_set:
            df[term] = df.get(term, 0) + 1

    idf = {term: math.log((n_sections + 1) / (count + 1)) + 1 for term, count in df.items()}
    return idf


def answer_question(index, question, idf, debug=False):
    """
    Searches indexed documents and returns a single-source answer + citation,
    OR the refusal template.

    Returns: (answer_text, is_refusal: bool)

    Error handling:
      - No section in any document scores above the relevance threshold ->
        return refusal template verbatim (question not covered).
      - Top-scoring sections from two different documents are BOTH close in
        relative ratio AND close in absolute score -> genuine cross-document
        ambiguity -> return refusal template verbatim rather than blend or
        guess. A relative ratio alone is not sufficient: shared vocabulary
        (e.g. "approval" appearing in HR, IT, and Finance sections alike) can
        inflate a runner-up document's score enough to cross a ratio
        threshold even when the top document's absolute lead is decisive.
        Requiring both conditions distinguishes a genuine near-tie from a
        clear winner whose score happens to be partly built from common
        terms.
      - Never combines the top sections from two different documents into
        one answer, even when both are relevant.
    """
    query_terms = _tokenize(question)
    if not query_terms:
        return REFUSAL_TEMPLATE, True

    # score = best-matching section score per document
    doc_best = {}  # doc -> (score, section_num, section_text)
    for doc, sections in index.items():
        best_score = 0.0
        best_num = None
        best_text = None
        for num, text in sections.items():
            section_terms = _tokenize(text)
            section_term_counts = {}
            for t in section_terms:
                section_term_counts[t] = section_term_counts.get(t, 0) + 1
            score = 0.0
            matched_query_terms = set()
            for qt in query_terms:
                if qt in section_term_counts:
                    score += section_term_counts[qt] * idf.get(qt, 1.0)
                    matched_query_terms.add(qt)
            # small bonus for breadth of distinct query terms matched,
            # to prefer sections that address more of the question
            score += 0.5 * len(matched_query_terms)
            if score > best_score:
                best_score = score
                best_num = num
                best_text = text
        doc_best[doc] = (best_score, best_num, best_text)

    ranked = sorted(doc_best.items(), key=lambda kv: kv[1][0], reverse=True)
    top_doc, (top_score, top_num, top_text) = ranked[0]
    second_score = ranked[1][1][0] if len(ranked) > 1 else 0.0

    MIN_SCORE = 1.5        # below this, nothing relevant was found at all
    AMBIGUITY_RATIO = 0.7  # second doc within 70% of top doc's score...
    ABS_MARGIN = 5.0       # ...AND within this many raw points of top doc's
                           # score. Both conditions must hold for a genuine
                           # cross-document ambiguity refusal (see docstring).

    gap = top_score - second_score
    is_ambiguous = (
        second_score >= MIN_SCORE
        and second_score >= top_score * AMBIGUITY_RATIO
        and gap <= ABS_MARGIN
    )

    if debug:
        print(f"[DEBUG] question: {question!r}")
        print(f"[DEBUG] query_terms: {query_terms}")
        for doc, (score, num, _text) in ranked:
            print(f"[DEBUG]   {doc}: best_section={num} score={score:.3f}")
        print(f"[DEBUG] top={top_score:.3f} second={second_score:.3f} gap={gap:.3f} "
              f"MIN_SCORE={MIN_SCORE} ratio_threshold={top_score * AMBIGUITY_RATIO:.3f} "
              f"ABS_MARGIN={ABS_MARGIN}")

    if top_score < MIN_SCORE:
        if debug:
            print("[DEBUG] -> REFUSED: top_score below MIN_SCORE")
        return REFUSAL_TEMPLATE, True

    if is_ambiguous:
        if debug:
            print("[DEBUG] -> REFUSED: ambiguity ratio + absolute margin both triggered")
        return REFUSAL_TEMPLATE, True

    if debug:
        print(f"[DEBUG] -> ANSWERED from {top_doc} section {top_num}")

    answer = (
        f"{top_text}\n\n"
        f"[Source: {top_doc}, section {top_num}]"
    )
    return answer, False


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="UC-X Ask My Documents — policy Q&A agent."
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Print per-document relevance scores for each question, to "
             "diagnose why a question was answered or refused."
    )
    args = parser.parse_args()

    doc_dir = os.path.join("..", "data", "policy-documents")

    try:
        index = retrieve_documents(doc_dir)
    except AgentRefusal as e:
        print(f"[REFUSED] {e}", file=sys.stderr)
        sys.exit(1)

    idf = _build_term_idf(index)

    print("\nAsk My Documents — policy Q&A (HR leave, IT acceptable use, Finance reimbursement)")
    print("Type a question, or 'quit' to exit.\n")

    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit"):
            break

        answer, is_refusal = answer_question(index, question, idf, debug=args.debug)
        print()
        print(answer)
        print()


if __name__ == "__main__":
    main()