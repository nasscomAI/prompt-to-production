"""
UC-X app.py — Interactive policy Q&A over 3 documents.
Built using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""

import argparse
import re
import os

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

DEFAULT_DOCS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}

STOPWORDS = {
    "the", "a", "an", "is", "are", "i", "my", "on", "to", "for", "of", "and",
    "or", "in", "at", "can", "what", "who", "do", "does", "it", "if", "be",
    "same", "with", "when", "from", "this", "that", "these", "those", "was",
    "were", "will", "would", "should", "could", "have", "has", "had", "not",
}


def retrieve_documents(paths: dict) -> dict:
    """
    Load all policy files and index content by document name and section number.
    Returns: dict[doc_name] -> dict[section_number] -> section_text
    """
    section_pattern = re.compile(
        r"^(\d+\.\d+)\s+(.*(?:\n(?!\d+\.\d+|\d+\.\s|═|\Z).*)*)", re.MULTILINE
    )
    docs = {}
    for doc_name, path in paths.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Policy document not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        sections = {}
        for match in section_pattern.finditer(text):
            num = match.group(1)
            body = " ".join(line.strip() for line in match.group(2).strip().splitlines())
            sections[num] = body
        docs[doc_name] = sections
    return docs

def _stem(word: str) -> str:
    for suffix in ("ing", "ed", "es", "s", "al", "e"):
        if word.endswith(suffix) and len(word) - len(suffix) > 3:
            return word[: -len(suffix)]
    return word


def _tokenize(text: str) -> set:
    words = re.findall(r"[a-zA-Z]+", text.lower())
    tokens = {_stem(w) for w in words if w not in STOPWORDS and len(w) > 2}
    if "lwp" in tokens:
        tokens |= {"leav", "without", "pay"}
    if {"leav", "without", "pay"}.issubset(tokens):
        tokens.add("lwp")
    return tokens

def answer_question(question: str, docs: dict) -> str:
    """
    Search indexed documents for the question. Return a single-source answer
    with citation, or the exact refusal template if not covered or if
    answering would require blending two documents.
    """
    q_tokens = _tokenize(question)
    if not q_tokens:
        return REFUSAL_TEMPLATE

    # Build a corpus of all sections across all documents, for IDF weighting.
    all_sections = []
    for doc_name, sections in docs.items():
        for sec_num, sec_text in sections.items():
            all_sections.append((doc_name, sec_num, sec_text, _tokenize(sec_text)))

    n_sections = len(all_sections)
    import math
    df = {}
    for _, _, _, tokens in all_sections:
        for t in tokens:
            df[t] = df.get(t, 0) + 1

    def idf(word):
        return math.log((n_sections + 1) / (df.get(word, 0) + 1)) + 1

    def score(section_tokens):
        matched = q_tokens & section_tokens
        return sum(idf(w) for w in matched)

    doc_scores = {}
    for doc_name, sections in docs.items():
        best_score, best_section, best_text = 0.0, None, None
        for sec_num, sec_text in sections.items():
            s = score(_tokenize(sec_text))
            if s > best_score:
                best_score, best_section, best_text = s, sec_num, sec_text
        doc_scores[doc_name] = (best_score, best_section, best_text)

    ranked = sorted(doc_scores.items(), key=lambda kv: kv[1][0], reverse=True)
    top_doc, (top_score, top_section, top_text) = ranked[0]
    second_score = ranked[1][1][0] if len(ranked) > 1 else 0.0

    if top_score < 1.0:
        return REFUSAL_TEMPLATE

    if second_score > 0 and second_score >= top_score * 0.85:
        return REFUSAL_TEMPLATE

    return f"{top_text} [Source: {top_doc}, Section {top_section}]"

def run_cli(docs: dict):
    print("Ask My Documents — type a question, or 'exit' to quit.")
    while True:
        try:
            question = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if question.lower() in ("exit", "quit"):
            print("Exiting.")
            break
        if not question:
            continue
        print(answer_question(question, docs))


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--hr", default=DEFAULT_DOCS["policy_hr_leave.txt"])
    parser.add_argument("--it", default=DEFAULT_DOCS["policy_it_acceptable_use.txt"])
    parser.add_argument("--finance", default=DEFAULT_DOCS["policy_finance_reimbursement.txt"])
    args = parser.parse_args()

    paths = {
        "policy_hr_leave.txt": args.hr,
        "policy_it_acceptable_use.txt": args.it,
        "policy_finance_reimbursement.txt": args.finance,
    }
    docs = retrieve_documents(paths)
    run_cli(docs)


if __name__ == "__main__":
    main()

