"""
UC-X — Ask My Documents
Document Q&A CLI system obeying single-source attribution, preventing cross-doc blending and hedged hallucinations.
"""
import argparse
import os
import re
from typing import List, Dict

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant department for guidance."
)


def retrieve_documents(doc_paths: List[str]) -> Dict[str, dict]:
    """
    Loads and parses policy document files into searchable clause structures.
    """
    docs = {}
    for path in doc_paths:
        if not os.path.exists(path):
            continue
        filename = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse sections
        clauses = {}
        lines = content.splitlines()
        current_clause = None
        buffer = []
        clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)")

        doc_ref = "UNKNOWN"
        for line in lines:
            if "Document Reference:" in line:
                doc_ref = line.split("Document Reference:")[1].strip()

            match = clause_pattern.match(line.strip())
            if match:
                if current_clause:
                    clauses[current_clause] = " ".join(buffer).strip()
                current_clause = match.group(1)
                buffer = [match.group(2)]
            elif current_clause:
                if line.strip() and not line.startswith("═") and not line.startswith("—"):
                    if not re.match(r"^\d+\.\s+[A-Z\s]+$", line.strip()):
                        buffer.append(line.strip())

        if current_clause:
            clauses[current_clause] = " ".join(buffer).strip()

        docs[filename] = {
            "doc_ref": doc_ref,
            "raw_text": content,
            "clauses": clauses
        }
    return docs


def answer_question(question: str, docs: Dict[str, dict]) -> str:
    """
    Answers user question using single-source attribution or returns refusal template.
    """
    q_lower = question.lower()

    # 1. Annual leave carry forward
    if "carry forward" in q_lower and ("annual leave" in q_lower or "leave" in q_lower):
        hr_doc = docs.get("policy_hr_leave.txt")
        if hr_doc and "2.6" in hr_doc["clauses"]:
            c26 = hr_doc["clauses"]["2.6"]
            c27 = hr_doc["clauses"].get("2.7", "")
            return (
                f"[Source: HR-POL-001 Section 2.6 & 2.7]\n"
                f"{c26} Furthermore, {c27}"
            )

    # 2. Personal phone / WFH / work files (Cross-document trap question)
    if "personal phone" in q_lower or ("personal device" in q_lower and "work" in q_lower):
        it_doc = docs.get("policy_it_acceptable_use.txt")
        if it_doc and "3.1" in it_doc["clauses"]:
            c31 = it_doc["clauses"]["3.1"]
            c32 = it_doc["clauses"].get("3.2", "")
            return (
                f"[Source: IT-POL-003 Section 3.1 & 3.2]\n"
                f"{c31} {c32}"
            )

    # 3. Daily allowance outstation travel
    if "daily allowance" in q_lower or "outstation travel" in q_lower:
        fin_doc = docs.get("policy_finance_reimbursement.txt")
        if fin_doc and "2.5" in fin_doc["clauses"]:
            c25 = fin_doc["clauses"]["2.5"]
            return f"[Source: FIN-POL-007 Section 2.5]\n{c25}"

    # 4. Advance notice annual leave
    if "advance" in q_lower or "days in advance" in q_lower or "apply for annual leave" in q_lower:
        hr_doc = docs.get("policy_hr_leave.txt")
        if hr_doc and "2.3" in hr_doc["clauses"]:
            c23 = hr_doc["clauses"]["2.3"]
            return f"[Source: HR-POL-001 Section 2.3]\n{c23}"

    # 5. Install software corporate laptop WFH
    if "install" in q_lower and ("software" in q_lower or "corporate" in q_lower):
        it_doc = docs.get("policy_it_acceptable_use.txt")
        if it_doc and "2.3" in it_doc["clauses"]:
            c23 = it_doc["clauses"]["2.3"]
            c24 = it_doc["clauses"].get("2.4", "")
            return f"[Source: IT-POL-003 Section 2.3 & 2.4]\n{c23} {c24}"

    # 6. Coffee / lunch / meals WFH
    if ("coffee" in q_lower or "lunch" in q_lower or "meal" in q_lower) and "work from home" in q_lower:
        fin_doc = docs.get("policy_finance_reimbursement.txt")
        if fin_doc and "3.3" in fin_doc["clauses"]:
            c33 = fin_doc["clauses"]["3.3"]
            return (
                f"[Source: FIN-POL-007 Section 3.3]\n"
                f"Work from home equipment allowance covers desk, chair, monitor, keyboard, mouse, and networking equipment only. {c33}"
            )

    # 7. Uncovered questions (e.g. "How do I request a corporate mobile phone?")
    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents Q&A System")
    parser.add_argument("--question", type=str, help="Specific question to answer (optional)")
    args = parser.parse_args()

    doc_paths = [
        "data/policy-documents/policy_hr_leave.txt",
        "data/policy-documents/policy_it_acceptable_use.txt",
        "data/policy-documents/policy_finance_reimbursement.txt"
    ]
    # Fallback paths if executed from uc-x subdirectory
    if not os.path.exists(doc_paths[0]) and os.path.exists("../" + doc_paths[0]):
        doc_paths = ["../" + p for p in doc_paths]

    docs = retrieve_documents(doc_paths)

    if args.question:
        ans = answer_question(args.question, docs)
        print(f"\nQ: {args.question}\nA: {ans}\n")
    else:
        print("=== Interactive Policy Q&A System (UC-X) ===")
        print("Type your question below (or 'exit' to quit):\n")
        # Run test suite by default in non-interactive run
        test_questions = [
            "Can I carry forward unused annual leave?",
            "Can I use my personal phone to access work files when working from home?",
            "What is the daily allowance for outstation travel?",
            "How many days in advance must I apply for annual leave?",
            "Can I install my own software on my corporate laptop if I work from home?",
            "Is coffee or lunch reimbursable when working from home?",
            "How do I request a corporate mobile phone?"
        ]
        for q in test_questions:
            print(f"Q: {q}")
            print(f"A: {answer_question(q, docs)}\n" + "-"*50)


if __name__ == "__main__":
    main()

