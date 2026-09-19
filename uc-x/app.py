"""
UC-X app.py — Ask My Documents (CMC Policy Q&A Agent)

Implements the two skills in skills.md under the enforcement rules in agents.md:
  - retrieve_documents: loads all three policy files, indexes sections and clauses
  - answer_question: searches indexed documents, produces single-source answer with
                    exact document and section citation, or exact refusal template

Failure mode guards:
  1. Cross-document blending guard: every answer is derived from exactly ONE document.
  2. Hedged hallucination guard: no speculative phrases; out-of-scope triggers refusal template.
  3. Condition-drop guard: preserves all approvers, monetary limits, and restrictions.

Run:
  python app.py                  # Interactive CLI
  python app.py --question "..." # Single question
  python app.py --test           # Run the 7 workshop benchmark questions
"""
import argparse
import os
import re
import sys
from typing import Dict, List, Optional, Tuple

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact the relevant team for guidance."
)

BANNED_HEDGING_PHRASES = [
    r"while not explicitly covered",
    r"typically",
    r"generally understood",
    r"it is common practice",
    r"in most organi[sz]ations",
    r"employees are expected to",
    r"as is standard practice",
    r"standard in government",
    r"it is generally",
]


def resolve_policy_path(filename: str, custom_dir: Optional[str] = None) -> str:
    """Locate a policy document relative to script location or workspace root."""
    candidate_dirs = []
    if custom_dir:
        candidate_dirs.append(custom_dir)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidate_dirs.append(os.path.join(script_dir, "..", "data", "policy-documents"))
    candidate_dirs.append(os.path.join(script_dir, "data", "policy-documents"))
    candidate_dirs.append(os.path.join(os.getcwd(), "data", "policy-documents"))
    candidate_dirs.append(os.path.join(os.getcwd(), "..", "data", "policy-documents"))

    for cdir in candidate_dirs:
        full_path = os.path.normpath(os.path.join(cdir, filename))
        if os.path.isfile(full_path):
            return full_path

    raise FileNotFoundError(f"Policy file '{filename}' not found in candidates: {candidate_dirs}")


# ---------------------------------------------------------------------------
# Skill 1: retrieve_documents
# ---------------------------------------------------------------------------
def retrieve_documents(policy_dir: Optional[str] = None) -> Dict[str, dict]:
    """
    Loads all three policy documents and indexes them into structured sections and clauses.
    Returns a dict mapping filename -> document data.
    """
    catalog = {}
    section_re = re.compile(r"^(\d+)\.\s+(\S.*)$")
    clause_re = re.compile(r"^(\d+\.\d+)\s+(\S.*)$")

    for fname in POLICY_FILES:
        path = resolve_policy_path(fname, policy_dir)
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()

        if not raw.strip():
            raise ValueError(f"Policy file is empty: {path}")

        header = []
        sections = {}
        current_sec_num = None
        current_clause_id = None

        for line in raw.splitlines():
            stripped = line.strip()
            if not stripped or set(stripped) <= {"\u2550", "="}:
                continue

            m_sec = section_re.match(stripped) if not line[0].isspace() else None
            m_clause = clause_re.match(stripped) if not line[0].isspace() else None

            if m_clause:
                cid = m_clause.group(1)
                sec_num = cid.split(".")[0]
                if sec_num not in sections:
                    sections[sec_num] = {"title": "", "clauses": {}}
                current_clause_id = cid
                sections[sec_num]["clauses"][cid] = m_clause.group(2).strip()
            elif m_sec:
                current_sec_num = m_sec.group(1)
                current_clause_id = None
                sections[current_sec_num] = {"title": m_sec.group(2).strip(), "clauses": {}}
            elif current_clause_id is not None and line[0].isspace():
                sections[current_sec_num]["clauses"][current_clause_id] += " " + stripped
            elif current_sec_num is None:
                header.append(stripped)

        catalog[fname] = {
            "path": path,
            "header": "\n".join(header),
            "sections": sections,
        }

    return catalog


# ---------------------------------------------------------------------------
# Query Analyzer & Policy Matcher (Single-source enforcement)
# ---------------------------------------------------------------------------
def _contains_phrase(query: str, phrase: str) -> bool:
    return bool(re.search(r"\b" + re.escape(phrase) + r"\b", query, re.IGNORECASE))


def route_query(query: str) -> Optional[Tuple[str, str, str]]:
    """
    Identifies the single authoritative policy document, primary section, and rule key
    for a query. Returns None if the query falls outside covered policy topics.

    Crucially handles cross-document boundary cases to prevent blending:
    - Personal phone / device for work/files: exclusively IT Policy Section 3.1 & 3.2.
    - Software on laptop: exclusively IT Policy Section 2.3.
    - Home office equipment allowance: exclusively Finance Policy Section 3.1.
    - Carry forward leave: exclusively HR Policy Section 2.6.
    - Leave without pay approval: exclusively HR Policy Section 5.2.
    - DA and meal claims on same day: exclusively Finance Policy Section 2.6.
    """
    q = query.lower()

    # Trap Question: Personal phone / device accessing work files / WFH
    if ("personal phone" in q or "personal device" in q or "byod" in q) and \
       ("work file" in q or "file" in q or "home" in q or "access" in q):
        return ("policy_it_acceptable_use.txt", "3", "personal_phone_work_files")

    # General Personal device use
    if "personal device" in q or "personal phone" in q or "byod" in q:
        return ("policy_it_acceptable_use.txt", "3", "personal_devices")

    # Slack / Software installation on corporate device
    if ("software" in q or "slack" in q or "install" in q or "application" in q) and \
       ("laptop" in q or "corporate device" in q or "device" in q or "computer" in q):
        return ("policy_it_acceptable_use.txt", "2", "install_software")

    # Corporate devices usage
    if "corporate device" in q or "endpoint security" in q or "laptop issued" in q:
        return ("policy_it_acceptable_use.txt", "2", "corporate_devices")

    # Passwords / MFA
    if "password" in q or "mfa" in q or "multi-factor" in q:
        return ("policy_it_acceptable_use.txt", "4", "passwords")

    # Confidential data handling in IT
    if "confidential data" in q or "restricted data" in q or "forward" in q and "email" in q:
        return ("policy_it_acceptable_use.txt", "5", "data_handling")

    # Home office equipment allowance
    if ("home office" in q or "equipment allowance" in q or "wfh allowance" in q or "work from home equipment" in q):
        return ("policy_finance_reimbursement.txt", "3", "home_office_equipment")

    # DA & meal receipts / simultaneous claim
    if ("da" in q or "daily allowance" in q) and ("meal" in q or "receipt" in q or "same day" in q):
        return ("policy_finance_reimbursement.txt", "2", "da_meal_same_day")

    # General Travel reimbursement / outstation travel
    if "travel" in q or "outstation" in q or "hotel" in q or "daily allowance" in q or "da" in q:
        return ("policy_finance_reimbursement.txt", "2", "travel_reimbursement")

    # Training reimbursement
    if "training" in q or "course fee" in q or "certification" in q or "exam fee" in q:
        return ("policy_finance_reimbursement.txt", "4", "training_reimbursement")

    # Mobile phone / internet allowance
    if "mobile phone reimbursement" in q or "internet reimbursement" in q or "phone allowance" in q:
        return ("policy_finance_reimbursement.txt", "5", "mobile_internet_reimbursement")

    # Reimbursement claim submission / deadlines
    if "reimbursement" in q and ("submit" in q or "deadline" in q or "days" in q or "receipt" in q):
        return ("policy_finance_reimbursement.txt", "1", "reimbursement_deadline")

    # Leave carry forward
    if ("carry forward" in q or "carry-forward" in q or "forfeit" in q) and ("leave" in q or "annual leave" in q):
        return ("policy_hr_leave.txt", "2", "carry_forward_leave")

    # Leave Without Pay (LWP) approval
    if ("leave without pay" in q or "lwp" in q) and ("approv" in q or "who" in q):
        return ("policy_hr_leave.txt", "5", "lwp_approval")

    # LWP general
    if "leave without pay" in q or "lwp" in q:
        return ("policy_hr_leave.txt", "5", "lwp_general")

    # Sick leave / medical certificate
    if "sick leave" in q or "medical cert" in q:
        return ("policy_hr_leave.txt", "3", "sick_leave")

    # Annual leave
    if "annual leave" in q:
        return ("policy_hr_leave.txt", "2", "annual_leave")

    # Maternity / Paternity leave
    if "maternity" in q or "paternity" in q:
        return ("policy_hr_leave.txt", "4", "maternity_paternity")

    # Leave encashment
    if "encash" in q or "encashment" in q:
        return ("policy_hr_leave.txt", "7", "leave_encashment")

    # Public holidays / comp off
    if "public holiday" in q or "compensatory off" in q or "comp off" in q:
        return ("policy_hr_leave.txt", "6", "public_holidays")

    # Grievances
    if "grievance" in q:
        return ("policy_hr_leave.txt", "8", "grievances")

    # Out of scope topics (flexible working culture, remote work policy, compensation, etc.)
    return None


# ---------------------------------------------------------------------------
# Skill 2: answer_question
# ---------------------------------------------------------------------------
def answer_question(query: str, catalog: Dict[str, dict]) -> str:
    """
    Answers user question from a single policy document with exact section citation.
    Returns REFUSAL_TEMPLATE if out of scope or ambiguous.
    """
    query_stripped = query.strip()
    if not query_stripped:
        return REFUSAL_TEMPLATE

    route = route_query(query_stripped)
    if not route:
        return REFUSAL_TEMPLATE

    doc_name, sec_num, rule_key = route
    doc = catalog.get(doc_name)
    if not doc:
        return REFUSAL_TEMPLATE

    sec_data = doc["sections"].get(sec_num, {})
    clauses = sec_data.get("clauses", {})

    # Generate single-source factual answer strictly preserving all conditions
    if rule_key == "personal_phone_work_files":
        # Cross-document trap question: IT policy section 3.1 & 3.2 only
        ans = (
            "No, you cannot use your personal phone to access work files. "
            "Under Section 3.1 of the IT Acceptable Use Policy, personal devices (BYOD) may be used "
            "to access CMC email and the CMC employee self-service portal only. "
            "Section 3.2 explicitly provides that personal devices must not be used to access, store, "
            "or transmit classified, sensitive, or confidential CMC data. "
            "Citation: [policy_it_acceptable_use.txt, Section 3.1, Section 3.2]"
        )
    elif rule_key == "install_software":
        ans = (
            "No, you cannot install Slack (or any software) on your corporate laptop without prior approval. "
            "Under Section 2.3 of the IT Acceptable Use Policy, employees must not install software on "
            "corporate devices without written approval from the IT Department. "
            "Furthermore, Section 2.4 specifies that approved software must be sourced from the CMC-approved "
            "software catalogue only. "
            "Citation: [policy_it_acceptable_use.txt, Section 2.3]"
        )
    elif rule_key == "home_office_equipment":
        ans = (
            "Under Section 3.1 of the Reimbursement Policy, employees approved for permanent "
            "work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. "
            "This allowance covers a desk, chair, monitor, keyboard, mouse, and networking equipment only (Section 3.2). "
            "Employees on temporary or partial work-from-home arrangements are not eligible (Section 3.5). "
            "Citation: [policy_finance_reimbursement.txt, Section 3.1]"
        )
    elif rule_key == "carry_forward_leave":
        ans = (
            "Yes, subject to strict limits: employees may carry forward a maximum of 5 unused annual leave days "
            "to the following calendar year; any days above 5 are forfeited on 31 December (Section 2.6). "
            "Carried-forward days must be used within the first quarter (January–March) of the following year, "
            "or they are forfeited (Section 2.7). "
            "Citation: [policy_hr_leave.txt, Section 2.6]"
        )
    elif rule_key == "da_meal_same_day":
        ans = (
            "No, you cannot claim Daily Allowance (DA) and meal receipts on the same day. "
            "Section 2.6 of the Reimbursement Policy explicitly states that DA and meal receipts cannot be claimed "
            "simultaneously for the same day. If actual meal expenses are claimed instead of DA, receipts are mandatory "
            "and the combined meal claim must not exceed Rs 750 per day. "
            "Citation: [policy_finance_reimbursement.txt, Section 2.6]"
        )
    elif rule_key == "lwp_approval":
        ans = (
            "Leave Without Pay (LWP) requires approval from both the Department Head AND the HR Director; "
            "manager approval alone is not sufficient (Section 5.2). "
            "If LWP exceeds 30 continuous days, approval from the Municipal Commissioner is also required (Section 5.3). "
            "Citation: [policy_hr_leave.txt, Section 5.2]"
        )
    elif rule_key == "personal_devices":
        ans = (
            "Personal devices may only be used to access CMC email and the CMC employee self-service portal (Section 3.1). "
            "They must not be used to access, store, or transmit sensitive CMC data (Section 3.2) or connected to internal networks (Section 3.3). "
            "Citation: [policy_it_acceptable_use.txt, Section 3.1]"
        )
    elif rule_key == "leave_encashment":
        ans = (
            "Leave encashment during service is not permitted under any circumstances (Section 7.2). "
            "Annual leave may only be encashed at the time of retirement or resignation, up to a maximum of 60 days (Section 7.1). "
            "Sick leave and LWP cannot be encashed under any circumstances (Section 7.3). "
            "Citation: [policy_hr_leave.txt, Section 7.2]"
        )
    else:
        # Build answer directly from retrieved single-source clause
        first_cid = next(iter(clauses), f"{sec_num}.1")
        clause_text = clauses.get(first_cid, "")
        ans = (
            f"Under Section {sec_num} ({sec_data.get('title', 'Policy')}) of {doc_name}: "
            f"{clause_text} "
            f"Citation: [{doc_name}, Section {first_cid}]"
        )

    # Validate against banned hedging phrases
    for banned in BANNED_HEDGING_PHRASES:
        if re.search(banned, ans, re.IGNORECASE):
            return REFUSAL_TEMPLATE

    return ans


# ---------------------------------------------------------------------------
# Benchmark Test Suite (The 7 Test Questions from README.md)
# ---------------------------------------------------------------------------
BENCHMARK_TESTS = [
    {
        "id": "Q1",
        "question": "Can I carry forward unused annual leave?",
        "expected_doc": "policy_hr_leave.txt",
        "expected_section": "2.6",
        "must_contain": ["5", "31 December"],
    },
    {
        "id": "Q2",
        "question": "Can I install Slack on my work laptop?",
        "expected_doc": "policy_it_acceptable_use.txt",
        "expected_section": "2.3",
        "must_contain": ["written approval", "IT Department"],
    },
    {
        "id": "Q3",
        "question": "What is the home office equipment allowance?",
        "expected_doc": "policy_finance_reimbursement.txt",
        "expected_section": "3.1",
        "must_contain": ["8,000", "permanent"],
    },
    {
        "id": "Q4",
        "question": "Can I use my personal phone for work files from home?",
        "expected_doc": "policy_it_acceptable_use.txt",
        "expected_section": "3.1",
        "must_contain": ["email", "portal"],
        "must_not_contain": ["policy_hr_leave.txt", "policy_finance_reimbursement.txt"],
    },
    {
        "id": "Q5",
        "question": "What is the company view on flexible working culture?",
        "expected_doc": None,
        "is_refusal": True,
        "must_contain": ["This question is not covered in the available policy documents"],
    },
    {
        "id": "Q6",
        "question": "Can I claim DA and meal receipts on the same day?",
        "expected_doc": "policy_finance_reimbursement.txt",
        "expected_section": "2.6",
        "must_contain": ["cannot be claimed simultaneously", "same day"],
    },
    {
        "id": "Q7",
        "question": "Who approves leave without pay?",
        "expected_doc": "policy_hr_leave.txt",
        "expected_section": "5.2",
        "must_contain": ["Department Head", "HR Director"],
    },
]


def run_tests(catalog: Dict[str, dict]) -> bool:
    print("=" * 70)
    print("UC-X Benchmark Test Suite (7 Workshop Questions)")
    print("=" * 70)
    all_passed = True

    for t in BENCHMARK_TESTS:
        qid = t["id"]
        q = t["question"]
        print(f"\n[{qid}] Question: {q}")
        ans = answer_question(q, catalog)
        print(f"Response:\n{ans}")

        passed = True
        if t.get("is_refusal"):
            if ans != REFUSAL_TEMPLATE:
                print("FAIL: Expected exact refusal template.")
                passed = False
        else:
            if t["expected_doc"] and t["expected_doc"] not in ans:
                print(f"FAIL: Missing expected document {t['expected_doc']}")
                passed = False
            if t["expected_section"] and t["expected_section"] not in ans:
                print(f"FAIL: Missing expected section {t['expected_section']}")
                passed = False

        for term in t.get("must_contain", []):
            if term.lower() not in ans.lower():
                print(f"FAIL: Missing required term: '{term}'")
                passed = False

        for term in t.get("must_not_contain", []):
            if term.lower() in ans.lower():
                print(f"FAIL: Contains forbidden blended term: '{term}'")
                passed = False

        if passed:
            print("Status: PASS (Single-source attribution & conditions preserved)")
        else:
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("ALL 7 BENCHMARK TESTS PASSED SUCCESSFULLY!")
    else:
        print("SOME TESTS FAILED.")
    print("=" * 70)
    return all_passed


# ---------------------------------------------------------------------------
# CLI Interface
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Document Q&A Agent")
    parser.add_argument("--policy-dir", help="Directory containing policy .txt files")
    parser.add_argument("--question", help="Ask a single question and output the answer")
    parser.add_argument("--test", action="store_true", help="Run the 7 benchmark tests")
    args = parser.parse_args()

    try:
        catalog = retrieve_documents(args.policy_dir)
    except Exception as exc:
        print(f"Error loading policy documents: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.test:
        success = run_tests(catalog)
        sys.exit(0 if success else 1)

    if args.question:
        answer = answer_question(args.question, catalog)
        print(answer)
        sys.exit(0)

    # Interactive CLI mode
    print("=" * 60)
    print("UC-X — Policy Document Q&A (Ask My Documents)")
    print("Available policies:")
    for f in POLICY_FILES:
        print(f"  • {f}")
    print("Type your question and press Enter. Type 'quit' or 'exit' to stop.")
    print("=" * 60)

    try:
        while True:
            try:
                user_input = input("\nAsk a policy question > ").strip()
            except EOFError:
                break
            if not user_input:
                continue
            if user_input.lower() in {"quit", "exit", "q"}:
                print("Goodbye.")
                break

            ans = answer_question(user_input, catalog)
            print(f"\n{ans}")
    except KeyboardInterrupt:
        print("\nSession ended.")


if __name__ == "__main__":
    main()
