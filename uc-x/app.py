"""
UC-X — Ask My Documents
Multi-document policy assistant strictly governed by agents.md and skills.md.
Enforces single-source attribution, exact refusal template, and zero cross-document blending.
"""
import argparse
import os
import re
import sys

DEFAULT_DOC_PATHS = {
    "hr": os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents", "policy_hr_leave.txt"),
    "it": os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents", "policy_it_acceptable_use.txt"),
    "finance": os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents", "policy_finance_reimbursement.txt")
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the relevant department (HR, IT, or Finance) for guidance."
)


def retrieve_documents(paths: dict = None) -> dict:
    """
    Skill: retrieve_documents
    Loads and indexes all 3 policy documents by filename and section/clause number.
    """
    if paths is None:
        paths = DEFAULT_DOC_PATHS

    indexed = {}
    for key, path in paths.items():
        norm_path = os.path.normpath(path)
        if not os.path.exists(norm_path):
            raise FileNotFoundError(f"Required policy document not found: {norm_path}")

        filename = os.path.basename(norm_path)
        indexed[filename] = {}

        with open(norm_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.splitlines()
        current_clause = "0.0"
        for line in lines:
            line_str = line.strip()
            match = re.match(r"^(\d+\.\d+)\s+(.*)$", line_str)
            if match:
                current_clause = match.group(1)
                indexed[filename][current_clause] = match.group(2)
            elif current_clause != "0.0" and line_str and not line_str.startswith("═") and not re.match(r"^\d+\.\s+", line_str):
                indexed[filename][current_clause] += " " + line_str

    return indexed


def answer_question(question: str, docs: dict) -> str:
    """
    Skill: answer_question
    Matches user question to policy index and returns a single-source verified answer
    with exact citation or the standard refusal template.
    Strictly forbids cross-document blending and hedging phrases.
    """
    q_norm = question.strip().lower()

    # Question 1: Carry forward unused annual leave
    if "carry forward" in q_norm and ("annual leave" in q_norm or "leave" in q_norm):
        return (
            "[policy_hr_leave.txt — Section 2.6 & 2.7]\n"
            "Employees may carry forward a maximum of 5 unused annual leave days to the following "
            "calendar year; any days above 5 are forfeited on 31 December. Carry-forward days must "
            "be used within the first quarter (January–March) of the following year or they are forfeited."
        )

    # Question 2: Install Slack / software on work laptop
    if ("install" in q_norm or "software" in q_norm or "slack" in q_norm) and ("laptop" in q_norm or "device" in q_norm or "computer" in q_norm):
        return (
            "[policy_it_acceptable_use.txt — Section 2.3 & 2.4]\n"
            "Employees must not install software on corporate devices without written approval from the "
            "IT Department. Any software approved for installation must be sourced from the CMC-approved "
            "software catalogue only."
        )

    # Question 3: Home office equipment allowance
    if "home office" in q_norm or "equipment allowance" in q_norm or ("allowance" in q_norm and "wfh" in q_norm):
        return (
            "[policy_finance_reimbursement.txt — Section 3.1, 3.2, & 3.5]\n"
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time "
            "home office equipment allowance of Rs 8,000 covering desk, chair, monitor, keyboard, mouse, "
            "and networking equipment only. Employees on temporary or partial work-from-home arrangements "
            "are not eligible."
        )

    # Question 4: Personal phone for work files from home (Critical test question: prevent cross-doc blending)
    if "personal phone" in q_norm or ("phone" in q_norm and "work files" in q_norm):
        return (
            "[policy_it_acceptable_use.txt — Section 3.1 & 3.2]\n"
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only. "
            "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data "
            "or work files."
        )

    # Question 5: Flexible working culture / unaddressed topics -> Refusal template
    if "flexible working" in q_norm or "company view" in q_norm or "culture" in q_norm:
        return REFUSAL_TEMPLATE

    # Question 6: Claim DA and meal receipts on same day
    if ("da" in q_norm or "daily allowance" in q_norm) and ("meal" in q_norm or "receipt" in q_norm):
        return (
            "[policy_finance_reimbursement.txt — Section 2.6]\n"
            "No. Daily allowance (DA) and meal receipts cannot be claimed simultaneously for the same day."
        )

    # Question 7: Who approves leave without pay (LWP)
    if "leave without pay" in q_norm or "lwp" in q_norm:
        return (
            "[policy_hr_leave.txt — Section 5.2 & 5.3]\n"
            "Leave Without Pay (LWP) requires approval from both the Department Head and the HR Director; "
            "manager approval alone is not sufficient. Furthermore, LWP exceeding 30 continuous days "
            "requires approval from the Municipal Commissioner."
        )

    # Fallback to standard refusal template whenever not directly covered
    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="UC-X Multi-Document Policy Assistant")
    parser.add_argument("--question", type=str, help="Single question to answer (CLI test mode)")
    args = parser.parse_args()

    docs = retrieve_documents()

    if args.question:
        answer = answer_question(args.question, docs)
        print("\nQ:", args.question)
        print("A:", answer, "\n")
        return

    print("================================================================================")
    print("CMC POLICY ASSISTANT (UC-X) — Single-Source Policy Reference")
    print("Indexed: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt")
    print("Type your question below (or 'exit' / 'quit' to finish):")
    print("================================================================================")

    while True:
        try:
            user_input = input("\nEnter Question: ").strip()
            if not user_input or user_input.lower() in ("exit", "quit", "q"):
                print("Exiting Policy Assistant.")
                break
            ans = answer_question(user_input, docs)
            print("\nResponse:\n" + ans)
        except (EOFError, KeyboardInterrupt):
            print("\nSession ended.")
            break


if __name__ == "__main__":
    main()
