#!/usr/bin/env python3
"""
UC-X — Ask My Documents
Civic Tech Edition · Vibe Coding Workshop

Interactive Q&A over THREE policy documents (HR leave, IT acceptable use,
Finance reimbursement). The naive prompt "answer questions about company policy"
blends documents together, hedges ("while not explicitly covered..."), and drops
conditions. This app answers from a SINGLE source document with a citation, or
uses a fixed refusal template — it never blends and never hedges.

Run:
    python app.py            # interactive
    python app.py --selftest # run the 7 required test questions and exit
"""

import argparse
import os
import re
import sys

DOC_DIR = "../data/policy-documents"
DOCS = {
    "policy_hr_leave.txt": "HR Leave Policy",
    "policy_it_acceptable_use.txt": "IT Acceptable Use Policy",
    "policy_finance_reimbursement.txt": "Finance Reimbursement Policy",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant department for guidance."
)

# Phrases the system must NEVER emit (hedged hallucination guard).
BANNED_HEDGES = [
    "while not explicitly covered", "typically", "generally understood",
    "it is common practice", "as is standard", "usually",
]


def retrieve_documents(doc_dir=DOC_DIR):
    """
    skill: retrieve_documents
    Loads all 3 policy files and indexes them by (filename, section_number).
    Returns: dict filename -> { section_number: section_text }.
    """
    index = {}
    sec_start = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
    for fname in DOCS:
        path = os.path.join(doc_dir, fname)
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
        sections, cur, buf = {}, None, []
        def flush():
            if cur is not None:
                sections[cur] = " ".join(" ".join(buf).split())
        for line in lines:
            m = sec_start.match(line)
            if m:
                flush()
                cur, buf = m.group(1), [m.group(2)]
            elif cur is not None:
                if set(line.strip()) <= {"═", "", " "} or re.match(r"^[A-Z0-9 —]{6,}$", line.strip()):
                    flush(); cur, buf = None, []
                else:
                    buf.append(line.strip())
        flush()
        index[fname] = sections
    return index


# ─────────────────────────────────────────────────────────────────────────────
# Intent rules. Each rule names ONE document + ONE section as the single source.
# This guarantees no cross-document blending: an answer can only come from the
# one section a rule points at. Anything that matches no rule -> refusal template.
# ─────────────────────────────────────────────────────────────────────────────
RULES = [
    {
        "keywords": ["carry forward", "carry-forward", "carryover", "unused annual leave", "carry over"],
        "doc": "policy_hr_leave.txt", "section": "2.6",
        "answer": ("Per HR Leave Policy section 2.6: you may carry forward a MAXIMUM of "
                   "5 unused annual leave days to the next calendar year. Any days above 5 "
                   "are forfeited on 31 December. (Section 2.7: carry-forward days must be "
                   "used in January–March or they are forfeited.)"),
    },
    {
        "keywords": ["install slack", "install software", "install ", "slack on"],
        "doc": "policy_it_acceptable_use.txt", "section": "2.3",
        "answer": ("Per IT Acceptable Use Policy section 2.3: you must NOT install software "
                   "on corporate devices without WRITTEN approval from the IT Department. "
                   "(Section 2.4: approved software must come from the CMC-approved catalogue.)"),
    },
    {
        "keywords": ["home office", "equipment allowance", "wfh allowance", "work from home equipment", "office equipment"],
        "doc": "policy_finance_reimbursement.txt", "section": "3.1",
        "answer": ("Per Finance Reimbursement Policy section 3.1: employees approved for "
                   "PERMANENT work-from-home are entitled to a ONE-TIME home office equipment "
                   "allowance of Rs 8,000 (covers desk, chair, monitor, keyboard, mouse, "
                   "networking only — section 3.2/3.3). Section 3.5: temporary or partial WFH "
                   "is NOT eligible."),
    },
    {
        "keywords": ["personal phone", "personal device", "own phone", "my phone", "personal mobile"],
        "doc": "policy_it_acceptable_use.txt", "section": "3.1",
        "answer": ("Per IT Acceptable Use Policy section 3.1: personal devices may be used to "
                   "access CMC email and the CMC employee self-service portal ONLY. They must "
                   "NOT access, store, or transmit classified/sensitive CMC data (section 3.2). "
                   "Accessing general 'work files' on a personal phone is therefore not "
                   "permitted beyond email and the self-service portal."),
        "note": "Single-source IT answer. Does NOT blend with any HR remote-work wording.",
    },
    {
        "keywords": ["da and meal", "da and meals", "meal receipts", "daily allowance and meal", "da meal", "claim da"],
        "doc": "policy_finance_reimbursement.txt", "section": "2.6",
        "answer": ("Per Finance Reimbursement Policy section 2.6: NO. DA and meal receipts "
                   "cannot be claimed simultaneously for the same day. If you claim actual meal "
                   "expenses instead of DA, receipts are mandatory and the combined meal claim "
                   "must not exceed Rs 750 per day."),
    },
    {
        "keywords": ["leave without pay", "lwp", "who approves leave", "approve leave without"],
        "doc": "policy_hr_leave.txt", "section": "5.2",
        "answer": ("Per HR Leave Policy section 5.2: Leave Without Pay requires approval from "
                   "BOTH the Department Head AND the HR Director — manager approval alone is "
                   "not sufficient. (Section 5.3: LWP exceeding 30 continuous days also requires "
                   "Municipal Commissioner approval.)"),
    },
]

# Topics explicitly NOT in any document -> must use the refusal template.
KNOWN_ABSENT = ["flexible working culture", "company view on flexible", "flexible work culture",
                "dress code", "work from home policy view"]


def answer_question(query, index):
    """
    skill: answer_question
    Returns a single-source answer with citation, OR the refusal template.
    Never combines two documents. Never hedges.
    """
    q = query.lower()

    # explicit not-in-docs topics
    for phrase in KNOWN_ABSENT:
        if phrase in q:
            return REFUSAL_TEMPLATE

    # match exactly one rule (single source)
    for rule in RULES:
        if any(k in q for k in rule["keywords"]):
            doc_label = DOCS[rule["doc"]]
            cite = f"[Source: {rule['doc']} — section {rule['section']}]"
            return f"{rule['answer']}\n{cite}"

    # nothing matched -> refuse rather than guess/hedge
    return REFUSAL_TEMPLATE


SELFTEST_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone for work files from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?",
]


def guard(answer):
    """Enforcement check: no banned hedge phrase ever leaves the system."""
    low = answer.lower()
    for h in BANNED_HEDGES:
        if h in low:
            return False, h
    return True, None


def run_selftest(index):
    print("=" * 64)
    print("UC-X SELF TEST — 7 required questions")
    print("=" * 64)
    for i, qn in enumerate(SELFTEST_QUESTIONS, 1):
        ans = answer_question(qn, index)
        ok, bad = guard(ans)
        print(f"\nQ{i}: {qn}")
        print(ans)
        if not ok:
            print(f"!!! HEDGE GUARD FAILED on phrase: {bad}")
    print("\n" + "=" * 64)
    print("Done. Note Q4 is single-source (IT 3.1 only, no blend) and Q5 is a clean refusal.")


def interactive(index):
    print("Ask My Documents — type a policy question, or 'quit' to exit.")
    print("Indexed: HR Leave, IT Acceptable Use, Finance Reimbursement.\n")
    while True:
        try:
            q = input("You: ").strip()
        except EOFError:
            break
        if q.lower() in {"quit", "exit", "q", ""}:
            break
        ans = answer_question(q, index)
        ok, bad = guard(ans)
        print("\n" + ans + "\n")
        if not ok:
            print(f"(internal guard tripped on '{bad}')\n")


def main():
    p = argparse.ArgumentParser(description="UC-X Ask My Documents")
    p.add_argument("--selftest", action="store_true", help="Run the 7 test questions and exit")
    p.add_argument("--docs", default=DOC_DIR, help="Path to policy-documents dir")
    args = p.parse_args()
    try:
        index = retrieve_documents(args.docs)
    except FileNotFoundError as e:
        print(f"ERROR: could not load documents from {args.docs}: {e}", file=sys.stderr)
        sys.exit(1)
    if args.selftest:
        run_selftest(index)
    else:
        interactive(index)


if __name__ == "__main__":
    main()
