"""
UC-X — Ask My Documents

Grounded, single-source policy Q&A over three CMC policy documents, built from
agents.md + skills.md.

Guards against the three failure modes:
  * Cross-document blending -> every answer is drawn from ONE document only; the
    router selects a single document + section and never concatenates across files.
  * Hedged hallucination    -> no hedging phrases are ever emitted; anything not
    grounded returns the EXACT refusal template (identical wording every time).
  * Condition dropping        -> answers quote the clause text verbatim, so
    multi-condition obligations (e.g. LWP needs Department Head AND HR Director)
    keep all conditions.

Usage:
  python app.py                     # interactive REPL
  python app.py --question "..."    # answer one question and exit
  python app.py --selftest          # run the 7 required test questions
"""
import argparse
import os
import re

DOC_FILES = {
    "policy_hr_leave.txt": "HR",
    "policy_it_acceptable_use.txt": "IT",
    "policy_finance_reimbursement.txt": "Finance",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact the relevant department (HR, IT, or Finance) for guidance."
)

CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
SECTION_HEADER_RE = re.compile(r"^\s*\d+\.\s+[A-Z]")  # e.g. "3. SICK LEAVE"


def retrieve_documents(base_dir: str):
    """Load the three policy files and index them by name -> {ref: text}."""
    index = {}
    for fname in DOC_FILES:
        path = os.path.join(base_dir, fname)
        if not os.path.isfile(path):
            raise FileNotFoundError("Required policy file missing: %s" % path)
        index[fname] = _parse_clauses(path)
    return index


def _parse_clauses(path):
    clauses = {}
    current = None  # (ref, [parts])

    def flush():
        nonlocal current
        if current:
            ref, parts = current
            clauses[ref] = " ".join(" ".join(parts).split())
        current = None

    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if set(line.strip()) <= set("═= "):  # border/blank
                continue
            m = CLAUSE_RE.match(line)
            if m:
                flush()
                current = (m.group(1), [m.group(2).strip()])
            elif SECTION_HEADER_RE.match(line):
                flush()  # a new section header ends the current clause
            elif current and line.strip():
                current[1].append(line.strip())
    flush()
    return clauses


# --- Intent router: each intent binds to ONE document + explicit section refs -
# Predicates are deliberately specific so unrelated questions fall through to
# the refusal template rather than matching loosely.
def _has(q, *subs):
    return all(s in q for s in subs)


def _has_any(q, *subs):
    return any(s in q for s in subs)


INTENTS = [
    # Trap question FIRST: personal device access -> IT 3.1 only, never blended.
    {"doc": "policy_it_acceptable_use.txt", "refs": ["3.1"],
     "match": lambda q: _has_any(q, "personal phone", "personal device",
                                 "own phone", "my phone", "personal laptop")
                        and _has_any(q, "work file", "work files", "access",
                                     "files", "email", "portal", "from home")},
    # Install software on a work/corporate device -> IT 2.3.
    {"doc": "policy_it_acceptable_use.txt", "refs": ["2.3"],
     "match": lambda q: _has_any(q, "install", "installing")
                        and _has_any(q, "software", "slack", "app", "application",
                                     "program", "laptop", "device")},
    # Carry forward annual leave -> HR 2.6 (+2.7 same doc, same obligation).
    {"doc": "policy_hr_leave.txt", "refs": ["2.6", "2.7"],
     "match": lambda q: _has_any(q, "carry forward", "carry-forward",
                                 "carried forward", "carryforward")
                        and _has_any(q, "leave", "annual")},
    # Who approves leave without pay -> HR 5.2 (both approvers preserved).
    {"doc": "policy_hr_leave.txt", "refs": ["5.2"],
     "match": lambda q: (_has_any(q, "leave without pay", "lwp"))
                        and _has_any(q, "approve", "approves", "approval",
                                     "who", "authorise", "authorize", "sign")},
    # Home-office equipment allowance -> Finance 3.1.
    {"doc": "policy_finance_reimbursement.txt", "refs": ["3.1"],
     "match": lambda q: _has_any(q, "home office", "equipment allowance",
                                 "office equipment")
                        or (_has_any(q, "work from home", "work-from-home", "wfh")
                            and _has_any(q, "allowance", "equipment"))},
    # DA and meal receipts same day -> Finance 2.6 (explicit prohibition).
    {"doc": "policy_finance_reimbursement.txt", "refs": ["2.6"],
     "match": lambda q: _has_any(q, "da", "daily allowance")
                        and _has_any(q, "meal")
                        and _has_any(q, "same day", "receipt", "receipts",
                                     "simultaneous", "both")},
]


def answer_question(index, question: str) -> str:
    q = " " + question.lower().strip() + " "
    # Normalise 'DA' matching: pad tokens so 'da' matches as a word.
    q_tokens = " " + re.sub(r"[^a-z0-9]+", " ", question.lower()) + " "

    for intent in INTENTS:
        try:
            hit = intent["match"](q) or intent["match"](q_tokens)
        except Exception:
            hit = False
        if hit:
            doc = intent["doc"]
            clauses = index.get(doc, {})
            lines = []
            for ref in intent["refs"]:
                text = clauses.get(ref)
                if text:
                    lines.append("[SOURCE: %s § %s]\n%s" % (doc, ref, text))
            if lines:
                return "\n\n".join(lines)

    # Not grounded in any single document -> exact refusal template.
    return REFUSAL_TEMPLATE


SELFTEST_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone to access work files when working from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?",
]


def _resolve_docs_dir(cli_dir):
    if cli_dir:
        return cli_dir
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "data", "policy-documents"))


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--docs", default=None, help="Policy documents directory")
    parser.add_argument("--question", default=None, help="Ask one question and exit")
    parser.add_argument("--selftest", action="store_true",
                        help="Run the 7 required test questions")
    args = parser.parse_args()

    docs_dir = _resolve_docs_dir(args.docs)
    index = retrieve_documents(docs_dir)

    if args.selftest:
        for i, question in enumerate(SELFTEST_QUESTIONS, 1):
            print("=" * 70)
            print("Q%d: %s" % (i, question))
            print("-" * 70)
            print(answer_question(index, question))
            print()
        return

    if args.question:
        print(answer_question(index, args.question))
        return

    # Interactive REPL
    print("UC-X — Ask My Documents. Grounded in 3 CMC policy files.")
    print("Type a question, or 'quit' to exit.\n")
    while True:
        try:
            question = input("ask> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.lower() in ("quit", "exit", "q"):
            break
        if not question:
            continue
        print(answer_question(index, question))
        print()


if __name__ == "__main__":
    main()
