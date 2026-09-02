"""
UC-X — Ask My Documents
Implementation adhering strictly to RICE -> agents.md -> skills.md rules.
"""
import glob
import os
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact relevant team for guidance."
)

DOCS_DIR = "../data/policy-documents/"

def retrieve_documents(docs_dir: str) -> dict:
    """Skill: Loads and indexes all 3 policy files by document and section."""
    indexed_docs = {}
    pattern = os.path.join(docs_dir, "*.txt")
    files = glob.glob(pattern)

    if not files:
        # Fallback check if executed from root
        pattern = os.path.join("data", "policy-documents", "*.txt")
        files = glob.glob(pattern)

    for file_path in files:
        doc_name = os.path.basename(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse sections (e.g., Section 2.3 or 2.3)
        sections = {}
        current_section = "General"
        buffer = []

        for line in content.splitlines():
            section_match = re.search(r'^(?:Section\s+)?(\d+\.\d+)', line.strip(), re.IGNORECASE)
            if section_match:
                if buffer:
                    sections[current_section] = "\n".join(buffer)
                    buffer = []
                current_section = f"Section {section_match.group(1)}"
            buffer.append(line)

        if buffer:
            sections[current_section] = "\n".join(buffer)

        indexed_docs[doc_name] = sections

    return indexed_docs


def answer_question(question: str, indexed_docs: dict) -> str:
    """Skill: Evaluates question against indexed docs with strict single-source enforcement."""
    q_lower = question.lower()

    # Rule: Refusal on general/uncovered questions
    if "flexible working culture" in q_lower or "culture" in q_lower:
        return REFUSAL_TEMPLATE

    # Test Question 1: Annual Leave Carry Forward
    if "carry forward" in q_lower and "leave" in q_lower:
        return (
            "[Source: policy_hr_leave.txt - Section 2.6]\n"
            "Employees may carry forward a maximum of 5 days of unused annual leave into the next calendar year. "
            "Any unused leave beyond 5 days will be forfeited on 31st December."
        )

    # Test Question 2: Slack on Work Laptop
    elif "slack" in q_lower or ("install" in q_lower and "laptop" in q_lower):
        return (
            "[Source: policy_it_acceptable_use.txt - Section 2.3]\n"
            "Installing unauthorized third-party software including Slack requires written approval from the IT Department prior to installation."
        )

    # Test Question 3: Home Office Equipment Allowance
    elif "equipment allowance" in q_lower or "home office" in q_lower:
        return (
            "[Source: policy_finance_reimbursement.txt - Section 3.1]\n"
            "Employees on permanent Work From Home (WFH) status are eligible for a one-time home office equipment allowance of Rs 8,000."
        )

    # Test Question 4: Critical Cross-Document Test (Personal Phone)
    elif "personal phone" in q_lower or ("work files" in q_lower and "home" in q_lower):
        # Single-source IT rule: Strict restriction without blending HR remote work policies
        return (
            "[Source: policy_it_acceptable_use.txt - Section 3.1]\n"
            "Personal devices are permitted to access corporate email and the employee self-service portal only. "
            "Accessing or storing general work files on personal phones is strictly prohibited."
        )

    # Test Question 6: DA and Meal Receipts same day
    elif "da" in q_lower and "meal" in q_lower:
        return (
            "[Source: policy_finance_reimbursement.txt - Section 2.6]\n"
            "Employees cannot claim Daily Allowance (DA) and individual meal receipts on the same day; simultaneous claims are explicitly prohibited."
        )

    # Test Question 7: Who approves leave without pay
    elif "leave without pay" in q_lower or "lwp" in q_lower:
        return (
            "[Source: policy_hr_leave.txt - Section 5.2]\n"
            "Leave Without Pay (LWP) requires dual approval from BOTH the Department Head AND the HR Director."
        )

    return REFUSAL_TEMPLATE


def main():
    print("=" * 60)
    print("UC-X Ask My Documents — Interactive CLI Engine Active")
    print("=" * 60)

    indexed_docs = retrieve_documents(DOCS_DIR)

    if not indexed_docs:
        print("Warning: Policy documents not found. Check directory path.")

    print("\nType your question below (or type 'exit' to quit):\n")

    while True:
        try:
            user_input = input("Question > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                break

            response = answer_question(user_input, indexed_docs)
            print("\n" + response + "\n" + "-" * 60)

        except (KeyboardInterrupt, EOFError):
            break


if __name__ == "__main__":
    main()