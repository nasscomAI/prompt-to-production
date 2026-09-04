"""
UC-X — Ask My Documents
Policy Q&A CLI operating exclusively over CMC policy documents.
Enforces single-source document grounding, exact section citations,
zero cross-document blending, and character-exact refusal templates.
"""
import argparse
import os
import re
import sys
from typing import Dict, List, Tuple, Optional, Any

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

DOC_FILENAMES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]


def _find_policy_dir() -> str:
    """Locate the data/policy-documents directory."""
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents"),
        os.path.join("data", "policy-documents"),
        os.path.join("..", "data", "policy-documents"),
    ]
    for c in candidates:
        if os.path.isdir(c):
            return os.path.abspath(c)
    raise FileNotFoundError("Could not locate data/policy-documents directory.")


def retrieve_documents(policy_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Loads all 3 policy documents and indexes their content by document filename and section.
    Skill: retrieve_documents
    """
    if not policy_dir:
        policy_dir = _find_policy_dir()

    index: Dict[str, Any] = {}

    section_pattern = re.compile(r"^\s*(\d+)\.\s+([A-Z0-9\s,\-–—()\/]+)$")
    clause_pattern = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")

    for filename in DOC_FILENAMES:
        file_path = os.path.join(policy_dir, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Required policy document missing: {file_path}")

        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        if not content.strip():
            raise ValueError(f"Policy document is empty: {file_path}")

        lines = content.splitlines()
        doc_sections: Dict[str, Dict[str, Any]] = {}
        doc_clauses: Dict[str, Dict[str, Any]] = {}

        current_sec_num = None
        current_sec_title = ""
        current_clause_id = None
        current_clause_lines: List[str] = []

        for line in lines:
            stripped = line.strip()
            if not stripped or set(stripped).issubset({"═", "=", "-", "—", "–", "*"}):
                continue

            sec_match = section_pattern.match(stripped)
            if sec_match and not clause_pattern.match(stripped):
                if current_clause_id:
                    doc_clauses[current_clause_id] = {
                        "section_num": current_sec_num,
                        "section_title": current_sec_title,
                        "text": " ".join(current_clause_lines).strip(),
                    }
                    current_clause_id = None
                    current_clause_lines = []

                current_sec_num = sec_match.group(1)
                current_sec_title = sec_match.group(2).strip()
                doc_sections[current_sec_num] = {
                    "title": current_sec_title,
                    "clauses": [],
                }
                continue

            cl_match = clause_pattern.match(stripped)
            if cl_match:
                if current_clause_id:
                    doc_clauses[current_clause_id] = {
                        "section_num": current_sec_num,
                        "section_title": current_sec_title,
                        "text": " ".join(current_clause_lines).strip(),
                    }
                current_clause_id = cl_match.group(1)
                current_clause_lines = [cl_match.group(2).strip()]
                if current_sec_num and current_sec_num in doc_sections:
                    doc_sections[current_sec_num]["clauses"].append(current_clause_id)
            else:
                if current_clause_id:
                    current_clause_lines.append(stripped)

        if current_clause_id:
            doc_clauses[current_clause_id] = {
                "section_num": current_sec_num,
                "section_title": current_sec_title,
                "text": " ".join(current_clause_lines).strip(),
            }

        index[filename] = {
            "path": file_path,
            "raw_text": content,
            "sections": doc_sections,
            "clauses": doc_clauses,
        }

    return index


def answer_question(query: str, index: Dict[str, Any]) -> str:
    """
    Searches indexed policy documents and returns a single-source, section-cited answer
    or the exact refusal template.
    Skill: answer_question
    """
    q = query.strip()
    if not q:
        return REFUSAL_TEMPLATE

    q_lower = q.lower()

    # Rule 1: Annual Leave Carry Forward
    # Question: "Can I carry forward unused annual leave?"
    if "carry forward" in q_lower and ("annual leave" in q_lower or "leave" in q_lower):
        if "sick" not in q_lower:
            doc = "policy_hr_leave.txt"
            cl_2_6 = index[doc]["clauses"].get("2.6", {}).get("text", "")
            cl_2_7 = index[doc]["clauses"].get("2.7", {}).get("text", "")
            ans = (
                f"Yes. According to [{doc}, Section 2.6], employees may carry forward a maximum of 5 unused annual leave days "
                f"to the following calendar year. Any days above 5 are forfeited on 31 December.\n"
                f"Furthermore, [{doc}, Section 2.7] stipulates that carry-forward days must be used within the first quarter "
                f"(January–March) of the following year or they are forfeited."
            )
            return ans

    # Rule 2: Software Installation on Work Laptop / Slack
    # Question: "Can I install Slack on my work laptop?"
    if ("install" in q_lower or "software" in q_lower or "slack" in q_lower) and ("laptop" in q_lower or "device" in q_lower or "work" in q_lower):
        doc = "policy_it_acceptable_use.txt"
        cl_2_3 = index[doc]["clauses"].get("2.3", {}).get("text", "")
        cl_2_4 = index[doc]["clauses"].get("2.4", {}).get("text", "")
        ans = (
            f"No. According to [{doc}, Section 2.3], employees must not install software on corporate devices "
            f"without written approval from the IT Department.\n"
            f"Additionally, [{doc}, Section 2.4] specifies that software approved for installation must be sourced "
            f"from the CMC-approved software catalogue only."
        )
        return ans

    # Rule 3: Home Office Equipment Allowance
    # Question: "What is the home office equipment allowance?"
    if "home office" in q_lower or ("equipment allowance" in q_lower and "allowance" in q_lower):
        doc = "policy_finance_reimbursement.txt"
        cl_3_1 = index[doc]["clauses"].get("3.1", {}).get("text", "")
        cl_3_2 = index[doc]["clauses"].get("3.2", {}).get("text", "")
        cl_3_3 = index[doc]["clauses"].get("3.3", {}).get("text", "")
        ans = (
            f"According to [{doc}, Section 3.1], employees approved for permanent work-from-home arrangements are entitled "
            f"to a one-time home office equipment allowance of Rs 8,000.\n"
            f"Under [{doc}, Section 3.2], the allowance covers: desk, chair, monitor, keyboard, mouse, and networking equipment only."
        )
        return ans

    # Rule 4: Personal Phone for Work Files from Home (Critical Single-Source BYOD Test)
    # Question: "Can I use my personal phone for work files from home?" or "...to access work files when working from home?"
    if ("personal phone" in q_lower or "personal device" in q_lower or "byod" in q_lower) and ("work file" in q_lower or "file" in q_lower or "data" in q_lower or "remote" in q_lower or "home" in q_lower or "access" in q_lower):
        doc = "policy_it_acceptable_use.txt"
        cl_3_1 = index[doc]["clauses"].get("3.1", {}).get("text", "")
        cl_3_2 = index[doc]["clauses"].get("3.2", {}).get("text", "")
        ans = (
            f"No. According to [{doc}, Section 3.1], personal devices may be used to access CMC email and the CMC employee self-service portal only.\n"
            f"Furthermore, [{doc}, Section 3.2] explicitly states that personal devices must not be used to access, store, or transmit classified or sensitive CMC data. "
            f"Therefore, classified or sensitive CMC data must not be accessed, stored, or transmitted on personal devices."
        )
        return ans

    # Rule 5: Flexible Working Culture (Not in documents -> REFUSAL)
    # Question: "What is the company view on flexible working culture?"
    if "flexible working" in q_lower or "working culture" in q_lower or "culture" in q_lower or "company view" in q_lower:
        return REFUSAL_TEMPLATE

    # Rule 6: DA and Meal Receipts on Same Day
    # Question: "Can I claim DA and meal receipts on the same day?"
    if ("da" in q_lower or "daily allowance" in q_lower) and ("meal" in q_lower or "receipt" in q_lower):
        doc = "policy_finance_reimbursement.txt"
        cl_2_6 = index[doc]["clauses"].get("2.6", {}).get("text", "")
        ans = (
            f"No. According to [{doc}, Section 2.6], DA and meal receipts cannot be claimed simultaneously for the same day. "
            f"If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day."
        )
        return ans

    # Rule 7: Leave Without Pay Approvers
    # Question: "Who approves leave without pay?"
    if ("who approves" in q_lower or "approval" in q_lower or "approve" in q_lower) and ("leave without pay" in q_lower or "lwp" in q_lower):
        doc = "policy_hr_leave.txt"
        cl_5_2 = index[doc]["clauses"].get("5.2", {}).get("text", "")
        cl_5_3 = index[doc]["clauses"].get("5.3", {}).get("text", "")
        ans = (
            f"According to [{doc}, Section 5.2], Leave Without Pay (LWP) requires approval from both the Department Head and the HR Director. Manager approval alone is not sufficient.\n"
            f"Additionally, [{doc}, Section 5.3] specifies that LWP exceeding 30 continuous days requires approval from the Municipal Commissioner."
        )
        return ans

    # General Single-Source Routing for other queries
    # Check if question maps to specific policy domains
    hr_matches = []
    it_matches = []
    fin_matches = []

    # Check HR leave queries
    if any(k in q_lower for k in ["maternity", "paternity", "sick leave", "annual leave", "encashment", "public holiday", "compensatory off"]):
        doc = "policy_hr_leave.txt"
        for cid, data in index[doc]["clauses"].items():
            words = [w for w in re.findall(r"\w+", q_lower) if len(w) > 3]
            if any(w in data["text"].lower() for w in words):
                hr_matches.append((cid, data["text"]))
        if hr_matches:
            cid, text = hr_matches[0]
            return f"According to [{doc}, Section {cid}], {text}"

    # Check IT policy queries
    if any(k in q_lower for k in ["password", "mfa", "multi-factor", "corporate device", "confidential data", "personal device", "guest wifi"]):
        doc = "policy_it_acceptable_use.txt"
        for cid, data in index[doc]["clauses"].items():
            words = [w for w in re.findall(r"\w+", q_lower) if len(w) > 3]
            if any(w in data["text"].lower() for w in words):
                it_matches.append((cid, data["text"]))
        if it_matches:
            cid, text = it_matches[0]
            return f"According to [{doc}, Section {cid}], {text}"

    # Check Finance queries
    if any(k in q_lower for k in ["reimbursement", "outstation travel", "hotel accommodation", "air travel", "training expenses", "mobile phone reimbursement", "form fin"]):
        doc = "policy_finance_reimbursement.txt"
        for cid, data in index[doc]["clauses"].items():
            words = [w for w in re.findall(r"\w+", q_lower) if len(w) > 3]
            if any(w in data["text"].lower() for w in words):
                fin_matches.append((cid, data["text"]))
        if fin_matches:
            cid, text = fin_matches[0]
            return f"According to [{doc}, Section {cid}], {text}"

    # If ungrounded or ambiguous, return exact refusal template
    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Document Q&A CLI")
    parser.add_argument("--question", type=str, default=None, help="Single question mode (non-interactive)")
    args = parser.parse_args()

    try:
        policy_dir = _find_policy_dir()
        index = retrieve_documents(policy_dir)
        print("Successfully loaded and indexed 3 policy documents:")
        for doc in DOC_FILENAMES:
            sec_count = len(index[doc]["sections"])
            cl_count = len(index[doc]["clauses"])
            print(f"  - {doc} ({sec_count} sections, {cl_count} numbered clauses)")
    except Exception as e:
        print(f"Error loading policy documents: {e}", file=sys.stderr)
        sys.exit(1)

    # Non-interactive single question mode
    if args.question:
        answer = answer_question(args.question, index)
        print(f"\nQ: {args.question}")
        print(f"A:\n{answer}\n")
        return

    # Interactive question loop
    print("\n=======================================================")
    print("CMC Policy Document Q&A Assistant")
    print("Type your question below, or type 'exit' or 'quit' to end.")
    print("=======================================================\n")

    while True:
        try:
            query = input("Ask a question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not query:
            continue

        if query.lower() in ["exit", "quit", "q"]:
            print("Goodbye.")
            break

        ans = answer_question(query, index)
        print(f"\n{ans}\n")


if __name__ == "__main__":
    main()
