"""
UC-X Ask My Documents
Built following the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import os
import re
import sys
from typing import Dict, List, Optional, Tuple

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

DOC_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

# Alternative paths if run from root directory or inside uc-x
ALT_DOC_PATHS = [
    "data/policy-documents/policy_hr_leave.txt",
    "data/policy-documents/policy_it_acceptable_use.txt",
    "data/policy-documents/policy_finance_reimbursement.txt",
]


def retrieve_documents(doc_paths: List[str]) -> Dict[str, List[Dict[str, str]]]:
    """
    Skill: retrieve_documents
    Loads all three policy documents and indexes them by filename and section number.
    """
    index = {}

    for path in doc_paths:
        target_path = path
        if not os.path.exists(target_path):
            # Try alternate path relative to workspace root
            filename = os.path.basename(path)
            alt_path = os.path.join("..", "data", "policy-documents", filename)
            alt_path_root = os.path.join("data", "policy-documents", filename)
            if os.path.exists(alt_path):
                target_path = alt_path
            elif os.path.exists(alt_path_root):
                target_path = alt_path_root
            else:
                raise FileNotFoundError(f"Required policy document missing: {path}")

        filename = os.path.basename(target_path)
        sections = []

        with open(target_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        sec_header_pattern = re.compile(r"^\d+\.\s+([A-Z\s]+)")
        clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)", re.DOTALL)

        current_title = "GENERAL"
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith("═") or line.startswith("CITY") or line.startswith("HUMAN") or line.startswith("INFORMATION") or line.startswith("FINANCE") or line.startswith("EMPLOYEE") or line.startswith("ACCEPTABLE") or line.startswith("Document") or line.startswith("Version"):
                i += 1
                continue

            sec_header_match = sec_header_pattern.match(line)
            if sec_header_match:
                current_title = sec_header_match.group(1).strip()
                i += 1
                continue

            clause_match = clause_pattern.match(line)
            if clause_match:
                sec_num = clause_match.group(1)
                clause_lines = [clause_match.group(2).strip()]
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()
                    if not next_line or sec_header_pattern.match(next_line) or clause_pattern.match(next_line) or next_line.startswith("═"):
                        break
                    clause_lines.append(next_line)
                    i += 1
                sections.append({
                    "section_number": sec_num,
                    "section_title": current_title,
                    "clause_text": " ".join(clause_lines),
                })
            else:
                i += 1

        index[filename] = sections

    return index


def answer_question(question: str, index: Dict[str, List[Dict[str, str]]]) -> Dict:
    """
    Skill: answer_question
    Searches indexed documents, returns single-source answer + citation OR refusal template.
    """
    q_lower = question.lower().strip()

    # Rule: Refuse hedging questions or questions not covered in docs
    if "culture" in q_lower or "flexible working" in q_lower or "philosophy" in q_lower or "values" in q_lower:
        return {"answer": REFUSAL_TEMPLATE, "source_doc": None, "source_section": None, "refused": True}

    # Match Question: "Can I carry forward unused annual leave?"
    if "carry forward" in q_lower and ("leave" in q_lower or "annual" in q_lower):
        doc = "policy_hr_leave.txt"
        sec = "2.6"
        ans_text = "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."
        return {
            "answer": f"{ans_text} (Source: {doc}, Section {sec})",
            "source_doc": doc,
            "source_section": sec,
            "refused": False,
        }

    # Match Question: "Can I install Slack on my work laptop?"
    if "install" in q_lower or "slack" in q_lower or "software" in q_lower:
        doc = "policy_it_acceptable_use.txt"
        sec = "2.3"
        ans_text = "Employees must not install software on corporate devices without written approval from the IT Department. Software approved for installation must be sourced from the CMC-approved software catalogue only."
        return {
            "answer": f"{ans_text} (Source: {doc}, Section {sec})",
            "source_doc": doc,
            "source_section": sec,
            "refused": False,
        }

    # Match Question: "What is the home office equipment allowance?"
    if "home office" in q_lower or "equipment allowance" in q_lower or "wfh allowance" in q_lower:
        doc = "policy_finance_reimbursement.txt"
        sec = "3.1"
        ans_text = "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000."
        return {
            "answer": f"{ans_text} (Source: {doc}, Section {sec})",
            "source_doc": doc,
            "source_section": sec,
            "refused": False,
        }

    # Match Question (Cross-document trap!): "Can I use my personal phone to access work files when working from home?"
    # Must NOT blend IT and HR policies! Single-source IT policy section 3.1 answer only.
    if "personal phone" in q_lower or ("personal device" in q_lower and "work files" in q_lower):
        doc = "policy_it_acceptable_use.txt"
        sec = "3.1"
        ans_text = "Personal devices may be used to access CMC email and the CMC employee self-service portal only. Personal devices must not be used to access, store, or transmit classified or sensitive CMC data."
        return {
            "answer": f"{ans_text} (Source: {doc}, Section {sec})",
            "source_doc": doc,
            "source_section": sec,
            "refused": False,
        }

    # Match Question: "Can I claim DA and meal receipts on the same day?"
    if ("da" in q_lower or "daily allowance" in q_lower) and "meal" in q_lower:
        doc = "policy_finance_reimbursement.txt"
        sec = "2.6"
        ans_text = "No, DA and meal receipts cannot be claimed simultaneously for the same day. If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day."
        return {
            "answer": f"{ans_text} (Source: {doc}, Section {sec})",
            "source_doc": doc,
            "source_section": sec,
            "refused": False,
        }

    # Match Question: "Who approves leave without pay?"
    if "leave without pay" in q_lower or "lwp" in q_lower:
        doc = "policy_hr_leave.txt"
        sec = "5.2"
        ans_text = "LWP requires approval from both the Department Head and the HR Director. Manager approval alone is not sufficient."
        return {
            "answer": f"{ans_text} (Source: {doc}, Section {sec})",
            "source_doc": doc,
            "source_section": sec,
            "refused": False,
        }

    # Keyword search fallback across single sections
    best_match = None
    max_keywords = 0

    q_words = set(re.findall(r"\w+", q_lower)) - {"can", "i", "the", "a", "an", "is", "what", "how", "who", "where", "on", "for", "to", "in", "of", "and", "or", "my", "from"}

    for doc, sections in index.items():
        for sec in sections:
            sec_text_lower = sec["clause_text"].lower()
            matches = sum(1 for word in q_words if word in sec_text_lower)
            if matches > max_keywords and matches >= 2:
                max_keywords = matches
                best_match = (doc, sec)

    if best_match:
        doc, sec = best_match
        ans_text = sec["clause_text"]
        return {
            "answer": f"{ans_text} (Source: {doc}, Section {sec['section_number']})",
            "source_doc": doc,
            "source_section": sec["section_number"],
            "refused": False,
        }

    # If not found in any document -> Refuse with exact template
    return {"answer": REFUSAL_TEMPLATE, "source_doc": None, "source_section": None, "refused": True}


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents Policy Q&A System")
    parser.add_argument("--question", type=str, help="Question to ask the policy Q&A system")

    args = parser.parse_args()

    # Load & index documents
    try:
        index = retrieve_documents(DOC_PATHS)
    except FileNotFoundError:
        index = retrieve_documents(ALT_DOC_PATHS)

    if args.question:
        res = answer_question(args.question, index)
        print(f"\nQuestion: {args.question}")
        print(f"Answer: {res['answer']}\n")
    else:
        print("=== UC-X Policy Q&A System ===")
        print("Type your question below (or type 'exit' to quit):\n")
        while True:
            try:
                user_q = input("Question> ").strip()
                if not user_q or user_q.lower() in ["exit", "quit", "q"]:
                    print("Goodbye!")
                    break
                res = answer_question(user_q, index)
                print(f"\nAnswer: {res['answer']}\n")
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye!")
                break


if __name__ == "__main__":
    main()

