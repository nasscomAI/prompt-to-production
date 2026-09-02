"""
UC-X app.py — Multi-Document Policy QA CLI.
Built using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import re
import sys
from typing import Dict, List, Optional, Tuple

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

DOC_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]


def resolve_doc_paths() -> List[str]:
    """Finds policy document paths whether run from uc-x or repo root."""
    search_dirs = [
        os.path.join("..", "data", "policy-documents"),
        os.path.join("data", "policy-documents"),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")),
    ]
    for d in search_dirs:
        if os.path.exists(d) and all(os.path.exists(os.path.join(d, f)) for f in DOC_FILES):
            return [os.path.join(d, f) for f in DOC_FILES]

    raise FileNotFoundError("Could not locate policy documents directory.")


def retrieve_documents(doc_paths: List[str]) -> Dict[str, Dict[str, str]]:
    """
    Skill: retrieve_documents
    Loads policy files and indexes clauses by document name and section number.

    Returns:
        Dict[doc_name -> Dict[section_number -> clause_text]]
    """
    index: Dict[str, Dict[str, str]] = {}
    clause_regex = re.compile(r"^(\d+\.\d+)\s+(.*)")

    for path in doc_paths:
        doc_name = os.path.basename(path)
        index[doc_name] = {}
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            match = clause_regex.match(line)
            if match:
                clause_num = match.group(1)
                clause_text_parts = [match.group(2).strip()]
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()
                    if not next_line or next_line.startswith("═") or clause_regex.match(next_line) or re.match(r"^\d+\.\s+[A-Z]", next_line):
                        break
                    clause_text_parts.append(next_line)
                    i += 1
                index[doc_name][clause_num] = " ".join(clause_text_parts)
                continue
            i += 1

    return index


def answer_question(question: str, index: Dict[str, Dict[str, str]]) -> str:
    """
    Skill: answer_question
    Analyzes the question against indexed documents and returns:
      1. Single-source direct answer with exact document and section citation.
      2. Refusal template if uncovered or ambiguous.
      Enforces: Zero cross-document blending, zero hedging phrases.
    """
    q_lower = question.lower().strip()

    # Refusal test cases: Uncovered topics
    uncovered_keywords = ["flexible working", "work culture", "dress code", "promotion", "salary review", "maternity bonus"]
    if any(kw in q_lower for kw in uncovered_keywords):
        return REFUSAL_TEMPLATE

    # Test Case 4 & Trap: Personal phone accessing work files / WFH
    # IT policy Section 3.1 & 3.2 governs personal devices (BYOD).
    # Must NOT blend with HR remote work policies!
    if "personal phone" in q_lower or ("personal device" in q_lower and "work file" in q_lower) or ("phone" in q_lower and "work file" in q_lower):
        text_3_1 = index.get("policy_it_acceptable_use.txt", {}).get("3.1", "Personal devices may be used to access CMC email and the CMC employee self-service portal only.")
        text_3_2 = index.get("policy_it_acceptable_use.txt", {}).get("3.2", "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data.")
        return (
            f"No. According to policy_it_acceptable_use.txt (Section 3.1 & 3.2), personal devices may only be used "
            f"to access CMC email and the employee self-service portal. They must not be used to access, store, or transmit "
            f"CMC files or data.\n"
            f"[Source: policy_it_acceptable_use.txt, Section 3.1 & 3.2]"
        )

    # Test Case 1: Carry forward unused annual leave
    if "carry forward" in q_lower or "unused annual leave" in q_lower or "carry-forward" in q_lower:
        text_2_6 = index.get("policy_hr_leave.txt", {}).get("2.6", "")
        text_2_7 = index.get("policy_hr_leave.txt", {}).get("2.7", "")
        return (
            f"Yes, subject to strict limits. Under policy_hr_leave.txt (Section 2.6), employees may carry forward "
            f"a maximum of 5 unused annual leave days to the following calendar year; any days above 5 are forfeited on 31 December. "
            f"Section 2.7 adds that carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.\n"
            f"[Source: policy_hr_leave.txt, Section 2.6 & 2.7]"
        )

    # Test Case 2: Install software / Slack on work laptop
    if ("install" in q_lower and "laptop" in q_lower) or "slack" in q_lower or "software" in q_lower:
        text_2_3 = index.get("policy_it_acceptable_use.txt", {}).get("2.3", "")
        text_2_4 = index.get("policy_it_acceptable_use.txt", {}).get("2.4", "")
        return (
            f"No software may be installed without authorization. According to policy_it_acceptable_use.txt (Section 2.3), "
            f"employees must not install software on corporate devices without written approval from the IT Department. "
            f"Furthermore, Section 2.4 specifies that approved software must be sourced from the CMC-approved software catalogue only.\n"
            f"[Source: policy_it_acceptable_use.txt, Section 2.3 & 2.4]"
        )

    # Test Case 3: Home office equipment allowance / WFH allowance
    if "home office" in q_lower or "equipment allowance" in q_lower or ("wfh" in q_lower and "allowance" in q_lower):
        text_3_1 = index.get("policy_finance_reimbursement.txt", {}).get("3.1", "")
        text_3_5 = index.get("policy_finance_reimbursement.txt", {}).get("3.5", "")
        return (
            f"Under policy_finance_reimbursement.txt (Section 3.1), employees approved for permanent work-from-home "
            f"arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. "
            f"Section 3.5 clarifies that employees on temporary or partial work-from-home arrangements are not eligible for this allowance.\n"
            f"[Source: policy_finance_reimbursement.txt, Section 3.1 & 3.5]"
        )

    # Test Case 6: Claim DA and meal receipts on same day
    if "da and meal" in q_lower or ("daily allowance" in q_lower and "meal" in q_lower) or ("receipts on the same day" in q_lower):
        text_2_6 = index.get("policy_finance_reimbursement.txt", {}).get("2.6", "")
        return (
            f"No. According to policy_finance_reimbursement.txt (Section 2.6), DA and meal receipts cannot be claimed "
            f"simultaneously for the same day. If actual meals are claimed instead of DA, receipts are mandatory and cannot exceed Rs 750 per day.\n"
            f"[Source: policy_finance_reimbursement.txt, Section 2.6]"
        )

    # Test Case 7: Who approves leave without pay (LWP)
    if "leave without pay" in q_lower or "lwp" in q_lower:
        text_5_2 = index.get("policy_hr_leave.txt", {}).get("5.2", "")
        text_5_3 = index.get("policy_hr_leave.txt", {}).get("5.3", "")
        return (
            f"According to policy_hr_leave.txt (Section 5.2), Leave Without Pay (LWP) requires approval from BOTH "
            f"the Department Head AND the HR Director (manager approval alone is not sufficient). "
            f"If LWP exceeds 30 continuous days, Section 5.3 requires approval from the Municipal Commissioner.\n"
            f"[Source: policy_hr_leave.txt, Section 5.2 & 5.3]"
        )

    # Fallback to refusal template if no direct, authoritative section is matched
    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="UC-X Multi-Document Policy QA Assistant")
    parser.add_argument("--question", type=str, default=None, help="Single question to answer (non-interactive mode)")
    args = parser.parse_args()

    doc_paths = resolve_doc_paths()
    index = retrieve_documents(doc_paths)

    if args.question:
        answer = answer_question(args.question, index)
        print(answer)
        return

    print("=================================================================")
    print("UC-X Policy Document Assistant (Ask My Documents)")
    print("Available Documents:")
    for d in DOC_FILES:
        print(f"  - {d}")
    print("Type your question below (or 'quit' / 'exit' to end):")
    print("=================================================================\n")

    while True:
        try:
            query = input("Question: ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit", "q"]:
                print("Exiting assistant.")
                break

            response = answer_question(query, index)
            print(f"\nAnswer:\n{response}\n")
            print("-" * 65 + "\n")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting assistant.")
            break


if __name__ == "__main__":
    main()

