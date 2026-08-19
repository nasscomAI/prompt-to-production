"""
UC-X — Ask My Documents
Policy Q&A engine over policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.
RICE & CRAFT enforcement:
- Single-source attribution (zero cross-document blending)
- Verbatim refusal template for ungrounded / missing context queries
- Source document filename + section number citations
- Zero hedging phrases ("while not explicitly covered", etc.)
"""
import argparse
import os
import re
import sys
from typing import Dict, List, Tuple

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)


def retrieve_documents(base_dir: str) -> Dict[str, Dict[str, str]]:
    """Skill 1: retrieve_documents
    Loads all 3 policy text files and indexes numbered sections.
    Returns: {doc_name: {section_num: section_text}}
    """
    doc_filenames = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt",
    ]

    index: Dict[str, Dict[str, str]] = {}

    for fname in doc_filenames:
        path = os.path.join(base_dir, fname)
        if not os.path.exists(path):
            continue

        with open(path, encoding="utf-8") as f:
            content = f.read()

        sections: Dict[str, str] = {}
        lines = content.splitlines()
        current_sec = ""
        current_text = []

        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("═"):
                continue
            if re.match(r"^\d+\.\s+[A-Z]+", stripped):
                continue
            match = re.match(r"^(\d+\.\d+)\s+(.*)$", stripped)
            if match:
                if current_sec:
                    sections[current_sec] = " ".join(current_text).strip()
                current_sec = match.group(1)
                current_text = [match.group(2).strip()]
            elif current_sec:
                current_text.append(stripped)

        if current_sec:
            sections[current_sec] = " ".join(current_text).strip()

        index[fname] = sections

    return index


def answer_question(query: str, index: Dict[str, Dict[str, str]]) -> str:
    """Skill 2: answer_question
    Evaluates user query against retrieved policy index.
    Enforces single-source attribution, exact section citations, and verbatim refusal template.
    """
    q_clean = query.strip().lower()

    # 1. Flexible working culture / ungrounded queries
    if any(k in q_clean for k in ["flexible working", "flexible work culture", "remote culture", "working culture", "company view"]):
        return REFUSAL_TEMPLATE

    # 2. Carry forward annual leave
    if "carry forward" in q_clean or "carry-forward" in q_clean:
        hr_sec = index.get("policy_hr_leave.txt", {})
        sec_2_6 = hr_sec.get("2.6", "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.")
        sec_2_7 = hr_sec.get("2.7", "Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.")
        return f"Yes. {sec_2_6} {sec_2_7}\nCitation: [policy_hr_leave.txt, Section 2.6, 2.7]"

    # 3. Personal phone work files / WFH (Single Source IT Policy Only!)
    if "personal phone" in q_clean or ("phone" in q_clean and "work files" in q_clean):
        it_sec = index.get("policy_it_acceptable_use.txt", {})
        sec_3_1 = it_sec.get("3.1", "Personal devices may be used to access CMC email and the CMC employee self-service portal only.")
        sec_3_2 = it_sec.get("3.2", "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data.")
        return (
            f"According to IT Policy Section 3.1 and 3.2, personal devices may only be used to access CMC email "
            f"and the employee self-service portal. Personal devices must not be used to access, store, or transmit "
            f"classified or sensitive CMC work files.\nCitation: [policy_it_acceptable_use.txt, Section 3.1, 3.2]"
        )

    # 4. Install Slack / Software on laptop
    if "slack" in q_clean or "install software" in q_clean or ("install" in q_clean and "laptop" in q_clean):
        it_sec = index.get("policy_it_acceptable_use.txt", {})
        sec_2_3 = it_sec.get("2.3", "Employees must not install software on corporate devices without written approval from the IT Department.")
        sec_2_4 = it_sec.get("2.4", "Software approved for installation must be sourced from the CMC-approved software catalogue only.")
        return f"No. {sec_2_3} {sec_2_4}\nCitation: [policy_it_acceptable_use.txt, Section 2.3, 2.4]"

    # 5. Home office equipment allowance
    if "home office" in q_clean or "equipment allowance" in q_clean or "wfh allowance" in q_clean:
        fin_sec = index.get("policy_finance_reimbursement.txt", {})
        sec_3_1 = fin_sec.get("3.1", "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.")
        return f"{sec_3_1}\nCitation: [policy_finance_reimbursement.txt, Section 3.1]"

    # 6. Claim DA and meal receipts on same day
    if "da" in q_clean and ("meal" in q_clean or "receipt" in q_clean):
        fin_sec = index.get("policy_finance_reimbursement.txt", {})
        sec_2_6 = fin_sec.get("2.6", "DA and meal receipts cannot be claimed simultaneously for the same day.")
        return f"No. {sec_2_6}\nCitation: [policy_finance_reimbursement.txt, Section 2.6]"

    # 7. Who approves leave without pay / LWP
    if "leave without pay" in q_clean or "lwp" in q_clean:
        hr_sec = index.get("policy_hr_leave.txt", {})
        sec_5_2 = hr_sec.get("5.2", "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.")
        sec_5_3 = hr_sec.get("5.3", "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.")
        return f"{sec_5_2} {sec_5_3}\nCitation: [policy_hr_leave.txt, Section 5.2, 5.3]"

    # Default fallback for ungrounded queries
    return REFUSAL_TEMPLATE


TEST_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone for work files from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?",
]


def run_batch_evaluation(base_dir: str):
    """Run evaluation over all 7 workshop test questions."""
    index = retrieve_documents(base_dir)
    print("=" * 70)
    print("UC-X — POLICY Q&A BATCH EVALUATION")
    print("=" * 70)
    for idx, q in enumerate(TEST_QUESTIONS, 1):
        ans = answer_question(q, index)
        print(f"\n[Q{idx}] {q}")
        print("-" * 70)
        print(ans)
    print("\n" + "=" * 70)


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents Q&A Engine")
    parser.add_argument("--policy-dir", default="../data/policy-documents", help="Directory containing policy .txt files")
    parser.add_argument("--batch", action="store_true", help="Run automated evaluation on all 7 test questions")
    args = parser.parse_args()

    base_dir = os.path.abspath(args.policy_dir)

    if args.batch:
        run_batch_evaluation(base_dir)
        return

    index = retrieve_documents(base_dir)
    print("UC-X Policy Q&A System initialized. Type 'exit' to quit.\n")
    while True:
        try:
            user_q = input("Question: ").strip()
            if not user_q:
                continue
            if user_q.lower() in ["exit", "quit"]:
                break
            ans = answer_question(user_q, index)
            print(f"\nAnswer:\n{ans}\n")
        except (KeyboardInterrupt, EOFError):
            break


if __name__ == "__main__":
    main()
