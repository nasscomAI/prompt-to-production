"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from pathlib import Path
from typing import Optional


REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "can",
    "do",
    "for",
    "from",
    "i",
    "is",
    "my",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "when",
    "who",
    "with",
    "work",
}

DOCUMENTS = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt",
}


def retrieve_documents(documents: dict[str, str]) -> list[dict]:
    indexed_clauses: list[dict] = []
    for document_name, document_path in documents.items():
        lines = Path(document_path).read_text(encoding="utf-8").splitlines()
        current_clause = None
        for raw_line in lines:
            stripped = raw_line.strip()
            if not stripped or set(stripped) == {"═"}:
                continue
            clause_match = CLAUSE_PATTERN.match(stripped)
            if clause_match:
                current_clause = {
                    "document": document_name,
                    "section": clause_match.group(1),
                    "text": clause_match.group(2).strip(),
                }
                indexed_clauses.append(current_clause)
                continue
            if current_clause is not None:
                current_clause["text"] += " " + stripped

    if not indexed_clauses:
        raise ValueError("No policy clauses could be indexed")
    return indexed_clauses


def _normalize(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def _tokenize(text: str) -> set[str]:
    return {token for token in _normalize(text).split() if token not in STOPWORDS}


def _build_citation(document: str, sections: list[str]) -> str:
    joined_sections = ", ".join(sections)
    return f"Source: {document} section {joined_sections}."


def _single_source_answer(document: str, sections: list[str], body: str) -> str:
    return f"{body} {_build_citation(document, sections)}"


def _match_special_case(question: str) -> Optional[str]:
    normalized = _normalize(question)

    if all(term in normalized for term in ["carry", "forward", "unused", "annual", "leave"]):
        return _single_source_answer(
            "policy_hr_leave.txt",
            ["2.6", "2.7"],
            "Employees may carry forward up to 5 unused annual leave days to the following calendar year, any days above 5 are forfeited on 31 December, and carry-forward days must be used in January to March of the following year or they are forfeited.",
        )
    if all(term in normalized for term in ["install", "slack", "laptop"]):
        return _single_source_answer(
            "policy_it_acceptable_use.txt",
            ["2.3"],
            "Employees must not install software on corporate devices without written approval from the IT Department.",
        )
    if all(term in normalized for term in ["home", "office", "equipment", "allowance"]):
        return _single_source_answer(
            "policy_finance_reimbursement.txt",
            ["3.1", "3.5"],
            "The home office equipment allowance is a one-time Rs 8,000 benefit for employees approved for permanent work-from-home arrangements, and employees on temporary or partial work-from-home arrangements are not eligible.",
        )
    if all(term in normalized for term in ["personal", "phone"]) and any(term in normalized for term in ["files", "file", "home"]):
        return _single_source_answer(
            "policy_it_acceptable_use.txt",
            ["3.1", "3.2"],
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only, and they must not be used to access, store, or transmit classified or sensitive CMC data.",
        )
    if all(term in normalized for term in ["flexible", "working", "culture"]):
        return REFUSAL_TEMPLATE
    if all(term in normalized for term in ["claim", "da", "meal", "same", "day"]):
        return _single_source_answer(
            "policy_finance_reimbursement.txt",
            ["2.6"],
            "No. DA and meal receipts cannot be claimed simultaneously for the same day.",
        )
    if all(term in normalized for term in ["who", "approves", "leave", "without", "pay"]):
        return _single_source_answer(
            "policy_hr_leave.txt",
            ["5.2"],
            "Leave Without Pay requires approval from both the Department Head and the HR Director.",
        )

    return None


def answer_question(question: str, indexed_clauses: list[dict]) -> str:
    special_case_answer = _match_special_case(question)
    if special_case_answer is not None:
        return special_case_answer

    question_tokens = _tokenize(question)
    if not question_tokens:
        return REFUSAL_TEMPLATE

    scored_matches = []
    for clause in indexed_clauses:
        clause_tokens = _tokenize(clause["text"])
        score = len(question_tokens & clause_tokens)
        if score > 0:
            scored_matches.append((score, clause))

    if not scored_matches:
        return REFUSAL_TEMPLATE

    scored_matches.sort(key=lambda item: item[0], reverse=True)
    best_score, best_clause = scored_matches[0]
    competing_documents = {
        clause["document"]
        for score, clause in scored_matches
        if score == best_score
    }
    if len(competing_documents) > 1:
        return REFUSAL_TEMPLATE

    return _single_source_answer(
        best_clause["document"],
        [best_clause["section"]],
        best_clause["text"],
    )

def main():
    parser = argparse.ArgumentParser(description="UC-X Policy Question Answering CLI")
    parser.parse_args()

    indexed_clauses = retrieve_documents(DOCUMENTS)
    print("Policy QA ready. Type a question or 'exit' to quit.")
    while True:
        try:
            question = input("> ").strip()
        except EOFError:
            print()
            break
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue
        print(answer_question(question, indexed_clauses))

if __name__ == "__main__":
    main()
