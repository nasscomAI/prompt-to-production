"""
UC-X — Ask My Documents
Built with the RICE + agents.md + skills.md + CRAFT workflow.

Enforcement implemented here (mirrors agents.md):
- answers quote clauses from exactly ONE document (never blends two)
- every claim cited as [document §section]
- no generated commentary, so no hedging phrases can appear
- questions not covered -> refusal template verbatim
- match threshold: a section must hit 2+ distinct meaningful question terms
"""
import os
import re
import sys

DOC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "data", "policy-documents")
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

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")

STOPWORDS = {
    "a", "an", "the", "i", "my", "me", "we", "our", "you", "your", "is", "are",
    "was", "be", "been", "can", "could", "may", "do", "does", "did", "will",
    "would", "should", "what", "who", "when", "where", "which", "how", "why",
    "to", "of", "on", "in", "at", "for", "and", "or", "if", "it", "its",
    "this", "that", "with", "from", "into", "about", "there", "use", "used",
    "using", "get", "have", "has", "am", "same", "any", "all",
}

# Question-term synonyms mapped to document vocabulary. One-way: adds document
# terms to the query, never rewrites the documents.
SYNONYMS = {
    "phone": ["device"],
    "phones": ["device"],
    "laptop": ["device"],
    "slack": ["software", "install"],
    "app": ["software"],
    "application": ["software"],
    "files": ["data"],
    "wfh": ["work-from-home"],
    "salary": ["pay"],
    "approves": ["approval"],
    "approve": ["approval"],
    "cert": ["certificate"],
}

# Phrases that map to a document keyword when present in the question
PHRASE_SYNONYMS = {
    "leave without pay": "lwp",
    "working from home": "work-from-home",
    "work from home": "work-from-home",
}


def retrieve_documents():
    """Load all 3 policy files, index clauses by (document, section)."""
    index = []
    for name in DOC_FILES:
        path = os.path.join(DOC_DIR, name)
        try:
            with open(path, encoding="utf-8") as f:
                lines = f.read().splitlines()
        except OSError as exc:
            sys.exit("Cannot read required document %s: %s" % (path, exc))

        current_no, current_text = None, []
        count_before = len(index)
        for line in lines:
            stripped = line.strip()
            m = CLAUSE_RE.match(stripped)
            if m:
                if current_no:
                    index.append((name, current_no, " ".join(current_text)))
                current_no, current_text = m.group(1), [m.group(2).strip()]
            elif current_no:
                if stripped and not stripped.startswith("═") and not stripped.isupper():
                    current_text.append(stripped)
                elif not stripped or stripped.startswith("═"):
                    index.append((name, current_no, " ".join(current_text)))
                    current_no, current_text = None, []
        if current_no:
            index.append((name, current_no, " ".join(current_text)))
        if len(index) == count_before:
            sys.exit("No numbered clauses found in %s — wrong file format." % path)
    return index


def _query_terms(question: str):
    low = question.lower()
    terms = set()
    for phrase, keyword in PHRASE_SYNONYMS.items():
        if phrase in low:
            terms.add(keyword)
    for word in re.findall(r"[a-z][a-z-]+|da", low):
        if word in STOPWORDS or len(word) < 2:
            continue
        terms.add(word)
        for syn in SYNONYMS.get(word, []):
            terms.add(syn)
    return terms


def _match_score(terms, clause_text: str) -> int:
    """Number of distinct question terms found in the clause.

    Word-boundary match so 'work' does not match inside 'networks';
    prefix allowed so 'laptop' still matches 'laptops'.
    """
    low = clause_text.lower()
    return sum(1 for t in terms if re.search(r"\b" + re.escape(t), low))


def answer_question(index, question: str) -> str:
    terms = _query_terms(question)
    if not terms:
        return REFUSAL_TEMPLATE

    scored = [(doc, sec, text, _match_score(terms, text)) for doc, sec, text in index]
    # Threshold: 2+ distinct meaningful terms (agents.md enforcement rule 5)
    hits = [h for h in scored if h[3] >= 2]
    if not hits:
        return REFUSAL_TEMPLATE

    # Single-source rule: pick the ONE document with the strongest match
    best_by_doc = {}
    for doc, sec, text, score in hits:
        best_by_doc[doc] = max(best_by_doc.get(doc, 0), score)
    top_score = max(best_by_doc.values())
    top_docs = [d for d, s in best_by_doc.items() if s == top_score]

    if len(top_docs) > 1:
        # Two documents match equally — name them, never blend them
        return ("This question matches more than one document equally (%s). "
                "These policies cannot be combined into a single answer. "
                "Please ask about one policy area at a time."
                % ", ".join(sorted(top_docs)))

    source_doc = top_docs[0]
    doc_hits = [h for h in hits if h[0] == source_doc]
    best_sec = min((h for h in doc_hits if h[3] == top_score), key=lambda h: h[1])[1]
    best_group = best_sec.split(".")[0]
    # Tie-break: stay in the same policy section group as the strongest hit,
    # so a BYOD question quotes Section 3.x, not a stray corporate-device clause
    doc_hits = sorted(
        doc_hits,
        key=lambda h: (-h[3], 0 if h[1].split(".")[0] == best_group else 1, h[1]),
    )[:2]

    lines = ["Answer (single source: %s):" % source_doc]
    for doc, sec, text, _score in doc_hits:
        lines.append('[%s Sec %s] "%s"' % (doc, sec, text))
    return "\n".join(lines)


def main():
    index = retrieve_documents()
    docs = sorted({doc for doc, _, _ in index})
    print("Ask My Documents - %d clauses indexed from: %s" % (len(index), ", ".join(docs)))
    print("Type a question, or 'exit' to quit.\n")

    while True:
        try:
            question = input("Q: ").strip()
        except EOFError:
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break
        print(answer_question(index, question))
        print()


if __name__ == "__main__":
    main()
