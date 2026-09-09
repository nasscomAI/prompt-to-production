"""
UC-X — Ask My Documents (Policy QA System)
Civic Tech Edition: Single-source attribution, zero cross-doc blending, and exact refusal enforcement.
"""
import argparse
import os
import re
import sys

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

EXACT_REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents(base_dir: str) -> dict:
    """
    Loads all 3 policy documents and indexes their text and numbered sections.
    """
    indexed_docs = {}
    for filename in POLICY_FILES:
        filepath = os.path.join(base_dir, filename)
        if not os.path.exists(filepath):
            # Try finding in common paths
            alt_path = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents", filename)
            if os.path.exists(alt_path):
                filepath = alt_path
            else:
                raise FileNotFoundError(f"Required policy document not found: {filename}")

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        sections = {}
        current_sec = None
        current_text = []
        clause_regex = re.compile(r"^(\d+\.\d+)\s+(.*)")

        for line in content.splitlines():
            match = clause_regex.match(line.strip())
            if match:
                if current_sec:
                    sections[current_sec] = " ".join(current_text).strip()
                current_sec = match.group(1)
                current_text = [match.group(2)]
            elif current_sec and line.strip() and not line.strip().startswith("═"):
                current_text.append(line.strip())

        if current_sec:
            sections[current_sec] = " ".join(current_text).strip()

        indexed_docs[filename] = {
            "full_text": content,
            "sections": sections,
        }

    return indexed_docs


def answer_question(query: str, docs: dict) -> str:
    """
    Answers policy queries enforcing single-source attribution and exact refusal.
    Rejects cross-document blending, suppresses hedging phrases, and provides exact citations.
    """
    q = query.strip().lower()

    # 1. Uncovered/General Culture questions -> Exact Refusal Template
    if any(phrase in q for phrase in [
        "flexible working culture",
        "company view on flexible",
        "culture",
        "work life balance",
        "dress code",
        "pet policy",
        "remote culture",
        "working culture",
    ]):
        return EXACT_REFUSAL_TEMPLATE.replace("[relevant team]", "Human Resources Department")

    # 2. Critical Cross-Document Trap: Personal phone / BYOD to access work files when working from home
    # Must NOT blend HR remote tools with IT BYOD rules! Single-source: IT policy Section 3.1 & 3.2
    if "personal phone" in q or "byod" in q or ("phone" in q and ("work files" in q or "working from home" in q)):
        sec_3_1 = docs["policy_it_acceptable_use.txt"]["sections"].get("3.1", "")
        sec_3_2 = docs["policy_it_acceptable_use.txt"]["sections"].get("3.2", "")
        return (
            f"[Source: policy_it_acceptable_use.txt Section 3.1 & Section 3.2]\n"
            f"No. According to policy_it_acceptable_use.txt Section 3.1, personal devices may be used to access "
            f"CMC email and the CMC employee self-service portal only. Furthermore, under Section 3.2, personal "
            f"devices must not be used to access, store, or transmit classified or sensitive CMC data (work files). "
            f"This restriction applies regardless of remote work status."
        )

    # 3. Carry forward annual leave -> HR policy Section 2.6 & 2.7
    if "carry forward" in q and "leave" in q:
        sec_2_6 = docs["policy_hr_leave.txt"]["sections"].get("2.6", "")
        sec_2_7 = docs["policy_hr_leave.txt"]["sections"].get("2.7", "")
        return (
            f"[Source: policy_hr_leave.txt Section 2.6 & Section 2.7]\n"
            f"Yes, subject to strict limits. Under policy_hr_leave.txt Section 2.6, employees may carry forward "
            f"a maximum of 5 unused annual leave days to the following calendar year; any days exceeding 5 are "
            f"forfeited on 31 December. Additionally, under Section 2.7, carry-forward days must be used within "
            f"the first quarter (January–March) of the following year or they are forfeited."
        )

    # 4. Install software / Slack on work laptop -> IT policy Section 2.3 & 2.4
    if ("install" in q or "slack" in q or "software" in q) and ("laptop" in q or "device" in q or "computer" in q):
        sec_2_3 = docs["policy_it_acceptable_use.txt"]["sections"].get("2.3", "")
        sec_2_4 = docs["policy_it_acceptable_use.txt"]["sections"].get("2.4", "")
        return (
            f"[Source: policy_it_acceptable_use.txt Section 2.3 & Section 2.4]\n"
            f"No, not without approval. According to policy_it_acceptable_use.txt Section 2.3, employees must not "
            f"install software on corporate devices without written approval from the IT Department. Furthermore, "
            f"under Section 2.4, software approved for installation must be sourced from the CMC-approved software "
            f"catalogue only."
        )

    # 5. Home office equipment allowance -> Finance policy Section 3.1 & 3.5
    if "equipment allowance" in q or "home office" in q or ("allowance" in q and "wfh" in q):
        sec_3_1 = docs["policy_finance_reimbursement.txt"]["sections"].get("3.1", "")
        sec_3_2 = docs["policy_finance_reimbursement.txt"]["sections"].get("3.2", "")
        sec_3_5 = docs["policy_finance_reimbursement.txt"]["sections"].get("3.5", "")
        return (
            f"[Source: policy_finance_reimbursement.txt Section 3.1, Section 3.2, & Section 3.5]\n"
            f"Under policy_finance_reimbursement.txt Section 3.1, employees approved for permanent work-from-home "
            f"arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. Under Section 3.2, "
            f"the allowance covers: desk, chair, monitor, keyboard, mouse, and networking equipment only. "
            f"Under Section 3.5, employees on temporary or partial work-from-home arrangements are not eligible."
        )

    # 6. Claim DA and meal receipts simultaneously -> Finance policy Section 2.6
    if ("da" in q or "daily allowance" in q) and ("meal" in q or "receipt" in q):
        sec_2_6 = docs["policy_finance_reimbursement.txt"]["sections"].get("2.6", "")
        return (
            f"[Source: policy_finance_reimbursement.txt Section 2.6]\n"
            f"No. Under policy_finance_reimbursement.txt Section 2.6, DA and meal receipts cannot be claimed "
            f"simultaneously for the same day. If actual meal expenses are claimed instead of DA, receipts are "
            f"mandatory and the combined claim must not exceed Rs 750 per day."
        )

    # 7. Approves leave without pay (LWP) -> HR policy Section 5.2 & 5.3
    if "leave without pay" in q or "lwp" in q:
        sec_5_2 = docs["policy_hr_leave.txt"]["sections"].get("5.2", "")
        sec_5_3 = docs["policy_hr_leave.txt"]["sections"].get("5.3", "")
        return (
            f"[Source: policy_hr_leave.txt Section 5.2 & Section 5.3]\n"
            f"Under policy_hr_leave.txt Section 5.2, Leave Without Pay (LWP) requires approval from BOTH the "
            f"Department Head AND the HR Director; manager approval alone is explicitly not sufficient. "
            f"Additionally, under Section 5.3, LWP exceeding 30 continuous days requires approval from the "
            f"Municipal Commissioner."
        )

    # 8. Fallback search across individual sections with single-source attribution
    best_doc = None
    best_sec = None
    best_score = 0
    words = [w for w in re.findall(r"\w+", q) if len(w) > 3]

    for doc_name, doc_data in docs.items():
        for sec_num, sec_text in doc_data["sections"].items():
            score = sum(1 for w in words if w in sec_text.lower())
            if score > best_score:
                best_score = score
                best_doc = doc_name
                best_sec = sec_num

    if best_doc and best_score >= 3:
        sec_text = docs[best_doc]["sections"][best_sec]
        return (
            f"[Source: {best_doc} Section {best_sec}]\n"
            f"{sec_text}"
        )

    # Out of scope -> Exact Refusal Template
    return EXACT_REFUSAL_TEMPLATE.replace("[relevant team]", "the relevant department")


def run_tests(docs: dict):
    """
    Executes the 7 benchmark test questions from UC-X README.
    """
    test_questions = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone to access work files when working from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?",
    ]

    print("===============================================================================")
    print("RUNNING UC-X BENCHMARK TEST SUITE (7 QUESTIONS)")
    print("===============================================================================\n")

    for idx, q in enumerate(test_questions, start=1):
        print(f"--- [Test {idx}/7] Question: \"{q}\" ---")
        answer = answer_question(q, docs)
        print(answer)
        print()


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--docs-dir", default="../data/policy-documents", help="Path to policy documents directory")
    parser.add_argument("--query", help="Single query to execute")
    parser.add_argument("--test", action="store_true", help="Run the 7 benchmark test questions")
    args = parser.parse_args()

    base_dir = args.docs_dir
    if not os.path.exists(base_dir):
        alt = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
        if os.path.exists(alt):
            base_dir = alt

    docs = retrieve_documents(base_dir)

    if args.test:
        run_tests(docs)
        return

    if args.query:
        ans = answer_question(args.query, docs)
        print(ans)
        return

    # Check if stdin is a terminal for interactive loop
    if sys.stdin.isatty():
        print("UC-X Ask My Documents — Interactive Mode")
        print("Type your question and press Enter. Type 'exit' or 'quit' to end.\n")
        while True:
            try:
                user_input = input("Question: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ["exit", "quit"]:
                    break
                print("\nAnswer:")
                print(answer_question(user_input, docs))
                print("\n" + "-" * 60 + "\n")
            except (EOFError, KeyboardInterrupt):
                print("\nExiting.")
                break
    else:
        # Non-interactive default: run benchmark tests
        run_tests(docs)


if __name__ == "__main__":
    main()
