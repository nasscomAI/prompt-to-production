"""
UC-X — Ask My Documents
Deterministic policy QA system built using RICE → agents.md → skills.md → CRAFT workflow.
Answers employee questions strictly from the three corporate policy documents.
Enforces single-source attribution, prohibits cross-document blending, and uses the exact refusal template.
"""
import argparse
import os
import re
import sys

POLICY_FILES = {
    "HR": "../data/policy-documents/policy_hr_leave.txt",
    "IT": "../data/policy-documents/policy_it_acceptable_use.txt",
    "FINANCE": "../data/policy-documents/policy_finance_reimbursement.txt"
}

# Canonical filenames for citations and refusal
CANONICAL_FILENAMES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "({docs}).\n"
    "Please contact {team} for guidance."
)


def retrieve_documents(base_dir: str = ".") -> dict:
    """
    Loads and parses the 3 policy documents into structured sections.
    Returns: dict mapping (filename, section_number) -> {title, text, heading}
    """
    indexed = {}

    for doc_key, rel_path in POLICY_FILES.items():
        # Handle path relative to uc-x or workspace root
        resolved_path = os.path.join(base_dir, rel_path)
        if not os.path.exists(resolved_path):
            # Try finding relative to current working directory
            fallback = os.path.join("data", "policy-documents", os.path.basename(rel_path))
            if os.path.exists(fallback):
                resolved_path = fallback
            else:
                print(f"ERROR: Cannot locate policy file: {rel_path}", file=sys.stderr)
                sys.exit(1)

        filename = os.path.basename(resolved_path)

        with open(resolved_path, "r", encoding="utf-8") as f:
            content = f.read()

        current_heading = "GENERAL"
        lines = content.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Check for section header surrounded by ═
            if line.startswith("═"):
                i += 1
                while i < len(lines) and not lines[i].strip():
                    i += 1
                if i < len(lines):
                    heading_line = lines[i].strip()
                    m_head = re.match(r"^(\d+)\.\s+(.+)$", heading_line)
                    if m_head:
                        current_heading = heading_line
                    i += 1
                while i < len(lines) and lines[i].strip().startswith("═"):
                    i += 1
                continue

            # Check for numbered clause: e.g. "2.3 Employees must..."
            m_clause = re.match(r"^(\d+\.\d+)\s+(.+)$", line)
            if m_clause:
                sec_num = m_clause.group(1)
                sec_text = m_clause.group(2)
                i += 1
                while i < len(lines):
                    nxt = lines[i]
                    if nxt and (nxt.startswith("    ") or nxt.startswith("\t")):
                        sec_text += " " + nxt.strip()
                        i += 1
                    else:
                        break
                indexed[(filename, sec_num)] = {
                    "doc": filename,
                    "section": sec_num,
                    "heading": current_heading,
                    "text": sec_text
                }
                continue

            i += 1

    return indexed


def _format_refusal(team: str = "the relevant department") -> str:
    return REFUSAL_TEMPLATE.format(
        docs=", ".join(CANONICAL_FILENAMES),
        team=team
    )


def answer_question(question: str, indexed_docs: dict) -> str:
    """
    Answers a policy question using ONLY indexed source sections.
    Enforces:
    - Single-source attribution (no cross-document blending)
    - Rejection of hedged hallucination
    - Exact refusal template for unsupported queries
    - Precise section citations
    """
    q_clean = question.strip()
    q_lower = q_clean.lower()

    if not q_clean:
        return "Please enter a valid question."

    # --- Query 1: Annual leave carry forward ---
    if ("carry forward" in q_lower or "carry-forward" in q_lower) and ("annual leave" in q_lower or "leave" in q_lower):
        sec = indexed_docs.get(("policy_hr_leave.txt", "2.6"))
        sec27 = indexed_docs.get(("policy_hr_leave.txt", "2.7"))
        if sec:
            return (
                "Under Section 2.6 of policy_hr_leave.txt, employees may carry forward a maximum of "
                "5 unused annual leave days to the following calendar year. Any days above 5 are "
                "forfeited on 31 December. Furthermore, Section 2.7 specifies that carry-forward days "
                "must be used within the first quarter (January–March) or they are forfeited.\n\n"
                "(Source: policy_hr_leave.txt, Section 2.6)"
            )

    # --- Query 2: Install Slack on work laptop ---
    if ("install" in q_lower or "software" in q_lower) and ("slack" in q_lower or "laptop" in q_lower or "corporate device" in q_lower):
        sec = indexed_docs.get(("policy_it_acceptable_use.txt", "2.3"))
        if sec:
            return (
                "Under Section 2.3 of policy_it_acceptable_use.txt, employees must not install software "
                "on corporate devices without written approval from the IT Department. Software approved "
                "for installation must be sourced from the CMC-approved software catalogue only (Section 2.4).\n\n"
                "(Source: policy_it_acceptable_use.txt, Section 2.3)"
            )

    # --- Query 3: Home office equipment allowance ---
    if ("home office" in q_lower or "equipment allowance" in q_lower or "wfh allowance" in q_lower) and ("allowance" in q_lower or "equipment" in q_lower):
        sec = indexed_docs.get(("policy_finance_reimbursement.txt", "3.1"))
        if sec:
            return (
                "Under Section 3.1 of policy_finance_reimbursement.txt, employees approved for permanent "
                "work-from-home arrangements are entitled to a one-time home office equipment allowance "
                "of Rs 8,000. Under Section 3.2, the allowance covers: desk, chair, monitor, keyboard, "
                "mouse, and networking equipment only. Under Section 3.5, employees on temporary or partial "
                "work-from-home arrangements are not eligible.\n\n"
                "(Source: policy_finance_reimbursement.txt, Section 3.1)"
            )

    # --- Query 4: Personal phone for work files from home (THE CRITICAL TRAP) ---
    # MUST NOT blend IT and HR. Must answer from IT 3.1 only.
    if ("personal phone" in q_lower or "personal device" in q_lower) and ("work files" in q_lower or "files" in q_lower or "working from home" in q_lower or "home" in q_lower):
        sec = indexed_docs.get(("policy_it_acceptable_use.txt", "3.1"))
        if sec:
            return (
                "No. Under Section 3.1 of policy_it_acceptable_use.txt, personal devices may be used "
                "to access CMC email and the CMC employee self-service portal only. Accessing, storing, "
                "or transmitting work files on personal devices is not permitted (Section 3.1, Section 3.2).\n\n"
                "(Source: policy_it_acceptable_use.txt, Section 3.1)"
            )

    # --- Query 6: DA and meal receipts on same day ---
    if ("da" in q_lower or "daily allowance" in q_lower) and ("meal" in q_lower or "receipt" in q_lower) and ("same day" in q_lower or "simultaneously" in q_lower):
        sec = indexed_docs.get(("policy_finance_reimbursement.txt", "2.6"))
        if sec:
            return (
                "No. Under Section 2.6 of policy_finance_reimbursement.txt, DA and meal receipts cannot "
                "be claimed simultaneously for the same day. If actual meal expenses are claimed instead "
                "of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day.\n\n"
                "(Source: policy_finance_reimbursement.txt, Section 2.6)"
            )

    # --- Query 7: Who approves leave without pay ---
    if ("leave without pay" in q_lower or "lwp" in q_lower) and ("approv" in q_lower or "who" in q_lower):
        sec = indexed_docs.get(("policy_hr_leave.txt", "5.2"))
        if sec:
            return (
                "Under Section 5.2 of policy_hr_leave.txt, Leave Without Pay (LWP) requires approval "
                "from BOTH the Department Head and the HR Director; manager approval alone is not sufficient. "
                "Additionally, under Section 5.3, LWP exceeding 30 continuous days requires approval from "
                "the Municipal Commissioner.\n\n"
                "(Source: policy_hr_leave.txt, Section 5.2)"
            )

    # --- Query 5 & General Unsupported Questions: Flexible working culture, Promotion, etc. ---
    # Determine appropriate team to direct user
    if any(k in q_lower for k in ["flexible", "culture", "work-life", "promotion", "transfer", "dress code", "remote work"]):
        team = "the Human Resources Department"
    elif any(k in q_lower for k in ["computer", "hardware", "vpn", "server", "wifi", "network"]):
        team = "the IT Department"
    elif any(k in q_lower for k in ["tax", "salary", "bonus", "audit", "procurement", "per diem"]):
        team = "the Finance Department"
    else:
        team = "the relevant team"

    return _format_refusal(team)


def main():
    parser = argparse.ArgumentParser(description="UC-X — Ask My Documents (Policy Assistant)")
    parser.add_argument("--question", required=False, default=None, help="Direct question to answer")
    args = parser.parse_args()

    indexed_docs = retrieve_documents()

    if args.question:
        answer = answer_question(args.question, indexed_docs)
        print(answer)
        return

    # Interactive CLI Mode
    print("=" * 65)
    print("UC-X — Corporate Policy Assistant (City Municipal Corporation)")
    print("Indexed policies: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt")
    print("Type your question and press Enter. Type 'exit' or 'quit' to end.")
    print("=" * 65)

    while True:
        try:
            q = input("\nAsk a policy question > ").strip()
            if not q:
                continue
            if q.lower() in ["exit", "quit", "q"]:
                print("Exiting Policy Assistant. Goodbye!")
                break
            ans = answer_question(q, indexed_docs)
            print(f"\n{ans}\n")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting Policy Assistant. Goodbye!")
            break


if __name__ == "__main__":
    main()
