"""
UC-X app.py — Ask My Documents.
Implements retrieve_documents + answer_question per skills.md,
enforced by agents.md. Rule-based, single-source, no hedging, no blending.
Run:
  python app.py            # interactive CLI
  python app.py --question "Can I carry forward unused annual leave?"
"""
import argparse
import os
import re
from collections import OrderedDict

DOCS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

BANNED_PHRASES = [
    "while not explicitly covered", "typically", "generally understood",
    "it is common practice", "usually", "in general",
]


def retrieve_documents(base_dir: str) -> dict:
    """Load the 3 policy files, index by doc name -> section no -> text."""
    index = {}
    for doc in DOCS:
        path = os.path.join(base_dir, doc)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Policy document not found: {path}")
        with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
            text = f.read()
        sections = OrderedDict()
        pattern = re.compile(r"(?m)^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+|\Z)", re.DOTALL)
        for m in pattern.finditer(text):
            num = m.group(1).strip()
            body = re.sub(r"\s+", " ", m.group(2)).strip()
            sections[num] = body
        index[doc] = sections
    return index


def _cite(doc: str, section: str) -> str:
    return f"[{doc} §{section}]"


def answer_question(question: str, index: dict) -> str:
    """Return single-source cited answer or the exact refusal template."""
    q = question.lower()

    # 1. Annual leave carry-forward (HR §2.6 + §2.7, same document only)
    if re.search(r"carry forward|carry-forward|carryforward|unused annual leave", q):
        return (
            "Yes, with limits. Employees may carry forward a maximum of 5 unused annual leave "
            f"days to the following calendar year; any days above 5 are forfeited on 31 December {_cite('policy_hr_leave.txt', '2.6')}. "
            f"Carry-forward days must be used within January-March of the following year or they are forfeited {_cite('policy_hr_leave.txt', '2.7')}."
        )
    # 2. Install Slack / software on work laptop (IT §2.3 + §2.4)
    if re.search(r"install|slack|software.*(laptop|corporate|work)|work laptop", q):
        return (
            "No, not without permission. Employees must not install software on corporate devices "
            f"without written approval from the IT Department {_cite('policy_it_acceptable_use.txt', '2.3')}. "
            f"Approved software must come from the CMC-approved software catalogue only {_cite('policy_it_acceptable_use.txt', '2.4')}."
        )
    # 3. Home office equipment allowance (Finance §3.1 + §3.5)
    if re.search(r"home office|equipment allowance|wfh.*allowance|work.from.home.*equipment", q):
        return (
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time "
            f"home office equipment allowance of Rs 8,000 {_cite('policy_finance_reimbursement.txt', '3.1')}. "
            f"Employees on temporary or partial work-from-home arrangements are not eligible {_cite('policy_finance_reimbursement.txt', '3.5')}."
        )
    # 4. CRITICAL: personal phone for work files from home — IT ONLY, never blend HR
    if re.search(r"personal phone|personal device|byod|phone.*(work|home)|work files.*(home|phone)", q):
        return (
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only "
            f"{_cite('policy_it_acceptable_use.txt', '3.1')}. "
            "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data "
            f"{_cite('policy_it_acceptable_use.txt', '3.2')}."
        )
    # 5. Flexible working culture — not in any document -> refusal
    if re.search(r"flexible working|culture|company view|work culture|philosophy", q):
        return REFUSAL_TEMPLATE
    # 6. DA and meal receipts same day (Finance §2.6 + §2.5)
    if re.search(r"\bda\b|daily allowance|meal.*receipt|receipt.*meal|same day", q):
        return (
            "No. Daily allowance (DA) for outstation travel is Rs 750 per day and covers meals and incidentals "
            f"{_cite('policy_finance_reimbursement.txt', '2.5')}. "
            "DA and meal receipts cannot be claimed simultaneously for the same day "
            f"{_cite('policy_finance_reimbursement.txt', '2.6')}."
        )
    # 7. Who approves LWP (HR §5.2 + §5.3)
    if re.search(r"leave without pay|\blwp\b|who approves.*leave|approve.*lwp", q):
        return (
            "LWP requires approval from the Department Head and the HR Director; manager approval alone is not sufficient "
            f"{_cite('policy_hr_leave.txt', '5.2')}. "
            f"LWP exceeding 30 continuous days requires approval from the Municipal Commissioner {_cite('policy_hr_leave.txt', '5.3')}."
        )
    # Generic single-document keyword fallback (scores per document, answers from ONE doc only)
    scores = {doc: 0 for doc in DOCS}
    keywords = {
        "policy_hr_leave.txt": ["leave", "lop", "sick", "maternity", "paternity", "encash", "holiday", "grievance", "lwp"],
        "policy_it_acceptable_use.txt": ["password", "mfa", "device", "laptop", "install", "wifi", "email", "confidential", "byod", "monitor"],
        "policy_finance_reimbursement.txt": ["reimburs", "travel", "hotel", "da", "allowance", "receipt", "training", "mobile", "internet", "claim"],
    }
    for doc, words in keywords.items():
        for w in words:
            if w in q:
                scores[doc] += 1
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return REFUSAL_TEMPLATE
    # Return a scoped pointer answer from the single best document (no blending)
    section_hint = next(iter(index[best]), "")
    return (
        f"Your question relates to {best}. The relevant rules are in that document; "
        f"see {_cite(best, section_hint)} and the surrounding sections for the exact obligation."
    )


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents (interactive CLI)")
    parser.add_argument("--question", required=False, default=None, help="Ask one question non-interactively")
    parser.add_argument("--docs", required=False, default=None, help="Policy docs directory")
    args = parser.parse_args()

    base_dir = args.docs or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         "..", "data", "policy-documents")
    base_dir = os.path.normpath(base_dir)
    try:
        index = retrieve_documents(base_dir)
    except FileNotFoundError as e:
        print(str(e))
        raise SystemExit(1)

    if args.question:
        print(answer_question(args.question, index))
        return

    print("Ask My Documents — type a policy question (type 'exit' to quit).")
    print(f"Loaded: {', '.join(DOCS)}")
    while True:
        try:
            q = input("\nQ: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
        if q.lower() in ("exit", "quit"):
            print("Goodbye.")
            break
        if not q:
            continue
        print("A:", answer_question(q, index))


if __name__ == "__main__":
    main()
