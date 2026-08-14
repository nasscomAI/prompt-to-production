"""
UC-X app.py — Ask My Documents
Built from agents.md (enforcement rules) and skills.md (skill contracts).
Interactive CLI — type questions, read answers. Type 'exit' to quit.
"""
import argparse
import glob
import math
import os
import re

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
)

SECTION_LINE = re.compile(r"^(\d+\.\d+)\s+(.*)$")

STOPWORDS = {
    "a", "an", "the", "is", "are", "am", "i", "my", "me", "to", "for", "of",
    "on", "in", "at", "and", "or", "can", "do", "does", "what", "who", "when",
    "if", "it", "this", "that", "be", "with", "as", "by", "from", "not", "no",
    "will", "must", "may", "any", "all", "up", "using", "use", "used",
}

# Domain abbreviations used in the source documents that a question is
# likely to spell out in full (or vice versa).
ACRONYM_EXPANSIONS = {
    "lwp": ["leave", "without", "pay"],
    "da": ["daily", "allowance"],
    "mfa": ["multi", "factor", "authentication"],
}

_STEM_SUFFIXES = ("ations", "ation", "ally", "edly", "ing", "ies", "ied", "es", "al", "ed", "s")


def _stem(word: str) -> str:
    for suf in _STEM_SUFFIXES:
        if word.endswith(suf) and len(word) - len(suf) >= 3:
            return word[: -len(suf)]
    return word


def _tokenize(text: str) -> set:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    tokens = set()
    for w in words:
        if w in ACRONYM_EXPANSIONS:
            tokens.update(_stem(t) for t in ACRONYM_EXPANSIONS[w])
            continue
        if w in STOPWORDS or len(w) <= 1:
            continue
        tokens.add(_stem(w))
    return tokens


def retrieve_documents(dir_path: str) -> list:
    """
    Load all 3 policy files and index their content by document name and
    section number.
    """
    file_paths = sorted(glob.glob(os.path.join(dir_path, "policy_*.txt")))
    if not file_paths:
        raise FileNotFoundError(f"No policy_*.txt files found in {dir_path}")

    index = []
    for file_path in file_paths:
        doc_name = os.path.basename(file_path)
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        current = None
        for line in lines:
            match = SECTION_LINE.match(line)
            if match:
                if current is not None:
                    index.append(current)
                current = {"doc_name": doc_name, "section": match.group(1), "text": match.group(2).strip()}
            elif current is not None and line.strip() and line.startswith((" ", "\t")):
                current["text"] = f"{current['text']} {line.strip()}"
            elif current is not None and (not line.strip() or not line.startswith((" ", "\t"))):
                index.append(current)
                current = None
        if current is not None:
            index.append(current)

    return index


def _build_doc_frequencies(index: list) -> dict:
    """document frequency of each stemmed token, across all indexed sections."""
    df = {}
    for entry in index:
        for token in _tokenize(entry["text"]):
            df[token] = df.get(token, 0) + 1
    return df


TOKEN_WEIGHT_CAP = 0.5  # no single rare word may dominate a section's score


def _weighted_score(q_tokens: set, entry_tokens: set, df: dict) -> float:
    shared = q_tokens & entry_tokens
    return sum(
        min(1.0 / (1.0 + math.log(df.get(token, 1))), TOKEN_WEIGHT_CAP)
        for token in shared
    )


MATCH_THRESHOLD = 0.45  # minimum weighted score to count as relevant at all
AMBIGUITY_RATIO = 0.75  # second-best doc within this fraction of the top = ambiguous


def answer_question(question: str, index: list) -> str:
    """
    Search the indexed documents for the question and return a single-source
    answer with citation, or the refusal template.
    """
    q_tokens = _tokenize(question)
    if not q_tokens:
        return REFUSAL_TEMPLATE

    df = _build_doc_frequencies(index)

    scored_entries = []
    best_per_doc = {}
    for entry in index:
        score = _weighted_score(q_tokens, _tokenize(entry["text"]), df)
        if score < MATCH_THRESHOLD:
            continue
        scored_entries.append((score, entry))
        doc = entry["doc_name"]
        if doc not in best_per_doc or score > best_per_doc[doc][0]:
            best_per_doc[doc] = (score, entry)

    if not best_per_doc:
        return REFUSAL_TEMPLATE

    ranked_docs = sorted(best_per_doc.items(), key=lambda x: x[1][0], reverse=True)

    top_doc, (top_score, _) = ranked_docs[0]
    if len(ranked_docs) > 1:
        _, (second_score, _) = ranked_docs[1]
        # Two different documents score comparably — genuine cross-document
        # ambiguity. Refuse rather than blend.
        if second_score >= top_score * AMBIGUITY_RATIO:
            return REFUSAL_TEMPLATE

    # Within the winning document, surface up to the top 2 relevant sections
    # (still single-source) so a strong-but-secondary clause isn't dropped.
    same_doc_matches = [(s, e) for s, e in scored_entries if e["doc_name"] == top_doc]
    same_doc_matches.sort(key=lambda x: x[0], reverse=True)
    top_matches = same_doc_matches[:2]

    return "\n\n".join(
        f"Source: {entry['doc_name']} Section {entry['section']}\n{entry['text']}"
        for _, entry in top_matches
    )


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--docs-dir", default="../data/policy-documents", help="Directory containing the policy .txt files")
    args = parser.parse_args()

    index = retrieve_documents(args.docs_dir)
    print(f"Loaded {len(index)} sections from {args.docs_dir}. Type a question, or 'exit' to quit.")

    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            break
        if not question or question.lower() == "exit":
            break
        print(answer_question(question, index))
        print()


if __name__ == "__main__":
    main()
