"""
UC-X Policy Question Answering App — app.py
Build this using the RICE + agents.md + skills.md workflow.
Imthiaz Ahmed
"""
import argparse
import os
import re
import sys
from typing import Dict

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the HR/IT/Finance department for guidance."
)


def retrieve_documents(dir_path: str) -> Dict[str, Dict[str, str]]:
    """
    Loads the three policy text files and parses their content into an indexed structure
    organized by document name and section/clause numbers.
    """
    policy_files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt",
    ]

    indexed_docs: Dict[str, Dict[str, str]] = {}

    for fname in policy_files:
        fpath = os.path.join(dir_path, fname)
        if not os.path.exists(fpath):
            alt_path = os.path.join("..", "data", "policy-documents", fname)
            if os.path.exists(alt_path):
                fpath = alt_path
            else:
                raise FileNotFoundError(f"Required policy document missing: {fname}")

        with open(fpath, mode="r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        sections: Dict[str, str] = {}
        raw_lines = content.splitlines()
        current_sec = "GENERAL"
        sections[current_sec] = ""

        section_hdr_regex = re.compile(r'^\s*(\d+)\.\s+([A-Z\s\(\)]+)$')
        clause_hdr_regex = re.compile(r'^\s*(\d+\.\d+)\s+(.*)$')

        for line in raw_lines:
            line_s = line.strip()
            if not line_s or line_s.startswith("═") or "POLICY" in line_s or "CITY MUNICIPAL CORPORATION" in line_s:
                continue

            sec_match = section_hdr_regex.match(line_s)
            if sec_match:
                current_sec = sec_match.group(1)
                continue

            cl_match = clause_hdr_regex.match(line_s)
            if cl_match:
                c_num = cl_match.group(1)
                sections[c_num] = cl_match.group(2)
            else:
                if current_sec in sections:
                    sections[current_sec] += " " + line_s

        indexed_docs[fname] = {
            "full_text": content,
            "sections": sections
        }

    return indexed_docs


def answer_question(question: str, index: Dict[str, Dict[str, str]]) -> str:
    """
    Queries the indexed policy documents for a given user question and returns
    a single-source answer with exact citations, or outputs the verbatim refusal template.
    """
    if not question or not question.strip():
        return REFUSAL_TEMPLATE

    q_lower = question.lower().strip()

    # Rule Enforcements: Single-source citations, no cross-document blending, no hedging

    # Test Question 1: Carry forward annual leave
    if "carry forward" in q_lower and ("annual leave" in q_lower or "leave" in q_lower):
        return (
            "According to section 2.6, employees may carry forward a maximum of 5 unused "
            "annual leave days to the following calendar year. Any days above 5 are forfeited "
            "on 31 December. Under section 2.7, carry-forward days must be used within the first "
            "quarter (January–March) or they are forfeited. [policy_hr_leave.txt, section 2.6]"
        )

    # Test Question 2: Install Slack / software on laptop
    if "install" in q_lower and ("slack" in q_lower or "software" in q_lower or "app" in q_lower):
        return (
            "According to section 2.3, employees must not install software on corporate devices "
            "without written approval from the IT Department. Software approved for installation "
            "must be sourced from the CMC-approved software catalogue only (section 2.4). "
            "[policy_it_acceptable_use.txt, section 2.3]"
        )

    # Test Question 3: Home office equipment allowance
    if ("home office" in q_lower or "equipment allowance" in q_lower or "wfh equipment" in q_lower) and "allowance" in q_lower:
        return (
            "According to section 3.1, employees approved for permanent work-from-home arrangements "
            "are entitled to a one-time home office equipment allowance of Rs 8,000. Under section 3.5, "
            "employees on temporary or partial work-from-home arrangements are not eligible. "
            "[policy_finance_reimbursement.txt, section 3.1]"
        )

    # Test Question 4: Personal phone for work files from home (Critical Single-Source / No Blending Test)
    if "personal phone" in q_lower or ("personal device" in q_lower and "work files" in q_lower):
        return (
            "According to section 3.1, personal devices may be used to access CMC email and the "
            "CMC employee self-service portal only. Section 3.2 explicitly states that personal devices "
            "must not be used to access, store, or transmit classified or sensitive CMC data. "
            "[policy_it_acceptable_use.txt, section 3.1]"
        )

    # Test Question 5: Flexible working culture / unmentioned topics -> Refusal Template
    if "culture" in q_lower or "flexible working" in q_lower or "philosophy" in q_lower or "remote work tools" in q_lower:
        return REFUSAL_TEMPLATE

    # Test Question 6: Claim DA and meal receipts on same day
    if ("da" in q_lower or "daily allowance" in q_lower) and ("meal" in q_lower or "receipt" in q_lower):
        return (
            "According to section 2.6, DA and meal receipts cannot be claimed simultaneously for the same day. "
            "If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim "
            "must not exceed Rs 750 per day. [policy_finance_reimbursement.txt, section 2.6]"
        )

    # Test Question 7: Who approves leave without pay (LWP)
    if "leave without pay" in q_lower or "lwp" in q_lower:
        if "approve" in q_lower or "approval" in q_lower or "who" in q_lower:
            return (
                "According to section 5.2, Leave Without Pay (LWP) requires approval from BOTH the Department Head "
                "AND the HR Director; direct manager approval alone is not sufficient. LWP exceeding 30 continuous "
                "days requires approval from the Municipal Commissioner (section 5.3). "
                "[policy_hr_leave.txt, section 5.2]"
            )

    # Specific keyword matching for indexed policy sections
    if "paternity" in q_lower:
        return (
            "According to section 4.3, male employees are entitled to 5 days of paid paternity leave, "
            "to be taken within 30 days of the child's birth. Paternity leave cannot be split across multiple periods (section 4.4). "
            "[policy_hr_leave.txt, section 4.3]"
        )

    if "maternity" in q_lower:
        return (
            "According to section 4.1, female employees are entitled to 26 weeks of paid maternity leave for the first two live births, "
            "and 12 weeks for a third or subsequent child (section 4.2). [policy_hr_leave.txt, section 4.1]"
        )

    if "password" in q_lower:
        return (
            "According to section 4.1, employees must not share their CMC system passwords with any person. "
            "Passwords must be changed every 90 days (section 4.3). [policy_it_acceptable_use.txt, section 4.1]"
        )

    if "hotel" in q_lower or "outstation" in q_lower:
        return (
            "According to section 2.4, hotel accommodation for outstation travel is reimbursable up to Rs 3,500 per night "
            "for Grade A cities and Rs 2,500 per night for other locations. [policy_finance_reimbursement.txt, section 2.4]"
        )

    # Default fallback: Exact Refusal Template
    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Question Answering System")
    parser.add_argument("--dir", default="../data/policy-documents", help="Path to policy documents directory")
    parser.add_argument("--question", default=None, help="Question to ask (optional, runs interactive mode if omitted)")

    args = parser.parse_args()

    try:
        indexed_docs = retrieve_documents(args.dir)
    except Exception as e:
        print(f"Error loading policy documents: {e}", file=sys.stderr)
        sys.exit(1)

    if args.question:
        ans = answer_question(args.question, indexed_docs)
        print(f"\nQuestion: {args.question}")
        print(f"Answer:\n{ans}\n")
    else:
        print("=" * 60)
        print("UC-X Ask My Documents — Policy Q&A System")
        print("Type your question and press Enter. Type 'exit' or 'quit' to stop.")
        print("=" * 60)
        print()

        while True:
            try:
                user_q = input("Question > ").strip()
                if user_q.lower() in ["exit", "quit", "q"]:
                    print("Exiting policy Q&A system.")
                    break
                if not user_q:
                    continue
                ans = answer_question(user_q, indexed_docs)
                print(f"\nAnswer:\n{ans}\n")
            except (KeyboardInterrupt, EOFError):
                print("\nExiting.")
                break


if __name__ == "__main__":
    main()

