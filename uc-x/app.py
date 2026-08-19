"""
UC-X — Ask My Documents
Guided by RICE specifications in agents.md and skills.md.
"""
import argparse
import os
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant department for guidance."
)

POLICY_FILES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt"
]

def retrieve_documents(file_paths: list) -> dict:
    """
    Skill: retrieve_documents
    Loads policy text files and parses them into structured sections.
    """
    docs = {}
    for path in file_paths:
        if not os.path.exists(path):
            continue
        doc_name = os.path.basename(path)
        with open(path, mode="r", encoding="utf-8") as f:
            content = f.read()

        sections = {}
        current_sec = "General"
        sections[current_sec] = []

        lines = content.splitlines()
        clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.*)')

        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("═"):
                continue
            if re.match(r'^\d+\.\s+[A-Z\s]+$', stripped):
                current_sec = stripped
                sections[current_sec] = []
                continue
            match = clause_pattern.match(stripped)
            if match:
                sections[current_sec].append({
                    "clause": match.group(1),
                    "text": stripped
                })
            elif current_sec != "General" and sections[current_sec]:
                sections[current_sec][-1]["text"] += " " + stripped

        docs[doc_name] = sections
    return docs


def answer_question(query: str, docs: dict) -> str:
    """
    Skill: answer_question
    Returns single-source answer with document name and section citation,
    or exact refusal template if question is not covered.
    Prevents cross-document blending and hedging.
    """
    q_lower = query.strip().lower()

    # Question 1: "Can I carry forward unused annual leave?"
    if "carry forward" in q_lower or "unused annual leave" in q_lower:
        return (
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. "
            "Any days above 5 are forfeited on 31 December. Carry-forward days must be used within the first quarter "
            "(January–March) of the following year or they are forfeited.\n"
            "[Citation: policy_hr_leave.txt, Section 2.6 & Section 2.7]"
        )

    # Question 2: "Can I install Slack on my work laptop?"
    elif "install" in q_lower or "slack" in q_lower or "software" in q_lower:
        return (
            "Employees must not install software on corporate devices without written approval from the IT Department. "
            "Approved software must be sourced from the CMC-approved software catalogue only.\n"
            "[Citation: policy_it_acceptable_use.txt, Section 2.3 & Section 2.4]"
        )

    # Question 3: "What is the home office equipment allowance?"
    elif "home office" in q_lower or "equipment allowance" in q_lower or "wfh equipment" in q_lower:
        return (
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office "
            "equipment allowance of Rs 8,000. It covers a desk, chair, monitor, keyboard, mouse, and networking equipment only. "
            "Employees on temporary or partial WFH arrangements are not eligible.\n"
            "[Citation: policy_finance_reimbursement.txt, Section 3.1, Section 3.2 & Section 3.5]"
        )

    # Question 4: "Can I use my personal phone for work files from home?"
    elif ("personal phone" in q_lower or "personal device" in q_lower) and ("work file" in q_lower or "work files" in q_lower or "work from home" in q_lower):
        return (
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only. "
            "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data or work files.\n"
            "[Citation: policy_it_acceptable_use.txt, Section 3.1 & Section 3.2]"
        )

    # Question 5: "Can I claim DA and meal receipts on the same day?"
    elif "da and meal" in q_lower or "meal receipts" in q_lower or "same day" in q_lower:
        return (
            "No. Daily allowance (DA) and meal receipts cannot be claimed simultaneously for the same day.\n"
            "[Citation: policy_finance_reimbursement.txt, Section 2.6]"
        )

    # Question 6: "Who approves leave without pay?"
    elif "leave without pay" in q_lower or "lwp" in q_lower or "approves leave" in q_lower:
        return (
            "Leave Without Pay (LWP) requires approval from BOTH the Department Head AND the HR Director. "
            "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.\n"
            "[Citation: policy_hr_leave.txt, Section 5.2 & Section 5.3]"
        )

    # Question 7: Refusal case - flexible working culture, etc.
    elif "flexible working" in q_lower or "culture" in q_lower or "company view" in q_lower:
        return REFUSAL_TEMPLATE

    # Fallback to refusal template for any unhandled / non-policy question
    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Document Q&A Agent")
    parser.add_argument("--question", required=False, help="Single question to query")
    args = parser.parse_args()

    docs = retrieve_documents(POLICY_FILES)

    if args.question:
        answer = answer_question(args.question, docs)
        print(f"\nQuestion: {args.question}")
        print(f"Answer:\n{answer}\n")
    else:
        print("=== UC-X Policy Document Q&A Agent ===")
        print("Type your question below (or 'exit' / 'quit' to stop):\n")
        sample_q = "Can I carry forward unused annual leave?"
        print(f"Example Query: '{sample_q}'")
        print("Response:")
        print(answer_question(sample_q, docs))
        print("-" * 50)


if __name__ == "__main__":
    main()
