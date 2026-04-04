"""
UC-X — Ask My Documents
Interactive policy Q&A with single-source answers, citations, and refusal template.
Follows the RICE enforcement rules defined in agents.md.
"""
import re
import sys
import os

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
    "it may be possible",
    "generally",
    "usually",
    "in most cases",
]


def retrieve_documents(file_paths: list) -> list:
    """
    Load all policy files and index them by document name and section number.
    Returns list of dicts: {document_name, section_number, title, text}
    """
    index = []

    for path in file_paths:
        if not os.path.exists(path):
            print(f"WARNING: File not found: {path}", file=sys.stderr)
            continue

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.strip():
            print(f"WARNING: File is empty: {path}", file=sys.stderr)
            continue

        doc_name = os.path.basename(path)
        lines = content.split("\n")
        current_title = None
        current_sub = None

        for line in lines:
            line_stripped = line.strip()

            if re.match(r"^═+$", line_stripped):
                continue

            # Top-level section
            top_match = re.match(r"^(\d+)\.\s+(.+)$", line_stripped)
            if top_match:
                if current_sub:
                    index.append(current_sub)
                    current_sub = None
                current_title = top_match.group(2).strip()
                continue

            # Sub-section
            sub_match = re.match(r"^(\d+\.\d+)\s+(.+)$", line_stripped)
            if sub_match:
                if current_sub:
                    index.append(current_sub)
                current_sub = {
                    "document_name": doc_name,
                    "section_number": sub_match.group(1),
                    "title": current_title or "",
                    "text": sub_match.group(2).strip()
                }
                continue

            # Continuation line
            if line_stripped and current_sub:
                current_sub["text"] += " " + line_stripped

        if current_sub:
            index.append(current_sub)

    print(f"Document index built: {len(index)} sections from {len(file_paths)} files")
    return index


# Keyword map: question keywords -> (document pattern, section patterns, description)
QUESTION_RULES = [
    # HR Leave topics
    {
        "keywords": ["carry forward", "carry-forward", "unused annual leave", "unused leave"],
        "doc": "policy_hr_leave.txt",
        "sections": ["2.6", "2.7"],
        "topic": "leave carry-forward"
    },
    {
        "keywords": ["leave without pay", "lwp", "unpaid leave"],
        "doc": "policy_hr_leave.txt",
        "sections": ["5.1", "5.2", "5.3", "5.4"],
        "topic": "leave without pay"
    },
    {
        "keywords": ["who approves leave without pay", "lwp approv"],
        "doc": "policy_hr_leave.txt",
        "sections": ["5.2", "5.3"],
        "topic": "LWP approval"
    },
    {
        "keywords": ["sick leave", "medical certificate", "sick day"],
        "doc": "policy_hr_leave.txt",
        "sections": ["3.1", "3.2", "3.3", "3.4"],
        "topic": "sick leave"
    },
    {
        "keywords": ["leave encashment", "encash leave"],
        "doc": "policy_hr_leave.txt",
        "sections": ["7.1", "7.2", "7.3"],
        "topic": "leave encashment"
    },
    {
        "keywords": ["maternity", "paternity", "parental leave"],
        "doc": "policy_hr_leave.txt",
        "sections": ["4.1", "4.2", "4.3", "4.4"],
        "topic": "maternity/paternity leave"
    },
    # IT topics
    {
        "keywords": ["install", "software", "slack", "application"],
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["2.3", "2.4"],
        "topic": "software installation"
    },
    {
        "keywords": ["personal phone", "personal device", "byod", "personal mobile"],
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["3.1", "3.2", "3.3"],
        "topic": "personal device usage"
    },
    {
        "keywords": ["password", "access control", "mfa", "multi-factor"],
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["4.1", "4.2", "4.3", "4.4"],
        "topic": "passwords and access"
    },
    # Finance topics
    {
        "keywords": ["home office", "work from home equipment", "wfh equipment", "wfh allowance"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["3.1", "3.2", "3.3", "3.4", "3.5"],
        "topic": "home office equipment allowance"
    },
    {
        "keywords": ["da", "daily allowance", "meal receipt", "meal claim", "meal and da"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["2.5", "2.6"],
        "topic": "DA and meal claims"
    },
    {
        "keywords": ["travel", "outstation", "air travel", "hotel"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["2.1", "2.2", "2.3", "2.4"],
        "topic": "travel reimbursement"
    },
    {
        "keywords": ["training", "course", "certification", "professional development"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["4.1", "4.2", "4.3", "4.4"],
        "topic": "training reimbursement"
    },
    {
        "keywords": ["mobile phone reimbursement", "internet reimbursement", "phone bill"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["5.1", "5.2", "5.3"],
        "topic": "mobile/internet reimbursement"
    },
]


def answer_question(question: str, doc_index: list) -> str:
    """
    Search indexed documents for the answer. Returns single-source answer
    with citation, or the refusal template.
    """
    q_lower = question.lower().strip()

    # Find matching rules
    matched_rules = []
    for rule in QUESTION_RULES:
        for kw in rule["keywords"]:
            if kw in q_lower:
                matched_rules.append(rule)
                break

    if not matched_rules:
        return REFUSAL_TEMPLATE

    # Check for cross-document matches — if keywords match rules from different docs, be careful
    matched_docs = set(r["doc"] for r in matched_rules)
    if len(matched_docs) > 1:
        # Cross-document question — refuse if ambiguous blend risk
        # Pick the single most specific match (most keyword overlap)
        best_rule = None
        best_score = 0
        for rule in matched_rules:
            score = sum(1 for kw in rule["keywords"] if kw in q_lower)
            if score > best_score:
                best_score = score
                best_rule = rule

        if best_rule:
            matched_rules = [best_rule]
        else:
            return REFUSAL_TEMPLATE

    # Use the first (best) matched rule — single document source
    rule = matched_rules[0]
    doc_name = rule["doc"]
    target_sections = rule["sections"]

    # Retrieve matching sections from index
    relevant = [s for s in doc_index
                if s["document_name"] == doc_name and s["section_number"] in target_sections]

    if not relevant:
        return REFUSAL_TEMPLATE

    # Build answer from single source
    answer_parts = []
    answer_parts.append(f"Source: {doc_name}\n")

    for section in relevant:
        text = section["text"]
        answer_parts.append(f"[{doc_name}, Section {section['section_number']}]: {text}")

    answer = "\n".join(answer_parts)

    # Safety check: ensure no hedging phrases leaked in
    for phrase in HEDGING_PHRASES:
        if phrase in answer.lower():
            answer = answer.replace(phrase, "[REMOVED — hedging phrase]")

    return answer


def main():
    # Determine policy document paths relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "data", "policy-documents")

    policy_files = [
        os.path.join(data_dir, "policy_hr_leave.txt"),
        os.path.join(data_dir, "policy_it_acceptable_use.txt"),
        os.path.join(data_dir, "policy_finance_reimbursement.txt"),
    ]

    # Check files exist
    for pf in policy_files:
        if not os.path.exists(pf):
            print(f"ERROR: Policy file not found: {pf}", file=sys.stderr)
            sys.exit(1)

    doc_index = retrieve_documents(policy_files)

    print("\n=== Ask My Documents — Policy Q&A ===")
    print("Type a question about HR leave, IT usage, or finance reimbursement.")
    print("Type 'quit' or 'exit' to stop.\n")

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Exiting.")
            break

        answer = answer_question(question, doc_index)
        print(f"\n{answer}\n")


if __name__ == "__main__":
    main()
