"""
UC-X — Ask My Documents
Interactive CLI that answers policy questions using only the content of three
CMC policy documents. Single-source citation, no cross-document blending,
refusal template for uncovered questions.
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
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact the relevant "
    "department for guidance."
)

HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "it may be possible",
    "you could try",
]


def retrieve_documents(policy_dir: str, filenames: list) -> dict:
    """
    Load all policy files and index by document name → {section_number: clause_text}.
    Returns {filename: {clause_num: clause_text, ...}, ...}
    """
    index = {}
    for fname in filenames:
        fpath = os.path.join(policy_dir, fname)
        if not os.path.exists(fpath):
            raise FileNotFoundError(f"Policy file not found: {fpath}")

        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        clauses = {}
        lines = content.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            clause_match = re.match(r'^(\d+\.\d+)\s+(.+)$', line)
            if clause_match:
                clause_num = clause_match.group(1)
                clause_text = clause_match.group(2)
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()
                    if not next_line or next_line.startswith("═"):
                        break
                    if re.match(r'^\d+\.\d+\s+', next_line):
                        break
                    if re.match(r'^\d+\.\s+[A-Z][A-Z\s()&/,\-]+$', next_line):
                        break
                    clause_text += " " + next_line
                    i += 1
                clauses[clause_num] = clause_text.strip()
                continue
            i += 1

        index[fname] = clauses
        if not clauses:
            print(f"WARNING: No clauses found in {fname}", file=sys.stderr)

    return index


# Keyword mapping: each entry maps search terms to (document, section, topic_label).
# Ordered so more specific matches come first.
KNOWLEDGE_MAP = [
    # HR Leave — Annual leave carry forward
    {
        "keywords": ["carry forward", "carry-forward", "unused annual leave", "unused leave"],
        "doc": "policy_hr_leave.txt",
        "sections": ["2.6", "2.7"],
        "topic": "annual leave carry-forward"
    },
    # HR Leave — Leave application / advance notice
    {
        "keywords": ["leave application", "advance notice", "apply for leave", "annual leave application"],
        "doc": "policy_hr_leave.txt",
        "sections": ["2.3", "2.4"],
        "topic": "leave application process"
    },
    # HR Leave — LWP approval
    {
        "keywords": ["leave without pay", "lwp", "who approves leave"],
        "doc": "policy_hr_leave.txt",
        "sections": ["5.1", "5.2", "5.3"],
        "topic": "leave without pay approval"
    },
    # HR Leave — Leave encashment
    {
        "keywords": ["leave encashment", "encash leave"],
        "doc": "policy_hr_leave.txt",
        "sections": ["7.1", "7.2", "7.3"],
        "topic": "leave encashment"
    },
    # HR Leave — Sick leave
    {
        "keywords": ["sick leave", "medical certificate", "sick day"],
        "doc": "policy_hr_leave.txt",
        "sections": ["3.1", "3.2", "3.3", "3.4"],
        "topic": "sick leave"
    },
    # HR Leave — Maternity/Paternity
    {
        "keywords": ["maternity", "paternity", "parental leave"],
        "doc": "policy_hr_leave.txt",
        "sections": ["4.1", "4.2", "4.3", "4.4"],
        "topic": "maternity and paternity leave"
    },
    # IT — Install software
    {
        "keywords": ["install", "software", "slack", "app on laptop", "install on work"],
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["2.3", "2.4"],
        "topic": "software installation on corporate devices"
    },
    # IT — Personal device / BYOD / personal phone
    {
        "keywords": ["personal phone", "personal device", "byod", "bring your own", "personal laptop", "work files from home"],
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["3.1", "3.2"],
        "topic": "personal device (BYOD) use"
    },
    # IT — Password
    {
        "keywords": ["password", "mfa", "multi-factor", "authentication"],
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["4.1", "4.2", "4.3", "4.4"],
        "topic": "passwords and access control"
    },
    # IT — Data handling
    {
        "keywords": ["confidential data", "restricted data", "data handling", "personal cloud"],
        "doc": "policy_it_acceptable_use.txt",
        "sections": ["5.1", "5.2", "5.3"],
        "topic": "data handling"
    },
    # Finance — DA and meal receipts
    {
        "keywords": ["da and meal", "meal receipts", "daily allowance", "da", "meal claim", "same day"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["2.5", "2.6"],
        "topic": "daily allowance and meal reimbursement"
    },
    # Finance — Home office / WFH equipment
    {
        "keywords": ["home office", "wfh equipment", "work from home equipment", "equipment allowance", "home equipment"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["3.1", "3.2", "3.3", "3.4", "3.5"],
        "topic": "work from home equipment allowance"
    },
    # Finance — Travel
    {
        "keywords": ["travel reimbursement", "outstation travel", "air travel", "hotel", "accommodation"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["2.1", "2.2", "2.3", "2.4"],
        "topic": "travel reimbursement"
    },
    # Finance — Training
    {
        "keywords": ["training", "course fee", "certification", "professional development"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["4.1", "4.2", "4.3", "4.4"],
        "topic": "training and professional development reimbursement"
    },
    # Finance — Mobile/Internet reimbursement
    {
        "keywords": ["mobile phone reimbursement", "internet reimbursement", "phone bill"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["5.1", "5.2", "5.3"],
        "topic": "mobile and internet reimbursement"
    },
    # Finance — Submission process
    {
        "keywords": ["submit claim", "reimbursement process", "claim submission", "fin-exp1"],
        "doc": "policy_finance_reimbursement.txt",
        "sections": ["6.1", "6.2", "6.3", "6.4"],
        "topic": "reimbursement submission process"
    },
]


def _find_matching_topics(question: str) -> list:
    """Find all knowledge map entries matching the question keywords."""
    q_lower = question.lower()
    matches = []
    for entry in KNOWLEDGE_MAP:
        score = sum(1 for kw in entry["keywords"] if kw in q_lower)
        if score > 0:
            matches.append((score, entry))
    matches.sort(key=lambda x: x[0], reverse=True)
    return [m[1] for m in matches]


def answer_question(question: str, doc_index: dict) -> str:
    """
    Answer a question using only the indexed documents.
    Returns a single-source cited answer or the refusal template.
    """
    if not question or not question.strip():
        return "Please provide a specific question about CMC policy."

    matches = _find_matching_topics(question)

    if not matches:
        return REFUSAL_TEMPLATE

    # Use only the top match (single source) to avoid cross-doc blending
    best = matches[0]
    doc_name = best["doc"]
    sections = best["sections"]
    clauses = doc_index.get(doc_name, {})

    # Check if multiple documents matched — warn about single-source rule
    unique_docs = set(m["doc"] for m in matches[:3])
    cross_doc_warning = ""
    if len(unique_docs) > 1:
        cross_doc_warning = (
            "\n\nNote: Other policy documents may also be relevant to this "
            "question, but per the single-source rule, this answer is based "
            "only on the document cited above. Consult the relevant department "
            "if you need a cross-policy interpretation."
        )

    answer_parts = []
    answer_parts.append(f"Based on {doc_name}:\n")

    for sec in sections:
        clause_text = clauses.get(sec)
        if clause_text:
            answer_parts.append(f"  [{doc_name}, Section {sec}]: {clause_text}")

    if len(answer_parts) == 1:
        return REFUSAL_TEMPLATE

    return "\n".join(answer_parts) + cross_doc_warning


def main():
    doc_index = retrieve_documents(POLICY_DIR, POLICY_FILES)

    total_clauses = sum(len(v) for v in doc_index.values())
    print(f"Loaded {len(doc_index)} policy documents ({total_clauses} clauses indexed).")
    print("Type a question and press Enter. Type 'quit' to exit.\n")

    while True:
        try:
            question = input("Q: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if question.lower() in ("quit", "exit", "q"):
            print("Exiting.")
            break

        if not question:
            continue

        answer = answer_question(question, doc_index)
        print(f"\nA: {answer}\n")


if __name__ == "__main__":
    main()
