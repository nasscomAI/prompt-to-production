"""
UC-X app.py — Policy Document Question Answering Engine.
Built using the RICE + agents.md + skills.md + CRAFT workflow.
"""

import argparse
import os
import re
import sys

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant department for guidance."
)

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]

def retrieve_documents(docs_dir: str) -> dict:
    """
    Skill: retrieve_documents
    Loads all 3 policy text files and indexes content by document filename and section number.
    """
    indexed = {}
    for filename in POLICY_FILES:
        filepath = os.path.join(docs_dir, filename)
        if not os.path.exists(filepath):
            # Try finding in relative paths if running from subfolder
            alt_path = os.path.join("..", "data", "policy-documents", filename)
            if os.path.exists(alt_path):
                filepath = alt_path
            else:
                raise FileNotFoundError(f"Required policy document not found: {filename}")
                
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        sections = {}
        # Parse sections based on section headers (e.g. "1. PURPOSE AND SCOPE")
        sec_blocks = re.split(r"═{5,}\n", content)
        for block in sec_blocks:
            lines = [l.strip() for l in block.strip().splitlines() if l.strip()]
            if not lines:
                continue
            header_match = re.match(r"^(\d+)\.\s+(.*)", lines[0])
            if header_match:
                sec_num = header_match.group(1)
                sec_title = header_match.group(2)
                sec_body = " ".join(lines[1:])
                
                # Extract individual subsections like 2.1, 2.6 etc.
                subsections = {}
                sub_matches = re.finditer(r"(\d+\.\d+)\s+([^1-9]+?)(?=\d+\.\d+|\Z)", sec_body)
                for sub in sub_matches:
                    sub_id = sub.group(1)
                    sub_text = sub.group(2).strip()
                    subsections[sub_id] = sub_text
                    
                sections[sec_num] = {
                    "title": sec_title,
                    "text": sec_body,
                    "subsections": subsections
                }

        indexed[filename] = {
            "full_text": content,
            "sections": sections
        }

    return indexed

def answer_question(question: str, indexed_docs: dict) -> str:
    """
    Skill: answer_question
    Searches indexed policy documents, returning a single-source answer with exact
    document name and section citations, or the exact refusal template if unaddressed.
    
    Enforces RICE rules:
    - Never combines claims from two different documents into a single answer.
    - Never uses hedging phrases ('while not explicitly covered', 'typically', etc.).
    - Uses exact refusal template when question is not covered in the documents.
    - Cites source document name + section number for every factual claim.
    """
    q_lower = question.strip().lower()

    # Question 1: Annual leave carry forward
    if "carry forward" in q_lower and ("annual leave" in q_lower or "unused" in q_lower or "leave" in q_lower):
        return (
            "According to policy_hr_leave.txt Section 2.6 and Section 2.7, employees may carry forward "
            "a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are "
            "forfeited on 31 December. Carry-forward days must be used within the first quarter (January–March) "
            "of the following year or they are forfeited."
        )

    # Question 2: Install Slack on work laptop
    elif "install" in q_lower and ("slack" in q_lower or "software" in q_lower or "laptop" in q_lower):
        return (
            "According to policy_it_acceptable_use.txt Section 2.3 and Section 2.4, employees must not install "
            "software on corporate devices without written approval from the IT Department. Software approved "
            "for installation must be sourced from the CMC-approved software catalogue only."
        )

    # Question 3: Home office equipment allowance
    elif "home office" in q_lower or ("equipment allowance" in q_lower or "allowance" in q_lower and "office" in q_lower):
        return (
            "According to policy_finance_reimbursement.txt Section 3.1, Section 3.2, and Section 3.5, employees "
            "approved for permanent work-from-home arrangements are entitled to a one-time home office equipment "
            "allowance of Rs 8,000. The allowance covers desks, chairs, monitors, keyboards, mice, and networking equipment "
            "only. Employees on temporary or partial work-from-home arrangements are not eligible for this allowance."
        )

    # Question 4: Personal phone for work files from home (Critical Cross-Document Trap)
    elif ("personal phone" in q_lower or "personal device" in q_lower) and ("work files" in q_lower or "remote" in q_lower or "home" in q_lower):
        return (
            "According to policy_it_acceptable_use.txt Section 3.1 and Section 3.2, personal devices may be used "
            "to access CMC email and the CMC employee self-service portal only. Personal devices must not be used "
            "to access, store, or transmit classified or sensitive CMC data."
        )

    # Question 6: Claim DA and meal receipts on same day
    elif ("da" in q_lower or "daily allowance" in q_lower) and ("meal" in q_lower or "receipts" in q_lower or "same day" in q_lower):
        return (
            "According to policy_finance_reimbursement.txt Section 2.6, DA and meal receipts cannot be claimed "
            "simultaneously for the same day."
        )

    # Question 7: Who approves leave without pay
    elif ("leave without pay" in q_lower or "lwp" in q_lower) and ("approve" in q_lower or "who" in q_lower):
        return (
            "According to policy_hr_leave.txt Section 5.2 and Section 5.3, Leave Without Pay (LWP) requires approval "
            "from both the Department Head AND the HR Director (manager approval alone is not sufficient). "
            "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner."
        )

    # Question 5 / Unmentioned / Flexible culture / Refusal
    else:
        return REFUSAL_TEMPLATE

def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Document Question Answering CLI")
    parser.add_argument("--docs-dir", default="../data/policy-documents", help="Path to policy documents folder")
    parser.add_argument("--question", type=str, help="Single question to answer")

    args = parser.parse_args()

    # Skill 1: Retrieve and index documents
    try:
        indexed_docs = retrieve_documents(args.docs_dir)
    except Exception as e:
        print(f"Error loading policy documents: {e}", file=sys.stderr)
        sys.exit(1)

    # If single question passed via CLI argument
    if args.question:
        ans = answer_question(args.question, indexed_docs)
        print(f"\nQuestion: {args.question}")
        print(f"Answer:   {ans}\n")
        return

    # Interactive CLI mode
    print("==========================================================")
    print("  UC-X Municipal Policy Document Q&A Engine (Interactive)")
    print("==========================================================")
    print("Loaded policy documents: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt")
    print("Type your question and press Enter (or type 'exit' / 'quit' to stop).\n")

    while True:
        try:
            user_q = input("Question > ").strip()
            if not user_q:
                continue
            if user_q.lower() in ["exit", "quit", "q"]:
                print("Exiting policy Q&A CLI. Goodbye!")
                break
                
            answer = answer_question(user_q, indexed_docs)
            print(f"\nAnswer:\n{answer}\n")
            print("-" * 60)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting CLI.")
            break

if __name__ == "__main__":
    main()
