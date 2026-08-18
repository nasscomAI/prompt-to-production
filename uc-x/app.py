"""
UC-X — Ask My Documents
Rule-based policy Q&A system built using the RICE → agents.md → skills.md → CRAFT workflow.
Answers questions from exactly 3 policy documents with single-source attribution.
Never blends documents. Uses exact refusal template for uncovered questions.
"""
import os
import re
import sys


# ── Refusal Template (from agents.md enforcement) ────────────────────────────
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact the relevant department for guidance."
)

# ── Hedging phrases that must NEVER appear in output (Enforcement Rule 2) ────
HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "employees are generally expected to",
]

# ── Policy documents path ────────────────────────────────────────────────────
POLICY_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]


# ── Skill: retrieve_documents ────────────────────────────────────────────────

def retrieve_documents(policy_dir: str, filenames: list) -> dict:
    """
    Load all policy documents, parse each into structured sections indexed
    by document name and section number.
    Returns dict: {filename: [{"section_heading", "clause_number", "clause_text"}, ...]}
    """
    documents = {}

    section_pattern = re.compile(r"^(\d+)\.\s+(.+)$")
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.+)$")
    separator_pattern = re.compile(r"^[═]+$")

    for fname in filenames:
        fpath = os.path.join(policy_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            print(f"WARNING: Policy file not found: {fpath}", file=sys.stderr)
            continue

        lines = content.split("\n")
        clauses = []
        current_section = ""
        current_clause_number = None
        current_clause_lines = []

        def _flush():
            if current_clause_number and current_clause_lines:
                full_text = " ".join(current_clause_lines)
                full_text = re.sub(r"\s+", " ", full_text).strip()
                clauses.append({
                    "section_heading": current_section,
                    "clause_number": current_clause_number,
                    "clause_text": full_text
                })

        for line in lines:
            stripped = line.strip()
            if not stripped or separator_pattern.match(stripped):
                continue

            section_match = section_pattern.match(stripped)
            if section_match:
                _flush()
                current_clause_number = None
                current_clause_lines = []
                current_section = stripped
                continue

            clause_match = clause_pattern.match(stripped)
            if clause_match:
                _flush()
                current_clause_number = clause_match.group(1)
                current_clause_lines = [clause_match.group(2)]
                continue

            if current_clause_number:
                current_clause_lines.append(stripped)

        _flush()
        documents[fname] = clauses

    print(f"Loaded {len(documents)} policy documents:")
    for fname, clauses in documents.items():
        print(f"  {fname}: {len(clauses)} clauses")
    print()

    if not documents:
        print("ERROR: No policy documents could be loaded.", file=sys.stderr)
        sys.exit(1)

    return documents


# ── Skill: answer_question ───────────────────────────────────────────────────

# Keyword mappings: question keywords → relevant (document, clause_numbers) to search
QUESTION_RULES = [
    {
        "keywords": ["carry forward", "carry-forward", "unused annual leave",
                     "annual leave carry"],
        "doc": "policy_hr_leave.txt",
        "clauses": ["2.6", "2.7"],
        "description": "Annual leave carry-forward rules"
    },
    {
        "keywords": ["install", "slack", "software", "application",
                     "install software", "install app"],
        "doc": "policy_it_acceptable_use.txt",
        "clauses": ["2.3", "2.4"],
        "description": "Software installation on corporate devices"
    },
    {
        "keywords": ["home office", "equipment allowance", "wfh equipment",
                     "work from home equipment", "home office equipment"],
        "doc": "policy_finance_reimbursement.txt",
        "clauses": ["3.1", "3.2", "3.3", "3.4", "3.5"],
        "description": "Home office equipment allowance"
    },
    {
        "keywords": ["personal phone", "personal device", "byod",
                     "work files from home", "personal phone for work"],
        "doc": "policy_it_acceptable_use.txt",
        "clauses": ["3.1", "3.2", "3.3", "3.4", "3.5"],
        "description": "Personal device (BYOD) usage policy"
    },
    {
        "keywords": ["da and meal", "meal receipts", "daily allowance and meal",
                     "claim da", "da or meal"],
        "doc": "policy_finance_reimbursement.txt",
        "clauses": ["2.5", "2.6"],
        "description": "Daily allowance and meal claims"
    },
    {
        "keywords": ["leave without pay", "lwp", "who approves lwp",
                     "approves leave without pay"],
        "doc": "policy_hr_leave.txt",
        "clauses": ["5.1", "5.2", "5.3", "5.4"],
        "description": "Leave without pay approval process"
    },
    {
        "keywords": ["sick leave", "medical certificate", "sick days"],
        "doc": "policy_hr_leave.txt",
        "clauses": ["3.1", "3.2", "3.3", "3.4"],
        "description": "Sick leave rules"
    },
    {
        "keywords": ["leave encashment", "encash leave"],
        "doc": "policy_hr_leave.txt",
        "clauses": ["7.1", "7.2", "7.3"],
        "description": "Leave encashment rules"
    },
    {
        "keywords": ["maternity", "paternity", "parental leave"],
        "doc": "policy_hr_leave.txt",
        "clauses": ["4.1", "4.2", "4.3", "4.4"],
        "description": "Maternity and paternity leave"
    },
    {
        "keywords": ["annual leave", "paid leave", "leave entitlement",
                     "how many days leave", "advance notice"],
        "doc": "policy_hr_leave.txt",
        "clauses": ["2.1", "2.2", "2.3", "2.4", "2.5"],
        "description": "Annual leave entitlements and application"
    },
    {
        "keywords": ["password", "mfa", "multi-factor", "authentication"],
        "doc": "policy_it_acceptable_use.txt",
        "clauses": ["4.1", "4.2", "4.3", "4.4"],
        "description": "Password and access control"
    },
    {
        "keywords": ["confidential", "data handling", "restricted data",
                     "personal cloud", "forward email"],
        "doc": "policy_it_acceptable_use.txt",
        "clauses": ["5.1", "5.2", "5.3"],
        "description": "Data handling and confidentiality"
    },
    {
        "keywords": ["travel", "outstation", "air travel", "hotel",
                     "reimbursement travel"],
        "doc": "policy_finance_reimbursement.txt",
        "clauses": ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6"],
        "description": "Travel reimbursement"
    },
    {
        "keywords": ["training", "course fees", "certification", "professional development"],
        "doc": "policy_finance_reimbursement.txt",
        "clauses": ["4.1", "4.2", "4.3", "4.4"],
        "description": "Training and professional development reimbursement"
    },
    {
        "keywords": ["mobile phone reimbursement", "internet reimbursement",
                     "mobile allowance"],
        "doc": "policy_finance_reimbursement.txt",
        "clauses": ["5.1", "5.2", "5.3"],
        "description": "Mobile and internet reimbursement"
    },
    {
        "keywords": ["public holiday", "compensatory off", "compensatory leave"],
        "doc": "policy_hr_leave.txt",
        "clauses": ["6.1", "6.2", "6.3"],
        "description": "Public holidays and compensatory off"
    },
    {
        "keywords": ["grievance", "dispute", "complaint about leave"],
        "doc": "policy_hr_leave.txt",
        "clauses": ["8.1", "8.2"],
        "description": "Grievance procedure"
    },
    {
        "keywords": ["violation", "disciplinary", "termination", "monitor"],
        "doc": "policy_it_acceptable_use.txt",
        "clauses": ["7.1", "7.2", "7.3"],
        "description": "Violations and consequences"
    },
    {
        "keywords": ["claim", "submit", "reimbursement claim", "receipt",
                     "expense form", "fin-exp1"],
        "doc": "policy_finance_reimbursement.txt",
        "clauses": ["1.3", "6.1", "6.2", "6.3", "6.4"],
        "description": "Claim submission process"
    },
    {
        "keywords": ["unapproved absence", "loss of pay", "lop"],
        "doc": "policy_hr_leave.txt",
        "clauses": ["2.5"],
        "description": "Unapproved absence consequences"
    },
    {
        "keywords": ["corporate device", "work laptop", "work phone",
                     "official device"],
        "doc": "policy_it_acceptable_use.txt",
        "clauses": ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6"],
        "description": "Corporate device usage"
    },
    {
        "keywords": ["internet use", "email use", "social media",
                     "personal email", "mass email"],
        "doc": "policy_it_acceptable_use.txt",
        "clauses": ["6.1", "6.2", "6.3"],
        "description": "Internet and email usage"
    },
]


def answer_question(question: str, documents: dict) -> str:
    """
    Search indexed documents for relevant clauses. Return single-source
    answer with citation, or exact refusal template.
    """
    question_lower = question.lower().strip()

    # Find matching rule
    best_match = None
    best_score = 0

    for rule in QUESTION_RULES:
        score = 0
        for kw in rule["keywords"]:
            if kw.lower() in question_lower:
                score += len(kw)  # Longer keyword = more specific match
        if score > best_score:
            best_score = score
            best_match = rule

    # No match → refusal template (Enforcement Rule 3)
    if not best_match or best_score == 0:
        return REFUSAL_TEMPLATE

    # Retrieve clauses from the single matched document (Enforcement Rule 1)
    doc_name = best_match["doc"]
    clause_numbers = best_match["clauses"]

    if doc_name not in documents:
        return REFUSAL_TEMPLATE

    doc_clauses = documents[doc_name]
    relevant = [c for c in doc_clauses if c["clause_number"] in clause_numbers]

    if not relevant:
        return REFUSAL_TEMPLATE

    # Build answer from single source (Enforcement Rule 1 & 4)
    lines = []
    lines.append(f"Based on {doc_name}:\n")

    for clause in relevant:
        lines.append(f"  Section {clause['clause_number']}: {clause['clause_text']}")
        lines.append(f"  [Source: {doc_name}, Section {clause['clause_number']}]\n")

    return "\n".join(lines)


# ── Main — Interactive CLI ───────────────────────────────────────────────────

def main():
    # Load documents
    policy_dir = os.path.normpath(POLICY_DIR)
    documents = retrieve_documents(policy_dir, POLICY_FILES)

    print("=" * 60)
    print("  UC-X — Ask My Documents")
    print("  Type a question about policy, or 'quit' to exit.")
    print("=" * 60)
    print()

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        answer = answer_question(question, documents)

        # Verify no hedging phrases leaked (Enforcement Rule 2)
        for phrase in HEDGING_PHRASES:
            if phrase.lower() in answer.lower():
                print(f"[!] ENFORCEMENT VIOLATION: Hedging phrase detected: '{phrase}'",
                      file=sys.stderr)

        print(f"\nAnswer:\n{answer}\n")
        print("-" * 60)
        print()


if __name__ == "__main__":
    main()
