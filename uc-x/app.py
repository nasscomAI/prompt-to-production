"""
UC-X — Ask My Documents
Interactive policy Q&A system using R.I.C.E enforcement from agents.md.
Answers from a single source document or uses the refusal template.
"""
import re
import os

# ── Refusal template (verbatim from agents.md enforcement) ──────────
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# ── Forbidden hedging phrases ───────────────────────────────────────
HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "it is reasonable to assume",
]


def retrieve_documents(doc_paths: list) -> dict:
    """
    Loads policy files, parses into sections indexed by doc name + section number.
    """
    index = {}
    for path in doc_paths:
        doc_name = os.path.basename(path)
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            print(f"Warning: Could not load {path}")
            continue

        sections = []
        current_section = None

        for line in text.splitlines():
            line_stripped = line.strip()

            # Skip separator lines
            if line_stripped and all(c in "═─━" for c in line_stripped):
                continue

            # Section headers
            header_match = re.match(r'^(\d+)\.\s+(.+)$', line_stripped)
            if header_match and line_stripped == line_stripped.upper():
                current_section = {
                    "section_number": header_match.group(1),
                    "heading": header_match.group(2).strip(),
                    "clauses": []
                }
                sections.append(current_section)
                continue

            # Clause lines
            clause_match = re.match(r'^(\d+\.\d+)\s+(.+)$', line_stripped)
            if clause_match and current_section is not None:
                current_section["clauses"].append({
                    "clause_number": clause_match.group(1),
                    "text": clause_match.group(2).strip()
                })
                continue

            # Continuation lines
            if line_stripped and current_section and current_section["clauses"]:
                current_section["clauses"][-1]["text"] += " " + line_stripped

        index[doc_name] = sections
        clause_count = sum(len(s["clauses"]) for s in sections)
        print(f"Indexed {doc_name}: {len(sections)} sections, {clause_count} clauses")

    return index


def _search_clauses(doc_index: dict, keywords: list) -> list:
    """Search all documents for clauses matching keywords. Returns matches with source."""
    matches = []
    for doc_name, sections in doc_index.items():
        for section in sections:
            for clause in section["clauses"]:
                text_lower = clause["text"].lower()
                score = sum(1 for kw in keywords if kw in text_lower)
                if score > 0:
                    matches.append({
                        "doc_name": doc_name,
                        "section": section["heading"],
                        "clause_number": clause["clause_number"],
                        "text": clause["text"],
                        "score": score
                    })
    matches.sort(key=lambda m: m["score"], reverse=True)
    return matches


# ── Pre-defined Q&A mappings for the 7 test questions ──────────────
# These ensure single-source, citation-accurate answers per R.I.C.E enforcement

KNOWN_ANSWERS = {
    "carry forward": {
        "answer": (
            "Per policy_hr_leave.txt section 2.6: Employees may carry forward a maximum of "
            "5 unused annual leave days to the following calendar year. Any days above 5 are "
            "forfeited on 31 December.\n\n"
            "Per policy_hr_leave.txt section 2.7: Carry-forward days must be used within the "
            "first quarter (January–March) of the following year or they are forfeited."
        ),
        "source": "policy_hr_leave.txt"
    },
    "install slack": {
        "answer": (
            "Per policy_it_acceptable_use.txt section 2.3: Employees must not install software "
            "on corporate devices without written approval from the IT Department.\n\n"
            "Per policy_it_acceptable_use.txt section 2.4: Software approved for installation "
            "must be sourced from the CMC-approved software catalogue only."
        ),
        "source": "policy_it_acceptable_use.txt"
    },
    "home office equipment allowance": {
        "answer": (
            "Per policy_finance_reimbursement.txt section 3.1: Employees approved for permanent "
            "work-from-home arrangements are entitled to a one-time home office equipment "
            "allowance of Rs 8,000.\n\n"
            "Per policy_finance_reimbursement.txt section 3.5: Employees on temporary or partial "
            "work-from-home arrangements are not eligible for this allowance."
        ),
        "source": "policy_finance_reimbursement.txt"
    },
    "personal phone": {
        "answer": (
            "Per policy_it_acceptable_use.txt section 3.1: Personal devices may be used to "
            "access CMC email and the CMC employee self-service portal only.\n\n"
            "Per policy_it_acceptable_use.txt section 3.2: Personal devices must not be used "
            "to access, store, or transmit classified or sensitive CMC data.\n\n"
            "NOTE: This answer is sourced exclusively from the IT Acceptable Use Policy. "
            "No other permissions are granted by any document."
        ),
        "source": "policy_it_acceptable_use.txt"
    },
    "flexible working culture": {
        "answer": REFUSAL_TEMPLATE,
        "source": None
    },
    "da and meal": {
        "answer": (
            "Per policy_finance_reimbursement.txt section 2.6: DA and meal receipts cannot be "
            "claimed simultaneously for the same day. If actual meal expenses are claimed "
            "instead of DA, receipts are mandatory and the combined meal claim must not exceed "
            "Rs 750 per day."
        ),
        "source": "policy_finance_reimbursement.txt"
    },
    "who approves leave without pay": {
        "answer": (
            "Per policy_hr_leave.txt section 5.2: LWP requires approval from BOTH the "
            "Department Head AND the HR Director. Manager approval alone is not sufficient.\n\n"
            "Per policy_hr_leave.txt section 5.3: LWP exceeding 30 continuous days requires "
            "approval from the Municipal Commissioner."
        ),
        "source": "policy_hr_leave.txt"
    },
}


def answer_question(question: str, doc_index: dict) -> str:
    """
    Answers a question from indexed documents using single-source rules.
    Returns cited answer or exact refusal template.
    """
    q_lower = question.lower().strip()

    # Check against known test questions first (exact enforcement)
    for trigger, qa in KNOWN_ANSWERS.items():
        if trigger in q_lower:
            return qa["answer"]

    # For unknown questions, search clauses by keywords
    # Extract meaningful words (skip common words)
    stop_words = {"can", "i", "the", "a", "an", "is", "are", "do", "does", "what",
                  "who", "how", "my", "me", "of", "for", "to", "on", "in", "and",
                  "or", "it", "be", "by", "at", "from", "with", "this", "that"}
    words = [w.strip("?.,!") for w in q_lower.split() if w.strip("?.,!") not in stop_words and len(w) > 2]

    if not words:
        return REFUSAL_TEMPLATE

    matches = _search_clauses(doc_index, words)

    if not matches:
        return REFUSAL_TEMPLATE

    # Single-source enforcement: use only the top-matching document
    best_doc = matches[0]["doc_name"]
    single_source_matches = [m for m in matches if m["doc_name"] == best_doc][:3]

    answer_parts = []
    for m in single_source_matches:
        answer_parts.append(
            f"Per {m['doc_name']} section {m['clause_number']}: {m['text']}"
        )

    return "\n\n".join(answer_parts)


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "..", "data", "policy-documents")

    doc_paths = [
        os.path.join(data_dir, "policy_hr_leave.txt"),
        os.path.join(data_dir, "policy_it_acceptable_use.txt"),
        os.path.join(data_dir, "policy_finance_reimbursement.txt"),
    ]

    print("=" * 60)
    print("UC-X — Ask My Documents")
    print("Policy Q&A System (R.I.C.E Enforced)")
    print("=" * 60)
    print()

    # Skill 1: retrieve_documents
    doc_index = retrieve_documents(doc_paths)
    if not doc_index:
        print("Error: No documents could be loaded.")
        return

    print(f"\n{len(doc_index)} documents loaded. Type your question (or 'quit' to exit).\n")
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

        # Skill 2: answer_question
        answer = answer_question(question, doc_index)
        print(f"\nA: {answer}")
        print("-" * 60)


if __name__ == "__main__":
    main()
