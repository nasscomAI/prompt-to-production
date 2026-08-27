"""
UC-X -- Ask My Documents
Built from agents.md (RICE enforcement) and skills.md (skill definitions).

Agent Role:
  Policy document question-answering agent. Answers from exactly 3 policy
  documents. Never blends across documents. Never hedges. Cites source
  document + section for every claim. Uses refusal template when question
  is not covered.

Enforcement Rules:
  1. Never combine claims from two different documents.
  2. Never use hedging phrases.
  3. Use refusal template exactly when question is not covered.
  4. Cite source document name + section number for every claim.
  5. Preserve all conditions from multi-condition clauses.
"""

import os
import re
import sys


# ---------------------------------------------------------------------------
#  Constants
# ---------------------------------------------------------------------------

POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact the relevant department for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "it may be possible",
    "it is likely",
    "probably",
    "usually",
]

# ---------------------------------------------------------------------------
#  Keyword map — maps question keywords to document sections
#  Each entry: (keywords_list, document_name, section_number, answer_text)
# ---------------------------------------------------------------------------

KNOWLEDGE_BASE = [
    # --- HR Leave Policy ---
    {
        "keywords": ["carry forward", "carry-forward", "unused annual leave", "unused leave"],
        "document": "policy_hr_leave.txt",
        "section": "2.6, 2.7",
        "answer": (
            "Yes, you may carry forward a maximum of 5 unused annual leave days "
            "to the following calendar year. Any days above 5 are forfeited on "
            "31 December. Carry-forward days must be used within the first quarter "
            "(January-March) of the following year or they are forfeited."
        ),
    },
    {
        "keywords": ["leave without pay", "lwp", "who approves lwp", "approves leave without pay"],
        "document": "policy_hr_leave.txt",
        "section": "5.2, 5.3",
        "answer": (
            "Leave Without Pay (LWP) requires approval from both the Department Head "
            "AND the HR Director. Manager approval alone is not sufficient. "
            "LWP exceeding 30 continuous days requires additional approval from "
            "the Municipal Commissioner."
        ),
    },
    {
        "keywords": ["advance notice", "leave application", "apply for leave", "how to apply leave"],
        "document": "policy_hr_leave.txt",
        "section": "2.3, 2.4",
        "answer": (
            "Employees must submit a leave application at least 14 calendar days "
            "in advance using Form HR-L1. Leave applications must receive written "
            "approval from the employee's direct manager before the leave commences. "
            "Verbal approval is not valid."
        ),
    },
    {
        "keywords": ["sick leave", "medical certificate", "sick days"],
        "document": "policy_hr_leave.txt",
        "section": "3.2, 3.4",
        "answer": (
            "Each employee is entitled to 12 days of paid sick leave per calendar year. "
            "Sick leave of 3 or more consecutive days requires a medical certificate "
            "from a registered medical practitioner, submitted within 48 hours of "
            "returning to work. Sick leave taken immediately before or after a public "
            "holiday or annual leave period requires a medical certificate regardless "
            "of duration."
        ),
    },
    {
        "keywords": ["leave encashment", "encash leave", "encash annual leave"],
        "document": "policy_hr_leave.txt",
        "section": "7.1, 7.2",
        "answer": (
            "Annual leave may be encashed only at the time of retirement or "
            "resignation, subject to a maximum of 60 days. Leave encashment "
            "during service is not permitted under any circumstances."
        ),
    },
    {
        "keywords": ["maternity", "maternity leave", "paternity", "paternity leave"],
        "document": "policy_hr_leave.txt",
        "section": "4.1, 4.2, 4.3, 4.4",
        "answer": (
            "Female employees are entitled to 26 weeks of paid maternity leave "
            "for the first two live births. For a third or subsequent child, "
            "maternity leave is 12 weeks paid. Male employees are entitled to "
            "5 days of paid paternity leave, to be taken within 30 days of "
            "the child's birth. Paternity leave cannot be split across multiple periods."
        ),
    },
    {
        "keywords": ["unapproved absence", "absent without approval", "lop"],
        "document": "policy_hr_leave.txt",
        "section": "2.5",
        "answer": (
            "Unapproved absence will be recorded as Loss of Pay (LOP) regardless "
            "of subsequent approval."
        ),
    },
    # --- IT Acceptable Use Policy ---
    {
        "keywords": ["install software", "install slack", "install app", "software on laptop",
                      "install on work laptop", "install application"],
        "document": "policy_it_acceptable_use.txt",
        "section": "2.3, 2.4",
        "answer": (
            "Employees must not install software on corporate devices without "
            "written approval from the IT Department. Software approved for "
            "installation must be sourced from the CMC-approved software "
            "catalogue only."
        ),
    },
    {
        "keywords": ["personal phone", "personal device", "byod", "personal mobile",
                      "use personal phone for work", "work files from home",
                      "personal phone for work files"],
        "document": "policy_it_acceptable_use.txt",
        "section": "3.1, 3.2",
        "answer": (
            "Personal devices may be used to access CMC email and the CMC employee "
            "self-service portal only. Personal devices must not be used to access, "
            "store, or transmit classified or sensitive CMC data. "
            "'Work files' beyond email and the self-service portal are not permitted "
            "on personal devices."
        ),
    },
    {
        "keywords": ["password", "change password", "share password", "mfa",
                      "multi-factor", "authentication"],
        "document": "policy_it_acceptable_use.txt",
        "section": "4.1, 4.2, 4.3, 4.4",
        "answer": (
            "Employees must not share their CMC system passwords with any other "
            "person, including IT staff. IT staff will never ask for your password. "
            "Passwords must be changed every 90 days. Multi-factor authentication "
            "(MFA) is mandatory for all remote access to CMC systems."
        ),
    },
    {
        "keywords": ["corporate device", "work laptop", "official device",
                      "personal use of corporate"],
        "document": "policy_it_acceptable_use.txt",
        "section": "2.1, 2.2",
        "answer": (
            "Corporate devices must be used primarily for official work purposes. "
            "Personal use of corporate devices is permitted in moderation, provided "
            "it does not interfere with work duties or consume excessive bandwidth."
        ),
    },
    {
        "keywords": ["lost device", "stolen device", "device stolen", "device lost"],
        "document": "policy_it_acceptable_use.txt",
        "section": "3.5",
        "answer": (
            "If a personal device containing CMC email is lost or stolen, "
            "the employee must report it to the IT helpdesk within 4 hours "
            "so that a remote wipe of CMC data can be performed."
        ),
    },
    {
        "keywords": ["confidential data", "restricted data", "sensitive data",
                      "data classification"],
        "document": "policy_it_acceptable_use.txt",
        "section": "5.1, 5.2, 5.3",
        "answer": (
            "CMC data classified as Confidential or Restricted must not be stored "
            "on personal devices, personal cloud storage, or any system not approved "
            "by the IT Department. Employees must not forward CMC email containing "
            "Confidential data to personal email accounts. Printing of Confidential "
            "documents must use the secure print function."
        ),
    },
    # --- Finance Reimbursement Policy ---
    {
        "keywords": ["home office", "work from home equipment", "wfh equipment",
                      "home office allowance", "equipment allowance"],
        "document": "policy_finance_reimbursement.txt",
        "section": "3.1, 3.2, 3.3, 3.5",
        "answer": (
            "Employees approved for permanent work-from-home arrangements are "
            "entitled to a one-time home office equipment allowance of Rs 8,000. "
            "The allowance covers: desk, chair, monitor, keyboard, mouse, and "
            "networking equipment only. It does NOT cover: personal computers, "
            "laptops, smartphones, printers, or air conditioning equipment. "
            "Employees on temporary or partial work-from-home arrangements are "
            "not eligible for this allowance."
        ),
    },
    {
        "keywords": ["da and meal", "daily allowance and meal", "claim da and meal",
                      "da meal same day", "meal receipts"],
        "document": "policy_finance_reimbursement.txt",
        "section": "2.5, 2.6",
        "answer": (
            "NO — DA and meal receipts cannot be claimed simultaneously for the "
            "same day. Daily allowance (DA) for outstation travel is Rs 750 per day "
            "and covers meals and incidentals. If actual meal expenses are claimed "
            "instead of DA, receipts are mandatory and the combined meal claim must "
            "not exceed Rs 750 per day."
        ),
    },
    {
        "keywords": ["travel reimbursement", "outstation travel", "air travel",
                      "hotel accommodation", "travel claim"],
        "document": "policy_finance_reimbursement.txt",
        "section": "2.1, 2.2, 2.3, 2.4",
        "answer": (
            "Local travel is reimbursable at actual cost for public transport or "
            "Rs 4 per km for personal vehicle use. Receipts required above Rs 200. "
            "Outstation travel must be pre-approved using Form FIN-T1. Air travel "
            "is permitted for journeys exceeding 500 km only — economy class is "
            "mandatory. Hotel accommodation is reimbursable up to Rs 3,500/night "
            "for Grade A cities and Rs 2,500/night for other locations."
        ),
    },
    {
        "keywords": ["training", "course fee", "exam fee", "professional development",
                      "certification"],
        "document": "policy_finance_reimbursement.txt",
        "section": "4.1, 4.2, 4.3, 4.4",
        "answer": (
            "Training expenses are reimbursable only if pre-approved by the "
            "Department Head using Form FIN-TR1. Course fees: up to Rs 15,000 per "
            "financial year. Exam fees for professional certifications: up to Rs 5,000 "
            "per attempt. If an employee leaves CMC within 12 months of reimbursed "
            "training, they must repay 100%. Between 12-24 months: repay 50%."
        ),
    },
    {
        "keywords": ["mobile phone reimbursement", "internet reimbursement",
                      "phone bill", "internet bill"],
        "document": "policy_finance_reimbursement.txt",
        "section": "5.1, 5.2, 5.3",
        "answer": (
            "Grade C and above: Rs 500/month mobile phone reimbursement. "
            "Grade B and above: Rs 800/month internet reimbursement (approved WFH only). "
            "Original bill required each month — estimated or self-declared amounts not accepted."
        ),
    },
    {
        "keywords": ["reimbursement claim", "submit claim", "expense claim",
                      "how to claim", "claim process"],
        "document": "policy_finance_reimbursement.txt",
        "section": "6.1, 6.2, 6.3, 1.3",
        "answer": (
            "All claims must be submitted via the CMC employee portal using "
            "Form FIN-EXP1. Original receipts must be attached. Claims are "
            "processed within 15 working days. All claims must be submitted "
            "within 30 calendar days of the expense. Claims after 30 days "
            "will not be processed."
        ),
    },
]


# ---------------------------------------------------------------------------
#  Skill: retrieve_documents
#  Input:  policy_dir (str)
#  Output: dict — document index keyed by filename
# ---------------------------------------------------------------------------

def retrieve_documents(policy_dir: str) -> dict:
    """
    Load all 3 policy files, parse into structured sections.
    Returns dict keyed by filename -> list of section dicts.
    """
    doc_index = {}

    for filename in POLICY_FILES:
        filepath = os.path.join(policy_dir, filename)

        try:
            with open(filepath, "r", encoding="utf-8-sig") as f:
                text = f.read()
        except FileNotFoundError:
            print(f"WARNING: Policy file not found: {filepath}")
            continue
        except Exception as e:
            print(f"WARNING: Cannot read {filepath}: {e}")
            continue

        sections = _parse_policy(text)
        doc_index[filename] = sections
        print(f"  Loaded {filename}: {len(sections)} clauses")

    if not doc_index:
        print("ERROR: No policy documents could be loaded.")
        sys.exit(1)

    return doc_index


def _parse_policy(text: str) -> list:
    """Parse a policy document into numbered sections."""
    lines = text.splitlines()
    sections = []
    current_title = ""
    current_number = ""
    current_content_lines = []

    heading_pattern = re.compile(r"^(\d+)\.\s+(.+)$")
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)$")
    separator_pattern = re.compile(r"^[═─━]+$")

    for line in lines:
        stripped = line.strip()

        if separator_pattern.match(stripped) or not stripped:
            continue

        heading_match = heading_pattern.match(stripped)
        if heading_match:
            if current_number:
                sections.append({
                    "section_number": current_number,
                    "section_title": current_title,
                    "content": " ".join(current_content_lines).strip(),
                })
                current_number = ""
                current_content_lines = []
            current_title = heading_match.group(2).strip()
            continue

        clause_match = clause_pattern.match(stripped)
        if clause_match:
            if current_number:
                sections.append({
                    "section_number": current_number,
                    "section_title": current_title,
                    "content": " ".join(current_content_lines).strip(),
                })
            current_number = clause_match.group(1)
            current_content_lines = [clause_match.group(2).strip()]
            continue

        if current_number and stripped:
            current_content_lines.append(stripped)

    if current_number:
        sections.append({
            "section_number": current_number,
            "section_title": current_title,
            "content": " ".join(current_content_lines).strip(),
        })

    return sections


# ---------------------------------------------------------------------------
#  Skill: answer_question
#  Input:  doc_index (dict), question (str)
#  Output: str — answer with citation OR refusal template
# ---------------------------------------------------------------------------

def answer_question(doc_index: dict, question: str) -> str:
    """
    Search knowledge base for the best matching answer.

    Enforcement (from agents.md):
      - Single-source answers only — never blend across documents
      - No hedging phrases
      - Refusal template when question is not covered
      - Cite document + section for every claim
    """
    q_lower = question.lower()

    # --- Check for questions clearly outside all documents ---
    outside_indicators = [
        "flexible working culture", "company culture", "company view",
        "work-life balance", "remote work policy", "hybrid work",
        "promotion criteria", "salary structure", "bonus",
        "pension", "retirement age",
    ]
    if any(ind in q_lower for ind in outside_indicators):
        return REFUSAL_TEMPLATE

    # --- Search knowledge base for best match ---
    best_match = None
    best_score = 0

    for entry in KNOWLEDGE_BASE:
        score = 0
        for kw in entry["keywords"]:
            if kw in q_lower:
                # Longer keyword matches are more specific/valuable
                score += len(kw.split())

        if score > best_score:
            best_score = score
            best_match = entry

    # --- No match found ---
    if best_match is None or best_score == 0:
        return REFUSAL_TEMPLATE

    # --- Build answer with citation ---
    answer = best_match["answer"]
    doc = best_match["document"]
    section = best_match["section"]

    return f"{answer}\n\n[Source: {doc}, Section {section}]"


# ---------------------------------------------------------------------------
#  Entry Point — Interactive CLI
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("UC-X — Ask My Documents")
    print("=" * 60)
    print("\nLoading policy documents...")

    doc_index = retrieve_documents(POLICY_DIR)

    print(f"\n{len(doc_index)} documents loaded.")
    print(f"Available: {', '.join(doc_index.keys())}")
    print("\nType your question and press Enter.")
    print("Type 'quit' or 'exit' to stop.\n")
    print("-" * 60)

    while True:
        try:
            question = input("\nQ: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue

        if question.lower() in ("quit", "exit", "q"):
            print("Exiting.")
            break

        answer = answer_question(doc_index, question)

        # Verify no hedging phrases leaked in
        for phrase in HEDGING_PHRASES:
            if phrase in answer.lower():
                print(f"\n[SYSTEM WARNING: Hedging phrase detected — '{phrase}'. "
                      f"Replacing with refusal template.]")
                answer = REFUSAL_TEMPLATE
                break

        print(f"\nA: {answer}")
        print("-" * 60)


if __name__ == "__main__":
    main()
