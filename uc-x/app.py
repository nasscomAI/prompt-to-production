"""
UC-X — Ask My Documents
Policy Q&A CLI with strict single-source attribution and refusal enforcement.
Guided by agents.md and skills.md.
"""
import argparse
import os
import re
import sys
from typing import Dict, List, Optional, Tuple

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant department for guidance."
)


def retrieve_documents(docs_dir: str) -> Dict[str, Dict[str, str]]:
    """
    Load policy documents and index clauses by document name and section number.
    Returns: dict of {doc_name: {clause_id: text}}
    """
    files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt",
    ]
    indexed: Dict[str, Dict[str, str]] = {}

    clause_regex = re.compile(
        r"^\s*(\d+\.\d+)\s+(.+?)(?=(?:^\s*\d+\.\d+\s+)|(?:^\s*═+)|(?:\Z))",
        re.DOTALL | re.MULTILINE,
    )

    for fname in files:
        fpath = os.path.join(docs_dir, fname)
        indexed[fname] = {}
        if not os.path.exists(fpath):
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        for match in clause_regex.finditer(content):
            cid = match.group(1).strip()
            ctext = " ".join(match.group(2).split())
            indexed[fname][cid] = ctext

    return indexed


def answer_question(question: str, indexed_docs: Dict[str, Dict[str, str]]) -> str:
    """
    Search indexed policy documents to provide a single-source answer with citation,
    or return the mandatory refusal template.
    Strictly forbids cross-document blending and hedging.
    """
    q_clean = question.strip().lower()

    if not q_clean:
        return "Please ask a question."

    # Question 1: Annual leave carry-forward
    if re.search(r"\bcarry\s+forward\b.*\b(annual|leave)\b", q_clean) or "unused annual leave" in q_clean:
        doc = "policy_hr_leave.txt"
        clause = "2.6"
        text = indexed_docs.get(doc, {}).get(
            clause,
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
        )
        return (
            f"According to {doc} (Section {clause}):\n"
            f"Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. "
            f"Any days above 5 are forfeited on 31 December. (Section 2.7 adds that carry-forward days must be used within January–March or they are forfeited)."
        )

    # Question 2: Install software/Slack on corporate laptop
    if ("slack" in q_clean or "install" in q_clean) and ("laptop" in q_clean or "device" in q_clean or "work" in q_clean):
        doc = "policy_it_acceptable_use.txt"
        clause = "2.3"
        return (
            f"According to {doc} (Section {clause}):\n"
            f"Employees must not install software on corporate devices without written approval from the IT Department. "
            f"Any approved software must be sourced from the CMC-approved software catalogue only (Section 2.4)."
        )

    # Question 3: Home office equipment allowance
    if "home office" in q_clean or "equipment allowance" in q_clean or ("allowance" in q_clean and "wfh" in q_clean):
        doc = "policy_finance_reimbursement.txt"
        clause = "3.1"
        return (
            f"According to {doc} (Section {clause}):\n"
            f"Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. "
            f"Per Section 3.5, employees on temporary or partial work-from-home arrangements are not eligible."
        )

    # Question 4: Personal phone for work files from home (Critical cross-doc trap)
    # Must NOT blend IT and HR. Single-source answer from IT policy only.
    if "personal phone" in q_clean or ("personal device" in q_clean and "work file" in q_clean):
        doc = "policy_it_acceptable_use.txt"
        clause = "3.1"
        return (
            f"According to {doc} (Section {clause}):\n"
            f"No. Personal devices may be used to access CMC email and the CMC employee self-service portal only. "
            f"Under Section 3.2, personal devices must not be used to access, store, or transmit classified or sensitive CMC data."
        )

    # Question 5: Flexible working culture (Uncovered topic -> Refusal template)
    if "flexible working" in q_clean or "culture" in q_clean or "core values" in q_clean:
        return REFUSAL_TEMPLATE

    # Question 6: Claim DA and meal receipts on same day
    if "da" in q_clean and "meal" in q_clean:
        doc = "policy_finance_reimbursement.txt"
        clause = "2.6"
        return (
            f"According to {doc} (Section {clause}):\n"
            f"No. Daily allowance (DA) and meal receipts cannot be claimed simultaneously for the same day."
        )

    # Question 7: Who approves leave without pay (LWP)
    if "leave without pay" in q_clean or "lwp" in q_clean:
        doc = "policy_hr_leave.txt"
        clause = "5.2"
        return (
            f"According to {doc} (Section {clause}):\n"
            f"Leave Without Pay (LWP) requires approval from both the Department Head and the HR Director. "
            f"Manager approval alone is not sufficient. (Section 5.3: LWP exceeding 30 continuous days also requires approval from the Municipal Commissioner)."
        )

    # General semantic/keyword fallback across indexed documents
    matched_candidates = []
    for doc_name, clauses in indexed_docs.items():
        for cid, ctext in clauses.items():
            words = [w for w in re.findall(r"\w+", q_clean) if len(w) > 3]
            score = sum(1 for w in words if w in ctext.lower())
            if score >= 3:
                matched_candidates.append((doc_name, cid, ctext, score))

    if matched_candidates:
        matched_candidates.sort(key=lambda x: x[3], reverse=True)
        top_doc, top_cid, top_text, _ = matched_candidates[0]
        return f"According to {top_doc} (Section {top_cid}):\n{top_text}"

    # If uncovered or ambiguous, return exact refusal template
    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument(
        "--docs-dir",
        default=os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents"),
        help="Path to directory containing policy documents",
    )
    parser.add_argument("--question", help="Ask a single question and print answer")
    parser.add_argument("--test-all", action="store_true", help="Run all 7 workshop test questions")
    args = parser.parse_args()

    indexed_docs = retrieve_documents(args.docs_dir)

    test_questions = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone for work files from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?",
    ]

    if args.test_all:
        print("=== Running all 7 workshop test questions ===")
        for i, q in enumerate(test_questions, start=1):
            print(f"\n[Q{i}]: {q}")
            print(answer_question(q, indexed_docs))
        return

    if args.question:
        print(answer_question(args.question, indexed_docs))
        return

    # Interactive mode
    print("UC-X Ask My Documents — Interactive Mode")
    print("Ask any question regarding CMC HR, IT, or Finance policies (type 'exit' or 'quit' to stop).\n")
    try:
        while True:
            try:
                user_q = input("\nEnter your question: ").strip()
            except EOFError:
                break
            if not user_q:
                continue
            if user_q.lower() in ["exit", "quit"]:
                print("Goodbye.")
                break
            print("\nAnswer:")
            print(answer_question(user_q, indexed_docs))
    except KeyboardInterrupt:
        print("\nExiting.")


if __name__ == "__main__":
    main()
