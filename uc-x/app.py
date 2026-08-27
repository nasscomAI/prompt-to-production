"""
UC-X app.py — Interactive document question answering.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import re
from pathlib import Path

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

SECTION_RE = re.compile(r'^(\d+\.\d+)\s+(.*)$')
STOP_WORDS = {
    "the", "is", "are", "a", "an", "and", "or", "of", "to", "in", "for",
    "with", "on", "that", "this", "it", "by", "from", "can", "be",
    "will", "into", "as", "not", "any", "which", "when", "what",
    "how", "do", "does", "may", "must", "your", "employee", "employees"
}


def tokenize(text: str):
    """Convert text to normalized tokens for simple matching."""
    return [token for token in re.findall(r"\w+", text.lower()) if token not in STOP_WORDS]


def retrieve_documents(paths):
    """Load policy files and index clause sections by document and section number."""
    documents = {}
    for path in paths:
        path = Path(path)
        text = path.read_text(encoding='utf-8')
        sections = []
        current_section = None
        current_text = []

        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue

            match = SECTION_RE.match(stripped)
            if match:
                if current_section is not None:
                    sections.append({
                        "section": current_section,
                        "text": " ".join(current_text).strip(),
                    })
                current_section = match.group(1)
                current_text = [match.group(2)]
            elif current_section is not None:
                current_text.append(stripped)

        if current_section is not None:
            sections.append({
                "section": current_section,
                "text": " ".join(current_text).strip(),
            })

        documents[path.name] = sections
    return documents


def score_section(question_tokens, section_text):
    """Score a document section by keyword overlap with the question."""
    section_tokens = tokenize(section_text)
    if not section_tokens:
        return 0
    return sum(1 for token in set(question_tokens) if token in section_tokens)


def find_best_section(document, question_tokens):
    """Return the highest scoring section in a single document."""
    best = None
    best_score = 0
    for section in document:
        score = score_section(question_tokens, section['text'])
        if score > best_score:
            best_score = score
            best = section
    return best, best_score


def answer_question(documents, question: str):
    """Answer a question from indexed documents, or return the exact refusal template."""
    question_tokens = tokenize(question)
    if not question_tokens:
        return REFUSAL_TEMPLATE

    doc_scores = []
    for doc_name, sections in documents.items():
        best_section, best_score = find_best_section(sections, question_tokens)
        doc_scores.append((best_score, doc_name, best_section))

    doc_scores.sort(reverse=True, key=lambda item: item[0])
    top_score, top_doc, top_section = doc_scores[0]
    second_score = doc_scores[1][0] if len(doc_scores) > 1 else 0

    if top_score == 0:
        return REFUSAL_TEMPLATE

    if second_score >= top_score * 0.75:
        return REFUSAL_TEMPLATE

    answer_text = top_section['text']
    return f"{answer_text} (Source: {top_doc} section {top_section['section']})"


def main():
    base = Path(__file__).resolve().parent
    paths = [
        base.parent / 'data' / 'policy-documents' / 'policy_hr_leave.txt',
        base.parent / 'data' / 'policy-documents' / 'policy_it_acceptable_use.txt',
        base.parent / 'data' / 'policy-documents' / 'policy_finance_reimbursement.txt',
    ]

    documents = retrieve_documents(paths)
    print("UC-X document QA. Type a question, or 'exit' to quit.")

    while True:
        question = input("Question: ").strip()
        if not question or question.lower() in {"exit", "quit", "q"}:
            print("Goodbye.")
            break

        print(answer_question(documents, question))


if __name__ == "__main__":
    main()
