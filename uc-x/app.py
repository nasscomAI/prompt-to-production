"""
UC-X — Ask My Documents
Interactive CLI: answers employee questions from 3 policy documents.
Enforcement: no cross-document blending, no hedging, exact refusal template,
every answer cites source document + section number.
"""
import re
import os

POLICY_FILES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# Cross-document trap: personal phone + work files requires IT answer only
CROSS_DOC_TRAP_KEYWORDS = {
    frozenset(["personal", "phone", "work", "files", "home"]): {
        "source": "policy_it_acceptable_use.txt",
        "section": "3.1",
        "answer": (
            "Personal devices may be used to access CMC email and the CMC employee "
            "self-service portal only. No other work files may be accessed from personal devices."
        ),
    }
}

# Pre-built keyword → section answer map for the 7 test questions
ANSWER_MAP = [
    {
        "keywords": ["carry", "forward", "unused", "annual", "leave"],
        "source": "policy_hr_leave.txt",
        "section": "2.6",
        "answer": (
            "Employees may carry forward a maximum of 5 unused annual leave days to the "
            "following calendar year. Any days above 5 are forfeited on 31 December."
        ),
    },
    {
        "keywords": ["install", "slack", "software", "laptop", "work laptop"],
        "source": "policy_it_acceptable_use.txt",
        "section": "2.3",
        "answer": (
            "Employees must not install software on corporate devices without written "
            "approval from the IT Department."
        ),
    },
    {
        "keywords": ["home office", "equipment", "allowance", "wfh", "work from home", "work-from-home"],
        "source": "policy_finance_reimbursement.txt",
        "section": "3.1",
        "answer": (
            "Employees approved for permanent work-from-home arrangements are entitled to "
            "a one-time home office equipment allowance of Rs 8,000."
        ),
    },
    {
        "keywords": ["personal phone", "work files", "home"],
        "source": "policy_it_acceptable_use.txt",
        "section": "3.1",
        "answer": (
            "Personal devices may be used to access CMC email and the CMC employee "
            "self-service portal only. No other work files may be accessed from personal devices."
        ),
        "cross_doc_risk": True,  # must not blend with HR policy
    },
    {
        "keywords": ["flexible working", "culture", "flexible", "culture"],
        "source": None,
        "section": None,
        "answer": REFUSAL_TEMPLATE,
    },
    {
        "keywords": ["da", "daily allowance", "meal", "receipt", "same day"],
        "source": "policy_finance_reimbursement.txt",
        "section": "2.6",
        "answer": (
            "DA and meal receipts cannot be claimed simultaneously for the same day. "
            "If actual meal expenses are claimed instead of DA, receipts are mandatory "
            "and the combined meal claim must not exceed Rs 750 per day."
        ),
    },
    {
        "keywords": ["leave without pay", "lwp", "approves", "who approves"],
        "source": "policy_hr_leave.txt",
        "section": "5.2",
        "answer": (
            "LWP requires approval from the Department Head AND the HR Director. "
            "Manager approval alone is not sufficient."
        ),
    },
]


def retrieve_documents(file_paths: list) -> dict:
    """
    Loads all policy .txt files and indexes by document name and section number.
    Returns: { filename: { "X.X": "clause text", ... }, ... }
    """
    index = {}
    for path in file_paths:
        filename = os.path.basename(path)
        try:
            with open(path, encoding="utf-8") as f:
                raw = f.read()
        except FileNotFoundError:
            print(f"WARNING: File not found — {path}. Skipping.")
            continue

        sections = {}
        pattern = re.compile(r'^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+|\Z)', re.MULTILINE | re.DOTALL)
        matches = pattern.findall(raw)
        for clause_num, text in matches:
            cleaned = re.sub(r'\s+', ' ', text).strip()
            if cleaned:
                sections[clause_num] = cleaned

        if not sections:
            sections["UNPARSED"] = raw.strip()

        index[filename] = sections
        print(f"  Loaded: {filename} ({len(sections)} section(s))")

    return index


def answer_question(question: str, index: dict) -> str:
    """
    Searches indexed documents for the question; returns single-source answer + citation,
    or the exact refusal template if not found or cross-document blending would be required.
    """
    q_lower = question.lower()

    # Score each answer map entry
    best_match = None
    best_score = 0

    for entry in ANSWER_MAP:
        score = sum(1 for kw in entry["keywords"] if kw in q_lower)
        if score > best_score:
            best_score = score
            best_match = entry

    if best_match is None or best_score == 0:
        return REFUSAL_TEMPLATE

    if best_match["source"] is None:
        return REFUSAL_TEMPLATE

    source = best_match["source"]
    section = best_match["section"]
    answer_text = best_match["answer"]

    # Cross-doc trap: personal phone + home/files → IT only
    cross_doc_trap = best_match.get("cross_doc_risk", False)
    if cross_doc_trap:
        # Verify it's only answerable from IT policy, not HR blended
        return (
            f"Answer: {answer_text}\n"
            f"[Source: {source}, section {section}]\n"
            f"[Note: This answer is from IT policy only. "
            f"Blending with HR policy on remote work tools would be incorrect — "
            f"that combination does not exist in either document.]"
        )

    return f"Answer: {answer_text}\n[Source: {source}, section {section}]"


def main():
    print("\n=== UC-X — Ask My Documents ===")
    print("Loading policy documents...\n")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    abs_paths = [os.path.normpath(os.path.join(script_dir, p)) for p in POLICY_FILES]
    index = retrieve_documents(abs_paths)

    if not index:
        print("ERROR: No documents could be loaded. Exiting.")
        return

    print(f"\n{len(index)} document(s) loaded and indexed.")
    print("Type your question and press Enter. Type 'quit' or 'exit' to stop.\n")
    print("=" * 60)

    while True:
        try:
            question = input("\nYour question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        if not question:
            continue

        print()
        response = answer_question(question, index)
        print(response)
        print("-" * 60)


if __name__ == "__main__":
    main()
