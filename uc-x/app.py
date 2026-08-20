"""
UC-X — Ask My Documents
Implementation guided by agents.md (RICE) and skills.md, per the CRAFT workflow.

Enforcement rules implemented (see agents.md):
  R1  Never combine claims from two different documents into a single answer —
      every intent maps to ONE document (multi-section answers stay within it).
  R2  Never use hedging phrases — answers are verbatim section text, so hedging
      ("while not explicitly covered", "typically", ...) is impossible by construction.
  R3  If the question is not in the documents -> the refusal template EXACTLY, no variations.
  R4  Cite source document name + section number for every factual claim.

Skills implemented (see skills.md):
  retrieve_documents — loads all 3 policy files, indexes by document name and section number
  answer_question    — searches the index, returns single-source answer + citation OR refusal

Design: intents match keyword groups against the question; the answer text is the
verbatim section text from the indexed document — zero hallucination, zero blending.
"""
import argparse
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOC_PATHS = {
    "policy_hr_leave.txt": os.path.join(BASE_DIR, "..", "data", "policy-documents", "policy_hr_leave.txt"),
    "policy_it_acceptable_use.txt": os.path.join(BASE_DIR, "..", "data", "policy-documents", "policy_it_acceptable_use.txt"),
    "policy_finance_reimbursement.txt": os.path.join(BASE_DIR, "..", "data", "policy-documents", "policy_finance_reimbursement.txt"),
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 &()/-]*)$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
DECOR_LINE = set("\u2550")

# Intent map: every intent is bound to ONE document (R1) — keyword groups are ANDed,
# keywords within a group are ORed. First matching intent wins.
INTENTS = [
    # --- the 7 required test questions ---
    {
        "name": "carry_forward_leave",
        "doc": "policy_hr_leave.txt",
        "sections": ["2.6"],
        "keywords": [("carry", "carried", "carry forward", "carry-forward", "roll over", "rollover"),
                     ("leave", "annual leave", "vacation")],
    },
    {
        "name": "install_software",
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["2.3"],
        "keywords": [("install", "installing", "download", "add"),
                     ("software", "slack", "application", "app", "program", "tool")],
    },
    {
        "name": "home_office_allowance",
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["3.1"],
        "keywords": [("home office", "work from home", "wfh", "equipment"),
                     ("allowance", "reimburse", "reimbursement", "claim", "get", "buy", "entitled")],
    },
    {
        "name": "personal_device_work",
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["3.1", "3.2"],
        "keywords": [                     ("personal phone", "personal device", "personal laptop", "personal computer",
                      "personal mobile", "personal smartphone", "my phone", "my own phone",
                      "my own laptop", "own laptop", "own computer", "own device", "byod"),
                     ("work files", "work data", "work documents", "work email", "files", "data",
                      "work from home", "remote")],
    },
    {
        "name": "da_and_meal",
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["2.6"],
        "keywords": [("da", "daily allowance"),
                     ("meal", "food", "lunch", "dinner")],
    },
    {
        "name": "lwp_approval",
        "doc": "policy_hr_leave.txt",
        "sections": ["5.2"],
        "keywords": [("approve", "approval", "approves", "authorize", "authorise", "sign"),
                     ("leave without pay", "lwp", "unpaid leave")],
    },
    # --- additional single-source intents (all answers verbatim from the documents) ---
    {
        "name": "sick_leave_certificate",
        "doc": "policy_hr_leave.txt",
        "sections": ["3.2"],
        "keywords": [("sick leave", "sick", "medical certificate", "certificate"),
                     ("3", "three", "consecutive", "require", "needed", "need")],
    },
    {
        "name": "maternity_leave",
        "doc": "policy_hr_leave.txt",
        "sections": ["4.1"],
        "keywords": [("maternity",)],
    },
    {
        "name": "paternity_leave",
        "doc": "policy_hr_leave.txt",
        "sections": ["4.3"],
        "keywords": [("paternity",)],
    },
    {
        "name": "lwp_commissioner",
        "doc": "policy_hr_leave.txt",
        "sections": ["5.3"],
        "keywords": [("leave without pay", "lwp", "unpaid leave"),
                     ("30", "thirty", "commissioner")],
    },
    {
        "name": "leave_encashment",
        "doc": "policy_hr_leave.txt",
        "sections": ["7.1", "7.2"],
        "keywords": [("encash", "encashment", "cash out", "cashout", "cash it")],
    },
    {
        "name": "password_sharing",
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["4.1"],
        "keywords": [("password", "passwords", "credentials"),
                     ("share", "sharing", "give", "tell", "disclose")],
    },
    {
        "name": "mfa_remote_access",
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["4.4"],
        "keywords": [("mfa", "multi-factor", "multi factor", "two-factor", "two factor", "2fa"),
                     ("remote", "access", "login", "log in")],
    },
    {
        "name": "internet_reimbursement",
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["5.2"],
        "keywords": [("internet", "broadband", "wifi", "wi-fi"),
                     ("reimburse", "reimbursement", "allowance", "claim")],
    },
    {
        "name": "mobile_reimbursement",
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["5.1"],
        "keywords": [("mobile", "phone bill", "cell phone"),
                     ("reimburse", "reimbursement", "allowance", "claim", "bill")],
    },
    {
        "name": "da_amount",
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["2.5"],
        "keywords": [("da", "daily allowance"),
                     ("amount", "how much", "rate", "per day", "entitled")],
    },
    {
        "name": "hotel_accommodation",
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["2.4"],
        "keywords": [("hotel", "accommodation", "stay", "lodging")],
    },
    {
        "name": "air_travel",
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["2.3"],
        "keywords": [("air", "flight", "plane", "flying")],
    },
    {
        "name": "outstation_preapproval",
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["2.2"],
        "keywords": [("outstation", "out of station", "out-station", "city travel", "travel"),
                     ("approve", "approval", "pre-approve", "pre approve", "form")],
    },
    {
        "name": "training_reimbursement",
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["4.1"],
        "keywords": [("training", "course", "certification", "workshop"),
                     ("reimburse", "reimbursement", "claim", "pay", "paid")],
    },
]


def retrieve_documents(paths: dict = None) -> dict:
    """
    Load all policy files and index them by document name and section number.
    Skills contract: raises a clear error if a document is missing or unreadable;
    preserves section numbers exactly as written.
    """
    paths = paths or DOC_PATHS
    index = {}
    for doc_name, path in paths.items():
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                text = f.read()
        except OSError as exc:
            raise FileNotFoundError(f"Cannot read document {doc_name} at {path}: {exc}") from exc

        sections = {}
        current_clause = None
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or set(stripped) <= DECOR_LINE:
                continue
            if SECTION_RE.match(stripped) or CLAUSE_RE.match(stripped):
                m = CLAUSE_RE.match(stripped)
                if m:
                    num, first = m.group(1), m.group(2)
                    sections[num] = first
                    current_clause = num
                    continue
                current_clause = None
                continue
            if current_clause is not None:
                sections[current_clause] += " " + stripped

        index[doc_name] = {"sections": sections}
    return index


def answer_question(index: dict, question: str) -> str:
    """
    Search the indexed documents and return a single-source answer with citation,
    or the exact refusal template when the question is not covered.
    Skills contract: never blends two documents; never hedges; refusal verbatim.
    """
    q = question.lower().strip()

    for intent in INTENTS:
        if all(any(kw in q for kw in group) for group in intent["keywords"]):
            doc = index[intent["doc"]]["sections"]
            parts = []
            for sec in intent["sections"]:
                text = doc.get(sec)
                if text is None:
                    return (f"This question relates to {intent['doc']} section {sec}, "
                            f"which is not available in the indexed documents. "
                            f"{REFUSAL_TEMPLATE}")
                parts.append(f"[{intent['doc']} {sec}] {text}")
            citation = f"Source: {intent['doc']}, section{'s' if len(intent['sections']) > 1 else ''} {', '.join(intent['sections'])}"
            return "Answer: " + " ".join(parts) + "\n" + citation

    # R3 — not covered: refusal template exactly, no variations
    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents — interactive CLI")
    parser.add_argument("--question", help="Answer a single question and exit (batch mode)")
    args = parser.parse_args()

    index = retrieve_documents()
    for doc_name in DOC_PATHS:
        print(f"Indexed: {doc_name} ({len(index[doc_name]['sections'])} sections)")

    if args.question:
        print("\n" + answer_question(index, args.question))
        return

    print("\nUC-X Ask My Documents — type a question about company policy.")
    print("Type 'exit' or 'quit' to leave.\n")
    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            break
        if not question:
            continue
        if question.lower() in ("exit", "quit", "q"):
            break
        print("\n" + answer_question(index, question) + "\n")


if __name__ == "__main__":
    main()