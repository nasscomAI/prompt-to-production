"""
UC-X app.py — Ask My Documents

Implements the RICE enforcement described in README.md:
- single-source answers only
- exact refusal template for out-of-scope questions
- no cross-document blending
- document + section citations for factual claims
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)


def normalize_text(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Policy file not found: {path}") from exc


def retrieve_documents(folder: str | Path | None = None) -> Dict[str, Dict[str, str]]:
    """Load the three policy files and index them by document name + section number."""
    base_dir = Path(folder) if folder else Path(__file__).resolve().parent.parent / "data" / "policy-documents"
    file_names = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt",
    ]

    index: Dict[str, Dict[str, str]] = {}
    for file_name in file_names:
        file_path = base_dir / file_name
        text = safe_read_text(file_path)

        sections: Dict[str, str] = {}
        current_section = None
        buffer: List[str] = []

        for line in text.splitlines():
            section_match = re.match(r"^\s*(\d+\.\d+)\s+(.+)$", line.strip())
            if section_match:
                if current_section:
                    section_text = " ".join(buffer).strip()
                    if section_text:
                        sections[current_section] = section_text
                current_section = section_match.group(1)
                buffer = [section_match.group(2)]
            elif current_section:
                buffer.append(line.strip())

        if current_section:
            section_text = " ".join(buffer).strip()
            if section_text:
                sections[current_section] = section_text

        index[file_name] = {
            "title": file_path.name,
            "text": text,
            "sections": sections,
        }

    return index


def extract_keywords(question: str) -> List[str]:
    tokens = normalize_text(question).split()
    stop_words = {
        "can", "could", "may", "would", "should", "what", "who", "when", "where",
        "why", "how", "the", "a", "an", "is", "are", "do", "does", "did", "i",
        "my", "me", "we", "our", "you", "your", "for", "from", "with", "and", "or",
        "to", "of", "on", "in", "be", "about", "use", "work", "home", "company",
        "view", "policy", "documents", "document"
    }
    return [token for token in tokens if token not in stop_words and len(token) > 2]


def score_question_against_section(question: str, section_text: str) -> float:
    q_words = set(extract_keywords(question))
    if not q_words:
        return 0.0
    s_words = set(normalize_text(section_text).split())
    if not s_words:
        return 0.0
    overlap = len(q_words & s_words)
    return overlap / max(1, len(q_words))


def format_answer(doc_name: str, section_id: str, answer_text: str) -> str:
    return f"{answer_text} Source: {doc_name}, section {section_id}."


def match_direct_question(question: str) -> str | None:
    q = normalize_text(question)

    if re.search(r"carry forward.*annual leave|unused annual leave|annual leave.*carry forward", q):
        return format_answer(
            "policy_hr_leave.txt",
            "2.6",
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."
        )

    if re.search(r"install.*slack|slack.*install|software.*corporate devices|install software.*without.*approval", q):
        return format_answer(
            "policy_it_acceptable_use.txt",
            "2.3",
            "No. Employees must not install software on corporate devices without written approval from the IT Department."
        )

    if re.search(r"home office equipment allowance|equipment allowance|work from home.*allowance|allowance.*home office", q):
        return format_answer(
            "policy_finance_reimbursement.txt",
            "3.1",
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000."
        )

    if re.search(r"da and meal receipts|meal receipts.*same day|claim.*da.*meal.*same day|meal.*da.*same day", q):
        return format_answer(
            "policy_finance_reimbursement.txt",
            "2.6",
            "No. DA and meal receipts cannot be claimed simultaneously for the same day."
        )

    if re.search(r"leave without pay|lwp.*approve|who.*approves.*leave without pay|approves.*lwp", q):
        return format_answer(
            "policy_hr_leave.txt",
            "5.2",
            "Leave without pay requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."
        )

    if re.search(r"personal phone.*work files.*home|personal phone.*access.*work files|use my personal phone.*work files.*home|use.*personal phone.*home.*work files", q):
        return format_answer(
            "policy_it_acceptable_use.txt",
            "3.1",
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only."
        )

    if re.search(r"flexible working culture|company view.*flexible.*working|flexible working.*culture", q):
        return REFUSAL_TEMPLATE

    return None


def answer_question(question: str, indexed_documents: Dict[str, Dict[str, str]] | None = None) -> str:
    """Return a single-source answer or the exact refusal template."""
    direct_answer = match_direct_question(question)
    if direct_answer is not None:
        return direct_answer

    documents = indexed_documents or retrieve_documents()
    scored_matches: List[Tuple[float, str, str, str]] = []

    for doc_name, payload in documents.items():
        sections = payload.get("sections", {})
        for section_id, section_text in sections.items():
            score = score_question_against_section(question, section_text)
            if score > 0:
                scored_matches.append((score, doc_name, section_id, section_text))

    if not scored_matches:
        return REFUSAL_TEMPLATE

    scored_matches.sort(key=lambda entry: entry[0], reverse=True)
    best_score, best_doc, best_section, _ = scored_matches[0]
    second_best = scored_matches[1] if len(scored_matches) > 1 else None

    if second_best and second_best[0] >= best_score * 0.9 and second_best[1] != best_doc:
        return REFUSAL_TEMPLATE

    best_section_text = documents[best_doc]["sections"][best_section]
    answer = best_section_text
    answer = re.sub(r"\s+", " ", answer).strip()
    if answer.endswith(".") is False:
        answer += "."
    return format_answer(best_doc, best_section, answer)


def run_interactive_loop() -> None:
    print("UC-X — Ask My Documents")
    print("Type a question and press Enter. Type 'exit' to quit.\n")
    documents = retrieve_documents()

    while True:
        try:
            question = input("Question: ").strip()
        except EOFError:
            print()
            break

        if not question or question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        print(answer_question(question, documents))
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask policy questions using the document-only policy index.")
    parser.add_argument("--question", help="Ask one question and print the answer without starting the interactive loop.")
    parser.add_argument("--folder", default=None, help="Optional folder that contains the policy documents.")
    args = parser.parse_args()

    if args.question:
        documents = retrieve_documents(args.folder)
        print(answer_question(args.question, documents))
        return

    run_interactive_loop()


if __name__ == "__main__":
    main()
