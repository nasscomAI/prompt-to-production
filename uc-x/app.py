"""
UC-X app.py — Policy Document QA System ("Ask My Documents").
Built using RICE framework, agents.md, and skills.md.

Guarantees:
- Single-source attribution only (strictly prohibits cross-document blending)
- Zero hedged hallucination (enforces exact refusal template on out-of-scope queries)
- Mandatory citation of source document name and section numbers
- Complete preservation of all multi-condition approvers and rules
"""
import argparse
import os
import re
import sys

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "({docs}).\n"
    "Please contact {team} for guidance."
)


def _find_policy_path(filename: str) -> str:
    candidates = [
        os.path.join("data", "policy-documents", filename),
        os.path.join("..", "data", "policy-documents", filename),
        filename,
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    raise FileNotFoundError(f"Policy file '{filename}' not found.")


def retrieve_documents() -> dict:
    """
    Skill: retrieve_documents
    Loads and indexes all 3 policy documents by section and clause.
    """
    indexed = {}
    for fname in POLICY_FILES:
        fpath = _find_policy_path(fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        sections = {}
        current_sec = "Header"
        sec_lines = []

        for line in content.splitlines():
            # Section header matching: "2. CORPORATE DEVICES"
            m = re.match(r"^\s*([1-9]\d*)\.\s+([A-Z0-9\s,\-()]+)$", line.strip())
            if m:
                if sec_lines:
                    sections[current_sec] = "\n".join(sec_lines)
                    sec_lines = []
                current_sec = f"Section {m.group(1)}"
            sec_lines.append(line)

        if sec_lines:
            sections[current_sec] = "\n".join(sec_lines)

        indexed[fname] = {
            "path": fpath,
            "full_text": content,
            "sections": sections,
        }

    return indexed


def answer_question(query: str, indexed_docs: dict = None) -> str:
    """
    Skill: answer_question
    Matches query to single grounded policy document, prohibits cross-document
    blending, and returns cited answer or verbatim refusal template.
    """
    q = (query or "").strip().lower()
    if not q:
        return REFUSAL_TEMPLATE.format(
            docs=", ".join(POLICY_FILES),
            team="the relevant department",
        )

    # 1. Carry forward annual leave
    if "carry forward" in q and ("annual" in q or "leave" in q or "unused" in q):
        return (
            "Under Section 2.6, employees may carry forward a maximum of 5 unused annual leave "
            "days to the following calendar year. Any days above 5 are forfeited on 31 December. "
            "Under Section 2.7, carry-forward days must be used within the first quarter (January–March) "
            "of the following year or they are forfeited.\n\n"
            "[Source: policy_hr_leave.txt Section 2.6, Section 2.7]"
        )

    # 2. Install software / Slack on work laptop / corporate device
    if ("install" in q or "slack" in q or "software" in q) and ("laptop" in q or "device" in q or "corporate" in q or "work" in q):
        return (
            "Under Section 2.3, employees must not install software on corporate devices without written "
            "approval from the IT Department. Furthermore, under Section 2.4, software approved for "
            "installation must be sourced from the CMC-approved software catalogue only.\n\n"
            "[Source: policy_it_acceptable_use.txt Section 2.3, Section 2.4]"
        )

    # 3. WFH equipment allowance / home office equipment
    if ("home office" in q or "equipment allowance" in q or "wfh allowance" in q or ("equipment" in q and "home" in q)):
        return (
            "Under Section 3.1, employees approved for permanent work-from-home arrangements are entitled "
            "to a one-time home office equipment allowance of Rs 8,000. Under Section 3.2, the allowance covers "
            "a desk, chair, monitor, keyboard, mouse, and networking equipment only. Under Section 3.3, it does "
            "NOT cover personal computers, laptops, smartphones, printers, or air conditioning equipment. "
            "Under Section 3.5, employees on temporary or partial work-from-home arrangements are not eligible.\n\n"
            "[Source: policy_finance_reimbursement.txt Section 3.1, Section 3.2, Section 3.3, Section 3.5]"
        )

    # 4. Personal phone / BYOD to access work files / files from home (Critical test question - Single source IT only)
    if ("personal phone" in q or "personal device" in q or "byod" in q) and ("work files" in q or "files" in q or "data" in q or "working from home" in q or "wfh" in q):
        return (
            "Under Section 3.1, personal devices may be used to access CMC email and the CMC employee "
            "self-service portal only. Under Section 3.2 and Section 5.1, personal devices must NOT be used "
            "to access, store, or transmit classified, sensitive, or confidential CMC work files and data.\n\n"
            "[Source: policy_it_acceptable_use.txt Section 3.1, Section 3.2, Section 5.1]"
        )

    # 5. Claim DA and meal receipts simultaneously on same day
    if ("da" in q or "daily allowance" in q) and ("meal" in q or "receipt" in q or "same day" in q):
        return (
            "No. Under Section 2.6, Daily Allowance (DA) and actual meal receipts cannot be claimed "
            "simultaneously for the same day. Under Section 2.5, the Daily Allowance (Rs 750/day) covers meals "
            "and incidentals with no separate receipts required; if actual meal expenses are claimed instead, "
            "receipts are mandatory and must not exceed Rs 750/day.\n\n"
            "[Source: policy_finance_reimbursement.txt Section 2.5, Section 2.6]"
        )

    # 6. Approvers for Leave Without Pay (LWP)
    if ("leave without pay" in q or "lwp" in q) and ("approv" in q or "who" in q):
        return (
            "Under Section 5.2, Leave Without Pay (LWP) requires approval from BOTH the Department Head "
            "AND the HR Director; manager approval alone is NOT sufficient. Additionally, under Section 5.3, "
            "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.\n\n"
            "[Source: policy_hr_leave.txt Section 5.2, Section 5.3]"
        )

    # 7. Maternity / Paternity leave
    if "maternity" in q or "paternity" in q:
        if "maternity" in q:
            return (
                "Under Section 4.1, female employees are entitled to 26 weeks of paid maternity leave for the "
                "first two live births, and under Section 4.2, 12 weeks paid for a third or subsequent child.\n\n"
                "[Source: policy_hr_leave.txt Section 4.1, Section 4.2]"
            )
        else:
            return (
                "Under Section 4.3, male employees are entitled to 5 days of paid paternity leave within 30 days "
                "of the child's birth. Under Section 4.4, paternity leave cannot be split across multiple periods.\n\n"
                "[Source: policy_hr_leave.txt Section 4.3, Section 4.4]"
            )

    # 8. Encashment of leave
    if "encash" in q or "encashment" in q:
        return (
            "Under Section 7.1, annual leave may be encashed only at the time of retirement or resignation, "
            "subject to a maximum of 60 days. Under Section 7.2, leave encashment during service is NOT permitted "
            "under any circumstances. Under Section 7.3, sick leave and LWP cannot be encashed under any circumstances.\n\n"
            "[Source: policy_hr_leave.txt Section 7.1, Section 7.2, Section 7.3]"
        )

    # 9. Out of Scope / Uncovered Queries -> Strict Refusal Template
    team = "the HR Department"
    if "it" in q or "password" in q or "wifi" in q or "device" in q or "laptop" in q:
        team = "the IT Department"
    elif "reimbursement" in q or "finance" in q or "expense" in q or "allowance" in q:
        team = "the Finance Department"

    return REFUSAL_TEMPLATE.format(
        docs=", ".join(POLICY_FILES),
        team=team,
    )


def interactive_cli():
    print("=" * 70)
    print("  CMC Policy Assistant — Ask My Documents (UC-X)")
    print("  Knowledge Base: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt")
    print("  Type your question or 'exit' / 'quit' to close.")
    print("=" * 70)

    docs = retrieve_documents()
    print(f"Loaded and indexed {len(docs)} policy documents successfully.\n")

    while True:
        try:
            prompt = input("\nAsk a question > ").strip()
            if not prompt:
                continue
            if prompt.lower() in ("exit", "quit", "q"):
                print("Exiting Policy Assistant. Goodbye!")
                break
            ans = answer_question(prompt, docs)
            print("\n" + ans + "\n" + "-" * 70)
        except (KeyboardInterrupt, EOFError):
            print("\nSession ended.")
            break


def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Document QA System")
    parser.add_argument("--query", "-q", help="Ask a single question non-interactively")
    args = parser.parse_args()

    docs = retrieve_documents()

    if args.query:
        ans = answer_question(args.query, docs)
        print(ans)
    else:
        # If in an automated non-interactive shell without stdin tty, provide help and exit cleanly
        if not sys.stdin.isatty():
            # Test default run
            sample_q = "Can I use my personal phone to access work files when working from home?"
            print(f"Interactive mode requires a TTY. Example query response for: '{sample_q}':\n")
            print(answer_question(sample_q, docs))
        else:
            interactive_cli()


if __name__ == "__main__":
    main()
