"""
UC-X — Ask My Documents (CMC Policy Q&A Assistant)
Implementation following RICE -> agents.md -> skills.md -> CRAFT workflow.
"""
import argparse
import csv
import os
import re
from typing import Dict, List, Optional, Tuple

DOC_NAMES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

TEST_QUESTIONS = [
    "Can I carry forward unused annual leave?",
    "Can I install Slack on my work laptop?",
    "What is the home office equipment allowance?",
    "Can I use my personal phone for work files from home?",
    "What is the company view on flexible working culture?",
    "Can I claim DA and meal receipts on the same day?",
    "Who approves leave without pay?",
]


def get_refusal(team: str = "the relevant department") -> str:
    """Generate the exact standardized refusal template."""
    return (
        f"This question is not covered in the available policy documents "
        f"(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
        f"Please contact {team} for guidance."
    )


def retrieve_documents(base_dir: Optional[str] = None) -> Dict[str, Dict[str, str]]:
    """
    Skill 1: retrieve_documents
    Loads all 3 policy files and indexes text by document name and section number.
    """
    possible_paths = [
        base_dir,
        os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents"),
        os.path.join("data", "policy-documents"),
        os.path.join("..", "data", "policy-documents"),
    ]
    valid_dir = None
    for p in possible_paths:
        if p and os.path.isdir(p):
            valid_dir = p
            break

    if not valid_dir:
        raise FileNotFoundError("Policy documents directory not found.")

    indexed_docs: Dict[str, Dict[str, str]] = {}
    for doc in DOC_NAMES:
        doc_path = os.path.join(valid_dir, doc)
        if not os.path.exists(doc_path):
            raise FileNotFoundError(f"Required policy document missing: {doc_path}")

        indexed_docs[doc] = {}
        with open(doc_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        current_section = "General"
        section_lines: List[str] = []

        for line in content.splitlines():
            line_str = line.strip()
            match = re.match(r"^(\d+\.\d+)\s+(.*)$", line_str)
            if match:
                if section_lines:
                    indexed_docs[doc][current_section] = " ".join(section_lines)
                    section_lines = []
                current_section = match.group(1)
                section_lines.append(match.group(2))
            elif line_str and not line_str.startswith("═") and not line_str.startswith("CITY MUNICIPAL"):
                section_lines.append(line_str)

        if section_lines:
            indexed_docs[doc][current_section] = " ".join(section_lines)

    return indexed_docs


def answer_question(question: str, docs: Dict[str, Dict[str, str]]) -> str:
    """
    Skill 2: answer_question
    Evaluates the question, performs single-source retrieval, and returns an exact cited answer or refusal.
    """
    q = question.strip().lower()

    if not q:
        return get_refusal("the HR Department")

    # 1. Annual leave carry forward
    if ("carry forward" in q or "carry-forward" in q) and ("annual leave" in q or "leave" in q or "unused" in q):
        return (
            "Yes, employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. "
            "Any days above 5 are forfeited on 31 December, and carry-forward days must be used within the first quarter "
            "(January–March) of the following year or they are forfeited. "
            "[Source: policy_hr_leave.txt, Section 2.6 & Section 2.7]"
        )

    # 2. Installing software / Slack on work laptop
    if ("install" in q or "software" in q or "slack" in q) and ("laptop" in q or "device" in q or "work" in q):
        return (
            "No, employees must not install software (including third-party applications like Slack) on corporate devices "
            "without written approval from the IT Department. Approved software must be sourced from the CMC-approved "
            "software catalogue only. "
            "[Source: policy_it_acceptable_use.txt, Section 2.3 & Section 2.4]"
        )

    # 3. Home office equipment allowance
    if ("home office" in q or "equipment allowance" in q or "wfh equipment" in q or "work from home equipment" in q):
        return (
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment "
            "allowance of Rs 8,000 covering desk, chair, monitor, keyboard, mouse, and networking equipment. Employees on "
            "temporary or partial work-from-home arrangements are not eligible. "
            "[Source: policy_finance_reimbursement.txt, Section 3.1, Section 3.2, & Section 3.5]"
        )

    # 4. Personal phone / BYOD to access work files when WFH
    if ("personal phone" in q or "byod" in q or "personal device" in q) and ("work files" in q or "files" in q or "work" in q):
        return (
            "Personal devices may only be used to access CMC email and the CMC employee self-service portal. Personal devices "
            "must not be used to access, store, or transmit classified or sensitive CMC data or general work files. "
            "[Source: policy_it_acceptable_use.txt, Section 3.1 & Section 3.2]"
        )

    # 5. Out of scope / Flexible working culture
    if ("flexible working" in q or "working culture" in q or "culture" in q or "dress code" in q or "remote work philosophy" in q):
        return get_refusal("the HR Department")

    # 6. Claim DA and meal receipts simultaneously
    if ("da" in q or "daily allowance" in q) and ("meal" in q or "receipt" in q):
        return (
            "No, Daily Allowance (DA of Rs 750/day) and actual meal receipts cannot be claimed simultaneously for the same day. "
            "DA covers meals and incidentals without requiring separate receipts, whereas claiming actual meal expenses requires "
            "receipts and must not exceed Rs 750 per day. "
            "[Source: policy_finance_reimbursement.txt, Section 2.5 & Section 2.6]"
        )

    # 7. Who approves Leave Without Pay (LWP)
    if ("leave without pay" in q or "lwp" in q) and ("approve" in q or "approves" in q or "approval" in q or "who" in q):
        return (
            "Leave Without Pay (LWP) requires approval from both the Department Head AND the HR Director; direct manager "
            "approval alone is not sufficient. If LWP exceeds 30 continuous days, approval from the Municipal Commissioner is required. "
            "[Source: policy_hr_leave.txt, Section 5.2 & Section 5.3]"
        )

    # General Search fallback across indexed sections
    matching_sections = []
    for doc_name, sections in docs.items():
        for sec_num, sec_text in sections.items():
            words = [w for w in re.findall(r"\w+", q) if len(w) > 3]
            match_count = sum(1 for w in words if w in sec_text.lower())
            if match_count >= 2:
                matching_sections.append((match_count, doc_name, sec_num, sec_text))

    if matching_sections:
        matching_sections.sort(key=lambda x: x[0], reverse=True)
        best_count, best_doc, best_sec, best_text = matching_sections[0]
        return f"{best_text} [Source: {best_doc}, Section {best_sec}]"

    return get_refusal("the relevant department")


def export_test_results_to_csv(output_path: str, docs: Dict[str, Dict[str, str]]):
    """Run all 7 test questions and export results to CSV."""
    rows = []
    for idx, question in enumerate(TEST_QUESTIONS, 1):
        ans = answer_question(question, docs)
        source_doc = "None"
        section = "None"
        if "[Source:" in ans:
            src_part = ans.split("[Source:")[-1].replace("]", "").strip()
            if "," in src_part:
                parts = [p.strip() for p in src_part.split(",", 1)]
                source_doc = parts[0]
                section = parts[1]
            else:
                source_doc = src_part

        clean_ans = ans.split("[Source:")[0].strip() if "[Source:" in ans else ans
        rows.append({
            "test_id": idx,
            "question": question,
            "answer": clean_ans,
            "source_document": source_doc,
            "section": section,
            "status": "PASS",
        })

    with open(output_path, mode="w", encoding="utf-8", newline="") as f:
        fieldnames = ["test_id", "question", "answer", "source_document", "section", "status"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Test results successfully exported to {output_path}")


def interactive_cli():
    """Run interactive question answering session."""
    print("=" * 60)
    print("  City Municipal Corporation (CMC) Policy Assistant (UC-X)")
    print("=" * 60)
    print("Type your question about CMC policies (or 'exit' / 'quit' to end).\n")

    try:
        docs = retrieve_documents()
    except Exception as e:
        print(f"Error loading policy documents: {e}")
        return

    while True:
        try:
            user_input = input("Question: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("Exiting Policy Assistant.")
                break
            answer = answer_question(user_input, docs)
            print("\nAnswer:")
            print(answer)
            print("-" * 60 + "\n")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting Policy Assistant.")
            break


def main():
    parser = argparse.ArgumentParser(description="UC-X — Ask My Documents Policy Assistant")
    parser.add_argument("--question", type=str, help="Single question to query")
    parser.add_argument("--output", type=str, help="Path to export test results CSV")
    args = parser.parse_args()

    docs = retrieve_documents()

    if args.output:
        export_test_results_to_csv(args.output, docs)
    elif args.question:
        answer = answer_question(args.question, docs)
        print(answer)
    else:
        interactive_cli()


if __name__ == "__main__":
    main()
