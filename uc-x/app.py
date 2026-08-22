"""
UC-X app.py — Ask My Documents.
Built from the RICE prompt in agents.md.

Retrieval-based Q&A over the three policy documents. By construction it can
never blend two documents into one answer: it always finds the single
best-matching clause and answers from that clause alone, or falls back to
the exact refusal template. This is the fix for cross-document blending and
hedged hallucination described in agents.md. Interactive CLI: run
`python app.py`, type questions, read answers; type "exit" or send EOF to quit.
"""
import argparse
import os
import re
import sys

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant department for guidance."
)

DEFAULT_DOCS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

CLAUSE_START_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_HEADER_RE = re.compile(r"^\d+\.\s+[A-Z].*$")
DIVIDER_RE = re.compile(r"^═+$")

STOPWORDS = {
    "a", "an", "the", "is", "are", "can", "i", "my", "to", "for", "of", "on",
    "in", "at", "and", "or", "do", "does", "what", "who", "when", "if", "be",
    "this", "that", "it", "with", "from", "as", "will", "must", "not", "any",
    "use", "work", "using",
}

# A small domain-vocabulary bridge — not question-specific hardcoding, just
# common synonyms for terms this policy corpus uses (device/software naming)
# so a question phrased casually ("phone", "Slack") still matches the
# formal policy wording ("personal devices", "software"). Applied only to
# the question's tokens, never to clause text, so it cannot inflate matches
# on unrelated clauses.
SYNONYMS = {
    "phone": {"device", "devices", "mobile"},
    "phones": {"device", "devices", "mobile"},
    "laptop": {"device", "devices"},
    "laptops": {"device", "devices"},
    "slack": {"software"},
    "app": {"software"},
    "apps": {"software"},
    "approves": {"approval"},
    "approve": {"approval"},
}

# Abbreviations the documents themselves define (e.g. section 5's heading
# "LEAVE WITHOUT PAY (LWP)") — expanded before tokenizing so a question
# using the full phrase still matches clauses that only use the short form,
# and vice versa. Applied to both question and clause text alike.
ABBREVIATIONS = {"lwp": "leave without pay"}

MIN_SCORE = 3  # confidence floor below which we refuse rather than guess

_SUFFIXES = ("ations", "ally", "ion", "ing", "ed", "al")


def _stem(word: str) -> str:
    """Crude suffix-stripping stemmer — just enough to unify plurals (so
    'device' and 'devices' collapse to one token, not two) and common
    noun/verb-form suffixes, without a full NLP stack."""
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith("es") and word[:-2].endswith(("s", "x", "z", "ch", "sh")):
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        word = word[:-1]
    for suffix in _SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def _expand_abbreviations(text: str) -> str:
    for abbr, expansion in ABBREVIATIONS.items():
        text = re.sub(rf"\b{abbr}\b", expansion, text, flags=re.I)
    return text


def _tokenize(text: str, expand_synonyms: bool = False):
    text = _expand_abbreviations(text)
    words = [w for w in re.findall(r"[a-z]+", text.lower()) if w not in STOPWORDS]
    tokens = {_stem(w) for w in words}
    if expand_synonyms:
        for w in words:
            for syn in SYNONYMS.get(w, ()):
                tokens.add(_stem(syn))
    return tokens


def retrieve_documents(paths=DEFAULT_DOCS):
    """
    Load all 3 policy files, indexed by (doc, clause). Raises if any file
    is missing rather than silently indexing a partial set.
    """
    index = []
    for path in paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"retrieve_documents: required policy file not found: {path}")

        doc_name = os.path.basename(path)
        current = None
        heading = ""
        with open(path, encoding="utf-8") as f:
            for raw_line in f:
                stripped = raw_line.strip()
                if not stripped or DIVIDER_RE.match(stripped):
                    continue
                if SECTION_HEADER_RE.match(stripped):
                    heading = stripped.split(".", 1)[1].strip()
                    continue
                match = CLAUSE_START_RE.match(stripped)
                if match:
                    if current:
                        index.append(current)
                    current = {"doc": doc_name, "clause": match.group(1), "heading": heading, "text": match.group(2).strip()}
                elif current:
                    current["text"] = (current["text"] + " " + stripped).strip()
            if current:
                index.append(current)
    return index


def answer_question(index, question: str):
    """
    Return the single best-matching clause as a cited answer, or the exact
    refusal template if nothing scores above MIN_SCORE. Never blends two
    documents — always answers from exactly one clause.
    """
    question = (question or "").strip()
    if not question:
        return {"answer": REFUSAL_TEMPLATE, "doc": None, "clause": None}

    q_tokens = _tokenize(question, expand_synonyms=True)
    if not q_tokens:
        return {"answer": REFUSAL_TEMPLATE, "doc": None, "clause": None}

    best = None
    best_score = 0
    for entry in index:
        c_tokens = _tokenize(entry["text"])
        # Section headings ("PERSONAL DEVICES (BYOD)" vs "CORPORATE DEVICES")
        # are a strong topical signal, so a question word that also appears
        # in the clause's heading counts extra — this is what keeps "my
        # personal phone" questions inside the Personal Devices section
        # instead of the lexically-similar-but-wrong Corporate Devices one.
        h_tokens = _tokenize(entry.get("heading", ""))
        score = len(q_tokens & c_tokens) + 2 * len(q_tokens & h_tokens)
        if score > best_score:
            best_score = score
            best = entry

    if best is None or best_score < MIN_SCORE:
        return {"answer": REFUSAL_TEMPLATE, "doc": None, "clause": None}

    citation = f"({best['doc']}, section {best['clause']})"
    return {
        "answer": f"{best['text']} {citation}",
        "doc": best["doc"],
        "clause": best["clause"],
    }


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--docs", nargs=3, default=DEFAULT_DOCS,
                         help="Paths to the 3 policy files (HR, IT, Finance)")
    args = parser.parse_args()

    index = retrieve_documents(args.docs)
    print(f"Loaded {len(index)} clauses from {len(args.docs)} documents. Ask a question (or 'exit' to quit).")

    for line in sys.stdin:
        question = line.strip()
        if not question:
            continue
        if question.lower() in ("exit", "quit"):
            break
        result = answer_question(index, question)
        print(result["answer"])


if __name__ == "__main__":
    main()
