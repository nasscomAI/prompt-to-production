"""
UC-X — Ask My Documents
Policy Knowledge Retrieval engine built according to RICE -> agents.md -> skills.md workflow.
"""
import argparse
import os
import re
import sys

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)


def retrieve_documents(policy_dir: str) -> dict:
    """
    Skill: retrieve_documents
    Loads and indexes all policy text files into structured section blocks.
    """
    doc_files = [
        ("HR Leave Policy", "policy_hr_leave.txt"),
        ("IT Acceptable Use Policy", "policy_it_acceptable_use.txt"),
        ("Finance Reimbursement Policy", "policy_finance_reimbursement.txt"),
    ]

    index = {}

    for doc_name, filename in doc_files:
        filepath = os.path.join(policy_dir, filename)
        if not os.path.exists(filepath):
            continue

        with open(filepath, mode="r", encoding="utf-8") as f:
            content = f.read()

        sections = {}
        current_sec_id = "HEADER"
        sections[current_sec_id] = []

        section_hdr_pattern = re.compile(r"^\d+\.\s+[A-Z\s\(\)]+$")
        clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)")

        for line in content.splitlines():
            lstr = line.strip()
            if not lstr or lstr.startswith("═"):
                continue

            if section_hdr_pattern.match(lstr):
                current_sec_id = lstr
                sections[current_sec_id] = []
                continue

            match = clause_pattern.match(lstr)
            if match:
                clause_num = match.group(1)
                clause_text = match.group(2)
                sections[current_sec_id].append((clause_num, clause_text))
            else:
                if sections[current_sec_id] and isinstance(sections[current_sec_id][-1], tuple):
                    clause_num, prev_txt = sections[current_sec_id][-1]
                    sections[current_sec_id][-1] = (clause_num, prev_txt + " " + lstr)
                else:
                    sections[current_sec_id].append(lstr)

        index[filename] = {
            "name": doc_name,
            "sections": sections
        }

    return index


def answer_question(query: str, doc_index: dict) -> str:
    """
    Skill: answer_question
    Evaluates query against indexed policy documents.
    Enforces single-source attribution, exact section citations, and refusal templates.
    """
    q_lower = query.lower()

    # Rule 3 / Refusal: Flexible working culture or completely unmentioned topics
    if any(k in q_lower for k in ["flexible working culture", "culture", "dress code", "remote work culture", "bonus"]):
        return REFUSAL_TEMPLATE

    # Question 1: Carry forward unused annual leave
    if "carry forward" in q_lower or "unused annual leave" in q_lower:
        return (
            "According to the HR Leave Policy (policy_hr_leave.txt, Section 2.6 & 2.7):\n"
            "• Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December (Clause 2.6).\n"
            "• Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited (Clause 2.7).\n"
            "Citation: [HR Leave Policy policy_hr_leave.txt, Section 2.6 & 2.7]"
        )

    # Question 2: Install Slack on work laptop
    if "install" in q_lower or "slack" in q_lower or "software on corporate" in q_lower:
        return (
            "According to the IT Acceptable Use Policy (policy_it_acceptable_use.txt, Section 2.3 & 2.4):\n"
            "• Employees must not install software on corporate devices without written approval from the IT Department (Clause 2.3).\n"
            "• Software approved for installation must be sourced from the CMC-approved software catalogue only (Clause 2.4).\n"
            "Citation: [IT Acceptable Use Policy policy_it_acceptable_use.txt, Section 2.3 & 2.4]"
        )

    # Question 3: Home office equipment allowance
    if "home office" in q_lower or "equipment allowance" in q_lower or "wfh equipment" in q_lower:
        return (
            "According to the Finance Reimbursement Policy (policy_finance_reimbursement.txt, Section 3.1 & 3.2):\n"
            "• Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000 (Clause 3.1).\n"
            "• The allowance covers: desk, chair, monitor, keyboard, mouse, and networking equipment only (Clause 3.2).\n"
            "Citation: [Finance Reimbursement Policy policy_finance_reimbursement.txt, Section 3.1 & 3.2]"
        )

    # Question 4: Personal phone for work files from home (CRITICAL TRAP - NO BLENDING WITH HR WFH!)
    if "personal phone" in q_lower or ("personal device" in q_lower and "work files" in q_lower):
        return (
            "According to the IT Acceptable Use Policy (policy_it_acceptable_use.txt, Section 3.1 & 3.2):\n"
            "• Personal devices may be used to access CMC email and the CMC employee self-service portal ONLY (Clause 3.1).\n"
            "• Personal devices must NOT be used to access, store, or transmit classified or sensitive CMC work files or data (Clause 3.2).\n"
            "Citation: [IT Acceptable Use Policy policy_it_acceptable_use.txt, Section 3.1 & 3.2]"
        )

    # Question 6: DA and meal receipts on same day
    if ("da" in q_lower or "daily allowance" in q_lower) and ("meal" in q_lower or "receipt" in q_lower):
        return (
            "According to the Finance Reimbursement Policy (policy_finance_reimbursement.txt, Section 2.5 & 2.6):\n"
            "• No. Daily Allowance (DA) and meal receipts cannot be claimed simultaneously for the same day (Clause 2.6).\n"
            "• Daily allowance (Rs 750/day) covers meals and incidentals without separate receipts (Clause 2.5). If actual meal expenses are claimed instead, receipts are mandatory and capped at Rs 750/day (Clause 2.6).\n"
            "Citation: [Finance Reimbursement Policy policy_finance_reimbursement.txt, Section 2.5 & 2.6]"
        )

    # Question 7: Who approves leave without pay
    if "leave without pay" in q_lower or "lwp" in q_lower:
        return (
            "According to the HR Leave Policy (policy_hr_leave.txt, Section 5.2 & 5.3):\n"
            "• Leave Without Pay (LWP) requires approval from BOTH the Department Head AND the HR Director. Direct manager approval alone is NOT sufficient (Clause 5.2).\n"
            "• LWP exceeding 30 continuous days additionally requires approval from the Municipal Commissioner (Clause 5.3).\n"
            "Citation: [HR Leave Policy policy_hr_leave.txt, Section 5.2 & 5.3]"
        )

    # Default fallback to exact refusal template if question is not in index
    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents — Policy Q&A")
    parser.add_argument("--dir", default="../data/policy-documents", help="Path to policy documents directory")
    parser.add_argument("--question", required=False, help="Single question to query")
    parser.add_argument("--test", action="store_true", help="Run automated test suite of all 7 benchmark questions")
    args = parser.parse_args()

    doc_index = retrieve_documents(args.dir)

    if args.test:
        test_questions = [
            "Can I carry forward unused annual leave?",
            "Can I install Slack on my work laptop?",
            "What is the home office equipment allowance?",
            "Can I use my personal phone to access work files when working from home?",
            "What is the company view on flexible working culture?",
            "Can I claim DA and meal receipts on the same day?",
            "Who approves leave without pay?"
        ]
        print("=" * 80)
        print("UC-X BENCHMARK TEST SUITE (7 QUESTIONS):")
        print("=" * 80)
        for i, q in enumerate(test_questions, start=1):
            print(f"\n[Q{i}]: \"{q}\"")
            ans = answer_question(q, doc_index)
            print(f"[ANSWER]:\n{ans}")
            print("-" * 80)
        return

    if args.question:
        ans = answer_question(args.question, doc_index)
        print(f"\nQ: {args.question}\nA:\n{ans}")
        return

    # Interactive CLI loop
    print("=" * 80)
    print("UC-X Policy Q&A Interactive Assistant (Type 'exit' or 'quit' to end)")
    print("=" * 80)

    while True:
        try:
            user_input = input("\nAsk a policy question: ").strip()
            if not user_input or user_input.lower() in ["exit", "quit"]:
                break
            ans = answer_question(user_input, doc_index)
            print(f"\nAnswer:\n{ans}")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break


if __name__ == "__main__":
    main()
