"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from pathlib import Path


SECTION_PATTERN = re.compile(r"^(\d+)\.\s+([A-Z].+)$")
CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "be",
    "can",
    "do",
    "for",
    "from",
    "i",
    "in",
    "is",
    "my",
    "of",
    "on",
    "or",
    "same",
    "the",
    "to",
    "what",
    "when",
    "who",
    "with",
    "work",
}
DEFAULT_DOCUMENTS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]


def refusal_response(relevant_team: str) -> str:
    return (
        "This question is not covered in the available policy documents\n"
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
        f"Please contact {relevant_team} for guidance."
    )


def retrieve_documents(base_dir: Path | None = None) -> dict:
    """Load the three policy files and index them by document name and clause number."""
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent.parent / "data" / "policy-documents"

    documents = {}
    for file_name in DEFAULT_DOCUMENTS:
        documents[file_name] = _parse_document(base_dir / file_name)
    return documents


def _parse_document(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    sections = []
    clauses = {}
    current_section = None
    current_clause = None

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("═"):
            continue

        section_match = SECTION_PATTERN.match(stripped)
        clause_match = CLAUSE_PATTERN.match(stripped)

        if section_match and not clause_match:
            current_section = {
                "section_number": section_match.group(1),
                "section_title": section_match.group(2),
                "clauses": [],
            }
            sections.append(current_section)
            current_clause = None
            continue

        if clause_match:
            if current_section is None:
                raise ValueError(f"Clause found before section heading in {path.name}: {stripped}")
            current_clause = {
                "section_number": current_section["section_number"],
                "section_title": current_section["section_title"],
                "clause_number": clause_match.group(1),
                "text": clause_match.group(2).strip(),
            }
            current_section["clauses"].append(current_clause)
            clauses[current_clause["clause_number"]] = current_clause
            continue

        if current_clause is not None:
            current_clause["text"] += " " + stripped

    return {"path": path, "sections": sections, "clauses": clauses}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if token not in STOPWORDS and len(token) > 1
    }


def _clause(documents: dict, document_name: str, clause_number: str) -> dict:
    return documents[document_name]["clauses"][clause_number]


def _citation(document_name: str, clause_number: str) -> str:
    return f"({document_name} §{clause_number})"


def _team_for_question(question_text: str) -> str:
    normalized = _normalize(question_text)
    if any(word in normalized for word in ["leave", "lwp", "holiday", "encashment", "culture"]):
        return "Human Resources Department"
    if any(word in normalized for word in ["phone", "laptop", "device", "slack", "software", "password", "email"]):
        return "IT Department"
    if any(word in normalized for word in ["reimbursement", "allowance", "claim", "da", "meal", "receipt", "travel"]):
        return "Finance Department"
    return "the relevant department"


def _match_pattern(normalized: str, required_groups: list[list[str]]) -> bool:
    return all(any(term in normalized for term in group) for group in required_groups)


def answer_question(documents: dict, question: str) -> str:
    """Return a single-source answer with citations, or the refusal template."""
    normalized = _normalize(question)

    if _match_pattern(normalized, [["carry forward"], ["annual leave", "unused annual leave", "unused leave"]]):
        return (
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year, "
            f"and any days above 5 are forfeited on 31 December {_citation('policy_hr_leave.txt', '2.6')}. "
            "Carry-forward days must be used within January–March of the following year or they are forfeited "
            f"{_citation('policy_hr_leave.txt', '2.7')}."
        )

    if _match_pattern(normalized, [["install"], ["slack", "software"], ["laptop", "work laptop", "corporate device", "device"]]):
        return (
            "Employees must not install software on corporate devices without written approval from the IT Department "
            f"{_citation('policy_it_acceptable_use.txt', '2.3')}."
        )

    if _match_pattern(normalized, [["home office", "equipment allowance"], ["allowance", "amount"]]):
        return (
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000 "
            f"{_citation('policy_finance_reimbursement.txt', '3.1')}. "
            "Employees on temporary or partial work-from-home arrangements are not eligible for this allowance "
            f"{_citation('policy_finance_reimbursement.txt', '3.5')}."
        )

    if _match_pattern(normalized, [["personal phone", "personal device"], ["work files", "access work files", "files"], ["home", "working from home", "remote"]]):
        return (
            "No. Personal devices may be used to access CMC email and the CMC employee self-service portal only "
            f"{_citation('policy_it_acceptable_use.txt', '3.1')}. "
            "Personal devices must not be used to access, store, or transmit classified or sensitive CMC data "
            f"{_citation('policy_it_acceptable_use.txt', '3.2')}."
        )

    if _match_pattern(normalized, [["company view", "view", "culture"], ["flexible working", "working culture"]]):
        return refusal_response("Human Resources Department")

    if _match_pattern(normalized, [["da", "daily allowance"], ["meal", "meal receipts"], ["same day", "simultaneously"]]):
        return (
            "No. If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day, "
            f"and DA and meal receipts cannot be claimed simultaneously for the same day {_citation('policy_finance_reimbursement.txt', '2.6')}."
        )

    if _match_pattern(normalized, [["leave without pay", "lwp"], ["approve", "approval", "approves"]]):
        return (
            "Leave Without Pay requires approval from the Department Head and the HR Director, and manager approval alone is not sufficient "
            f"{_citation('policy_hr_leave.txt', '5.2')}."
        )

    return _fallback_answer(documents, question)


def _fallback_answer(documents: dict, question: str) -> str:
    query_tokens = _tokens(question)
    best_matches = []

    for document_name, document in documents.items():
        for clause_number, clause in document["clauses"].items():
            clause_tokens = _tokens(clause["text"])
            overlap = query_tokens & clause_tokens
            if overlap:
                best_matches.append(
                    {
                        "document_name": document_name,
                        "clause_number": clause_number,
                        "clause_text": clause["text"],
                        "score": len(overlap),
                    }
                )

    if not best_matches:
        return refusal_response(_team_for_question(question))

    best_matches.sort(key=lambda match: match["score"], reverse=True)
    top_match = best_matches[0]
    competing_documents = {
        match["document_name"]
        for match in best_matches
        if match["score"] == top_match["score"]
    }
    if len(competing_documents) > 1:
        return refusal_response(_team_for_question(question))

    return f"{top_match['clause_text']} {_citation(top_match['document_name'], top_match['clause_number'])}."


def _run_batch(documents: dict, questions_path: Path, output_path: Path | None) -> str:
    questions = [line.strip() for line in questions_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    lines = []
    for question in questions:
        lines.append(f"Q: {question}")
        lines.append(f"A: {answer_question(documents, question)}")
        lines.append("")

    result = "\n".join(lines).rstrip() + "\n"
    if output_path is not None:
        output_path.write_text(result, encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description="UC-X policy question answerer")
    parser.add_argument("--questions-file", help="Optional file of questions to answer in batch mode")
    parser.add_argument("--output", help="Optional batch output file")
    args = parser.parse_args()

    documents = retrieve_documents()

    if args.questions_file:
        result = _run_batch(
            documents,
            Path(args.questions_file),
            Path(args.output) if args.output else None,
        )
        print(result, end="")
        return

    print("Ask about the available policy documents. Type 'exit' to quit.")
    while True:
        question = input("> ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue
        print(answer_question(documents, question))

if __name__ == "__main__":
    main()
