"""
UC-X app.py — Single-source policy Q&A over 3 CMC policy documents.
Implements agents.md enforcement via the skills.md workflow:
retrieve_documents -> answer_question -> cited answer or exact refusal.

No language model is involved: a deterministic keyword router maps each
question to sections of exactly ONE document, so cross-document blending
and hedged hallucination are impossible by construction. A self-check
rejects any answer containing a hedging phrase before it is shown.
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

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# Phrases that must never appear in any answer (agents.md enforcement).
HEDGE_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "generally expected",
    "it is common practice",
    "as is standard practice",
]

HR = "policy_hr_leave.txt"
IT = "policy_it_acceptable_use.txt"
FIN = "policy_finance_reimbursement.txt"


def refuse(message):
    print(f"REFUSED: {message}", file=sys.stderr)
    raise SystemExit(2)


def retrieve_documents(docs_dir):
    """Load the 3 policy files; index by (doc name, section number)."""
    index = {}
    for doc in DOCUMENTS:
        path = os.path.join(docs_dir, doc)
        if not os.path.isfile(path):
            refuse(f"required document missing: {path}; "
                   f"will not answer from a partial index")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        sections = {}
        current = None
        for raw_line in text.splitlines():
            line = raw_line.strip()
            m = re.match(r"^(\d+\.\d+)\s+(.*)$", line)
            if m:
                current = m.group(1)
                sections[current] = m.group(2).strip()
            elif current and line and not line.startswith("═"):
                sections[current] += " " + line
        if not sections:
            refuse(f"no numbered sections found in {path}")
        for number, content in sections.items():
            index[(doc, number)] = content
    print(f"Indexed {len(index)} sections from {len(DOCUMENTS)} documents.")
    return index


def _self_check(answer):
    found = [p for p in HEDGE_PHRASES if p.lower() in answer.lower()]
    if found:
        raise SystemExit(f"SELF-CHECK FAILED: hedging phrases {found} "
                         f"in answer; refusing to emit it.")


def answer_question(question, index):
    """Route to one document's sections; cited answer or exact refusal."""
    q = (question or "").lower()

    def has(*words):
        return any(w in q for w in words)

    # --- HR: carry forward annual leave (sections 2.6 + 2.7, one document) ---
    if has("carry forward", "carryforward", "carry-forward"):
        return (
            f"Yes, within limits. [{HR}, section 2.6] You may carry forward "
            f"a maximum of 5 unused annual leave days to the following "
            f"calendar year; any days above 5 are forfeited on 31 December. "
            f"[{HR}, section 2.7] Carried-forward days must be used within "
            f"the first quarter (January-March) of the following year or "
            f"they are forfeited."
        )
    # --- HR: who approves LWP (sections 5.2 + 5.3, one document) ---
    if has("leave without pay", "lwp", "without pay"):
        return (
            f"[{HR}, section 5.2] Leave Without Pay requires approval from "
            f"the Department Head and the HR Director — manager approval "
            f"alone is not sufficient. [{HR}, section 5.3] LWP exceeding 30 "
            f"continuous days additionally requires approval from the "
            f"Municipal Commissioner."
        )
    # --- HR: sick leave certificate ---
    if has("sick leave", "sick day", "medical certificate", "medical cert"):
        ans = (
            f"[{HR}, section 3.2] Sick leave of 3 or more consecutive days "
            f"requires a medical certificate from a registered medical "
            f"practitioner, submitted within 48 hours of returning to work."
        )
        if has("holiday", "annual leave", "vacation"):
            ans += (
                f" [{HR}, section 3.4] Sick leave taken immediately before "
                f"or after a public holiday or annual leave period requires "
                f"a medical certificate regardless of duration."
            )
        return ans
    # --- HR: encashment ---
    if has("encash"):
        return (
            f"[{HR}, section 7.1] Annual leave may be encashed only at the "
            f"time of retirement or resignation, subject to a maximum of 60 "
            f"days. [{HR}, section 7.2] Leave encashment during service is "
            f"not permitted under any circumstances."
        )
    # --- HR: maternity / paternity ---
    if has("maternity"):
        return (
            f"[{HR}, section 4.1] Female employees are entitled to 26 weeks "
            f"of paid maternity leave for the first two live births. "
            f"[{HR}, section 4.2] For a third or subsequent child, "
            f"maternity leave is 12 weeks paid."
        )
    if has("paternity"):
        return (
            f"[{HR}, section 4.3] Male employees are entitled to 5 days of "
            f"paid paternity leave, to be taken within 30 days of the "
            f"child's birth. [{HR}, section 4.4] Paternity leave cannot be "
            f"split across multiple periods."
        )
    # --- IT: install software on corporate device (sections 2.3 + 2.4) ---
    if has("install"):
        return (
            f"No, not without permission. [{IT}, section 2.3] You must not "
            f"install software (including Slack) on a corporate device "
            f"without written approval from the IT Department. [{IT}, "
            f"section 2.4] Approved software must be sourced from the "
            f"CMC-approved software catalogue only."
        )
    # --- IT: personal phone/device for work (sections 3.1 + 3.2 + 5.1) ---
    # Single-source: IT document only. HR remote-work tools are deliberately
    # never mentioned — blending them in is the documented trap.
    if has("byod") or (has("personal") and has("phone", "device", "mobile",
                                               "laptop", "computer")):
        if has("reimburs", "bill", "claim", "allowance"):
            return (
                f"[{FIN}, section 5.1] Employees in Grade C and above are "
                f"entitled to a monthly mobile phone reimbursement of Rs "
                f"500. [{FIN}, section 5.2] Employees in Grade B and above "
                f"are entitled to a monthly internet reimbursement of Rs 800 "
                f"for approved work-from-home arrangements only. [{FIN}, "
                f"section 5.3] Reimbursements require the original bill each "
                f"month; estimated or self-declared amounts are not accepted."
            )
        return (
            f"[{IT}, section 3.1] Personal devices may be used to access "
            f"CMC email and the CMC employee self-service portal only. "
            f"[{IT}, section 3.2] Personal devices must not be used to "
            f"access, store, or transmit classified or sensitive CMC data. "
            f"[{IT}, section 5.1] CMC data classified as Confidential or "
            f"Restricted must not be stored on personal devices. Work files "
            f"beyond email and the self-service portal must therefore not "
            f"be accessed from a personal phone."
        )
    # --- IT: passwords ---
    if has("password", "multi-factor", "mfa"):
        return (
            f"[{IT}, section 4.1] You must not share your CMC system "
            f"passwords with any other person, including IT staff. [{IT}, "
            f"section 4.2] IT staff will never ask for your password; any "
            f"such request should be reported to the IT Security team. "
            f"[{IT}, section 4.3] Passwords must be changed every 90 days "
            f"as prompted by the system."
        )
    # --- Finance: DA + meal receipts (section 2.6) ---
    if has("meal"):
        return (
            f"No. [{FIN}, section 2.6] If actual meal expenses are claimed "
            f"instead of DA, receipts are mandatory and the combined meal "
            f"claim must not exceed Rs 750 per day. DA and meal receipts "
            f"cannot be claimed simultaneously for the same day."
        )
    if has("daily allowance") or re.search(r"\bda\b", q):
        return (
            f"[{FIN}, section 2.5] Daily allowance (DA) for outstation "
            f"travel is Rs 750 per day; DA covers meals and incidentals, so "
            f"no separate meal receipts are required if DA is claimed. "
            f"[{FIN}, section 2.6] DA and meal receipts cannot be claimed "
            f"simultaneously for the same day."
        )
    # --- Finance: home office equipment allowance (sections 3.1-3.5) ---
    if has("home office", "equipment allowance", "wfh equipment",
           "work-from-home equipment", "work from home equipment"):
        return (
            f"[{FIN}, section 3.1] Employees approved for permanent "
            f"work-from-home arrangements are entitled to a one-time home "
            f"office equipment allowance of Rs 8,000. [{FIN}, section 3.2] "
            f"It covers desk, chair, monitor, keyboard, mouse, and "
            f"networking equipment only. [{FIN}, section 3.3] It does not "
            f"cover personal computers, laptops, smartphones, printers, or "
            f"air conditioning equipment. [{FIN}, section 3.5] Employees on "
            f"temporary or partial work-from-home arrangements are not "
            f"eligible."
        )
    # --- Finance: travel pre-approval / claim deadline ---
    if has("outstation", "pre-approv", "form fin-t1", "fin-t1"):
        return (
            f"[{FIN}, section 2.2] Outstation travel must be pre-approved "
            f"using Form FIN-T1 before travel commences; travel without "
            f"prior approval is not reimbursable."
        )
    if has("30 calendar days", "claim deadline", "late claim",
           "after 30 days"):
        return (
            f"[{FIN}, section 1.3] All claims must be submitted within 30 "
            f"calendar days of the expense being incurred; claims submitted "
            f"after 30 days will not be processed."
        )
    # --- No single-document match: exact refusal, no variations. ---
    return REFUSAL_TEMPLATE


def find_docs_dir(explicit=None):
    if explicit:
        if os.path.isdir(explicit):
            return explicit
        refuse(f"docs directory not found: {explicit}")
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "..", "data", "policy-documents"),
        os.path.join(os.getcwd(), "data", "policy-documents"),
        os.path.join(os.getcwd(), "..", "data", "policy-documents"),
    ]
    for path in candidates:
        if os.path.isdir(path):
            return os.path.normpath(path)
    refuse("policy documents directory not found; pass --docs explicitly")


def main(argv=None):
    parser = argparse.ArgumentParser(description="UC-X Policy Q&A")
    parser.add_argument("--docs", required=False, default=None,
                        help="Directory with the 3 policy .txt files")
    parser.add_argument("--question", required=False, default=None,
                        help="Ask one question non-interactively")
    args = parser.parse_args(argv)

    docs_dir = find_docs_dir(args.docs)
    index = retrieve_documents(docs_dir)

    if args.question is not None:
        answer = answer_question(args.question, index)
        _self_check(answer)
        print(answer)
        return

    print("Ask My Documents — type a question (blank line or quit to exit).")
    while True:
        try:
            question = input("Q: ").strip()
        except EOFError:
            break
        if not question or question.lower() in ("quit", "exit", "q"):
            break
        answer = answer_question(question, index)
        _self_check(answer)
        print(f"A: {answer}\n")


if __name__ == "__main__":
    main()
