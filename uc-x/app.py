"""
UC-X app.py — Ask My Documents (no-API, TF-IDF retrieval)
Answers from 3 CMC policy files with subsection citations, or refuses exactly.
Run: python app.py
"""

import math
import re
import sys
from collections import defaultdict
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

POLICY_FILES = {
    "policy_hr_leave.txt":            Path(__file__).parent / "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt":   Path(__file__).parent / "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": Path(__file__).parent / "../data/policy-documents/policy_finance_reimbursement.txt",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# If the runner-up from a *different* document scores >= this fraction of the
# top score, the question is cross-document ambiguous → refuse.
AMBIGUITY_RATIO = 0.5

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "i", "my", "me", "we", "our",
    "you", "your", "it", "its", "this", "that", "these", "those",
    "in", "on", "at", "by", "for", "with", "about", "to", "from", "of",
    "and", "or", "but", "not", "if", "when", "where", "what", "how", "who",
    "must", "only", "all", "any", "no", "also", "which", "than", "more",
    "after", "before", "within", "under", "each", "per", "its", "such",
}


# ── Text helpers ──────────────────────────────────────────────────────────────

def stem(word: str) -> str:
    """Minimal suffix stripping — plurals and gerunds only."""
    if len(word) > 5 and word.endswith("ing"):
        return word[:-3]
    # Strip trailing 's' unless the word ends in 'ss', 'us', 'is', 'as'
    if len(word) > 3 and word[-1] == "s" and word[-2] not in ("s", "u", "i", "a"):
        return word[:-1]
    return word


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-z]+", text.lower())
    return [stem(w) for w in words if w not in STOP_WORDS and len(w) > 2]


# ── Skill: retrieve_documents ─────────────────────────────────────────────────

def retrieve_documents() -> dict[str, str]:
    """Load all 3 policy files. Halts on any missing or unreadable file."""
    documents = {}
    for name, path in POLICY_FILES.items():
        resolved = path.resolve()
        if not resolved.exists():
            sys.exit(f"ERROR: Policy file not found: {resolved}")
        try:
            documents[name] = resolved.read_text(encoding="utf-8")
        except OSError as e:
            sys.exit(f"ERROR: Could not read {resolved}: {e}")
    return documents


# ── Parsing: document → subsections ──────────────────────────────────────────

def parse_into_subsections(documents: dict[str, str]) -> list[dict]:
    """
    Split each document into subsections (e.g. '2.6 Employees may carry forward…').
    Returns a list of dicts with keys: doc, cite, text, tokens.
    """
    all_subsections = []

    for doc_name, content in documents.items():
        # Sections are wrapped in ═══ dividers: split on them
        parts = re.split(r"═{3,}", content)
        # Odd indices = section headings, even indices = section bodies
        for i in range(1, len(parts) - 1, 2):
            heading = parts[i].strip()
            body = parts[i + 1].strip() if i + 1 < len(parts) else ""

            section_match = re.match(r"^(\d+)\.\s+(.+)$", heading)
            if not section_match:
                continue
            section_num = section_match.group(1)

            # Split body into subsections on lines starting with N.M pattern
            sub_pat = re.compile(r"(?m)^(\d+\.\d+)\s+")
            splits = sub_pat.split(body)

            if len(splits) <= 1:
                # No subsections — use full body under the section number
                all_subsections.append({
                    "doc": doc_name,
                    "cite": f"{doc_name}, section {section_num}",
                    "text": body,
                    "tokens": tokenize(body),
                })
            else:
                # splits = ["preamble", "N.M", "text", "N.M+1", "text", …]
                for j in range(1, len(splits), 2):
                    sub_num = splits[j]
                    sub_text = splits[j + 1].strip() if j + 1 < len(splits) else ""
                    if not sub_text:
                        continue
                    all_subsections.append({
                        "doc": doc_name,
                        "cite": f"{doc_name}, section {sub_num}",
                        "text": f"{sub_num} {sub_text}",
                        "tokens": tokenize(sub_text),
                    })

    return all_subsections


# ── TF-IDF index ──────────────────────────────────────────────────────────────

def build_tfidf_index(subsections: list[dict]) -> dict:
    N = len(subsections)
    df: dict[str, int] = defaultdict(int)
    for s in subsections:
        for term in set(s["tokens"]):
            df[term] += 1
    idf = {term: math.log(N / count) for term, count in df.items()}

    for s in subsections:
        tokens = s["tokens"]
        if not tokens:
            s["tfidf"] = {}
            continue
        tf: dict[str, int] = defaultdict(int)
        for t in tokens:
            tf[t] += 1
        total = len(tokens)
        s["tfidf"] = {t: (c / total) * idf.get(t, 0.0) for t, c in tf.items()}

    return {"subsections": subsections, "idf": idf}


# ── Skill: answer_question ────────────────────────────────────────────────────

def answer_question(question: str, index: dict) -> str:
    """
    Return a single-source answer with subsection citation,
    or the exact refusal template when the question is not covered
    or requires cross-document blending.
    """
    subsections = index["subsections"]
    idf = index["idf"]
    q_tokens = tokenize(question)

    if not q_tokens:
        return REFUSAL_TEMPLATE

    def score(s: dict) -> float:
        tfidf = s.get("tfidf", {})
        return sum(idf.get(t, 0.0) * tfidf.get(t, 0.0) for t in q_tokens)

    scored = sorted(((score(s), s) for s in subsections), reverse=True)

    top_score, top = scored[0]
    if top_score <= 0:
        return REFUSAL_TEMPLATE

    top_doc = top["doc"]

    # Enforce: if any other-document subsection scores >= AMBIGUITY_RATIO of
    # the top score, the question spans documents → refuse rather than blend.
    for sc, s in scored[1:]:
        if s["doc"] != top_doc and sc > 0:
            if sc / top_score >= AMBIGUITY_RATIO:
                return REFUSAL_TEMPLATE
            break  # only compare against the best rival-document result

    return f"{top['text']}\n\n(Source: {top['cite']})"


# ── Interactive CLI ───────────────────────────────────────────────────────────

def main():
    print("Loading policy documents...", flush=True)
    documents = retrieve_documents()
    print(f"Loaded: {', '.join(documents)}")

    subsections = parse_into_subsections(documents)
    index = build_tfidf_index(subsections)
    print(f"Indexed {len(subsections)} subsections across {len(documents)} documents.\n")

    print("CMC Policy Q&A — type your question, or 'quit' to exit.\n")
    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in {"quit", "exit", "q"}:
            break
        print(f"\nAnswer: {answer_question(question, index)}\n")


if __name__ == "__main__":
    main()
