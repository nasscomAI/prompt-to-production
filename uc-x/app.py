"""
UC-X — Ask My Documents

BASELINE RUN. This is the naive prompt turned into code:
"Answer questions about company policy."

It indexes all three policy documents together, retrieves whatever clauses look
relevant regardless of which document they came from, stitches them into one
answer, and softens the edges when the match is weak. It never refuses.

Committed as-is so the failure is on the record before it is fixed.

Usage:
    python app.py                 # interactive
    python app.py --ask "..."     # single question
"""

import argparse
import os
import re
import sys


DOCUMENTS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]
DEFAULT_DOC_DIR = os.path.join("..", "data", "policy-documents")

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(\S.*)$")
SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 \-&/(),']+)$")
SEPARATOR_RE = re.compile(r"^[═─\-=_\s]+$")

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "can", "could",
    "do", "does", "did", "i", "my", "me", "we", "our", "you", "your", "to", "of",
    "for", "on", "in", "at", "by", "with", "and", "or", "if", "it", "this",
    "that", "what", "who", "when", "where", "how", "any", "some", "from", "as",
    "will", "would", "should", "may", "might", "have", "has", "had", "am",
}


def tokenize(text):
    return [w for w in re.findall(r"[a-z0-9\-]+", text.lower()) if w not in STOPWORDS]


def retrieve_documents(doc_dir=DEFAULT_DOC_DIR):
    """Load all three policies into one flat list of clauses."""
    index = []
    for name in DOCUMENTS:
        path = os.path.join(doc_dir, name)
        if not os.path.isfile(path):
            raise IOError("Missing policy document: {}".format(path))
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.read().splitlines()

        section = ("0", "PREAMBLE")
        clause = None
        for line in lines:
            stripped = line.strip()
            if not stripped or SEPARATOR_RE.match(stripped):
                continue
            sec = SECTION_RE.match(stripped)
            if sec:
                section = (sec.group(1), sec.group(2).strip())
                clause = None
                continue
            cla = CLAUSE_RE.match(stripped)
            if cla:
                clause = {
                    "document": name,
                    "section": section[0],
                    "section_title": section[1],
                    "id": cla.group(1),
                    "text": cla.group(2).strip(),
                }
                index.append(clause)
                continue
            if clause is not None:
                clause["text"] = (clause["text"] + " " + stripped).strip()

    for clause in index:
        clause["text"] = re.sub(r"\s+", " ", clause["text"]).strip()
        clause["terms"] = set(tokenize(clause["text"]))
    return index


def answer_question(index, question, top_n=3):
    """Take the best-matching clauses from anywhere in the corpus and stitch them together."""
    terms = set(tokenize(question))
    scored = []
    for clause in index:
        overlap = len(terms & clause["terms"])
        if overlap:
            scored.append((overlap, clause))
    scored.sort(key=lambda pair: -pair[0])

    if not scored:
        return "I could not find anything specific, but generally speaking, policy would apply."

    best = [clause for _, clause in scored[:top_n]]
    body = " ".join(clause["text"] for clause in best)
    strong = scored[0][0] >= 2
    prefix = "" if strong else "While not explicitly covered, it is generally understood that "
    return prefix + body


def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Q&A (baseline)")
    parser.add_argument("--docs", default=DEFAULT_DOC_DIR)
    parser.add_argument("--ask", help="Ask one question and exit")
    args = parser.parse_args()

    index = retrieve_documents(args.docs)

    if args.ask:
        print(answer_question(index, args.ask))
        return 0

    print("Ask my documents. Blank line or Ctrl-D to quit.")
    while True:
        try:
            question = input("\n> ").strip()
        except EOFError:
            break
        if not question:
            break
        print(answer_question(index, question))
    return 0


if __name__ == "__main__":
    sys.exit(main())
