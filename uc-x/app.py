"""
UC-X — Ask My Documents
Implements retrieve_documents and answer_question per agents.md and skills.md.
Interactive CLI: type a question, get a single-source cited answer or a refusal.

Matching uses TF*IDF scoring (smoothed IDF = log(N/df)+1) with light stemming:
 - TF breaks ties: section 5.2 cites "approval" twice so beats 5.3 (once)
 - Smoothed IDF prevents total zero for ubiquitous words like "approval"
 - Section headers (=== lines) captured by the regex are stripped before indexing
"""
import math
import os
import re
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
POLICY_FILES = [
    os.path.join(_HERE, "..", "data", "policy-documents", "policy_hr_leave.txt"),
    os.path.join(_HERE, "..", "data", "policy-documents", "policy_it_acceptable_use.txt"),
    os.path.join(_HERE, "..", "data", "policy-documents", "policy_finance_reimbursement.txt"),
]

# agents.md refusal_template — stored verbatim, used exactly (enforcement rule 3)
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

STOPWORDS = {
    "the", "and", "for", "are", "was", "were", "can", "this", "that", "with",
    "have", "has", "had", "from", "will", "not", "but", "all", "any", "may",
    "must", "shall", "its", "their", "than", "then", "been", "being", "also",
    "into", "only", "such", "each", "under", "upon", "used", "use", "per",
    "who", "what", "how", "when", "where", "which", "they", "them", "these",
    "those", "your", "our", "his", "her", "more", "most", "some", "same",
    "other", "both", "own", "out", "one", "two", "via", "without", "within",
    "about", "above", "after", "before", "between", "during", "following",
    "including", "towards", "applicable", "provided", "related", "relevant",
    # Hardware nouns: too generic — appear descriptively in 2.1 (device list),
    # not as policy concepts; causes 2.1 to outscore specific rule sections.
    "laptop", "laptops", "computer", "computers",
}

# Policy term expansions (abbreviations in document text)
EXPANSIONS = {
    "lwp": ["leave", "pay"],
    "lop": ["loss", "pay"],
    "wfh": ["work", "home"],
    "cmc": ["city", "municipal"],
    "da":  ["daily", "allowance"],
}

# Query-side synonym expansions: map user question words to document vocabulary.
# Use PLURAL forms so _stem produces the same result as the document ("devices"→"devic").
# Do NOT expand "install" — both 2.3 and 2.4 stem "installation"→"install",
# so they tie on {install} and section order (2.3 before 2.4) picks the right one.
QUERY_SYNONYMS = {
    "phone":      ["devices", "personal"],  # phone→IT personal-devices context
    "smartphone": ["devices", "personal"],
}

# Second-best document must score below this fraction of top to avoid refusal
BLEND_THRESHOLD = 0.6

# Refuse if the top section's best-matching query terms are all universal (IDF <= this).
# Prevents generic words like "work" from producing a false positive answer.
MIN_DISCRIMINATIVE_IDF = 1.2


# ---------------------------------------------------------------------------
# Text utilities
# ---------------------------------------------------------------------------

def _stem(word):
    """Light suffix stripping: approves/approval/approved all -> approv."""
    for suffix in ("ation", "ations", "ment", "ments", "ing", "tion",
                   "ions", "ion", "ies", "ers", "er", "ed", "al", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[:-len(suffix)]
    return word


def _tokenize_tf(text):
    """Return Counter of stemmed, non-stopword tokens (TF = count per term)."""
    raw = re.findall(r"\b[a-z]+\b", text.lower())
    tf = Counter()
    for w in raw:
        if len(w) < 3 or w in STOPWORDS:
            continue
        if w in EXPANSIONS:
            for ew in EXPANSIONS[w]:
                if ew not in STOPWORDS and len(ew) >= 3:
                    tf[_stem(ew)] += 1
        tf[_stem(w)] += 1
    return tf


def _tokenize_query(text):
    """Return set of stemmed query terms, with query-side synonym expansion."""
    tf = _tokenize_tf(text)
    stems = set(tf.keys())
    raw = re.findall(r"\b[a-z]+\b", text.lower())
    for w in raw:
        if w in QUERY_SYNONYMS:
            for syn in QUERY_SYNONYMS[w]:
                if len(syn) >= 3:
                    stems.add(_stem(syn))
    return stems


def _build_idf(index):
    """
    Smoothed IDF: log(N/df) + 1.
    Adding 1 prevents total zero for ubiquitous terms (e.g. "approval" in all docs)
    so TF still differentiates sections that cite the term more frequently.
    """
    n_docs = len(index)
    df: dict = {}
    for sections in index.values():
        doc_terms: set = set()
        for tf in sections.values():   # sections stores TF counters after loading
            doc_terms |= set(tf.keys())
        for term in doc_terms:
            df[term] = df.get(term, 0) + 1
    return {term: math.log(n_docs / count) + 1 for term, count in df.items()}


def _score(q_stems, sec_tf, idf):
    """TF*IDF score: sum over matching query terms of TF(term) * IDF(term)."""
    return sum(sec_tf[t] * idf.get(t, 0.0) for t in q_stems if t in sec_tf)


# ---------------------------------------------------------------------------
# skill: retrieve_documents
# ---------------------------------------------------------------------------

def retrieve_documents(file_paths):
    """
    Load all policy .txt files and index by document name -> section -> TF counter.

    Input:  list of file paths (str)
    Output: dict { filename: { section_number: (section_text, tf_counter) } }
    Error handling (skills.md):
      - FileNotFoundError if any file is missing
      - ValueError if any file is empty or has no parseable sections
      - All three must load successfully before questions are accepted
    """
    if not file_paths:
        raise ValueError("No document paths provided to retrieve_documents.")

    pattern = re.compile(
        r"^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    index = {}
    for path in file_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Policy file not found: {path}")
        with open(path, encoding="utf-8") as f:
            raw = f.read()
        if not raw.strip():
            raise ValueError(f"Policy file is empty: {path}")

        filename = os.path.basename(path)
        sections = {}
        for match in pattern.finditer(raw):
            sec_num = match.group(1).strip()
            sec_text = match.group(2)
            # Strip decorative section headers (=== lines + ALL-CAPS titles)
            # that the regex captures before the next numbered clause.
            sec_text = re.sub(r"\s*\u2550+.*", "", sec_text, flags=re.DOTALL)
            sec_text = re.sub(r"\s+", " ", sec_text).strip()
            if sec_text:
                sections[sec_num] = (sec_text, _tokenize_tf(sec_text))

        if not sections:
            raise ValueError(f"No parseable sections found in: {path}")
        index[filename] = sections
    return index


# ---------------------------------------------------------------------------
# skill: answer_question
# ---------------------------------------------------------------------------

def answer_question(question, index, idf):
    """
    Search indexed documents for a single-source answer; return citation or refusal.

    Input:  question (str), index (dict from retrieve_documents), idf (dict)
    Output: dict — answer, source_document, source_section, refused
    Enforcement (agents.md):
      - Cross-document ambiguity -> refused=True, exact refusal template
      - No cross-document blending under any circumstances
    """
    if not index:
        raise ValueError("No documents loaded. Call retrieve_documents first.")

    q_stems = _tokenize_query(question)
    if not q_stems:
        return {"answer": REFUSAL_TEMPLATE, "source_document": None,
                "source_section": None, "refused": True}

    # Per document: find best-scoring section by TF*IDF
    doc_best = {}
    for filename, sections in index.items():
        best_score = 0.0
        best_sec = None
        best_text = None
        for sec_num, (sec_text, sec_tf) in sections.items():
            s = _score(q_stems, sec_tf, idf)
            if s > best_score:   # strict >: first max wins (prefers earlier, more general clause)
                best_score, best_sec, best_text = s, sec_num, sec_text
        if best_score > 0:
            doc_best[filename] = (best_sec, best_text, best_score)

    if not doc_best:
        # agents.md enforcement rule 3: exact refusal template, no variation
        return {"answer": REFUSAL_TEMPLATE, "source_document": None,
                "source_section": None, "refused": True}

    ranked = sorted(doc_best.items(), key=lambda x: x[1][2], reverse=True)
    top_doc, (top_sec, top_text, top_score) = ranked[0]

    # agents.md enforcement rule 1: refuse if cross-document blend risk.
    # Only count a second document as a genuine rival if it also has at least
    # one discriminative match (IDF > threshold) — a second doc scoring only
    # from universal terms (e.g. "work") is not a real alternative source.
    if len(ranked) > 1:
        second_doc, (second_sec, _, second_score) = ranked[1]
        second_sec_tf = index[second_doc][second_sec][1]
        second_is_genuine = any(
            idf.get(t, 0) > MIN_DISCRIMINATIVE_IDF
            for t in q_stems if t in second_sec_tf
        )
        if second_is_genuine and second_score >= BLEND_THRESHOLD * top_score:
            return {"answer": REFUSAL_TEMPLATE, "source_document": None,
                    "source_section": None, "refused": True}

    # Require at least one matched term to be discriminative (not universal).
    # If only generic words like "work" (IDF=1, in all docs) drove the score,
    # the question isn't meaningfully answered by this document — refuse.
    top_sec_tf = index[top_doc][top_sec][1]
    has_discriminative = any(
        idf.get(t, 0) > MIN_DISCRIMINATIVE_IDF
        for t in q_stems if t in top_sec_tf
    )
    if not has_discriminative:
        return {"answer": REFUSAL_TEMPLATE, "source_document": None,
                "source_section": None, "refused": True}

    # agents.md enforcement rule 4: cite document + section on every answer
    answer = f"{top_text}\n\n[Source: {top_doc}, Section {top_sec}]"
    return {"answer": answer, "source_document": top_doc,
            "source_section": top_sec, "refused": False}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    print("UC-X — Ask My Documents")
    print("Loading policy documents...")
    index = retrieve_documents(POLICY_FILES)
    # Build IDF from the TF counters stored in the index
    idf_input = {
        fname: {k: v for k, v in {sn: tf for sn, (_, tf) in secs.items()}.items()}
        for fname, secs in index.items()
    }
    # Rebuild index-compatible structure for _build_idf
    idf_index = {fname: {sn: tf for sn, (_, tf) in secs.items()} for fname, secs in index.items()}
    idf = _build_idf(idf_index)

    total = sum(len(s) for s in index.values())
    print(f"Loaded: {', '.join(index.keys())}")
    print(f"{total} sections indexed across {len(index)} documents.")
    print("\nType your question and press Enter. Type 'quit' to exit.\n")

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
        result = answer_question(question, index, idf)
        if result["refused"]:
            print(f"\nREFUSED: {result['answer']}\n")
        else:
            print(f"\nANSWER:\n{result['answer']}\n")


if __name__ == "__main__":
    main()
