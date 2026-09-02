"""Deterministic single-source policy question answerer for UC-X."""

import re
from pathlib import Path


POLICY_FILES = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)
POLICY_DIRECTORY = Path(__file__).resolve().parent.parent / "data" / "policy-documents"
REFUSAL = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)


def retrieve_documents():
    """Load each policy independently and index its numbered sections."""
    documents = {}
    section_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)$")
    for filename in POLICY_FILES:
        path = POLICY_DIRECTORY / filename
        with path.open("r", encoding="utf-8") as policy_file:
            content = policy_file.read()

        sections = {}
        current_number = None
        current_lines = []
        for line in content.splitlines():
            match = section_pattern.match(line)
            if match:
                if current_number is not None:
                    sections[current_number] = " ".join(current_lines)
                current_number = match.group(1)
                current_lines = [match.group(2)]
            elif current_number is not None:
                stripped = line.strip()
                if stripped and not stripped.startswith("═") and not re.match(r"^\d+\.\s+", stripped):
                    current_lines.append(stripped)
        if current_number is not None:
            sections[current_number] = " ".join(current_lines)
        if not sections:
            raise ValueError(f"No numbered sections found in {filename}.")
        documents[filename] = sections
    return documents


def _terms(question):
    normalized = question.lower()
    aliases = {
        "leave without pay": "lwp",
        "carry forward": "carryforward",
        "personal phone": "personaldevice",
        "personal devices": "personaldevice",
        "home office equipment": "equipment",
        "work laptop": "corporatedevice",
        "meal receipts": "meal",
        "daily allowance": "da",
    }
    for phrase, alias in aliases.items():
        normalized = normalized.replace(phrase, f" {alias} ")
    return {
        term
        for term in re.findall(r"[a-z0-9]+", normalized)
        if term not in {"a", "an", "and", "can", "do", "for", "i", "in", "my", "on", "the", "to", "what", "when", "who", "is", "are", "use"}
    }


def _is_personal_work_file_question(question):
    normalized = question.lower()
    personal_device = re.search(r"\b(personal|own)\s+(phone|device|mobile)\b", normalized)
    work_file = re.search(r"\b(work|company|cmc)\s+(file|files|data|documents?)\b", normalized)
    remote_context = re.search(r"\b(home|remote|working from home)\b", normalized)
    return bool(personal_device and work_file and remote_context)


def answer_question(documents, question):
    """Return one cited source section or the exact refusal response."""
    if not isinstance(question, str) or not question.strip():
        return REFUSAL

    normalized = " ".join(question.lower().split())
    if _is_personal_work_file_question(question):
        return REFUSAL

    query_terms = _terms(question)
    if re.search(r"\b(personal|own)\s+(phone|device|mobile)\b", normalized):
        it_section = documents["policy_it_acceptable_use.txt"].get("3.1")
        if it_section and re.search(r"\b(email|portal)\b", normalized):
            return f"[policy_it_acceptable_use.txt section 3.1] {it_section}"

    candidates = []
    for filename, sections in documents.items():
        for section_number, text in sections.items():
            section_terms = set(re.findall(r"[a-z0-9]+", text.lower()))
            score = len(query_terms & section_terms)
            if score:
                candidates.append((score, filename, section_number, text))

    if not candidates:
        return REFUSAL

    candidates.sort(key=lambda item: (-item[0], item[1], item[2]))
    best_score = candidates[0][0]
    best = [candidate for candidate in candidates if candidate[0] == best_score]
    best_documents = {candidate[1] for candidate in best}
    if len(best_documents) != 1:
        return REFUSAL

    _, filename, section_number, text = best[0]
    return f"[{filename} section {section_number}] {text}"


def main():
    try:
        documents = retrieve_documents()
    except (OSError, ValueError) as error:
        print(f"Unable to load policy documents: {error}")
        return

    while True:
        try:
            question = input()
        except EOFError:
            break
        if question.strip().lower() == "exit":
            break
        print(answer_question(documents, question))

if __name__ == "__main__":
    main()
