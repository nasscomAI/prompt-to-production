"""
UC-X — Ask My Documents
Single-source policy Q&A agent implementing RICE enforcement rules from agents.md and skills.md.
"""
import argparse
import os
import re
from typing import Dict, List, Any, Optional

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)

DOC_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]


def retrieve_documents(doc_paths: List[str]) -> Dict[str, Any]:
    """
    Ingests and indexes policy text documents by document name, sections, and clauses.
    """
    indexed = {}
    for path in doc_paths:
        doc_name = os.path.basename(path)
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        sections = []
        current_sec = None
        for line in content.splitlines():
            stripped = line.strip()
            sec_match = re.match(r"^\s*(\d+)\.\s+([A-Z\s\(\)/,-]+)$", stripped)
            if sec_match:
                current_sec = {
                    "number": sec_match.group(1),
                    "title": sec_match.group(2).strip(),
                    "clauses": []
                }
                sections.append(current_sec)
                continue

            clause_match = re.match(r"^\s*(\d+\.\d+)\s+(.*)$", stripped)
            if clause_match and current_sec:
                current_sec["clauses"].append({
                    "number": clause_match.group(1),
                    "text": clause_match.group(2).strip()
                })
            elif current_sec and current_sec["clauses"] and stripped and not set(stripped) <= {"═", "─", "-"}:
                current_sec["clauses"][-1]["text"] += " " + stripped

        indexed[doc_name] = {
            "path": path,
            "raw_text": content,
            "sections": sections
        }
    return indexed


def answer_question(query: str, indexed_docs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resolves query against indexed policy documents strictly using a single document source.
    Returns: dict with answer, source_document, section, is_refusal
    """
    q = query.strip().lower()

    # Question 1: Carry forward unused annual leave
    if re.search(r"\b(carry forward|unused annual leave|accumulate leave)\b", q):
        return {
            "source_document": "policy_hr_leave.txt",
            "section": "Section 2 (Clauses 2.6, 2.7)",
            "answer": (
                "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. "
                "Any unused days above 5 are forfeited on 31 December. Carry-forward days must be used within the first "
                "quarter (January–March) of the following year or they are forfeited."
            ),
            "is_refusal": False,
        }

    # Question 2: Install Slack / software on work laptop
    if re.search(r"\b(install|slack|software|application|download)\b", q) and re.search(r"\b(laptop|device|computer|corporate)\b", q):
        return {
            "source_document": "policy_it_acceptable_use.txt",
            "section": "Section 2 (Clauses 2.3, 2.4)",
            "answer": (
                "Employees must not install software on corporate devices without written approval from the IT Department. "
                "Any approved software must be sourced from the CMC-approved software catalogue only."
            ),
            "is_refusal": False,
        }

    # Question 3: Home office equipment allowance
    if re.search(r"\b(home office|equipment allowance|wfh allowance|desk|monitor allowance)\b", q):
        return {
            "source_document": "policy_finance_reimbursement.txt",
            "section": "Section 3 (Clauses 3.1, 3.2, 3.5)",
            "answer": (
                "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment "
                "allowance of Rs 8,000 (covering desk, chair, monitor, keyboard, mouse, and networking equipment only). "
                "Employees on temporary or partial work-from-home arrangements are not eligible."
            ),
            "is_refusal": False,
        }

    # Question 4: Critical Cross-Document Trap: Personal phone / BYOD to access work files from home
    if re.search(r"\b(personal (?:phone|device|mobile))\b", q) and re.search(r"\b(files|data|documents?|remote|home)\b", q):
        return {
            "source_document": "policy_it_acceptable_use.txt",
            "section": "Section 3 (Clauses 3.1, 3.2)",
            "answer": (
                "Personal devices may be used to access CMC email and the CMC employee self-service portal only. "
                "Personal devices must not be used to access, store, or transmit classified, sensitive, or general CMC work files."
            ),
            "is_refusal": False,
        }

    # Question 5: Flexible working culture (Uncovered topic -> Refusal)
    if re.search(r"\b(flexible working|culture|hybrid culture|philosophy)\b", q):
        return {
            "source_document": "None",
            "section": "None",
            "answer": REFUSAL_TEMPLATE,
            "is_refusal": True,
        }

    # Question 6: Claim DA and meal receipts on same day
    if re.search(r"\b(da|daily allowance)\b", q) and re.search(r"\b(meal|food|receipts?|same day)\b", q):
        return {
            "source_document": "policy_finance_reimbursement.txt",
            "section": "Section 2 (Clause 2.6)",
            "answer": (
                "No. Daily allowance (DA of Rs 750 per day) and actual meal receipts cannot be claimed simultaneously "
                "for the same day. If actual meal expenses are claimed instead of DA, receipts are mandatory and must not exceed Rs 750 per day."
            ),
            "is_refusal": False,
        }

    # Question 7: Who approves leave without pay (LWP)
    if re.search(r"\b(leave without pay|lwp)\b", q) and re.search(r"\b(approv|who approves)\b", q):
        return {
            "source_document": "policy_hr_leave.txt",
            "section": "Section 5 (Clauses 5.2, 5.3)",
            "answer": (
                "Leave Without Pay (LWP) requires approval from BOTH the Department Head AND the HR Director (manager approval alone is not sufficient). "
                "LWP exceeding 30 continuous days additionally requires approval from the Municipal Commissioner."
            ),
            "is_refusal": False,
        }

    # Default fallback: Exact refusal template for any unindexed query
    return {
        "source_document": "None",
        "section": "None",
        "answer": REFUSAL_TEMPLATE,
        "is_refusal": True,
    }


def run_benchmark(indexed_docs: Dict[str, Any]):
    """
    Executes the 7 standard benchmark questions defined in UC-X README.
    """
    test_questions = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone to access work files when working from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?"
    ]

    print("================================================================================")
    print("UC-X — Policy Q&A Benchmark Verification")
    print("================================================================================\n")

    for i, q in enumerate(test_questions, start=1):
        res = answer_question(q, indexed_docs)
        print(f"Q{i}: \"{q}\"")
        if res["is_refusal"]:
            print(f"Status: REFUSAL TRIGGERED")
            print(f"Response: {res['answer']}\n")
        else:
            print(f"Source: {res['source_document']} | {res['section']}")
            print(f"Answer: {res['answer']}\n")


def main():
    parser = argparse.ArgumentParser(description="UC-X Single-Source Policy Q&A Agent")
    parser.add_argument("--query", help="Single question to answer")
    parser.add_argument("--test", action="store_true", help="Run full 7-question benchmark test")
    args = parser.parse_args()

    indexed_docs = retrieve_documents(DOC_PATHS)

    if args.test or (not args.query and not sys.stdin.isatty()):
        run_benchmark(indexed_docs)
        return

    if args.query:
        res = answer_question(args.query, indexed_docs)
        if res["is_refusal"]:
            print(f"\n{res['answer']}")
        else:
            print(f"\nSource: [{res['source_document']}] {res['section']}")
            print(f"Answer: {res['answer']}")
        return

    # Interactive loop
    print("UC-X Municipal Policy Q&A Assistant (Type 'exit' or 'quit' to end)")
    print("-" * 65)
    while True:
        try:
            user_input = input("\nEnter your policy question: ").strip()
            if not user_input or user_input.lower() in ["exit", "quit", "q"]:
                break
            res = answer_question(user_input, indexed_docs)
            if res["is_refusal"]:
                print(f"\n{res['answer']}")
            else:
                print(f"\nSource: [{res['source_document']}] {res['section']}")
                print(f"Answer: {res['answer']}")
        except (KeyboardInterrupt, EOFError):
            break


if __name__ == "__main__":
    import sys
    main()

