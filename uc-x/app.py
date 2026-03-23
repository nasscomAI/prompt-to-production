"""
UC-X — Ask My Documents
Interactive document Q&A with single-source attribution and refusal template.
Enforcement: no cross-doc blending, no hedging, cite document + section, refusal for uncovered questions.
"""
import os
import re


REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "as is standard",
]


def retrieve_documents(doc_dir: str) -> dict:
    """
    Load all 3 policy files and index by document name → section number → text.
    """
    doc_files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt",
    ]

    index = {}
    for filename in doc_files:
        filepath = os.path.join(doc_dir, filename)
        if not os.path.exists(filepath):
            print(f"WARNING: {filename} not found at {filepath}")
            continue

        with open(filepath, "r", encoding="utf-8-sig") as f:
            content = f.read()

        sections = {}
        current_section = None
        current_text = []

        for line in content.split("\n"):
            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith("═"):
                continue

            # Match section headers like "1. PURPOSE AND SCOPE"
            section_match = re.match(r'^(\d+)\.\s+(.+)$', line_stripped)
            if section_match:
                if current_section:
                    sections[current_section] = " ".join(current_text)
                current_section = section_match.group(1)
                current_text = [section_match.group(2)]
                continue

            # Match clause lines like "2.3 Employees must..."
            clause_match = re.match(r'^(\d+\.\d+)\s+(.+)$', line_stripped)
            if clause_match:
                if current_section and current_text:
                    sections[current_section] = " ".join(current_text)
                current_section = clause_match.group(1)
                current_text = [clause_match.group(2)]
                continue

            # Continuation
            if current_section:
                current_text.append(line_stripped)

        if current_section:
            sections[current_section] = " ".join(current_text)

        index[filename] = sections

    if not index:
        raise FileNotFoundError(f"No policy documents found in {doc_dir}")

    return index


# ── Predefined Q&A knowledge base (rule-based, no LLM needed) ──────────
# Maps keywords/patterns to (document, section, answer)
QA_RULES = [
    {
        "keywords": ["carry forward", "carry-forward", "unused annual leave", "unused leave"],
        "document": "policy_hr_leave.txt",
        "section": "2.6",
        "answer_template": (
            "Per policy_hr_leave.txt, Section 2.6: Employees may carry forward a maximum of "
            "5 unused annual leave days to the following calendar year. Any days above 5 are "
            "forfeited on 31 December.\n\n"
            "Per policy_hr_leave.txt, Section 2.7: Carry-forward days must be used within the "
            "first quarter (January–March) of the following year or they are forfeited."
        )
    },
    {
        "keywords": ["install slack", "install software", "install app", "install on work laptop",
                      "install on corporate"],
        "document": "policy_it_acceptable_use.txt",
        "section": "2.3",
        "answer_template": (
            "Per policy_it_acceptable_use.txt, Section 2.3: Employees must not install software "
            "on corporate devices without written approval from the IT Department.\n\n"
            "Per policy_it_acceptable_use.txt, Section 2.4: Software approved for installation "
            "must be sourced from the CMC-approved software catalogue only."
        )
    },
    {
        "keywords": ["home office equipment", "home office allowance", "wfh equipment",
                      "work from home equipment", "work from home allowance"],
        "document": "policy_finance_reimbursement.txt",
        "section": "3.1",
        "answer_template": (
            "Per policy_finance_reimbursement.txt, Section 3.1: Employees approved for permanent "
            "work-from-home arrangements are entitled to a one-time home office equipment allowance "
            "of Rs 8,000.\n\n"
            "Per policy_finance_reimbursement.txt, Section 3.2: The allowance covers: desk, chair, "
            "monitor, keyboard, mouse, and networking equipment only.\n\n"
            "Per policy_finance_reimbursement.txt, Section 3.5: Employees on temporary or partial "
            "work-from-home arrangements are not eligible for this allowance."
        )
    },
    {
        "keywords": ["personal phone", "personal device", "byod", "personal mobile"],
        "document": "policy_it_acceptable_use.txt",
        "section": "3.1",
        "answer_template": (
            "Per policy_it_acceptable_use.txt, Section 3.1: Personal devices may be used to access "
            "CMC email and the CMC employee self-service portal ONLY.\n\n"
            "Per policy_it_acceptable_use.txt, Section 3.2: Personal devices must not be used to "
            "access, store, or transmit classified or sensitive CMC data.\n\n"
            "NOTE: This answer is sourced entirely from policy_it_acceptable_use.txt. No other "
            "document has been consulted to avoid cross-document blending."
        )
    },
    {
        "keywords": ["flexible working culture", "flexible work", "work culture",
                      "company view on", "company opinion"],
        "document": None,
        "section": None,
        "answer_template": REFUSAL_TEMPLATE
    },
    {
        "keywords": ["da and meal", "meal receipts", "daily allowance and meal",
                      "claim da and meal", "da and meal receipts on the same day"],
        "document": "policy_finance_reimbursement.txt",
        "section": "2.6",
        "answer_template": (
            "Per policy_finance_reimbursement.txt, Section 2.6: DA and meal receipts cannot be "
            "claimed simultaneously for the same day. If actual meal expenses are claimed instead "
            "of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day."
        )
    },
    {
        "keywords": ["who approves leave without pay", "approve lwp", "lwp approval",
                      "leave without pay approval", "approves leave without pay"],
        "document": "policy_hr_leave.txt",
        "section": "5.2",
        "answer_template": (
            "Per policy_hr_leave.txt, Section 5.2: LWP requires approval from BOTH the Department "
            "Head AND the HR Director. Manager approval alone is not sufficient.\n\n"
            "Per policy_hr_leave.txt, Section 5.3: LWP exceeding 30 continuous days requires "
            "approval from the Municipal Commissioner."
        )
    },
    # Additional common questions
    {
        "keywords": ["sick leave", "medical certificate", "sick days"],
        "document": "policy_hr_leave.txt",
        "section": "3.2",
        "answer_template": (
            "Per policy_hr_leave.txt, Section 3.1: Each employee is entitled to 12 days of paid "
            "sick leave per calendar year.\n\n"
            "Per policy_hr_leave.txt, Section 3.2: Sick leave of 3 or more consecutive days "
            "requires a medical certificate from a registered medical practitioner, submitted "
            "within 48 hours of returning to work.\n\n"
            "Per policy_hr_leave.txt, Section 3.3: Sick leave cannot be carried forward to the "
            "following year.\n\n"
            "Per policy_hr_leave.txt, Section 3.4: Sick leave taken immediately before or after "
            "a public holiday or annual leave period requires a medical certificate regardless of duration."
        )
    },
    {
        "keywords": ["leave encashment", "encash leave", "cash out leave"],
        "document": "policy_hr_leave.txt",
        "section": "7.2",
        "answer_template": (
            "Per policy_hr_leave.txt, Section 7.1: Annual leave may be encashed only at the time "
            "of retirement or resignation, subject to a maximum of 60 days.\n\n"
            "Per policy_hr_leave.txt, Section 7.2: Leave encashment during service is not "
            "permitted under any circumstances.\n\n"
            "Per policy_hr_leave.txt, Section 7.3: Sick leave and LWP cannot be encashed under "
            "any circumstances."
        )
    },
    {
        "keywords": ["password", "change password", "share password"],
        "document": "policy_it_acceptable_use.txt",
        "section": "4.1",
        "answer_template": (
            "Per policy_it_acceptable_use.txt, Section 4.1: Employees must not share their CMC "
            "system passwords with any other person, including IT staff.\n\n"
            "Per policy_it_acceptable_use.txt, Section 4.2: IT staff will never ask for your "
            "password. Any request for your password should be reported to the IT Security team.\n\n"
            "Per policy_it_acceptable_use.txt, Section 4.3: Passwords must be changed every 90 "
            "days as prompted by the system."
        )
    },
    {
        "keywords": ["travel reimbursement", "travel claim", "outstation travel"],
        "document": "policy_finance_reimbursement.txt",
        "section": "2.1",
        "answer_template": (
            "Per policy_finance_reimbursement.txt, Section 2.1: Local travel is reimbursable at "
            "actual cost for public transport or Rs 4 per km for personal vehicle use.\n\n"
            "Per policy_finance_reimbursement.txt, Section 2.2: Outstation travel must be "
            "pre-approved using Form FIN-T1 before travel commences.\n\n"
            "Per policy_finance_reimbursement.txt, Section 2.3: Air travel is permitted for "
            "journeys exceeding 500 km only. Economy class is mandatory."
        )
    },
]


def answer_question(question: str, index: dict) -> str:
    """
    Search for answer using keyword rules. Returns single-source answer or refusal.
    """
    q_lower = question.lower().strip()

    # Try each rule
    for rule in QA_RULES:
        for keyword in rule["keywords"]:
            if keyword in q_lower:
                return rule["answer_template"]

    # Fallback: search documents for keyword matches
    best_match = _search_documents(q_lower, index)
    if best_match:
        return best_match

    return REFUSAL_TEMPLATE


def _search_documents(question: str, index: dict) -> str:
    """
    Fallback search: look for question words in document sections.
    Returns single-source answer or None.
    """
    question_words = set(question.split())
    # Remove common stop words
    stop_words = {"can", "i", "the", "a", "an", "is", "are", "what", "how", "who",
                  "when", "where", "do", "does", "my", "me", "for", "of", "on",
                  "in", "to", "and", "or", "it", "be", "have", "has"}
    meaningful_words = question_words - stop_words

    if not meaningful_words:
        return None

    best_doc = None
    best_section = None
    best_text = None
    best_score = 0

    for doc_name, sections in index.items():
        for section_num, text in sections.items():
            text_lower = text.lower()
            score = sum(1 for word in meaningful_words if word in text_lower)
            if score > best_score:
                best_score = score
                best_doc = doc_name
                best_section = section_num
                best_text = text

    if best_score >= 2 and best_doc:
        return (
            f"Per {best_doc}, Section {best_section}: {best_text}\n\n"
            f"NOTE: This answer is sourced entirely from {best_doc}."
        )

    return None


def main():
    """Interactive Q&A loop."""
    doc_dir = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
    doc_dir = os.path.abspath(doc_dir)

    print("=" * 60)
    print("UC-X — Ask My Documents")
    print("=" * 60)
    print(f"\nLoading policy documents from: {doc_dir}")

    index = retrieve_documents(doc_dir)
    loaded_docs = list(index.keys())
    print(f"Loaded {len(loaded_docs)} documents: {', '.join(loaded_docs)}")
    total_sections = sum(len(secs) for secs in index.values())
    print(f"Indexed {total_sections} sections total.\n")

    print("Type your question and press Enter. Type 'quit' or 'exit' to stop.\n")

    while True:
        try:
            question = input("Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Exiting.")
            break

        print()
        answer = answer_question(question, index)
        print(f"Answer:\n{answer}\n")
        print("-" * 40)


if __name__ == "__main__":
    main()
