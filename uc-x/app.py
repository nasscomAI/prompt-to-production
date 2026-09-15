"""
UC-X app.py — Ask My Documents
Built using the RICE + agents.md + skills.md + CRAFT workflow.
Interactive CLI: type a question, get a single-source answer or a refusal.
"""
import re
import glob
import os

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact [relevant team] "
    "for guidance."
)

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "can", "i", "my", "me",
    "to", "for", "of", "on", "in", "and", "or", "do", "does", "what",
    "who", "when", "how", "at", "with", "this", "that", "it", "be",
    "from", "as", "if", "also", "will", "shall", "must", "not", "use",
    "used", "employees", "employee", "work", "policy", "company",
}

CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_HEADER_PATTERN = re.compile(r"^\d+\.\s+[A-Z][A-Z \-/()]+$")

DOCUMENT_FILES = {
    "policy_hr_leave.txt": "HR Leave Policy",
    "policy_it_acceptable_use.txt": "IT Acceptable Use Policy",
    "policy_finance_reimbursement.txt": "Finance Reimbursement Policy",
}


def _stem(word: str) -> str:
    """Light suffix stripping so 'approves'/'approval'/'approved' etc. connect."""
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith("ing") and len(word) > 5:
        return word[:-3]
    if word.endswith("ed") and len(word) > 4:
        return word[:-2]
    if word.endswith("es") and len(word) > 4:
        return word[:-2]
    if word.endswith("al") and len(word) > 5:
        return word[:-2]
    if word.endswith("s") and len(word) > 3:
        return word[:-1]
    return word


# Documents use acronyms interchangeably with their spelled-out forms
# (e.g. "LWP" for "Leave Without Pay", "DA" for "Daily Allowance"). This
# expands a question so it can match whichever form the source text uses.
PHRASE_EXPANSIONS = {
    "leave without pay": "lwp",
    "daily allowance": "da",
}


def tokenize(text: str) -> list:
    lowered = text.lower()
    for phrase, acronym in PHRASE_EXPANSIONS.items():
        if phrase in lowered:
            lowered += " " + acronym
    words = re.findall(r"[a-zA-Z]+", lowered)
    return [_stem(w) for w in words if w not in STOPWORDS and len(w) > 2]


def retrieve_documents(directory: str) -> dict:
    """
    Loads all 3 policy files and indexes them by document name and
    section number. Returns:
    { doc_filename: { section_number: clause_text } }
    Handles clauses that wrap across multiple lines.
    """
    documents = {}
    for filename in DOCUMENT_FILES:
        path = os.path.join(directory, filename)
        sections = {}
        current_num = None

        with open(path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or not any(ch.isalnum() for ch in line):
                    continue
                if SECTION_HEADER_PATTERN.match(line):
                    continue

                match = CLAUSE_PATTERN.match(line)
                if match:
                    current_num = match.group(1)
                    sections[current_num] = match.group(2)
                elif current_num:
                    sections[current_num] += " " + line

        documents[filename] = sections
    return documents


def _build_idf(documents: dict) -> dict:
    """
    Rarer words (appearing in fewer sections across all documents) get
    a higher weight. Common words like 'employee' or 'work' appear
    everywhere and get weighted down to near zero — this is what stops
    a generic word from causing a false cross-document match.
    """
    doc_freq = {}
    total_sections = 0
    for sections in documents.values():
        for text in sections.values():
            total_sections += 1
            for word in set(tokenize(text)):
                doc_freq[word] = doc_freq.get(word, 0) + 1

    idf = {}
    for word, freq in doc_freq.items():
        idf[word] = 1.0 / freq
    return idf


def answer_question(question: str, documents: dict, idf: dict) -> str:
    """
    Searches indexed documents and returns a single-source answer with
    citation, or the exact refusal template if no document scores
    highly enough. Never combines sections from two different documents
    into one answer.
    """
    q_tokens = set(tokenize(question))
    if not q_tokens:
        return REFUSAL_TEMPLATE

    # --- Score every section across every document individually. Using
    # the single best-scoring section (not a summed document total) means
    # one document can't "win" just by containing a common word in many
    # sections — the document is chosen by its single strongest match. ---
    # Rank by (how many distinct question words matched, then weighted
    # score) so a section covering several relevant words beats a section
    # that happens to share just one rare word with the question.
    all_scores = {}  # (filename, section_number) -> (overlap_count, weighted_score)
    for filename, sections in documents.items():
        for number, text in sections.items():
            section_tokens = set(tokenize(text))
            overlap = q_tokens & section_tokens
            if not overlap:
                continue
            weighted = sum(idf.get(t, 0) for t in overlap)
            all_scores[(filename, number)] = (len(overlap), weighted)

    if not all_scores:
        return REFUSAL_TEMPLATE

    MIN_OVERLAP_COUNT = 1
    ABSOLUTE_SCORE_THRESHOLD = 0.5
    best_key = max(all_scores, key=all_scores.get)
    best_count, best_score = all_scores[best_key]
    if best_count < MIN_OVERLAP_COUNT or best_score < ABSOLUTE_SCORE_THRESHOLD:
        return REFUSAL_TEMPLATE

    best_doc = best_key[0]

    # --- Gather other strong sections from that same document only ---
    sections = documents[best_doc]
    section_scores = {
        num: weighted for (fname, num), (count, weighted) in all_scores.items()
        if fname == best_doc
    }
    top_score = max(section_scores.values())
    SECTION_RELATIVE_THRESHOLD = 0.5
    matched = [
        (num, sections[num]) for num, s in section_scores.items()
        if s >= top_score * SECTION_RELATIVE_THRESHOLD
    ]
    matched.sort(key=lambda pair: pair[0])
    matched = matched[:3]  # cap at 3 clauses to keep answers focused

    doc_label = DOCUMENT_FILES[best_doc]
    lines = [f"Source: {doc_label} ({best_doc})"]
    for number, text in matched:
        lines.append(f"  [{number}] {text}")
    return "\n".join(lines)


def main():
    data_dir = os.path.join("..", "data", "policy-documents")
    if not os.path.isdir(data_dir):
        data_dir = os.path.join("data", "policy-documents")

    documents = retrieve_documents(data_dir)
    idf = _build_idf(documents)

    print("UC-X — Ask My Documents")
    print("Type a question about HR leave, IT acceptable use, or Finance "
          "reimbursement policy. Type 'exit' to quit.\n")

    while True:
        question = input("> ").strip()
        if question.lower() in ("exit", "quit"):
            break
        if not question:
            continue
        print()
        print(answer_question(question, documents, idf))
        print()


if __name__ == "__main__":
    main()