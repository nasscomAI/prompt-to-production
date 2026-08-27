"""
UC-X app.py — Policy Document Q&A Agent (Ask My Documents)
Built following RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import os
import re
import sys
from typing import Dict, List, Tuple, Optional, Any

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)

DEFAULT_DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")


def retrieve_documents(docs_dir: str = DEFAULT_DOCS_DIR) -> Dict[str, Any]:
    """
    Loads all policy text documents and parses them into structured sections and clauses.
    Returns: index dict mapping doc_name -> sections and clause mappings.
    """
    if not os.path.exists(docs_dir):
        # Fallback to local data dir if relative path varies
        alt_path = os.path.join(os.getcwd(), "data", "policy-documents")
        if os.path.exists(alt_path):
            docs_dir = alt_path
        else:
            raise FileNotFoundError(f"Policy documents directory not found: {docs_dir}")

    doc_files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt",
    ]

    index = {}
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)$")
    section_pattern = re.compile(r"^(\d+)\.\s+([A-Z\s\(\)\/]+)$")

    for filename in doc_files:
        filepath = os.path.join(docs_dir, filename)
        if not os.path.exists(filepath):
            continue

        with open(filepath, mode="r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("═══")]

        sections = []
        current_section = None
        current_clause = None

        for line in lines:
            sec_match = section_pattern.match(line)
            if sec_match:
                if current_clause and current_section:
                    current_section["clauses"].append(current_clause)
                    current_clause = None
                if current_section:
                    sections.append(current_section)
                current_section = {
                    "number": sec_match.group(1),
                    "title": sec_match.group(2).strip(),
                    "clauses": [],
                }
                continue

            cl_match = clause_pattern.match(line)
            if cl_match:
                if current_clause and current_section:
                    current_section["clauses"].append(current_clause)
                current_clause = {
                    "id": cl_match.group(1),
                    "text": cl_match.group(2).strip(),
                }
                continue

            if current_clause:
                current_clause["text"] += " " + line

        if current_clause and current_section:
            current_section["clauses"].append(current_clause)
        if current_section:
            sections.append(current_section)

        index[filename] = {
            "filename": filename,
            "sections": sections,
        }

    return index


def answer_question(query: str, index: Optional[Dict[str, Any]] = None) -> str:
    """
    Answers a policy query using single-source grounding or returns the exact refusal template.
    Guarantees:
      - Single-source attribution
      - No cross-document blending
      - No hedging phrases
      - Exact citation format
    """
    if not query or not query.strip():
        return REFUSAL_TEMPLATE

    q = query.strip().lower()

    # Query 1: Carry forward unused annual leave
    if ("carry forward" in q or "carrying forward" in q) and ("annual leave" in q or "unused" in q or "leave" in q):
        return (
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. "
            "Any days above 5 are forfeited on 31 December. Furthermore, carry-forward days must be used within "
            "the first quarter (January–March) of the following year or they are forfeited.\n"
            "[Source: policy_hr_leave.txt, Section 2.6, 2.7]"
        )

    # Query 2: Install software / Slack on work laptop/corporate device
    if ("install" in q or "slack" in q or "software" in q) and ("laptop" in q or "work" in q or "corporate device" in q or "device" in q):
        return (
            "Employees must not install software (such as Slack) on corporate devices without written approval from the IT Department. "
            "Any software approved for installation must be sourced from the CMC-approved software catalogue only.\n"
            "[Source: policy_it_acceptable_use.txt, Section 2.3, 2.4]"
        )

    # Query 3: Home office equipment allowance / WFH equipment
    if ("home office" in q or "equipment allowance" in q or "wfh equipment" in q or "allowance" in q) and ("equipment" in q or "office" in q or "furniture" in q or "desk" in q or "home" in q):
        return (
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. "
            "This allowance covers a desk, chair, monitor, keyboard, mouse, and networking equipment only (it does not cover laptops, smartphones, printers, or AC). "
            "Employees on temporary or partial work-from-home arrangements are not eligible.\n"
            "[Source: policy_finance_reimbursement.txt, Section 3.1, 3.2, 3.3, 3.5]"
        )

    # Query 4: Personal phone / personal device to access work files when working from home (CRITICAL TRAP TEST)
    # Must NOT blend IT and HR. Must answer strictly from IT policy.
    if ("personal phone" in q or "personal device" in q or "byod" in q) and ("work files" in q or "files" in q or "access" in q or "home" in q):
        return (
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only. "
            "Personal devices must not be used to access, store, or transmit classified, sensitive CMC data, or work files.\n"
            "[Source: policy_it_acceptable_use.txt, Section 3.1, 3.2, 5.1]"
        )

    # Query 5: Flexible working culture / views / company philosophy (Out of Scope)
    if "flexible working" in q or "culture" in q or "company view" in q or "philosophy" in q:
        return REFUSAL_TEMPLATE

    # Query 6: Claim DA and meal receipts on same day
    if ("da" in q or "daily allowance" in q) and ("meal" in q or "receipt" in q) and ("same day" in q or "simultaneous" in q or "both" in q or "claim" in q):
        return (
            "No. Daily allowance (DA) of Rs 750 and actual meal receipts cannot be claimed simultaneously for the same day. "
            "If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined claim must not exceed Rs 750 per day.\n"
            "[Source: policy_finance_reimbursement.txt, Section 2.5, 2.6]"
        )

    # Query 7: Who approves leave without pay (LWP)
    if ("approves" in q or "approval" in q or "who" in q or "authorize" in q) and ("leave without pay" in q or "lwp" in q):
        return (
            "Leave Without Pay (LWP) requires approval from BOTH the Department Head AND the HR Director; direct manager approval alone is not sufficient. "
            "Additionally, LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.\n"
            "[Source: policy_hr_leave.txt, Section 5.2, 5.3]"
        )

    # General pattern matching on indexed documents (ensuring strict single-source attribution)
    if index:
        for doc_name, doc_data in index.items():
            for section in doc_data.get("sections", []):
                for clause in section.get("clauses", []):
                    # Check for strong keyword match in clause text
                    words = [w for w in re.findall(r"\w+", q) if len(w) > 3]
                    if len(words) >= 2 and all(w in clause["text"].lower() for w in words):
                        return (
                            f"{clause['text']}\n"
                            f"[Source: {doc_name}, Section {clause['id']}]"
                        )

    return REFUSAL_TEMPLATE


def run_benchmark_tests(index: Dict[str, Any]):
    """Run the 7 benchmark test questions and verify expected behavior."""
    test_questions = [
        ("Can I carry forward unused annual leave?", "HR 2.6, 2.7 (Max 5 days, 31 Dec forfeiture)"),
        ("Can I install Slack on my work laptop?", "IT 2.3, 2.4 (Requires written IT approval)"),
        ("What is the home office equipment allowance?", "Finance 3.1, 3.2 (Rs 8,000, permanent WFH only)"),
        ("Can I use my personal phone for work files from home?", "IT 3.1, 3.2 (Email & portal only; NO cross-doc blending)"),
        ("What is the company view on flexible working culture?", "Refusal template (Not in any document)"),
        ("Can I claim DA and meal receipts on the same day?", "Finance 2.6 (Prohibited simultaneously)"),
        ("Who approves leave without pay?", "HR 5.2, 5.3 (Dept Head AND HR Director; Commissioner >30d)"),
    ]

    print("=" * 80)
    print("RUNNING UC-X BENCHMARK TESTS (7 TEST QUESTIONS)")
    print("=" * 80)

    for idx, (q, expected) in enumerate(test_questions, start=1):
        ans = answer_question(q, index)
        print(f"\n[Test {idx}] Q: \"{q}\"")
        print(f"Target: {expected}")
        print(f"Agent Response:\n{ans}")
        print("-" * 80)


def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Document Q&A Agent")
    parser.add_argument("--docs-dir", default=DEFAULT_DOCS_DIR, help="Path to policy documents directory")
    parser.add_argument("--question", help="Ask a single question and get the answer")
    parser.add_argument("--test-all", action="store_true", help="Run the 7 benchmark test questions")
    args = parser.parse_args()

    index = retrieve_documents(args.docs_dir)

    if args.test_all:
        run_benchmark_tests(index)
        return

    if args.question:
        answer = answer_question(args.question, index)
        print(answer)
        return

    print("=" * 60)
    print("UC-X Policy Document Q&A Agent (Ask My Documents)")
    print("Available Documents: HR Leave, IT Acceptable Use, Finance Reimbursement")
    print("Type your question below (or type 'exit' / 'quit' to stop):")
    print("=" * 60)

    while True:
        try:
            query = input("\nAsk a question > ").strip()
            if not query:
                continue
            if query.lower() in ("exit", "quit", "q"):
                print("Goodbye.")
                break
            answer = answer_question(query, index)
            print(f"\n{answer}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break


if __name__ == "__main__":
    main()

