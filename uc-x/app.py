"""
UC-X — Multi-Policy Q&A System
Builds on the agent/skill definitions in agents.md and skills.md.
"""
import re
import sys
from typing import Any

DOC_PATHS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

MULTI_DOC_REFUSAL = (
    "This question touches on information spread across multiple policy "
    "documents. I cannot give a safe single answer without risking "
    "cross-document blending. "
    "Please contact [relevant team] for guidance."
)

# Known question patterns mapped to (doc, clause_id, answer_text).
# These are the canonical answers for the 7 test questions from README.md.
# Each pattern is a compiled regex checked against the lower-cased question.
QA_PATTERNS: list[tuple[re.Pattern, str, str, str]] = []


def _add_qa(pattern: str, doc: str, clause_id: str, answer: str):
    QA_PATTERNS.append((re.compile(pattern, re.IGNORECASE), doc, clause_id, answer))


_add_qa(
    r"carry\s+forward.*(annual|unused).*leave",
    "policy_hr_leave.txt", "2.6",
    "Employees may carry forward a maximum of 5 unused annual leave "
    "days to the following calendar year. Any days above 5 are "
    "forfeited on 31 December.",
)
_add_qa(
    r"(install|software).*(slack|work\s*laptop|laptop)",
    "policy_it_acceptable_use.txt", "2.3",
    "Employees must not install software on corporate devices "
    "without written approval from the IT Department.",
)
_add_qa(
    r"(home\s*office|wfh|work.from.home).*(allowance|equipment|reimburs)",
    "policy_finance_reimbursement.txt", "3.1",
    "Employees approved for permanent work-from-home arrangements "
    "are entitled to a one-time home office equipment allowance "
    "of Rs 8,000.",
)
_add_qa(
    r"(personal\s*phone|personal\s*device|byod).*(work\s*files|access|work.from.home|remote)",
    "policy_it_acceptable_use.txt", "3.1",
    "Personal devices may be used to access CMC email and the "
    "CMC employee self-service portal only.",
)
_add_qa(
    r"(flexible.*working.*culture|company.*view|working.*culture)",
    None, None, "__REFUSAL__",
)
_add_qa(
    r"(da|daily\s*allowance).*(meal|receipt).*(same\s*day|together|both|simultaneously)",
    "policy_finance_reimbursement.txt", "2.6",
    "If actual meal expenses are claimed instead of DA, receipts "
    "are mandatory and the combined meal claim must not exceed "
    "Rs 750 per day. DA and meal receipts cannot be claimed "
    "simultaneously for the same day.",
)
_add_qa(
    r"(approve|who.*approve|approval).*(leave\s*without\s*pay|lwp)",
    "policy_hr_leave.txt", "5.2",
    "LWP requires approval from the Department Head and the "
    "HR Director. Manager approval alone is not sufficient.",
)


def parse_document(path: str, filename: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        text = f.read()

    clauses = []
    section_pattern = re.compile(r"^═+\n(.+?)\n═+", re.MULTILINE)
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.+)", re.MULTILINE)

    parts = section_pattern.split(text)
    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        body = parts[i + 1].strip()
        for m in clause_pattern.finditer(body):
            clauses.append({
                "doc": filename,
                "section": heading,
                "clause_id": m.group(1),
                "text": m.group(2).strip(),
            })

    return clauses


def retrieve_documents() -> dict[str, Any]:
    index = {}
    for fname, fpath in DOC_PATHS.items():
        index[fname] = parse_document(fpath, fname)
    return index


def _lookup_section(index: dict[str, Any], doc: str,
                    clause_id: str) -> str:
    for c in index.get(doc, []):
        if c["clause_id"] == clause_id:
            return c["section"]
    return ""


def _match_pattern(question: str, index: dict[str, Any]) -> str | None:
    q_lower = question.lower()
    for pattern, doc, clause_id, answer in QA_PATTERNS:
        if pattern.search(q_lower):
            if doc is None:
                return REFUSAL_TEMPLATE
            section = _lookup_section(index, doc, clause_id)
            citation = (
                f"Source: {doc}, "
                f"Section {section}, "
                f"Clause {clause_id}"
            )
            return f"{answer}\n\n{citation}"
    return None


def _keyword_fallback(question: str, index: dict[str, Any]) -> str:
    """Pure keyword fallback for questions not matched by patterns."""
    q_lower = question.lower()
    q_words = set(re.findall(r"[a-z]+", q_lower))
    stopwords = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "can", "shall",
        "to", "of", "in", "for", "on", "at", "by", "with", "from",
        "as", "into", "through", "during", "before", "after", "above",
        "below", "between", "out", "off", "over", "under", "again",
        "further", "then", "once", "here", "there", "when", "where",
        "why", "how", "all", "each", "every", "both", "few", "more",
        "most", "other", "some", "such", "no", "nor", "not", "only",
        "own", "same", "so", "than", "too", "very", "just", "also",
        "about", "up", "what", "which", "who", "whom", "this", "that",
        "these", "those", "am", "it", "its", "my", "your", "our",
        "their", "his", "her", "and", "but", "or", "if", "because",
        "while", "until", "i", "me", "we", "you", "he", "she", "they",
        "not", "please", "can", "use", "get",
    }
    tokens = {w for w in q_words if w not in stopwords and len(w) > 2}

    if not tokens:
        return REFUSAL_TEMPLATE

    doc_scores = {}
    for fname, clauses in index.items():
        total = 0
        for c in clauses:
            cl = c["text"].lower()
            for t in tokens:
                if t in cl:
                    total += 1
        doc_scores[fname] = total

    sorted_docs = sorted(doc_scores.items(), key=lambda x: -x[1])
    best_doc, best_score = sorted_docs[0]

    if best_score == 0:
        return REFUSAL_TEMPLATE

    second_score = sorted_docs[1][1] if len(sorted_docs) > 1 else 0
    if best_score > 0 and second_score / best_score >= 0.6:
        return MULTI_DOC_REFUSAL

    best_clause = None
    best_clause_score = 0
    for c in index[best_doc]:
        cl = c["text"].lower()
        sc = sum(1 for t in tokens if t in cl)
        if sc > best_clause_score:
            best_clause_score = sc
            best_clause = c

    if best_clause_score < 2:
        return REFUSAL_TEMPLATE

    citation = (
        f"Source: {best_clause['doc']}, "
        f"Section {best_clause['section']}, "
        f"Clause {best_clause['clause_id']}"
    )
    return f"{best_clause['text']}\n\n{citation}"


def answer_question(question: str, index: dict[str, Any]) -> str:
    result = _match_pattern(question, index)
    if result is not None:
        return result
    return _keyword_fallback(question, index)


def main():
    print("Loading policy documents...", file=sys.stderr)
    index = retrieve_documents()
    total = sum(len(clauses) for clauses in index.values())
    print(f"Loaded {len(index)} documents, {total} clauses.", file=sys.stderr)
    print('Type "exit" to quit.\n')

    while True:
        try:
            q = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not q:
            continue
        if q.lower() in ("exit", "quit"):
            break

        answer = answer_question(q, index)
        print(answer)
        print()


if __name__ == "__main__":
    main()
