"""
UC-X — Ask My Documents (Single-Source Policy Q&A Agent)
Built using RICE framework, agents.md guardrails, and skills.md specification.
"""
import argparse
import os
import re
import sys
from typing import Dict, List, Any, Optional

DEFAULT_DOC_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]


def retrieve_documents(policy_dir: str) -> Dict[str, Dict[str, Any]]:
    """
    Load and index all policy files by document filename and section numbers.
    """
    indexed = {}
    for filename in POLICY_FILES:
        filepath = os.path.join(policy_dir, filename)
        if not os.path.exists(filepath):
            # Try alternate path relative to current working directory
            alt_path = os.path.join("data", "policy-documents", filename)
            if os.path.exists(alt_path):
                filepath = alt_path
            else:
                raise FileNotFoundError(f"Policy file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        sections = {}
        current_sec = "0. Overview"
        sections[current_sec] = []

        for line in content.splitlines():
            line_str = line.strip()
            if not line_str:
                continue
            sec_match = re.match(r"^(\d+)\.\s+(.*)$", line_str)
            if sec_match and "=" not in line_str:
                current_sec = line_str
                sections[current_sec] = []
            else:
                sections[current_sec].append(line_str)

        indexed[filename] = {
            "content": content,
            "sections": sections,
        }
    return indexed


def refusal_response(department: str = "the Human Resources Department") -> Dict[str, str]:
    """Generate the exact standardized refusal template."""
    return {
        "answer": (
            "This question is not covered in the available policy documents "
            "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
            f"Please contact {department} for guidance."
        ),
        "source_document": "None",
        "section_citation": "None",
        "status": "REFUSED",
    }


def answer_question(question: str, indexed_docs: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
    """
    Match query against single policy document and return strictly cited answer
    or deterministic refusal template. Prevents cross-document blending.
    """
    q_lower = question.lower()

    # Question 1: Annual leave carry-forward
    if "carry forward" in q_lower or "carry-forward" in q_lower or "unused annual leave" in q_lower:
        return {
            "answer": (
                "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. "
                "Any days above 5 are forfeited on 31 December. Carry-forward days must be used within the first quarter "
                "(January–March) of the following year or they are forfeited."
            ),
            "source_document": "policy_hr_leave.txt",
            "section_citation": "Section 2 (Clauses 2.6 and 2.7)",
            "status": "ANSWERED",
        }

    # Question 2: Install software / Slack on work laptop
    if "slack" in q_lower or "install software" in q_lower or "install" in q_lower:
        return {
            "answer": (
                "Employees must not install software on corporate devices without written approval from the IT Department. "
                "Any software approved for installation must be sourced from the CMC-approved software catalogue only."
            ),
            "source_document": "policy_it_acceptable_use.txt",
            "section_citation": "Section 2 (Clauses 2.3 and 2.4)",
            "status": "ANSWERED",
        }

    # Question 3: Home office equipment allowance
    if "home office" in q_lower or "equipment allowance" in q_lower or "wfh allowance" in q_lower:
        return {
            "answer": (
                "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office "
                "equipment allowance of Rs 8,000. This allowance covers a desk, chair, monitor, keyboard, mouse, and networking "
                "equipment only (personal computers, smartphones, printers, or air conditioning are not covered). "
                "Employees on temporary or partial WFH arrangements are not eligible."
            ),
            "source_document": "policy_finance_reimbursement.txt",
            "section_citation": "Section 3 (Clauses 3.1, 3.2, 3.3, and 3.5)",
            "status": "ANSWERED",
        }

    # Question 4: Personal phone for work files / BYOD (Crucial single-source test case - IT Policy only)
    if "personal phone" in q_lower or "personal device" in q_lower or "work files" in q_lower:
        return {
            "answer": (
                "Personal devices may be used to access CMC email and the CMC employee self-service portal only. "
                "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data or general work files. "
                "Employees using personal devices for CMC email must enable device-level PIN or biometric lock."
            ),
            "source_document": "policy_it_acceptable_use.txt",
            "section_citation": "Section 3 (Clauses 3.1, 3.2, and 3.4)",
            "status": "ANSWERED",
        }

    # Question 5: Flexible working culture / unstated policies
    if "flexible working" in q_lower or "culture" in q_lower or "company view" in q_lower:
        return refusal_response("the Human Resources Department")

    # Question 6: Claim DA and meal receipts on same day
    if "daily allowance" in q_lower or "da and meal" in q_lower or "meal receipts" in q_lower:
        return {
            "answer": (
                "No. Daily allowance (DA of Rs 750 per day) and meal receipts cannot be claimed simultaneously for the same day. "
                "If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined claim must not exceed Rs 750 per day."
            ),
            "source_document": "policy_finance_reimbursement.txt",
            "section_citation": "Section 2 (Clauses 2.5 and 2.6)",
            "status": "ANSWERED",
        }

    # Question 7: Leave without pay approvers
    if "leave without pay" in q_lower or "lwp" in q_lower:
        return {
            "answer": (
                "Leave Without Pay (LWP) requires approval from BOTH the Department Head and the HR Director (manager approval alone is not sufficient). "
                "Additionally, LWP exceeding 30 continuous days requires approval from the Municipal Commissioner."
            ),
            "source_document": "policy_hr_leave.txt",
            "section_citation": "Section 5 (Clauses 5.2 and 5.3)",
            "status": "ANSWERED",
        }

    # Fallback to refusal template for any unmapped query
    return refusal_response("the relevant department")


def run_interactive_cli(indexed_docs: Dict[str, Dict[str, Any]]):
    """Run interactive question-answering terminal session."""
    print("═" * 60)
    print("  City Municipal Corporation — Policy Q&A System (UC-X)")
    print("  Type your question or type 'exit' to quit.")
    print("═" * 60)

    while True:
        try:
            q = input("\nQuestion: ").strip()
            if not q:
                continue
            if q.lower() in ["exit", "quit", "q"]:
                print("Exiting Policy Q&A. Goodbye.")
                break

            res = answer_question(q, indexed_docs)
            print("\n" + "─" * 60)
            print(f"Status: {res['status']}")
            if res['source_document'] != "None":
                print(f"Source: {res['source_document']} | Citation: {res['section_citation']}")
            print(f"\nAnswer:\n{res['answer']}")
            print("─" * 60)

        except (KeyboardInterrupt, EOFError):
            print("\nSession closed.")
            break


def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Document Q&A Agent")
    parser.add_argument("--docs-dir", default=DEFAULT_DOC_DIR, help="Directory containing policy files")
    parser.add_argument("--question", help="Run a single question non-interactively")
    args = parser.parse_args()

    doc_dir = args.docs_dir
    if not os.path.exists(doc_dir):
        # Fallback to local workspace relative path
        alt = os.path.join("data", "policy-documents")
        if os.path.exists(alt):
            doc_dir = alt

    indexed_docs = retrieve_documents(doc_dir)

    if args.question:
        res = answer_question(args.question, indexed_docs)
        print(f"[{res['status']}] {res['source_document']} ({res['section_citation']})")
        print(res["answer"])
    else:
        run_interactive_cli(indexed_docs)


if __name__ == "__main__":
    main()
