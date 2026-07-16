"""
UC-X app.py — Ask My Documents
Built via RICE -> agents.md -> skills.md -> CRAFT workflow.
Interactive CLI: loads 3 policy documents, answers from a single source or refuses.
"""
import re
import os

DOC_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_HEADER_PATTERN = re.compile(r"^\d+\.\s+[A-Z][A-Z\s()]+$")

STOPWORDS = {
    "a", "an", "the", "is", "are", "to", "for", "on", "and", "do", "does",
    "my", "i", "can", "of", "that", "this", "in", "at", "with", "from",
    "please", "what", "who", "when", "or", "be", "it", "if", "me", "am",
    "will", "was", "were", "as", "by", "how", "am", "you", "your",
    # Device/location nouns used as illustrative examples across all three
    # documents (e.g. "laptops, desktops, mobile phones" as a device list) —
    # low signal for distinguishing which clause governs, regardless of IDF.
    "device", "devices", "laptop", "laptops", "phone", "phones", "mobile",
    "computer", "computers", "desktop", "desktops", "home", "work",
}

# Abbreviations the source documents define once and then use in place of
# the full phrase (e.g. clause 5.2 says "LWP requires approval..." after
# defining LWP in the section 5 header) — expand so keyword search still
# connects a fully-spelled-out question to the abbreviated clause.
ABBREVIATION_EXPANSIONS = {
    "lwp": ["leave", "without", "pay"],
    "da": ["daily", "allowance"],
    "mfa": ["multi", "factor", "authentication"],
}


def _stem(word: str) -> str:
    return word[:5] if len(word) >= 6 else word


def _tokenize(text: str):
    words = re.findall(r"[a-zA-Z]+", text.lower())
    tokens = []
    for w in words:
        if w in STOPWORDS:
            continue
        tokens.append(_stem(w))
        for expansion in ABBREVIATION_EXPANSIONS.get(w, []):
            tokens.append(_stem(expansion))
    return tokens


def retrieve_documents(file_paths):
    """
    Loads all 3 policy files and indexes their content by document name and section number.
    Returns: list of {doc, clause, text} dicts.
    """
    index = []
    for path in file_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Required policy document missing: {path}")
        doc_name = os.path.basename(path)
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()

        current_clause = None
        current_lines = []
        for line in lines:
            stripped = line.strip()
            match = CLAUSE_PATTERN.match(stripped)
            if match:
                if current_clause is not None:
                    index.append({"doc": doc_name, "clause": current_clause, "text": " ".join(current_lines).strip()})
                current_clause = match.group(1)
                current_lines = [match.group(2)]
            elif (
                current_clause is not None
                and stripped
                and not stripped.startswith("═")
                and not SECTION_HEADER_PATTERN.match(stripped)
            ):
                current_lines.append(stripped)
        if current_clause is not None:
            index.append({"doc": doc_name, "clause": current_clause, "text": " ".join(current_lines).strip()})

    return index


def answer_question(question: str, index):
    """
    Searches the indexed documents for a question.
    Returns: {answer, source, refused}
    """
    q_tokens = set(_tokenize(question))
    if not q_tokens:
        return {"answer": REFUSAL_TEMPLATE, "source": None, "refused": True}

    # Weight matches by inverse document frequency so a rare, distinguishing
    # token (e.g. "install") outweighs a token that appears in nearly every
    # clause (e.g. "work", "use") and would otherwise win on raw count alone.
    clause_tokens = [(entry, set(_tokenize(entry["text"]))) for entry in index]
    doc_freq = {}
    for _, ctoks in clause_tokens:
        for t in ctoks:
            doc_freq[t] = doc_freq.get(t, 0) + 1

    scored = []
    for entry, ctoks in clause_tokens:
        overlap = q_tokens & ctoks
        score = sum(1.0 / doc_freq[t] for t in overlap)
        scored.append((score, entry))

    scored.sort(key=lambda x: (-x[0], x[1]["doc"], x[1]["clause"]))
    top_score = scored[0][0]

    if top_score < 0.3:
        return {"answer": REFUSAL_TEMPLATE, "source": None, "refused": True}

    top_doc = scored[0][1]["doc"]
    best_other_doc_score = next((s for s, e in scored if e["doc"] != top_doc), 0)

    if best_other_doc_score >= top_score * 0.8:
        return {"answer": REFUSAL_TEMPLATE, "source": None, "refused": True}

    supporting = [e for s, e in scored if e["doc"] == top_doc and s == top_score][:3]
    supporting.sort(key=lambda e: e["clause"])

    citation = ", ".join(f"§{e['clause']}" for e in supporting)
    lines = [f"[{top_doc} {citation}]"]
    for e in supporting:
        lines.append(f"  {e['clause']}: {e['text']}")

    return {"answer": "\n".join(lines), "source": f"{top_doc} {citation}", "refused": False}


def main():
    index = retrieve_documents(DOC_PATHS)
    print("UC-X Ask My Documents — loaded", len(index), "clauses from 3 policy documents.")
    print("Type a question, or 'quit' to exit.\n")
    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            break
        if not question or question.lower() in ("quit", "exit"):
            break
        result = answer_question(question, index)
        print(result["answer"])
        print()


if __name__ == "__main__":
    main()
