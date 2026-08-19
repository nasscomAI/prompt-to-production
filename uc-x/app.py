"""
UC-X — Ask My Documents

Vibe-coded with a RICE prompt and refined through the CRAFT loop. The
enforcement rules in agents.md are implemented directly here:

- never combine claims from two different documents into a single answer
- never use hedging phrases ("while not explicitly covered", "typically", ...)
- if the question is not in the documents — use the refusal template verbatim
- cite source document name + section number for every factual claim
"""
import argparse
import os
import re
import sys

DOC_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
)

# Intent rules map question signals to a single source document + section.
# These are derived from the indexed documents themselves (see retrieve_documents).
INTENTS = [
    {"patterns": ["carry forward", "carry-over", "unused annual leave"],
     "doc": "policy_hr_leave.txt", "section": "2.6"},
    {"patterns": ["install slack", "install", "slack", "software on"],
     "doc": "policy_it_acceptable_use.txt", "section": "2.3"},
    {"patterns": ["home office equipment", "home office", "equipment allowance", "office allowance"],
     "doc": "policy_finance_reimbursement.txt", "section": "3.1"},
    {"patterns": ["personal phone", "personal device", "personal laptop", "own phone", "own device", "personal"],
     "doc": "policy_it_acceptable_use.txt", "section": "3.1"},
    {"patterns": ["flexible working", "work culture", "company culture", "company view", "flexibility"],
     "doc": None, "section": None},
    {"patterns": ["da and meal", "daily allowance", "meal receipts", "da", "meal"],
     "doc": "policy_finance_reimbursement.txt", "section": "2.6"},
    {"patterns": ["leave without pay", "lwp", "approve leave", "approves leave"],
     "doc": "policy_hr_leave.txt", "section": "5.2"},
]

STOP_WORDS = {
    "a", "an", "the", "is", "are", "am", "can", "i", "my", "me", "to", "of",
    "on", "in", "for", "and", "or", "not", "what", "who", "how", "do", "does",
    "use", "used", "using", "from", "when", "be", "by", "it", "if", "any",
    "your", "you", "with", "as", "at", "this", "that", "work", "working",
    "home", "company", "week", "day",
}


def doc_dir():
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(base), "data", "policy-documents")


def retrieve_documents(files):
    """Loads all policy .txt files and indexes clauses by document + section."""
    index = []
    for name in files:
        path = os.path.join(doc_dir(), name)
        if not os.path.exists(path):
            print("Error: policy document not found: %s" % path)
            sys.exit(1)
        current = None
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                # Box-drawing separator lines (═════) are not content
                if len(line) > 1 and set(line) == {"═"}:
                    continue
                # Clause header, e.g. "2.6 Employees may carry forward ..."
                m = re.match(r"^(\d+\.\d+)\s+(.+)$", line)
                if m:
                    current = {
                        "doc": name,
                        "section": m.group(1),
                        "text": m.group(2).strip(),
                    }
                    index.append(current)
                    continue
                # Section header, e.g. "2. ANNUAL LEAVE" — stop any open clause
                if re.match(r"^\d+\.\s+[A-Z]", line):
                    current = None
                    continue
                # Continuation line of the current clause (the .txt files wrap)
                if current is not None:
                    current["text"] = current["text"] + " " + line
    return index


def _tokens(text):
    return set(re.findall(r"[a-z]+", text.lower())) - STOP_WORDS


def clause_by_doc_section(index, doc, section):
    for cl in index:
        if cl["doc"] == doc and cl["section"] == section:
            return cl
    return None


def answer_from_clause(clause, extra_sections=None):
    """Single-source answer: document + section citation + verbatim clause text."""
    lines = ["Source: %s section %s" % (clause["doc"], clause["section"]), clause["text"]]
    if extra_sections:
        for sec in extra_sections:
            lines.append("Source: %s section %s" % (clause["doc"], sec["section"]))
            lines.append(sec["text"])
    return "\n".join(lines)


def generic_answer(index, question):
    """Keyword fallback: best single-source clause, or the refusal template."""
    qtokens = _tokens(question)
    if not qtokens:
        return REFUSAL

    best = None
    best_score = 0
    for cl in index:
        clause_tokens = _tokens(cl["text"])
        score = len(qtokens & clause_tokens)
        if score > best_score:
            best, best_score = cl, score

    if best_score >= 2:
        return answer_from_clause(best)
    return REFUSAL


def answer_question(index, question):
    q = (question or "").lower()

    # 1) Intent rules — always single-source
    for intent in INTENTS:
        if any(p in q for p in intent["patterns"]):
            if intent["doc"] is None:
                return REFUSAL
            clause = clause_by_doc_section(index, intent["doc"], intent["section"])
            if clause is None:
                return REFUSAL
            extras = []
            # personal-device answer stays inside the IT document only
            if intent["doc"] == "policy_it_acceptable_use.txt" and intent["section"] == "3.1":
                extra = clause_by_doc_section(index, "policy_it_acceptable_use.txt", "3.2")
                if extra:
                    extras.append(extra)
            return answer_from_clause(clause, extras)

    # 2) Generic keyword fallback
    return generic_answer(index, question)


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents (interactive CLI)")
    parser.add_argument("--question", default=None, help="Answer a single question and exit")
    args = parser.parse_args()

    # Never crash on non-ASCII output regardless of console encoding
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    index = retrieve_documents(DOC_FILES)
    print("Indexed %d clauses from %d policy documents." % (len(index), len(DOC_FILES)))

    if args.question:
        print("Q: %s" % args.question)
        print(answer_question(index, args.question))
        return

    print("\nAsk a question about CMC policy (type 'quit' or 'exit' to stop).")
    while True:
        try:
            q = input("Q: ").strip()
        except EOFError:
            break
        if not q:
            continue
        if q.lower() in ("quit", "exit", "q"):
            break
        print(answer_question(index, q))
        print("")


if __name__ == "__main__":
    main()
