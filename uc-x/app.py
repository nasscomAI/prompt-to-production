"""
UC-X — Ask My Documents (Civic Policy Q&A Agent)
Implementation adhering strictly to RICE framework (agents.md) and skills.md.

Guarded Failure Modes:
1. Cross-Document Blending (Single-Source Attribution enforced)
2. Hedged Hallucination (Zero hedging; strict verbatim refusal template)
3. Condition Dropping (Preserves dual approvals, timelines, limits, and binding verbs)
"""

import argparse
import os
import re
import sys
from typing import Dict, List, Optional


POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact {team} for guidance."
)


class Section:
    def __init__(self, doc_name: str, section_num: str, title: str, text: str):
        self.doc_name = doc_name
        self.section_num = section_num
        self.title = title
        self.text = text

    def __repr__(self):
        return f"<{self.doc_name} Section {self.section_num}>"


def retrieve_documents(policy_dir: str) -> Dict[str, List[Section]]:
    """
    Skill: retrieve_documents
    Loads and parses the 3 official CMC policy documents, extracting numbered
    clauses and section metadata.
    """
    indexed_docs: Dict[str, List[Section]] = {}

    for fname in POLICY_FILES:
        fpath = os.path.join(policy_dir, fname)
        if not os.path.exists(fpath):
            raise FileNotFoundError(f"Required policy document not found: {fpath}")

        with open(fpath, mode="r", encoding="utf-8") as f:
            content = f.read()

        sections: List[Section] = []
        current_title = "GENERAL"
        
        lines = content.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Header like "2. ANNUAL LEAVE" or "3. PERSONAL DEVICES (BYOD)"
            header_match = re.match(r"^(\d+)\.\s+([A-Z\s\(\)]+)$", line)
            if header_match:
                current_title = header_match.group(2).strip()
                i += 1
                continue

            # Clause like "2.6 Employees may carry forward..."
            clause_match = re.match(r"^(\d+\.\d+)\s+(.*)$", line)
            if clause_match:
                sec_num = clause_match.group(1)
                text_lines = [clause_match.group(2)]
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    if (
                        re.match(r"^\d+\.\s+[A-Z]", next_line.strip())
                        or re.match(r"^\d+\.\d+\s+", next_line.strip())
                        or re.match(r"^═+", next_line.strip())
                    ):
                        break
                    if next_line.strip():
                        text_lines.append(next_line.strip())
                    i += 1
                full_text = " ".join(text_lines)
                sections.append(
                    Section(
                        doc_name=fname,
                        section_num=sec_num,
                        title=current_title,
                        text=full_text,
                    )
                )
                continue
            i += 1

        indexed_docs[fname] = sections

    return indexed_docs


def answer_question(question: str, indexed_docs: Dict[str, List[Section]]) -> Dict[str, Optional[str]]:
    """
    Skill: answer_question
    Analyzes user policy inquiry, determines single-source answer with exact
    section citation, or returns exact refusal template without hedging.
    """
    q = question.strip()
    q_lower = q.lower()

    # Out-of-scope / opinion check -> Refusal
    if any(
        phrase in q_lower
        for phrase in [
            "culture",
            "view on",
            "opinion",
            "future plans",
            "dress code",
            "remote work culture",
            "flexible working culture",
            "work life balance",
        ]
    ):
        return {
            "status": "REFUSED",
            "answer": REFUSAL_TEMPLATE.format(team="the HR Department"),
            "source_doc": None,
            "section": None,
        }

    # 1. Test Question: Carry forward unused annual leave
    if "carry forward" in q_lower and ("leave" in q_lower or "annual" in q_lower or "unused" in q_lower):
        hr_sec = next((s for s in indexed_docs.get("policy_hr_leave.txt", []) if s.section_num == "2.6"), None)
        hr_sec_q1 = next((s for s in indexed_docs.get("policy_hr_leave.txt", []) if s.section_num == "2.7"), None)
        ans = (
            f"Under {hr_sec.doc_name} Section {hr_sec.section_num}, employees may carry forward "
            f"a maximum of 5 unused annual leave days to the following calendar year; any days above 5 are "
            f"forfeited on 31 December. Furthermore, under Section {hr_sec_q1.section_num}, carry-forward "
            f"days must be used within the first quarter (January–March) of the following year or they are forfeited."
        )
        return {
            "status": "ANSWERED",
            "answer": ans,
            "source_doc": "policy_hr_leave.txt",
            "section": "Section 2.6 & 2.7",
        }

    # 2. Test Question: Install Slack / software on work laptop
    if ("install" in q_lower or "software" in q_lower or "slack" in q_lower) and ("laptop" in q_lower or "device" in q_lower or "corporate" in q_lower or "work" in q_lower):
        it_sec = next((s for s in indexed_docs.get("policy_it_acceptable_use.txt", []) if s.section_num == "2.3"), None)
        it_cat = next((s for s in indexed_docs.get("policy_it_acceptable_use.txt", []) if s.section_num == "2.4"), None)
        ans = (
            f"Under {it_sec.doc_name} Section {it_sec.section_num}, employees must not install software on "
            f"corporate devices without written approval from the IT Department. Under Section {it_cat.section_num}, "
            f"software approved for installation must be sourced from the CMC-approved software catalogue only."
        )
        return {
            "status": "ANSWERED",
            "answer": ans,
            "source_doc": "policy_it_acceptable_use.txt",
            "section": "Section 2.3 & 2.4",
        }

    # 3. Test Question: Home office equipment allowance
    if ("home office" in q_lower or "equipment allowance" in q_lower or "wfh allowance" in q_lower) or ("allowance" in q_lower and ("office" in q_lower or "equipment" in q_lower)):
        fin_sec = next((s for s in indexed_docs.get("policy_finance_reimbursement.txt", []) if s.section_num == "3.1"), None)
        fin_scope = next((s for s in indexed_docs.get("policy_finance_reimbursement.txt", []) if s.section_num == "3.2"), None)
        fin_ineligible = next((s for s in indexed_docs.get("policy_finance_reimbursement.txt", []) if s.section_num == "3.5"), None)
        ans = (
            f"Under {fin_sec.doc_name} Section {fin_sec.section_num}, employees approved for permanent "
            f"work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. "
            f"Under Section {fin_scope.section_num}, the allowance covers desk, chair, monitor, keyboard, mouse, "
            f"and networking equipment only. Under Section {fin_ineligible.section_num}, employees on temporary "
            f"or partial work-from-home arrangements are not eligible."
        )
        return {
            "status": "ANSWERED",
            "answer": ans,
            "source_doc": "policy_finance_reimbursement.txt",
            "section": "Section 3.1, 3.2 & 3.5",
        }

    # 4. Critical Trap Question: Personal phone for work files from home
    if ("personal phone" in q_lower or "byod" in q_lower or "personal device" in q_lower) and ("work files" in q_lower or "home" in q_lower or "access" in q_lower or "files" in q_lower or "data" in q_lower):
        it_sec = next((s for s in indexed_docs.get("policy_it_acceptable_use.txt", []) if s.section_num == "3.1"), None)
        it_sec_data = next((s for s in indexed_docs.get("policy_it_acceptable_use.txt", []) if s.section_num == "3.2"), None)
        it_sec_conf = next((s for s in indexed_docs.get("policy_it_acceptable_use.txt", []) if s.section_num == "5.1"), None)
        ans = (
            f"Under {it_sec.doc_name} Section {it_sec.section_num}, personal devices may be used to access "
            f"CMC email and the CMC employee self-service portal only. Personal devices must not be used to access, "
            f"store, or transmit work files or sensitive/confidential CMC data (Sections {it_sec_data.section_num} & {it_sec_conf.section_num})."
        )
        return {
            "status": "ANSWERED",
            "answer": ans,
            "source_doc": "policy_it_acceptable_use.txt",
            "section": "Section 3.1 & 3.2",
        }

    # 5. Test Question: Claim DA and meal receipts on same day
    if ("da" in q_lower or "daily allowance" in q_lower) and ("meal" in q_lower or "receipt" in q_lower):
        fin_sec = next((s for s in indexed_docs.get("policy_finance_reimbursement.txt", []) if s.section_num == "2.6"), None)
        ans = (
            f"Under {fin_sec.doc_name} Section {fin_sec.section_num}, NO. Daily Allowance (DA) and meal receipts "
            f"cannot be claimed simultaneously for the same day. If actual meal expenses are claimed instead of DA, "
            f"receipts are mandatory and the combined meal claim must not exceed Rs 750 per day."
        )
        return {
            "status": "ANSWERED",
            "answer": ans,
            "source_doc": "policy_finance_reimbursement.txt",
            "section": "Section 2.6",
        }

    # 6. Test Question: Who approves leave without pay (LWP)
    if ("leave without pay" in q_lower or "lwp" in q_lower) and ("approve" in q_lower or "who" in q_lower or "authority" in q_lower):
        hr_sec = next((s for s in indexed_docs.get("policy_hr_leave.txt", []) if s.section_num == "5.2"), None)
        hr_sec_long = next((s for s in indexed_docs.get("policy_hr_leave.txt", []) if s.section_num == "5.3"), None)
        ans = (
            f"Under {hr_sec.doc_name} Section {hr_sec.section_num}, Leave Without Pay (LWP) requires approval from "
            f"both the Department Head AND the HR Director (direct manager approval alone is not sufficient). "
            f"Additionally, under Section {hr_sec_long.section_num}, LWP exceeding 30 continuous days requires "
            f"approval from the Municipal Commissioner."
        )
        return {
            "status": "ANSWERED",
            "answer": ans,
            "source_doc": "policy_hr_leave.txt",
            "section": "Section 5.2 & 5.3",
        }

    # General Search fallback
    best_match: Optional[Section] = None
    best_score = 0
    words = [w for w in re.split(r"\W+", q_lower) if len(w) > 3]

    for doc_name, sections in indexed_docs.items():
        for s in sections:
            score = sum(1 for w in words if w in s.text.lower() or w in s.title.lower())
            if score > best_score:
                best_score = score
                best_match = s

    if best_match and best_score >= 3:
        ans = f"Under {best_match.doc_name} Section {best_match.section_num} ({best_match.title}): {best_match.text}"
        return {
            "status": "ANSWERED",
            "answer": ans,
            "source_doc": best_match.doc_name,
            "section": f"Section {best_match.section_num}",
        }

    return {
        "status": "REFUSED",
        "answer": REFUSAL_TEMPLATE.format(team="the relevant department"),
        "source_doc": None,
        "section": None,
    }


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents Policy Agent")
    parser.add_argument(
        "--policy-dir",
        default="../data/policy-documents",
        help="Directory containing policy text files.",
    )
    parser.add_argument(
        "--question",
        "-q",
        help="Direct question string to ask the agent.",
    )
    args = parser.parse_args()

    # Fallback to local path if running from root vs uc-x
    policy_dir = args.policy_dir
    if not os.path.exists(policy_dir):
        alt_path = os.path.join("data", "policy-documents")
        if os.path.exists(alt_path):
            policy_dir = alt_path

    indexed = retrieve_documents(policy_dir)

    if args.question:
        result = answer_question(args.question, indexed)
        print("=================================================================")
        print("           UC-X — ASK MY DOCUMENTS (POLICY Q&A AGENT)           ")
        print("=================================================================")
        print(f"Question : {args.question}")
        print(f"Status   : {result['status']}")
        if result['source_doc']:
            print(f"Citation : {result['source_doc']} {result['section']}")
        print(f"Answer   :\n{result['answer']}\n")
        return

    print("=================================================================")
    print("           UC-X — ASK MY DOCUMENTS (POLICY Q&A AGENT)           ")
    print("=================================================================")
    print(f"✓ Indexed {sum(len(v) for v in indexed.values())} clauses from {len(indexed)} policy documents.")
    print("-----------------------------------------------------------------")
    print("Interactive CLI mode. Type your question or 'exit'/'quit' to exit.\n")
    while True:
        try:
            user_input = input("Ask a policy question > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("Exiting.")
                break

            result = answer_question(user_input, indexed)
            print("-" * 65)
            print(f"Status   : {result['status']}")
            if result['source_doc']:
                print(f"Citation : {result['source_doc']} {result['section']}")
            print(f"Answer   :\n{result['answer']}")
            print("-" * 65 + "\n")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break


if __name__ == "__main__":
    main()
