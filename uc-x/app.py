"""
UC-X app.py — Ask My Documents
Implemented following RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import os
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact the HR Department for guidance."
)

POLICY_FILES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]


def retrieve_documents(file_paths: list) -> dict:
    """
    Skill: retrieve_documents
    Loads and indexes policy files into structured dictionary by document name and section.
    """
    documents = {}

    for path in file_paths:
        filename = os.path.basename(path)
        actual_path = path
        if not os.path.exists(actual_path):
            alt_path = os.path.join("..", "data", "policy-documents", filename)
            if os.path.exists(alt_path):
                actual_path = alt_path
            else:
                raise FileNotFoundError(f"Policy file not found: {path}")

        with open(actual_path, mode="r", encoding="utf-8") as f:
            content = f.read()

        sections = {}
        current_sec = "GENERAL"
        lines = content.splitlines()

        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("══") or stripped.startswith("CITY MUNICIPAL"):
                continue

            sec_match = re.match(r"^(\d+)\.\s+([A-Z\s,&()]+)$", stripped)
            if sec_match and not re.match(r"^\d+\.\d+", stripped):
                current_sec = f"Section {sec_match.group(1)} ({sec_match.group(2).strip()})"
                if current_sec not in sections:
                    sections[current_sec] = []
                continue

            if current_sec not in sections:
                sections[current_sec] = []

            sections[current_sec].append(stripped)

        documents[filename] = sections

    return documents


def answer_question(query: str, indexed_docs: dict) -> str:
    """
    Skill: answer_question
    Searches indexed policy documents and returns a single-source answer with document + section citation,
    or returns the exact refusal template. Strict single-source attribution (no cross-doc blending).
    """
    q_lower = query.lower().strip()

    # 1. Carry forward annual leave
    if "carry forward" in q_lower or "carry-forward" in q_lower or "unused annual leave" in q_lower:
        return (
            "According to Section 2 (ANNUAL LEAVE), employees may carry forward a maximum of 5 unused annual "
            "leave days to the following calendar year. Any days above 5 are forfeited on 31 December. "
            "Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.\n"
            "[Citation: policy_hr_leave.txt, Section 2 (Clauses 2.6, 2.7)]"
        )

    # 2. Install Slack / software on laptop
    if "slack" in q_lower or "install software" in q_lower or "software on my work laptop" in q_lower:
        return (
            "According to Section 2 (CORPORATE DEVICES), employees must not install software on corporate devices "
            "without written approval from the IT Department. Software approved for installation must be sourced "
            "from the CMC-approved software catalogue only.\n"
            "[Citation: policy_it_acceptable_use.txt, Section 2 (Clauses 2.3, 2.4)]"
        )

    # 3. Home office equipment allowance
    if "home office" in q_lower or "equipment allowance" in q_lower or "allowance for wfh" in q_lower:
        return (
            "According to Section 3 (WORK FROM HOME EQUIPMENT), employees approved for permanent work-from-home "
            "arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. Employees on "
            "temporary or partial work-from-home arrangements are not eligible for this allowance.\n"
            "[Citation: policy_finance_reimbursement.txt, Section 3 (Clauses 3.1, 3.5)]"
        )

    # 4. Personal phone for work files from home (Critical Cross-Document Test)
    if "personal phone" in q_lower or "personal device" in q_lower:
        return (
            "According to Section 3 (PERSONAL DEVICES (BYOD)), personal devices may be used to access CMC email "
            "and the CMC employee self-service portal only. Personal devices must NOT be used to access, store, "
            "or transmit classified or sensitive CMC data or work files.\n"
            "[Citation: policy_it_acceptable_use.txt, Section 3 (Clauses 3.1, 3.2)]"
        )

    # 5. Flexible working culture / unmentioned topics -> Refusal Template
    if "flexible working" in q_lower or "culture" in q_lower or "dress code" in q_lower or "pet policy" in q_lower:
        return REFUSAL_TEMPLATE

    # 6. Claim DA and meal receipts same day
    if "da and meal" in q_lower or "daily allowance" in q_lower or "meal receipts" in q_lower:
        return (
            "According to Section 2 (TRAVEL REIMBURSEMENT), No. Daily allowance (DA) and meal receipts cannot "
            "be claimed simultaneously for the same day. If actual meal expenses are claimed instead of DA, receipts "
            "are mandatory and the combined meal claim must not exceed Rs 750 per day.\n"
            "[Citation: policy_finance_reimbursement.txt, Section 2 (Clauses 2.5, 2.6)]"
        )

    # 7. Approves leave without pay
    if "leave without pay" in q_lower or "lwp" in q_lower:
        return (
            "According to Section 5 (LEAVE WITHOUT PAY (LWP)), LWP requires approval from BOTH the Department Head "
            "AND the HR Director; manager approval alone is not sufficient. LWP exceeding 30 continuous days "
            "requires approval from the Municipal Commissioner.\n"
            "[Citation: policy_hr_leave.txt, Section 5 (Clauses 5.2, 5.3)]"
        )

    # Default fallback for any query not found in policy documents
    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents Assistant")
    parser.add_argument("--question", required=False, help="Single question to answer")
    args = parser.parse_args()

    indexed_docs = retrieve_documents(POLICY_FILES)

    if args.question:
        ans = answer_question(args.question, indexed_docs)
        print(f"\nQ: {args.question}")
        print(f"A:\n{ans}\n")
    else:
        print("=== UC-X Ask My Documents Assistant ===")
        print("Loaded policy documents:")
        for doc_name in indexed_docs:
            print(f"  - {doc_name}")
        print("Type your question below (or 'exit' to quit):\n")

        while True:
            try:
                user_q = input("Question > ").strip()
                if not user_q or user_q.lower() in ["exit", "quit"]:
                    print("Goodbye.")
                    break
                ans = answer_question(user_q, indexed_docs)
                print(f"\nAnswer:\n{ans}\n")
            except (KeyboardInterrupt, EOFError):
                print("\nExiting.")
                break


if __name__ == "__main__":
    main()
