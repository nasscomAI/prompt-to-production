"""
UC-X — Ask My Documents
Policy Q&A agent built to satisfy the enforcement rules in agents.md
and the skill contracts in skills.md.

Enforcement rules implemented:
1. Never combine claims from two different documents into a single
   answer — every answer is built from exactly ONE clause of ONE
   document, quoted verbatim, with a citation.
2. No hedging phrases — the system either answers from a document or
   uses the refusal template. There is no middle ground.
3. If a question is not covered by the documents, the refusal template
   is emitted exactly, with no variations.
4. Every factual answer cites the source document name and section
   number.

Retrieval is deliberately conservative: a question is answered only if
at least 2 distinct content terms AND at least half of its content
terms match a single clause. Anything weaker gets the refusal template.
"""
import argparse
import math
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCUMENT_DIR = os.path.join(BASE_DIR, "..", "data", "policy-documents")
DOCUMENT_NAMES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEAM = "[relevant team]"
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(%s).\n"
    "Please contact %s for guidance."
) % (", ".join(DOCUMENT_NAMES), REFUSAL_TEAM)

HEADING_RE = re.compile(r"^\s*(\d+)\.\s+([A-Z][A-Z &()\-]+)\s*$")
CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
RULE_LINE_RE = re.compile(r"^[\s=\u2550]+$")

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "am", "do", "does", "did", "done", "can", "could", "should", "would",
    "may", "might", "must", "shall", "will", "i", "me", "my", "we", "our",
    "you", "your", "it", "its", "this", "that", "these", "those", "there",
    "here", "of", "in", "on", "at", "to", "for", "from", "with", "within",
    "without", "and", "or", "if", "then", "than", "so", "such", "as", "by",
    "about", "into", "over", "under", "up", "out", "off", "when", "while",
    "what", "which", "who", "whom", "whose", "how", "why", "where",
}

# Domain abbreviations expanded in both questions and indexed clauses.
ABBREVIATIONS = {
    "lwp": ["leave", "without", "pay"],
    "lwop": ["leave", "without", "pay"],
    "wfh": ["work", "from", "home"],
    "mfa": ["multi", "factor", "authentication"],
    "da": ["daily", "allowance"],
}

# Conservative synonym sets: a query term also matches these related
# words in a clause. Only mappings that are safe for this corpus.
SYNONYMS = {
    "slack": ["software", "application", "app"],
    "laptop": ["computer", "device"],
    "phone": ["mobile", "smartphone", "device"],
}


def _stem(word):
    """Return the set of roots for a word (original included)."""
    roots = {word}
    current = word
    for _ in range(3):
        for suffix in ("ing", "ed", "ly", "es", "s", "e"):
            if current.endswith(suffix) and len(current) - len(suffix) >= 4:
                current = current[: -len(suffix)]
                roots.add(current)
                break
        else:
            break
    return roots


def _tokenise(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in STOPWORDS]


def _query_terms(question):
    """Content terms for a question -> sorted list of root-sets."""
    terms = {}
    for word in _tokenise(question):
        expansions = ABBREVIATIONS.get(word, [])
        roots = _stem(word)
        entry = set(roots)
        for root in list(roots):
            entry.update(SYNONYMS.get(root, []))
        for exp in expansions:
            entry.update(_stem(exp))
        if word == "da":
            entry.add("da")  # keep the literal abbreviation too
        key = min(entry)    # dedupe terms that reduce to the same roots
        terms.setdefault(key, set()).update(entry)
    return [terms[k] for k in sorted(terms)]


def retrieve_documents(document_dir=None):
    """
    Load all policy files and index them by document name and section
    number. Returns a list of clause dicts:
        {doc, id, title, text, words}
    """
    document_dir = document_dir or DOCUMENT_DIR
    index = []
    missing = []
    for name in DOCUMENT_NAMES:
        path = os.path.join(document_dir, name)
        if not os.path.exists(path):
            missing.append(name)
            continue
        try:
            with open(path, "r", encoding="utf-8") as fh:
                lines = fh.read().splitlines()
        except OSError as exc:
            print("ERROR: cannot read %s: %s" % (path, exc), file=sys.stderr)
            raise SystemExit(1)

        title = ""
        for raw in lines:
            line = raw.rstrip()
            if RULE_LINE_RE.match(line):
                continue
            heading = HEADING_RE.match(line)
            clause = CLAUSE_RE.match(line)
            if heading:
                title = "%s. %s" % (heading.group(1), heading.group(2))
                continue
            if clause:
                index.append({"doc": name, "id": clause.group(1),
                              "title": title,
                              "text": clause.group(2).strip(),
                              "words": []})
                continue
            if not line.strip():
                continue
            if index and index[-1]["doc"] == name:
                index[-1]["text"] += " " + line.strip()
    # Tokenise each clause once (with abbreviation expansion).
    for entry in index:
        words = []
        for word in re.findall(r"[a-z0-9]+", entry["text"].lower()):
            words.append(word)
            words.extend(ABBREVIATIONS.get(word, []))
        entry["words"] = words

    if missing:
        print("ERROR: missing policy document(s): %s" % ", ".join(missing),
              file=sys.stderr)
        raise SystemExit(1)
    return index


def answer_question(question, index):
    """
    Search the indexed documents. Returns a single-source answer with a
    citation, or the refusal template. Never blends documents.
    Clauses are ranked by inverse-document-frequency so that specific
    query terms (e.g. "access") outweigh common ones (e.g. "use").
    """
    terms = _query_terms(question)
    if not terms:
        return REFUSAL_TEMPLATE

    # First pass: which clauses match each term, and how often.
    n_docs = len(index)
    per_term = []  # [(clause_pos -> hits), ...] per term
    for term_roots in terms:
        matches = {}
        for pos, entry in enumerate(index):
            hits = 0
            for word in entry["words"]:
                if len(word) >= 3:
                    hit = any(
                        len(root) >= 3 and (
                            word.startswith(root) or root.startswith(word))
                        for root in term_roots)
                else:
                    hit = word in term_roots  # short words: exact only
                if hit:
                    hits += 1
            if hits:
                matches[pos] = hits
        per_term.append(matches)

    scores = {}  # pos -> [idf_score, distinct, hits]
    for matches in per_term:
        df = len(matches)
        idf = math.log(n_docs / df) if df else math.log(n_docs + 1)
        for pos, hits in matches.items():
            stats = scores.setdefault(pos, [0.0, 0, 0])
            stats[0] += idf
            stats[1] += 1      # distinct terms matched
            stats[2] += hits   # total word hits

    if not scores:
        return REFUSAL_TEMPLATE

    def rank_key(item):
        pos, (idf_score, distinct, hits) = item
        entry = index[pos]
        doc_order = DOCUMENT_NAMES.index(entry["doc"])
        return (-idf_score, -distinct, -hits, doc_order, pos)

    best_pos, (idf_score, distinct, hits) = min(
        scores.items(), key=rank_key)
    coverage = distinct / float(len(terms))
    # Rule: refuse rather than answer on a weak match.
    if distinct < 2 or coverage < 0.5:
        return REFUSAL_TEMPLATE

    entry = index[best_pos]
    return (
        "%s\n"
        "[Source: %s, section %s]"
        % (entry["text"], entry["doc"], entry["id"])
    )


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--documents", dest="document_dir", default=None,
                        help="Optional path to the policy-documents folder")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
        sys.stderr.reconfigure(errors="replace")

    index = retrieve_documents(args.document_dir)
    print("UC-X — Ask My Documents")
    print("Indexed %d clause(s) from %d document(s)."
          % (len(index), len(DOCUMENT_NAMES)))
    print("Type your question (or 'quit' to exit).")
    while True:
        try:
            question = input("\nQ: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            print("No question entered. Please type a question about "
                  "company policy, or 'quit' to exit.")
            continue
        if question.lower() in ("quit", "exit", "q"):
            break
        print("A: %s" % answer_question(question, index))
    return 0


if __name__ == "__main__":
    sys.exit(main())
