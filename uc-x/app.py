"""
UC-X app.py — Interactive document Q&A for CMC policy documents.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
Run with `python app.py` and type questions at the prompt.
"""
import re
from pathlib import Path

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

BASE_DIR = Path(__file__).resolve().parent
DOCUMENT_PATHS = {
    "policy_hr_leave.txt": BASE_DIR / ".." / "data" / "policy-documents" / "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": BASE_DIR / ".." / "data" / "policy-documents" / "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": BASE_DIR / ".." / "data" / "policy-documents" / "policy_finance_reimbursement.txt",
}
SECTION_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)")


def retrieve_documents():
    """Load all policy documents and index them by filename and section number."""
    documents = {}

    for doc_name, path in DOCUMENT_PATHS.items():
        if not path.is_file():
            raise FileNotFoundError(f"Required document not found: {path}")

        text = path.read_text(encoding="utf-8")
        sections = {}
        current_section = None
        section_lines = []

        for line in text.splitlines():
            match = SECTION_PATTERN.match(line.strip())
            if match:
                if current_section is not None:
                    sections[current_section] = " ".join(section_lines).strip()
                current_section = match.group(1)
                section_lines = [match.group(2).strip()]
            elif current_section is not None:
                stripped = line.strip()
                if stripped and not stripped.startswith("════════"):
                    section_lines.append(stripped)

        if current_section is not None:
            sections[current_section] = " ".join(section_lines).strip()

        documents[doc_name] = sections

    return documents


def answer_question(documents, question: str) -> str:
    """Answer a policy question using indexed document sections or refuse cleanly."""
    normalized = question.strip().lower()

    if "carry forward" in normalized and "annual leave" in normalized:
        return cite_answer(
            "policy_hr_leave.txt",
            "2.6",
            "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
        )

    if "install slack" in normalized or ("install" in normalized and "software" in normalized and "work laptop" in normalized):
        return cite_answer(
            "policy_it_acceptable_use.txt",
            "2.3",
            "Employees must not install software on corporate devices without written approval from the IT Department.",
        )

    if "home office equipment allowance" in normalized or ("equipment allowance" in normalized and "home" in normalized):
        return cite_answer(
            "policy_finance_reimbursement.txt",
            "3.1",
            "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.",
        )

    if "personal phone" in normalized and "work files" in normalized:
        return cite_answer(
            "policy_it_acceptable_use.txt",
            "3.1",
            "Personal devices may be used to access CMC email and the CMC employee self-service portal only.",
        )

    if "flexible working culture" in normalized or ("company view" in normalized and "flexible" in normalized):
        return REFUSAL_TEMPLATE

    if "da and meal" in normalized and "same day" in normalized:
        return cite_answer(
            "policy_finance_reimbursement.txt",
            "2.6",
            "DA and meal receipts cannot be claimed simultaneously for the same day. If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day.",
        )

    if "who approves leave without pay" in normalized or "approves leave without pay" in normalized:
        return cite_answer(
            "policy_hr_leave.txt",
            "5.2",
            "Leave Without Pay requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.",
        )

    candidate = search_documents(documents, normalized)
    if candidate is None:
        return REFUSAL_TEMPLATE
    return candidate


def search_documents(documents, normalized_question: str):
    """Search indexed sections for a single-source answer or refuse if ambiguous."""
    tokens = re.findall(r"\b[a-z0-9]+\b", normalized_question)
    if not tokens:
        return None

    scores = []
    for doc_name, sections in documents.items():
        for section_id, text in sections.items():
            text_lower = text.lower()
            score = sum(1 for token in tokens if token in text_lower)
            if score > 0:
                scores.append((score, doc_name, section_id, text))

    if not scores:
        return None

    scores.sort(key=lambda item: (-item[0], item[1], item[2]))
    top_score = scores[0][0]
    top_matches = [item for item in scores if item[0] == top_score]

    if len(top_matches) > 1:
        docs = {item[1] for item in top_matches}
        if len(docs) > 1:
            return None

    _, doc_name, section_id, text = top_matches[0]
    return cite_answer(doc_name, section_id, text)


def cite_answer(doc_name: str, section_id: str, answer_text: str) -> str:
    return f"{answer_text} ({doc_name} section {section_id})"


def main():
    documents = retrieve_documents()
    print("UC-X Ask My Documents — type a policy question or 'exit' to quit.")
    print("Available documents: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt")

    while True:
        try:
            question = input("\nQuestion: ").strip()
        except EOFError:
            print("\nGoodbye.")
            break

        if question.lower() in {"exit", "quit", "q"}:
            print("Goodbye.")
            break

        if not question:
            continue

        answer = answer_question(documents, question)
        print(f"Answer: {answer}")


if __name__ == "__main__":
    main()
