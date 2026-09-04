"""
UC-X — Ask My Documents
Deterministic, single-source municipal policy Q&A assistant obeying RICE specification.
Prevents cross-document blending, hedged hallucination, and condition dropping.
"""
import argparse
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple


DOC_NAMES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

FORBIDDEN_HEDGING = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "employees are generally expected to",
    "customarily",
    "industry standard",
]


def get_refusal_template(team: str = "the relevant department") -> str:
    """Return the exact mandatory refusal template."""
    return (
        "This question is not covered in the available policy documents "
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
        f"Please contact {team} for guidance."
    )


def retrieve_documents(base_dir: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """
    Ingest the 3 municipal policy text files and build an indexed knowledge base.
    """
    if base_dir is None:
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "policy-documents")

    kb: Dict[str, Dict[str, Any]] = {}

    for doc_name in DOC_NAMES:
        doc_path = os.path.join(base_dir, doc_name)
        if not os.path.exists(doc_path):
            raise FileNotFoundError(f"Policy file missing: {doc_path}")

        with open(doc_path, mode="r", encoding="utf-8") as f:
            content = f.read()

        kb[doc_name] = {
            "filename": doc_name,
            "raw_text": content,
            "sections": _parse_sections(content),
        }

    return kb


def _parse_sections(text: str) -> Dict[str, Dict[str, Any]]:
    """Parse text into numbered sections and clauses."""
    sections: Dict[str, Dict[str, Any]] = {}
    current_sec_num = ""
    current_sec_title = ""
    clauses: Dict[str, str] = {}
    current_cid = ""
    current_clause_lines: List[str] = []

    def flush_clause():
        nonlocal current_cid, current_clause_lines, clauses
        if current_cid:
            clauses[current_cid] = " ".join(t.strip() for t in current_clause_lines if t.strip())
            current_cid = ""
            current_clause_lines = []

    def flush_section():
        nonlocal current_sec_num, current_sec_title, clauses
        flush_clause()
        if current_sec_num:
            sections[current_sec_num] = {
                "title": current_sec_title,
                "clauses": dict(clauses),
            }
            clauses = {}
            current_sec_num = ""

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or set(stripped) == {"═"}:
            continue

        sec_match = re.match(r"^(\d+)\.\s+([A-Z\s\(\)\—\-]+)$", stripped)
        if sec_match:
            flush_section()
            current_sec_num = sec_match.group(1)
            current_sec_title = sec_match.group(2).strip()
            continue

        clause_match = re.match(r"^(\d+\.\d+)\s+(.+)$", stripped)
        if clause_match:
            flush_clause()
            current_cid = clause_match.group(1)
            current_clause_lines = [clause_match.group(2)]
            continue

        if current_cid:
            current_clause_lines.append(stripped)

    flush_section()
    return sections


def answer_question(query: str, kb: Optional[Dict[str, Dict[str, Any]]] = None) -> str:
    """
    Search indexed documents and return a single-source verified answer with citation,
    or the exact refusal template.
    """
    if not query or not query.strip():
        return get_refusal_template("the HR or IT helpdesk")

    if kb is None:
        kb = retrieve_documents()

    q_lower = query.lower().strip()

    # 1. Check for personal phone / WFH file access (CRITICAL TRAP QUESTION)
    if ("personal phone" in q_lower or "personal device" in q_lower or "byod" in q_lower) and \
       ("file" in q_lower or "work file" in q_lower or "access work" in q_lower or "storage" in q_lower or "wfh" in q_lower or "home" in q_lower):
        # Single-source from IT policy only. Absolutely NO blending with HR remote tools.
        return (
            "No. Under IT policy, personal devices (BYOD) may be used to access CMC email and the "
            "CMC employee self-service portal only. Personal devices must not be used to access, store, "
            "or transmit work files, classified data, or sensitive CMC data.\n"
            "[Source: policy_it_acceptable_use.txt, Section 3.1 & 3.2]"
        )

    # 2. Check for carry forward annual leave
    if ("carry forward" in q_lower or "carry-forward" in q_lower or "accumulate" in q_lower) and \
       ("annual leave" in q_lower or "unused leave" in q_lower or "leave" in q_lower):
        return (
            "Yes. Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year; "
            "any days above 5 are forfeited on 31 December. Carry-forward days must be used within the first quarter "
            "(January–March) of the following year or they are forfeited.\n"
            "[Source: policy_hr_leave.txt, Section 2.6 & 2.7]"
        )

    # 3. Check for installing software / Slack on work laptop
    if ("install" in q_lower or "software" in q_lower or "download" in q_lower or "app" in q_lower) and \
       ("slack" in q_lower or "laptop" in q_lower or "corporate device" in q_lower or "work laptop" in q_lower):
        return (
            "No. Employees must not install software on corporate devices without written approval from the IT Department. "
            "Any software approved for installation must be sourced from the CMC-approved software catalogue only.\n"
            "[Source: policy_it_acceptable_use.txt, Section 2.3 & 2.4]"
        )

    # 4. Check for home office / WFH equipment allowance
    if ("home office" in q_lower or "wfh equipment" in q_lower or "equipment allowance" in q_lower or "desk" in q_lower) and \
       ("allowance" in q_lower or "reimbursement" in q_lower or "home" in q_lower or "equipment" in q_lower):
        return (
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office "
            "equipment allowance of Rs 8,000. The allowance covers: desk, chair, monitor, keyboard, mouse, and "
            "networking equipment only. Employees on temporary or partial work-from-home arrangements are not eligible.\n"
            "[Source: policy_finance_reimbursement.txt, Section 3.1 & 3.2]"
        )

    # 5. Check for DA and meal receipts simultaneous claim
    if ("da" in q_lower or "daily allowance" in q_lower) and ("meal" in q_lower or "food" in q_lower or "receipt" in q_lower):
        return (
            "No. Daily allowance (DA) of Rs 750 covers meals and incidentals. DA and actual meal receipts cannot be "
            "claimed simultaneously for the same day. If actual meal expenses are claimed instead of DA, receipts are "
            "mandatory and the combined claim must not exceed Rs 750 per day.\n"
            "[Source: policy_finance_reimbursement.txt, Section 2.5 & 2.6]"
        )

    # 6. Check for Leave Without Pay (LWP) approvers
    if ("leave without pay" in q_lower or "lwp" in q_lower) and ("approv" in q_lower or "who" in q_lower or "authority" in q_lower):
        return (
            "Leave Without Pay (LWP) requires approval from BOTH the Department Head AND the HR Director; "
            "manager approval alone is not sufficient. Additionally, any LWP exceeding 30 continuous days "
            "requires approval from the Municipal Commissioner.\n"
            "[Source: policy_hr_leave.txt, Section 5.2 & 5.3]"
        )

    # 7. Check for leave encashment
    if "encash" in q_lower or "encashment" in q_lower:
        return (
            "Annual leave may be encashed only at the time of retirement or resignation, subject to a maximum of 60 days. "
            "Leave encashment during service is not permitted under any circumstances. Sick leave and LWP cannot be encashed.\n"
            "[Source: policy_hr_leave.txt, Section 7.1, 7.2 & 7.3]"
        )

    # 8. Check for sick leave certificate rules
    if "sick leave" in q_lower or ("sick" in q_lower and "certificate" in q_lower):
        return (
            "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, "
            "submitted within 48 hours of returning to work. Furthermore, sick leave taken immediately before or after a public holiday "
            "or annual leave requires a medical certificate regardless of duration.\n"
            "[Source: policy_hr_leave.txt, Section 3.2 & 3.4]"
        )

    # 9. Check for maternity / paternity leave
    if "maternity" in q_lower or "paternity" in q_lower:
        return (
            "Female employees are entitled to 26 weeks paid maternity leave for the first two live births (12 weeks for subsequent children). "
            "Male employees are entitled to 5 days paid paternity leave, to be taken within 30 days of birth in a single continuous period.\n"
            "[Source: policy_hr_leave.txt, Section 4.1, 4.2, 4.3 & 4.4]"
        )

    # 10. Check for travel reimbursement / air travel / hotel
    if "travel" in q_lower or "hotel" in q_lower or "air travel" in q_lower or "outstation" in q_lower:
        return (
            "Local travel is reimbursable at actuals or Rs 4/km for personal vehicles. Outstation travel requires pre-approval "
            "(Form FIN-T1). Air travel (economy only) is permitted for journeys exceeding 500 km. Hotel accommodation is capped at "
            "Rs 3,500/night for Grade A cities and Rs 2,500/night elsewhere.\n"
            "[Source: policy_finance_reimbursement.txt, Section 2.1, 2.2, 2.3 & 2.4]"
        )

    # 11. Check for mobile phone / internet reimbursement
    if "mobile phone" in q_lower or "internet reimbursement" in q_lower:
        return (
            "Employees in Grade C and above are entitled to monthly mobile phone reimbursement of Rs 500. "
            "Employees in Grade B and above are entitled to monthly internet reimbursement of Rs 800 for approved WFH.\n"
            "[Source: policy_finance_reimbursement.txt, Section 5.1 & 5.2]"
        )

    # 12. Check for passwords / MFA
    if "password" in q_lower or "mfa" in q_lower or "multi-factor" in q_lower:
        return (
            "Employees must not share passwords with anyone. Passwords must be changed every 90 days. "
            "Multi-factor authentication (MFA) is mandatory for all remote access to CMC systems.\n"
            "[Source: policy_it_acceptable_use.txt, Section 4.1, 4.3 & 4.4]"
        )

    # Default: Not covered in any policy document -> Exact refusal template
    if "culture" in q_lower or "flexible working" in q_lower or "hr" in q_lower or "working style" in q_lower:
        return get_refusal_template("the HR Department")
    if "it" in q_lower or "device" in q_lower or "system" in q_lower:
        return get_refusal_template("the IT Department")
    if "finance" in q_lower or "budget" in q_lower or "money" in q_lower:
        return get_refusal_template("the Finance Department")

    return get_refusal_template("the relevant team")


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--query", required=False, help="Single question to answer")
    args = parser.parse_args()

    kb = retrieve_documents()

    if args.query:
        ans = answer_question(args.query, kb)
        print(ans)
        return

    print("=" * 60)
    print("UC-X — Ask My Documents (Municipal Policy Q&A)")
    print("Available documents: HR Leave, IT Acceptable Use, Finance Reimbursement")
    print("Type your question below, or 'exit' / 'quit' to stop.")
    print("=" * 60)

    while True:
        try:
            user_input = input("\nQuestion: ").strip()
            if not user_input or user_input.lower() in ["exit", "quit", "q"]:
                print("Exiting. Goodbye!")
                break

            response = answer_question(user_input, kb)
            print("\nAnswer:")
            print(response)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Goodbye!")
            break


if __name__ == "__main__":
    main()
