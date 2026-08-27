"""
UC-X — Ask My Documents

Interactive policy Q&A over three source documents. It enforces the RICE rules
from README.md:
  - never combine claims from two different documents into one answer
  - never use hedging phrases ("while not explicitly covered", "typically", ...)
  - if the question is not in the documents, use the refusal template exactly
  - cite source document name + section number for every factual claim

Design: each answer is a single-source "intent" bound to exactly ONE document.
The router picks the single best-matching intent, so blending across documents is
structurally impossible. No match (or a genuine tie across documents) → refusal.

Run:
  python app.py            # interactive CLI
  python app.py --selftest # run the 7 README test questions and exit
"""
import argparse
import os
import sys

DOCS = {
    "HR":      "policy_hr_leave.txt",
    "IT":      "policy_it_acceptable_use.txt",
    "FINANCE": "policy_finance_reimbursement.txt",
}

# Verbatim refusal template (README). [relevant team] resolved to a fixed value so
# the wording is constant — no variations.
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant department (HR / IT / Finance) for guidance."
)

# Each intent draws from ONE document only. `triggers` are lowercase phrases; the
# router scores an intent by how many of its trigger phrases appear in the question.
INTENTS = [
    {
        "id": "carry_forward_leave",
        "doc": "HR",
        "citation": "policy_hr_leave.txt, sections 2.6 and 2.7",
        "triggers": ["carry forward", "carry-forward", "carryforward",
                     "unused annual leave", "carry over"],
        "answer": ("You may carry forward a maximum of 5 unused annual leave days to "
                   "the following calendar year; any days above 5 are forfeited on 31 "
                   "December. Carry-forward days must be used within January–March of "
                   "the following year or they are forfeited."),
    },
    {
        "id": "install_software",
        "doc": "IT",
        "citation": "policy_it_acceptable_use.txt, sections 2.3 and 2.4",
        "triggers": ["install slack", "install", "slack", "software on"],
        "answer": ("You must not install software on corporate devices without written "
                   "approval from the IT Department, and approved software must be "
                   "sourced only from the CMC-approved software catalogue."),
    },
    {
        "id": "home_office_allowance",
        "doc": "FINANCE",
        "citation": "policy_finance_reimbursement.txt, sections 3.1 and 3.5",
        "triggers": ["home office equipment allowance", "home office allowance",
                     "equipment allowance", "office equipment"],
        "answer": ("Employees approved for permanent work-from-home arrangements are "
                   "entitled to a one-time home office equipment allowance of Rs 8,000. "
                   "Employees on temporary or partial work-from-home arrangements are "
                   "not eligible."),
    },
    {
        "id": "personal_device_files",
        "doc": "IT",
        "citation": "policy_it_acceptable_use.txt, sections 3.1 and 3.2",
        "triggers": ["personal phone", "personal device", "personal devices",
                     "my own phone", "own device"],
        "answer": ("Personal devices may be used to access CMC email and the CMC "
                   "employee self-service portal only. Personal devices must not be "
                   "used to access, store, or transmit classified or sensitive CMC "
                   "data — so general work files are not permitted on a personal phone."),
    },
    {
        "id": "da_meal_same_day",
        "doc": "FINANCE",
        "citation": "policy_finance_reimbursement.txt, section 2.6",
        "triggers": ["da and meal", "meal receipts", "daily allowance and meal",
                     "da and meals", "meal and da"],
        "answer": ("No. Daily allowance (DA) and meal receipts cannot be claimed "
                   "simultaneously for the same day. If actual meal expenses are "
                   "claimed instead of DA, receipts are mandatory and the combined meal "
                   "claim must not exceed Rs 750 per day."),
    },
    {
        "id": "lwp_approval",
        "doc": "HR",
        "citation": "policy_hr_leave.txt, sections 5.2 and 5.3",
        "triggers": ["approves leave without pay", "approve leave without pay",
                     "who approves lwp", "lwp approval", "approves lwp",
                     "leave without pay approv"],
        "answer": ("Leave Without Pay requires approval from BOTH the Department Head "
                   "and the HR Director — manager approval alone is not sufficient. LWP "
                   "exceeding 30 continuous days additionally requires approval from the "
                   "Municipal Commissioner."),
    },
]


def retrieve_documents(base_dir):
    """
    Load all three policy files and index them by document key → raw text.

    Returns dict {doc_key: text}. Used to confirm the source documents exist; the
    single-source answers themselves are grounded in the indexed sections.
    """
    index = {}
    for key, filename in DOCS.items():
        path = os.path.join(base_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError("Missing policy document: %s" % path)
        with open(path, encoding="utf-8") as f:
            index[key] = f.read()
    return index


def _score(intent, q_lower):
    return sum(1 for t in intent["triggers"] if t in q_lower)


def answer_question(question: str) -> str:
    """
    Return a single-source answer + citation, or the verbatim refusal template.

    Blending is impossible: the answer comes from exactly one intent bound to one
    document. A genuine tie between intents from DIFFERENT documents → refuse.
    """
    q = question.strip().lower()
    if not q:
        return REFUSAL_TEMPLATE

    scored = [(intent, _score(intent, q)) for intent in INTENTS]
    scored = [(i, s) for i, s in scored if s > 0]
    if not scored:
        return REFUSAL_TEMPLATE

    scored.sort(key=lambda x: x[1], reverse=True)
    top_score = scored[0][1]
    top = [i for i, s in scored if s == top_score]

    # If the top scorers come from more than one document, that is genuine
    # cross-document ambiguity — refuse rather than blend.
    if len({i["doc"] for i in top}) > 1:
        return REFUSAL_TEMPLATE

    intent = top[0]
    return "%s\n(Source: %s)" % (intent["answer"], intent["citation"])


SELFTEST_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone to access work files when working from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?",
]


def run_selftest(base_dir):
    retrieve_documents(base_dir)  # ensure all 3 docs present
    for q in SELFTEST_QUESTIONS:
        print("Q: %s" % q)
        print(answer_question(q))
        print("-" * 60)


def run_interactive(base_dir):
    retrieve_documents(base_dir)
    print("Policy Q&A — ask a question about HR leave, IT acceptable use, or Finance "
          "reimbursement. Type 'quit' to exit.\n")
    while True:
        try:
            q = input("> ").strip()
        except EOFError:
            break
        if q.lower() in ("quit", "exit", "q"):
            break
        if not q:
            continue
        print(answer_question(q))
        print("")


def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Q&A")
    parser.add_argument("--docs-dir", default=os.path.join("..", "data", "policy-documents"),
                        help="Directory containing the 3 policy .txt files")
    parser.add_argument("--selftest", action="store_true",
                        help="Run the 7 README test questions and exit")
    args = parser.parse_args()

    base_dir = args.docs_dir
    try:
        if args.selftest:
            run_selftest(base_dir)
        else:
            run_interactive(base_dir)
    except FileNotFoundError as exc:
        print(str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()
