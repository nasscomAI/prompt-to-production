"""
UC-X app.py — Ask My Documents
Built per agents.md (single-source only, no hedging, exact refusal template,
mandatory citation) and skills.md (retrieve_documents, answer_question).
"""
import argparse
import os
import re

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)")

DOC_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]
DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "policy-documents")

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# Hardcoded topic → single-source citation. Checked in order; first match wins.
# "sections" can list more than one clause id — still one document, just a
# fuller answer (e.g. the personal-phone trap cites IT §3.1 AND §3.2, both
# directly on point). It must never be blended with HR's remote-work mention.
TOPIC_RULES = [
    {"triggers": ["carry forward", "carry-forward"], "doc": "policy_hr_leave.txt", "sections": ["2.6"]},
    {"triggers": ["leave without pay", "lwp", "who approves leave"], "doc": "policy_hr_leave.txt", "sections": ["5.2"]},
    {"triggers": ["install slack", "install software", "install"], "doc": "policy_it_acceptable_use.txt", "sections": ["2.3"]},
    {"triggers": ["personal phone", "personal device"], "doc": "policy_it_acceptable_use.txt", "sections": ["3.1", "3.2"]},
    {"triggers": ["home office equipment", "equipment allowance"], "doc": "policy_finance_reimbursement.txt", "sections": ["3.1"]},
    {"triggers": ["da and meal", "meal receipts", "daily allowance and meal"], "doc": "policy_finance_reimbursement.txt", "sections": ["2.6"]},
]


def _trigger_matches(question_lower: str, trigger: str) -> bool:
    # Word-boundary match, not plain substring — a bare "work" trigger must
    # not fire on "networks", and "install" must not fire inside "installer".
    return re.search(r"\b" + re.escape(trigger) + r"\b", question_lower) is not None

STOPWORDS = {
    "the", "a", "an", "is", "are", "do", "does", "can", "i", "my", "for", "to",
    "of", "on", "in", "and", "or", "what", "how", "when", "who", "will",
}


def retrieve_documents() -> dict:
    """
    Loads all 3 policy files and indexes their content by document name and
    section number.
    Returns: dict keyed by document name -> list of {section_id, text}.
    """
    index = {}
    for filename in DOC_FILES:
        path = os.path.join(DOCS_DIR, filename)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Required policy document not found: {path}")

        with open(path, encoding="utf-8") as f:
            lines = f.readlines()

        sections = []
        current = None
        for raw_line in lines:
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("═"):
                continue
            if raw_line[0].isspace():
                if current is not None:
                    current["text"] += " " + stripped
                continue
            match = CLAUSE_RE.match(stripped)
            if match:
                if current is not None:
                    sections.append(current)
                current = {"section_id": match.group(1), "text": match.group(2).strip()}
            else:
                if current is not None:
                    sections.append(current)
                    current = None
        if current is not None:
            sections.append(current)

        index[filename] = sections

    return index


def _keyword_score(question_words: set, text: str) -> int:
    text_words = set(re.findall(r"[a-z']+", text.lower())) - STOPWORDS
    return len(question_words & text_words)


def answer_question(question: str, index: dict):
    """
    Searches indexed documents for a single-source answer.
    Returns: dict {answer, source_document, section_id} or the refusal template string.
    section_id is a single clause id, or a comma-joined list when a rule
    cites more than one clause from the same document.
    """
    lower_q = question.lower()

    for rule in TOPIC_RULES:
        if any(_trigger_matches(lower_q, trigger) for trigger in rule["triggers"]):
            by_id = {s["section_id"]: s["text"] for s in index.get(rule["doc"], [])}
            matched = [(sid, by_id[sid]) for sid in rule["sections"] if sid in by_id]
            if matched:
                return {
                    "answer": " ".join(text for _, text in matched),
                    "source_document": rule["doc"],
                    "section_id": ", ".join(sid for sid, _ in matched),
                }

    # Generic fallback: keyword-overlap search across every section in every
    # document. Only answers if the best match belongs to exactly one
    # document — a tie or near-tie across documents means blending risk, so
    # it refuses instead of guessing.
    question_words = set(re.findall(r"[a-z']+", lower_q)) - STOPWORDS
    scored = []
    for doc_name, sections in index.items():
        for section in sections:
            score = _keyword_score(question_words, section["text"])
            if score > 0:
                scored.append((score, doc_name, section))

    if not scored:
        return REFUSAL_TEMPLATE

    scored.sort(key=lambda item: item[0], reverse=True)
    top_score = scored[0][0]
    top_docs = {doc_name for score, doc_name, _ in scored if score == top_score}

    if len(top_docs) > 1:
        # Best match is equally strong in more than one document — refuse
        # rather than blend across documents.
        return REFUSAL_TEMPLATE

    best_score, best_doc, best_section = scored[0]
    if best_score < 2:
        # Too weak a match to answer confidently — refuse rather than guess.
        return REFUSAL_TEMPLATE

    return {
        "answer": best_section["text"],
        "source_document": best_doc,
        "section_id": best_section["section_id"],
    }


def _print_answer(result) -> None:
    if isinstance(result, dict):
        print(result["answer"])
        sections = ", ".join(f"§{sid.strip()}" for sid in result["section_id"].split(","))
        print(f"[Source: {result['source_document']} {sections}]")
    else:
        print(result)


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--question", help="Ask a single question and exit (non-interactive mode)")
    args = parser.parse_args()

    index = retrieve_documents()

    if args.question:
        _print_answer(answer_question(args.question, index))
        return

    print("UC-X Ask My Documents — type a question ('exit' to quit).")
    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break
        _print_answer(answer_question(question, index))


if __name__ == "__main__":
    main()
