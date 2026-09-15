"""
UC-X app.py — Ask My Documents
Built from agents.md (RICE) and skills.md via the CRAFT workflow.
"""
import re

DOCUMENT_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
)

SECTION_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_HEADER_PATTERN = re.compile(r"^\d+\.\s+[A-Z]")

STOPWORDS = {
    "a", "an", "the", "is", "are", "can", "i", "to", "for", "on", "in", "of",
    "and", "or", "my", "what", "do", "does", "when", "which", "who", "with",
    "at", "as", "be", "this", "that", "it", "not", "about", "from", "by",
    "use", "used", "have", "has", "you", "your", "if", "work", "official",
}

# The source documents abbreviate "Leave Without Pay" as "LWP" in several
# clauses (5.2-5.4) while questions spell it out — expand it in the search
# index only, so scoring sees both forms. The displayed/cited text is
# unaffected (it comes from the original, unexpanded "text" field).
ABBREVIATION_EXPANSIONS = {
    "lwp": "leave without pay",
}


def retrieve_documents(file_paths: list[str]) -> list[dict]:
    """
    Load all policy .txt files and index their content by document name
    and section number.
    """
    sections = []
    for path in file_paths:
        doc_name = path.rsplit("/", 1)[-1]
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()

        current = None
        for line in lines:
            stripped = line.strip()
            match = SECTION_PATTERN.match(stripped)
            if match:
                if current:
                    sections.append(current)
                current = {"doc_name": doc_name, "section": match.group(1), "text": match.group(2)}
            elif (
                current
                and stripped
                and not stripped.startswith(("=", "─", "═"))
                and not SECTION_HEADER_PATTERN.match(stripped)
            ):
                current["text"] += " " + stripped
        if current:
            sections.append(current)

    return sections


def _keywords(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z']+", text.lower())
    return {w for w in words if len(w) >= 3 and w not in STOPWORDS}


def answer_question(question: str, sections: list[dict]) -> str:
    """
    Search indexed sections for a question. Returns a single-source cited
    answer, or the exact refusal template if no match or matches span more
    than one document.
    """
    query_keywords = _keywords(question)
    if not query_keywords:
        return REFUSAL_TEMPLATE

    scored = []
    for sec in sections:
        text_lower = sec["text"].lower()
        for abbr, expansion in ABBREVIATION_EXPANSIONS.items():
            if abbr in text_lower:
                text_lower += " " + expansion
        # Match on a short prefix of each keyword so different word forms
        # of the same root (e.g. "approves" vs "approval") still count.
        matched = {kw for kw in query_keywords if kw[:6] in text_lower}
        if matched:
            scored.append((matched, sec))

    if not scored:
        return REFUSAL_TEMPLATE

    # Find the best single-clause match first (most distinct keywords
    # matched in one clause). If the top clauses span more than one
    # document, break the tie by which document's top clauses collectively
    # cover more of the question's distinct keywords — this rewards a
    # document with several clauses supporting different parts of the
    # question over one clause elsewhere with a single incidental overlap.
    # Only refuse if that still ties across documents.
    top_clause_score = max(len(matched) for matched, _ in scored)
    candidates = [(matched, sec) for matched, sec in scored if len(matched) == top_clause_score]

    docs_involved = {sec["doc_name"] for _, sec in candidates}
    if len(docs_involved) > 1:
        doc_support = {}
        for matched, sec in candidates:
            doc_support.setdefault(sec["doc_name"], set()).update(matched)
        top_support = max(len(kws) for kws in doc_support.values())
        top_docs = [doc for doc, kws in doc_support.items() if len(kws) == top_support]
        if len(top_docs) > 1:
            return REFUSAL_TEMPLATE
        winning_doc = top_docs[0]
        candidates = [(matched, sec) for matched, sec in candidates if sec["doc_name"] == winning_doc]

    lines = [
        f"Per {sec['doc_name']} section {sec['section']}: {sec['text']}"
        for _, sec in candidates
    ]
    return "\n".join(lines)


def main():
    sections = retrieve_documents(DOCUMENT_PATHS)
    print("UC-X Ask My Documents. Type a question, or 'quit' to exit.")
    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            break
        if not question or question.lower() in ("quit", "exit"):
            break
        print(answer_question(question, sections))
        print()


if __name__ == "__main__":
    main()
