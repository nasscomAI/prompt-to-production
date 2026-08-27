"""
UC-X app.py
Single-source policy QA with explicit refusal behavior.
"""
import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

DOCUMENTS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

HEDGING_PHRASES = {
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
}

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "can",
    "for",
    "from",
    "i",
    "in",
    "is",
    "it",
    "my",
    "of",
    "on",
    "or",
    "the",
    "to",
    "we",
    "what",
    "when",
    "who",
    "with",
    "work",
}


def tokenize(text: str) -> List[str]:
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOPWORDS]


def split_sections(text: str) -> List[Tuple[str, str]]:
    lines = text.splitlines()
    sections: List[Tuple[str, str]] = []
    current_section = "intro"
    current_lines: List[str] = []
    pattern = re.compile(r"^\s*(\d+(?:\.\d+)*)[\).\-\s].*")

    for line in lines:
        m = pattern.match(line)
        if m:
            if current_lines:
                sections.append((current_section, "\n".join(current_lines).strip()))
            current_section = m.group(1)
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_section, "\n".join(current_lines).strip()))
    return sections


def retrieve_documents(base_dir: Path) -> Dict[str, List[Tuple[str, str]]]:
    index: Dict[str, List[Tuple[str, str]]] = {}
    for doc_name in DOCUMENTS:
        doc_path = base_dir / doc_name
        if not doc_path.exists():
            raise FileNotFoundError(f"Missing required document: {doc_name}")
        content = doc_path.read_text(encoding="utf-8")
        index[doc_name] = split_sections(content)
    return index


def _best_match_for_doc(
    question_tokens: set, sections: List[Tuple[str, str]]
) -> Tuple[int, str, str]:
    best_score = 0
    best_section = ""
    best_text = ""
    for section_number, section_text in sections:
        section_tokens = set(tokenize(section_text))
        score = len(question_tokens.intersection(section_tokens))
        if score > best_score:
            best_score = score
            best_section = section_number
            best_text = section_text
    return best_score, best_section, best_text


def answer_question(question: str, index: Dict[str, List[Tuple[str, str]]]) -> str:
    q = question.strip()
    if not q:
        return REFUSAL_TEMPLATE

    lowered = q.lower()
    if any(phrase in lowered for phrase in HEDGING_PHRASES):
        return REFUSAL_TEMPLATE

    question_tokens = set(tokenize(q))
    if not question_tokens:
        return REFUSAL_TEMPLATE

    doc_scores = []
    for doc_name, sections in index.items():
        score, section, section_text = _best_match_for_doc(question_tokens, sections)
        doc_scores.append((score, doc_name, section, section_text))

    doc_scores.sort(reverse=True, key=lambda x: x[0])
    top_score, top_doc, top_section, top_text = doc_scores[0]

    if top_score == 0:
        return REFUSAL_TEMPLATE

    if len(doc_scores) > 1 and top_score == doc_scores[1][0]:
        return REFUSAL_TEMPLATE

    snippet = " ".join(line.strip() for line in top_text.splitlines() if line.strip())
    if not top_section or not snippet:
        return REFUSAL_TEMPLATE

    return f"{snippet}\nsource: {top_doc}, section: {top_section}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ask questions about policy documents.")
    parser.add_argument(
        "--docs-dir",
        default="data/policy-documents",
        help="Directory containing policy documents",
    )
    return parser.parse_args()


def resolve_docs_dir(docs_dir_arg: str) -> Path:
    candidate_paths = [
        Path(docs_dir_arg),
        Path(__file__).resolve().parent.parent / "data" / "policy-documents",
    ]
    for candidate in candidate_paths:
        if candidate.exists():
            return candidate
    return Path(docs_dir_arg)


def main() -> None:
    args = parse_args()
    docs_dir = resolve_docs_dir(args.docs_dir)
    index = retrieve_documents(docs_dir)

    print("UC-X Policy QA ready. Type your question (or 'exit' to quit).")
    while True:
        question = input("> ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        print(answer_question(question, index))
        print()


if __name__ == "__main__":
    main()
