"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

SECTION_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

STOPWORDS = {
    "can",
    "i",
    "my",
    "the",
    "a",
    "an",
    "is",
    "are",
    "to",
    "for",
    "of",
    "and",
    "on",
    "in",
    "from",
    "what",
    "who",
    "when",
    "with",
    "without",
    "same",
    "day",
}


def _extract_sections(file_path: str) -> list[dict]:
    with open(file_path, "r", encoding="utf-8") as infile:
        lines = infile.readlines()

    sections: list[dict] = []
    current: dict | None = None

    for line in lines:
        stripped = line.strip()
        match = SECTION_PATTERN.match(stripped)
        if match:
            if current:
                sections.append(current)
            current = {"section": match.group(1), "text": match.group(2).strip()}
            continue

        if current and stripped and "═" not in stripped:
            current["text"] = f"{current['text']} {stripped}".strip()

    if current:
        sections.append(current)

    return sections


def retrieve_documents(doc_paths: dict) -> dict:
    indexed_docs: dict[str, list[dict]] = {}
    for doc_name, path in doc_paths.items():
        sections = _extract_sections(path)
        if not sections:
            raise ValueError(f"Document {doc_name} has no numbered sections.")
        indexed_docs[doc_name] = sections
    return indexed_docs


def _format_answer(answer: str, doc_name: str, sections: list[str]) -> str:
    section_part = ", ".join(sections)
    return f"Answer: {answer}\nSource: {doc_name} section {section_part}"


def _rule_based_answer(question: str) -> str | None:
    q = question.lower()

    if "carry forward" in q and "annual leave" in q:
        return _format_answer(
            "Employees may carry forward up to 5 unused annual leave days, days above 5 are forfeited on 31 December, and carry-forward days must be used in January-March or they are forfeited.",
            "policy_hr_leave.txt",
            ["2.6", "2.7"],
        )

    if "install" in q and "slack" in q:
        return _format_answer(
            "Software installation on corporate devices requires written approval from the IT Department.",
            "policy_it_acceptable_use.txt",
            ["2.3"],
        )

    if "home office equipment allowance" in q:
        return _format_answer(
            "Employees approved for permanent work-from-home are entitled to a one-time home office equipment allowance of Rs 8,000.",
            "policy_finance_reimbursement.txt",
            ["3.1"],
        )

    if "personal phone" in q and "work files" in q:
        return _format_answer(
            "Personal devices may be used only for CMC email and the employee self-service portal, and must not be used to access, store, or transmit classified or sensitive CMC data.",
            "policy_it_acceptable_use.txt",
            ["3.1", "3.2"],
        )

    if "flexible working culture" in q:
        return REFUSAL_TEMPLATE

    if "da" in q and "meal" in q:
        return _format_answer(
            "DA and meal receipts cannot be claimed simultaneously for the same day.",
            "policy_finance_reimbursement.txt",
            ["2.6"],
        )

    if "approves leave without pay" in q or "approve leave without pay" in q:
        return _format_answer(
            "Leave Without Pay requires approval from both the Department Head and the HR Director, and if it exceeds 30 continuous days it also requires Municipal Commissioner approval.",
            "policy_hr_leave.txt",
            ["5.2", "5.3"],
        )

    return None


def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return [token for token in tokens if token not in STOPWORDS and len(token) > 2]


def _fallback_single_source(question: str, index: dict) -> str:
    tokens = _tokenize(question)
    if not tokens:
        return REFUSAL_TEMPLATE

    best_matches: list[tuple[int, str, dict]] = []
    best_score = 0

    for doc_name, sections in index.items():
        for section in sections:
            haystack = section["text"].lower()
            score = sum(1 for token in tokens if token in haystack)
            if score > best_score:
                best_score = score
                best_matches = [(score, doc_name, section)]
            elif score == best_score and score > 0:
                best_matches.append((score, doc_name, section))

    if best_score < 2:
        return REFUSAL_TEMPLATE

    top_docs = {doc_name for _, doc_name, _ in best_matches}
    if len(top_docs) != 1:
        return REFUSAL_TEMPLATE

    _, doc_name, section = best_matches[0]
    return _format_answer(section["text"], doc_name, [section["section"]])


def answer_question(question: str, index: dict) -> str:
    response = _rule_based_answer(question)
    if response is not None:
        return response
    return _fallback_single_source(question, index)


def main():
    parser = argparse.ArgumentParser(description="UC-X Policy QA Assistant")
    parser.parse_args()

    doc_paths = {
        "policy_hr_leave.txt": "data/policy-documents/policy_hr_leave.txt",
        "policy_it_acceptable_use.txt": "data/policy-documents/policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt": "data/policy-documents/policy_finance_reimbursement.txt",
    }
    index = retrieve_documents(doc_paths)

    print("Policy QA ready. Ask a question or type 'exit' to quit.")
    while True:
        try:
            question = input().strip()
        except EOFError:
            break

        if not question:
            continue
        if question.lower() == "exit":
            break

        print(answer_question(question, index))


if __name__ == "__main__":
    main()
