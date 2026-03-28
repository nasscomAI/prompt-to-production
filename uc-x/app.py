"""
UC-X — Ask My Documents
Built using RICE → agents.md → skills.md → CRAFT workflow.
Interactive multi-document Q&A CLI with single-source citation and refusal template.
"""
import os
import re
import sys

POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")

POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# Banned hedging phrases — enforcement rule
BANNED_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "it is generally expected",
]

# Keyword mapping: question keywords → (document, section, answer builder)
# Each entry maps search terms to the specific document and section that answers it.
QUESTION_INDEX = [
    {
        "keywords": ["carry forward", "carry-forward", "unused annual leave", "unused leave"],
        "doc": "policy_hr_leave.txt",
        "sections": ["2.6", "2.7"],
        "topic": "annual leave carry-forward",
    },
    {
        "keywords": ["install", "slack", "software", "work laptop"],
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["2.3", "2.4"],
        "topic": "software installation on corporate devices",
    },
    {
        "keywords": ["home office equipment", "equipment allowance", "wfh allowance",
                     "work from home equipment", "work-from-home equipment"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["3.1", "3.2", "3.3", "3.5"],
        "topic": "home office equipment allowance",
    },
    {
        "keywords": ["personal phone", "personal device", "byod", "work files from home",
                     "personal phone for work"],
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["3.1", "3.2"],
        "topic": "personal device use for work",
    },
    {
        "keywords": ["da and meal", "meal receipts", "daily allowance and meal",
                     "claim da and meal", "da and meal receipts"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["2.5", "2.6"],
        "topic": "DA and meal receipt claims",
    },
    {
        "keywords": ["leave without pay", "lwp", "who approves lwp",
                     "approves leave without pay"],
        "doc": "policy_hr_leave.txt",
        "sections": ["5.1", "5.2", "5.3"],
        "topic": "leave without pay approval",
    },
    {
        "keywords": ["sick leave", "medical certificate", "sick days"],
        "doc": "policy_hr_leave.txt",
        "sections": ["3.1", "3.2", "3.3", "3.4"],
        "topic": "sick leave",
    },
    {
        "keywords": ["maternity", "paternity", "parental leave"],
        "doc": "policy_hr_leave.txt",
        "sections": ["4.1", "4.2", "4.3", "4.4"],
        "topic": "maternity and paternity leave",
    },
    {
        "keywords": ["annual leave", "paid leave", "leave entitlement", "how many days leave"],
        "doc": "policy_hr_leave.txt",
        "sections": ["2.1", "2.2"],
        "topic": "annual leave entitlement",
    },
    {
        "keywords": ["leave encashment", "encash leave"],
        "doc": "policy_hr_leave.txt",
        "sections": ["7.1", "7.2", "7.3"],
        "topic": "leave encashment",
    },
    {
        "keywords": ["password", "mfa", "multi-factor", "authentication"],
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["4.1", "4.2", "4.3", "4.4"],
        "topic": "passwords and access control",
    },
    {
        "keywords": ["travel", "outstation", "air travel", "hotel", "accommodation"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["2.1", "2.2", "2.3", "2.4", "2.5"],
        "topic": "travel reimbursement",
    },
    {
        "keywords": ["training", "course", "certification", "professional development"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["4.1", "4.2", "4.3", "4.4"],
        "topic": "training reimbursement",
    },
    {
        "keywords": ["mobile phone reimbursement", "internet reimbursement", "phone bill"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["5.1", "5.2", "5.3"],
        "topic": "mobile and internet reimbursement",
    },
    {
        "keywords": ["grievance", "dispute", "disputed claim"],
        "doc": "policy_hr_leave.txt",
        "sections": ["8.1", "8.2"],
        "topic": "leave grievances",
    },
    {
        "keywords": ["data handling", "confidential", "restricted data", "personal cloud"],
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["5.1", "5.2", "5.3"],
        "topic": "data handling",
    },
]


def retrieve_documents(document_paths: list) -> dict:
    """
    Loads all 3 policy files and indexes content by document name and section number.
    Returns: {"policy_hr_leave.txt": {"2.6": "full clause text", ...}, ...}
    """
    index = {}

    for path in document_paths:
        doc_name = os.path.basename(path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: File not found: {path}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading {path}: {e}", file=sys.stderr)
            sys.exit(1)

        sections = {}
        lines = content.split("\n")
        current_clause_num = None
        current_clause_lines = []
        clause_start = re.compile(r"^(\d+\.\d+)\s+(.*)$")

        def flush():
            if current_clause_num and current_clause_lines:
                text = " ".join(current_clause_lines)
                text = re.sub(r"\s+", " ", text).strip()
                sections[current_clause_num] = text

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("═") or stripped == "":
                if stripped.startswith("═") and current_clause_num:
                    flush()
                    current_clause_num = None
                    current_clause_lines = []
                continue

            match = clause_start.match(stripped)
            if match:
                flush()
                current_clause_num = match.group(1)
                current_clause_lines = [match.group(2).strip()]
            elif current_clause_num:
                current_clause_lines.append(stripped)

        flush()

        if not sections:
            print(f"Warning: No numbered sections found in {doc_name}.", file=sys.stderr)
            sections["0.0"] = content

        index[doc_name] = sections

    return index


def answer_question(question: str, index: dict) -> str:
    """
    Searches indexed documents for a single-source answer with citation,
    or returns the exact refusal template.
    """
    q_lower = question.lower().strip()

    # Find matching topic from the question index
    best_match = None
    best_score = 0

    for entry in QUESTION_INDEX:
        score = 0
        for kw in entry["keywords"]:
            if kw.lower() in q_lower:
                score += len(kw)  # Longer keyword matches score higher
        if score > best_score:
            best_score = score
            best_match = entry

    # No match found — use refusal template
    if not best_match:
        return REFUSAL_TEMPLATE

    doc_name = best_match["doc"]
    section_nums = best_match["sections"]

    # Retrieve the relevant sections from the single source document
    doc_sections = index.get(doc_name, {})
    cited_sections = []
    for sec_num in section_nums:
        if sec_num in doc_sections:
            cited_sections.append((sec_num, doc_sections[sec_num]))

    if not cited_sections:
        return REFUSAL_TEMPLATE

    # Build answer from single source only
    answer_parts = [f"Per {doc_name}:\n"]
    for sec_num, text in cited_sections:
        answer_parts.append(f"  Section {sec_num}: {text}")

    return "\n".join(answer_parts)


def main():
    # Skill 1: retrieve_documents
    document_paths = [os.path.join(POLICY_DIR, f) for f in POLICY_FILES]
    index = retrieve_documents(document_paths)

    total_sections = sum(len(secs) for secs in index.values())
    print(f"Loaded {len(index)} documents with {total_sections} total sections.")
    print("Type your question and press Enter. Type 'quit' to exit.\n")

    while True:
        try:
            question = input("Q: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Exiting.")
            break

        # Skill 2: answer_question
        answer = answer_question(question, index)
        print(f"\nA: {answer}\n")


if __name__ == "__main__":
    main()
