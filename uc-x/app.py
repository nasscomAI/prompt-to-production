"""
UC-X app.py — Document-based QA for policy documents.

Behaviour:
- Loads multiple policy text files and indexes sections by document and clause.
- Answers questions using a single source where possible, citing document and section.
- Refuses with a fixed refusal template when the question is not covered or would require blending across documents.
"""
import argparse
import glob
import os
import re
from typing import Dict, List, Optional, Tuple

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

CLAUSE_RE = re.compile(r"^(\d+(?:\.\d+)*)(?:\.)?\s+(.*)$")


def retrieve_documents(paths: List[str]) -> Dict[str, Dict[str, str]]:
    """Load documents and index numbered clauses by document name."""
    docs: Dict[str, Dict[str, str]] = {}
    for path in paths:
        name = os.path.basename(path)
        sections: Dict[str, str] = {}
        with open(path, "r", encoding="utf-8") as f:
            current_section: Optional[str] = None
            for line in f:
                raw = line.rstrip("\n")
                stripped = raw.strip()
                if not stripped:
                    continue
                if re.match(r"^[^A-Za-z0-9]+$", stripped):
                    continue
                m = CLAUSE_RE.match(stripped)
                if m:
                    section_id = m.group(1)
                    section_text = m.group(2).strip()
                    current_section = section_id
                    sections[section_id] = section_text
                elif current_section:
                    sections[current_section] = f"{sections[current_section]} {stripped}".strip()
        docs[name] = sections
    return docs


STOPWORDS = {
    "the", "is", "are", "and", "of", "for", "a", "an", "to", "in", "on", "at",
    "by", "with", "that", "this", "from", "as", "if", "or", "not", "can", "what",
    "who", "when", "where", "how", "do", "does", "will", "may", "must", "be",
    "my", "your", "etc", "any", "same", "only", "all", "each", "every",
}

TERM_SYNONYMS = {
    "phone": ["device", "devices", "smartphone", "mobile", "cellphone"],
    "laptop": ["computer", "device", "devices", "machine"],
    "install": ["install", "installed", "installation", "software", "application", "app"],
    "files": ["documents", "data", "portal", "email", "records"],
    "home": ["home", "remote", "work-from-home", "wfh"],
    "leave": ["leave", "lwp", "absence"],
    "pay": ["pay", "payment", "paid", "unpaid"],
    "da": ["da", "daily", "allowance", "meal", "meals"],
    "approval": ["approval", "approve", "approves", "approving", "approver"],
    "equipment": ["equipment", "allowance", "desk", "chair", "monitor", "keyboard", "mouse", "networking"],
}

PHRASE_SYNONYMS = {
    "personal phone": ["personal device", "personal devices", "byod", "mobile device"],
    "work laptop": ["corporate device", "corporate devices", "work device"],
    "install slack": ["install software", "install application", "software installation"],
    "home office equipment": ["work from home equipment", "home office allowance", "work-from-home equipment"],
    "meal receipts": ["meal claim", "meal expense", "meal expenses"],
    "leave without pay": ["lwp", "leave without pay"],
}

APPROVAL_TERMS = {"approve", "approval", "approves", "approving", "approver"}


def _tokenize_text(text: str) -> List[str]:
    return [word for word in re.findall(r"\w+", text.lower()) if word not in STOPWORDS]


def _ngrams(tokens: List[str], n: int) -> List[str]:
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]


def _score_section(text: str, query: str) -> int:
    query_terms = _tokenize_text(query)
    section_terms = _tokenize_text(text)
    section_term_set = set(section_terms)
    score = sum(1 for term in query_terms if term in section_term_set)

    for term in query_terms:
        synonyms = TERM_SYNONYMS.get(term, [])
        for syn in synonyms:
            if syn in section_term_set:
                score += 1

    query_bigrams = _ngrams(query_terms, 2)
    section_bigrams = set(_ngrams(section_terms, 2))
    score += 2 * sum(1 for bigram in query_bigrams if bigram in section_bigrams)

    for phrase, variants in PHRASE_SYNONYMS.items():
        if phrase in query.lower():
            for variant in variants:
                if variant in text.lower():
                    score += 2

    if any(term in APPROVAL_TERMS for term in query_terms) and any(term in section_term_set for term in APPROVAL_TERMS):
        score += 2

    return score


def _is_answerable_section(section_id: str) -> bool:
    return "." in section_id


def answer_question(docs: Dict[str, Dict[str, str]], question: str) -> str:
    """Return an answer with citation or the fixed refusal template."""
    if not question.strip():
        return REFUSAL_TEMPLATE

    normalized_q = question.strip().lower()
    scored_hits: List[Tuple[str, str, str, int]] = []

    for doc_name, sections in docs.items():
        for section_id, section_text in sections.items():
            if not _is_answerable_section(section_id):
                continue
            score = _score_section(section_text, normalized_q)
            if score > 0:
                scored_hits.append((doc_name, section_id, section_text, score))

    if not scored_hits:
        return REFUSAL_TEMPLATE

    scored_hits.sort(key=lambda hit: hit[3], reverse=True)
    best_score = scored_hits[0][3]
    best_hits = [hit for hit in scored_hits if hit[3] == best_score]

    if best_score < 2:
        return REFUSAL_TEMPLATE

    docs_with_best = set(hit[0] for hit in best_hits)
    if len(docs_with_best) > 1:
        return REFUSAL_TEMPLATE

    doc_name, section_id, text, _ = best_hits[0]
    return f"{text} (Source: {doc_name} section {section_id})"


def _is_direct_answer(text: str, query: str) -> bool:
    """Heuristic: direct answer should include enough terms from the query."""
    return sum(1 for word in query.split() if word in text.lower()) >= max(3, len(query.split()) // 2)


def main():
    parser = argparse.ArgumentParser(description="UC-X Document QA")
    parser.add_argument("--input", nargs="*", default=[
        "../data/policy-documents/policy_hr_leave.txt",
        "../data/policy-documents/policy_it_acceptable_use.txt",
        "../data/policy-documents/policy_finance_reimbursement.txt",
    ], help="Paths to policy documents")
    args = parser.parse_args()

    docs = retrieve_documents(args.input)
    print("Loaded documents:", ", ".join(docs.keys()))
    print("Ask a question, or type 'exit' to quit.")

    while True:
        question = input("Question: ").strip()
        if not question or question.lower() == "exit":
            break
        answer = answer_question(docs, question)
        print(answer)


if __name__ == "__main__":
    main()
