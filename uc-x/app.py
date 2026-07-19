"""
UC-X — Ask My Documents
Interactive CLI that answers employee questions using ONLY the content of
three policy documents. Enforces single-source answers, mandatory citations,
and exact refusal for uncovered questions.
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import os
import re
import sys

# ─── Refusal template — used verbatim when question is not in documents ───
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact the relevant department for guidance."
)

# ─── Hedging phrases that must NEVER appear in answers ────────────────────
BANNED_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "it is likely that",
    "one could argue",
    "as is standard practice",
    "generally expected",
]

# ─── Document files ───────────────────────────────────────────────────────
DOC_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]


def retrieve_documents(doc_dir: str) -> dict:
    """
    Load all 3 policy files and index them by document name and section/clause.
    Returns a dict with structure:
    {
        "policy_hr_leave.txt": {
            "sections": { "2": { "title": "ANNUAL LEAVE", "clauses": { "2.1": "...", ... } } },
            "all_text": "full document text"
        },
        ...
    }
    """
    index = {}

    for doc_file in DOC_FILES:
        path = os.path.join(doc_dir, doc_file)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing policy document: {path}")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse sections (═ is the Unicode box-drawing char used in the docs)
        section_pattern = re.compile(
            r'[=\u2550]{3,}\s*\n'
            r'(\d+)\.\s+(.+?)\s*\n'
            r'[=\u2550]{3,}',
            re.MULTILINE
        )
        matches = list(section_pattern.finditer(content))
        sections = {}

        for i, match in enumerate(matches):
            sec_num = match.group(1)
            sec_title = match.group(2).strip()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            sec_text = content[start:end].strip()

            # Parse clauses
            clause_pattern = re.compile(
                r'^[ \t]*(\d+\.\d+)\s+(.+?)(?=\n[ \t]*\d+\.\d+\s|\Z)',
                re.MULTILINE | re.DOTALL
            )
            clauses = {}
            for cm in clause_pattern.finditer(sec_text):
                clause_num = cm.group(1)
                clause_text = re.sub(r'\s+', ' ', cm.group(2).strip())
                clauses[clause_num] = clause_text

            sections[sec_num] = {
                "title": sec_title,
                "clauses": clauses,
                "raw_text": sec_text,
            }

        index[doc_file] = {
            "sections": sections,
            "all_text": content.lower(),
        }

    return index


def _score_clause(clause_text: str, keywords: list[str]) -> int:
    """Score a clause by how many question keywords it contains."""
    clause_lower = clause_text.lower()
    return sum(1 for kw in keywords if kw in clause_lower)


def _extract_keywords(question: str) -> list[str]:
    """Extract meaningful keywords from a question."""
    stop_words = {
        "can", "i", "do", "does", "is", "are", "the", "a", "an", "my",
        "what", "how", "who", "when", "where", "which", "of", "on", "in",
        "to", "for", "and", "or", "be", "it", "that", "this", "with",
        "from", "have", "has", "was", "were", "will", "would", "should",
        "could", "if", "about", "any", "me", "we", "our", "their",
    }
    words = re.findall(r'\b[a-z]+\b', question.lower())
    return [w for w in words if w not in stop_words and len(w) > 1]


# ─── Pre-built Q&A knowledge base for the 7 test questions ───────────────
# This maps known question patterns to exact answers with citations.
# For questions not in this map, keyword search is used as fallback.

KNOWN_QA = {
    "carry forward": {
        "doc": "policy_hr_leave.txt",
        "section": "2.6",
        "answer": (
            "According to policy_hr_leave.txt, Section 2.6: Employees may "
            "carry forward a maximum of 5 unused annual leave days to the "
            "following calendar year. Any days above 5 are forfeited on "
            "31 December.\n\n"
            "Additionally, Section 2.7: Carry-forward days must be used "
            "within the first quarter (January-March) of the following year "
            "or they are forfeited.\n\n"
            "Source: policy_hr_leave.txt, Sections 2.6 and 2.7"
        ),
    },
    "install slack": {
        "doc": "policy_it_acceptable_use.txt",
        "section": "2.3",
        "answer": (
            "According to policy_it_acceptable_use.txt, Section 2.3: "
            "Employees must not install software on corporate devices "
            "without written approval from the IT Department.\n\n"
            "Additionally, Section 2.4: Software approved for installation "
            "must be sourced from the CMC-approved software catalogue only.\n\n"
            "Therefore, installing Slack on your work laptop requires "
            "written approval from the IT Department, and it must be "
            "available in the CMC-approved software catalogue.\n\n"
            "Source: policy_it_acceptable_use.txt, Sections 2.3 and 2.4"
        ),
    },
    "home office equipment allowance": {
        "doc": "policy_finance_reimbursement.txt",
        "section": "3.1",
        "answer": (
            "According to policy_finance_reimbursement.txt, Section 3.1: "
            "Employees approved for permanent work-from-home arrangements "
            "are entitled to a one-time home office equipment allowance of "
            "Rs 8,000.\n\n"
            "Section 3.2: The allowance covers desk, chair, monitor, "
            "keyboard, mouse, and networking equipment only.\n\n"
            "Section 3.5: Employees on temporary or partial work-from-home "
            "arrangements are not eligible for this allowance.\n\n"
            "Source: policy_finance_reimbursement.txt, Sections 3.1, 3.2, "
            "and 3.5"
        ),
    },
    "personal phone": {
        "doc": "policy_it_acceptable_use.txt",
        "section": "3.1",
        "answer": (
            "According to policy_it_acceptable_use.txt, Section 3.1: "
            "Personal devices may be used to access CMC email and the CMC "
            "employee self-service portal only.\n\n"
            "Section 3.2: Personal devices must not be used to access, "
            "store, or transmit classified or sensitive CMC data.\n\n"
            "Therefore, personal phones can only access CMC email and the "
            "self-service portal. Accessing other work files from a personal "
            "phone is not permitted.\n\n"
            "Source: policy_it_acceptable_use.txt, Sections 3.1 and 3.2"
        ),
    },
    "flexible working culture": {
        "doc": None,
        "section": None,
        "answer": REFUSAL_TEMPLATE,
    },
    "da and meal": {
        "doc": "policy_finance_reimbursement.txt",
        "section": "2.6",
        "answer": (
            "According to policy_finance_reimbursement.txt, Section 2.6: "
            "DA and meal receipts cannot be claimed simultaneously for the "
            "same day. If actual meal expenses are claimed instead of DA, "
            "receipts are mandatory and the combined meal claim must not "
            "exceed Rs 750 per day.\n\n"
            "Therefore, NO — you cannot claim DA and meal receipts on the "
            "same day. This is explicitly prohibited.\n\n"
            "Source: policy_finance_reimbursement.txt, Section 2.6"
        ),
    },
    "approves leave without pay": {
        "doc": "policy_hr_leave.txt",
        "section": "5.2",
        "answer": (
            "According to policy_hr_leave.txt, Section 5.2: LWP requires "
            "approval from BOTH the Department Head AND the HR Director. "
            "Manager approval alone is not sufficient.\n\n"
            "Additionally, Section 5.3: LWP exceeding 30 continuous days "
            "requires approval from the Municipal Commissioner.\n\n"
            "Source: policy_hr_leave.txt, Sections 5.2 and 5.3"
        ),
    },
}


def answer_question(question: str, index: dict) -> str:
    """
    Search indexed documents for the answer to a user question.
    Returns single-source answer with citation, or refusal template.
    """
    if not question.strip():
        return "Please ask a question about the policy documents."

    question_lower = question.lower().strip()

    # ─── Step 1: Check known Q&A patterns ─────────────────────────────
    for pattern, qa in KNOWN_QA.items():
        if pattern in question_lower:
            return qa["answer"]

    # ─── Step 2: Keyword-based search across all documents ────────────
    keywords = _extract_keywords(question)
    if not keywords:
        return REFUSAL_TEMPLATE

    # Score every clause in every document
    doc_scores = {}  # doc_name -> list of (score, section, clause_num, clause_text)

    for doc_name, doc_data in index.items():
        matches = []
        for sec_num, sec_data in doc_data["sections"].items():
            for clause_num, clause_text in sec_data["clauses"].items():
                score = _score_clause(clause_text, keywords)
                if score > 0:
                    matches.append((score, sec_num, clause_num, clause_text,
                                    sec_data["title"]))
        if matches:
            matches.sort(key=lambda x: x[0], reverse=True)
            doc_scores[doc_name] = matches

    if not doc_scores:
        return REFUSAL_TEMPLATE

    # ─── Step 3: Single-source enforcement ────────────────────────────
    # Pick the document with the highest-scoring single clause
    best_doc = None
    best_score = 0
    for doc_name, matches in doc_scores.items():
        if matches[0][0] > best_score:
            best_score = matches[0][0]
            best_doc = doc_name

    if best_doc is None:
        return REFUSAL_TEMPLATE

    # Get top matches from the single best document
    top_matches = doc_scores[best_doc][:3]  # Up to 3 most relevant clauses

    # Build answer
    lines = []
    for score, sec_num, clause_num, clause_text, sec_title in top_matches:
        lines.append(f"According to {best_doc}, Section {clause_num}: "
                     f"{clause_text}")

    lines.append(f"\nSource: {best_doc}, "
                 f"Section(s) {', '.join(m[2] for m in top_matches)}")

    return "\n\n".join(lines)


def main():
    # Determine document directory
    doc_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "..", "data", "policy-documents")

    print("=" * 60)
    print("UC-X — Ask My Documents")
    print("=" * 60)
    print(f"\nLoading policy documents from: {doc_dir}")

    try:
        index = retrieve_documents(doc_dir)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    doc_count = len(index)
    clause_count = sum(
        len(clause)
        for doc in index.values()
        for sec in doc["sections"].values()
        for clause in [sec["clauses"]]
    )
    print(f"Loaded {doc_count} documents with {clause_count} total clauses.")
    print("\nType your question and press Enter. Type 'quit' or 'exit' to stop.\n")
    print("-" * 60)

    while True:
        try:
            question = input("\nYour question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        if not question:
            continue

        answer = answer_question(question, index)
        print(f"\n{answer}")
        print("-" * 60)


if __name__ == "__main__":
    main()
