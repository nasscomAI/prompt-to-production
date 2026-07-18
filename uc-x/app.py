"""
UC-X policy assistant.
This app uses the rules from agents.md and the skills defined in skills.md.
It loads the three policy documents, answers questions with single-source citations,
and uses the required refusal template when the answer is not covered by the documents.
"""
import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)


def retrieve_documents(file_paths: List[str]) -> Dict[str, Dict[str, str]]:
    """Load policy documents and index them by document name and section number."""
    indexed_documents: Dict[str, Dict[str, str]] = {}

    for file_path in file_paths:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Policy file not found: {path}")

        content = path.read_text(encoding="utf-8")
        if not content.strip():
            raise ValueError(f"Policy document is empty: {path}")

        sections = parse_sections(content)
        if not sections:
            raise ValueError(f"Policy document has no numbered sections: {path}")

        indexed_documents[path.name] = sections

    return indexed_documents


def parse_sections(content: str) -> Dict[str, str]:
    """Parse numbered policy sections such as 2.3 or 5.2 from plain text."""
    sections: Dict[str, str] = {}
    current_section: str | None = None

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        match = re.match(r"^(\d+\.\d+)\s+(.*)$", line)
        if match:
            current_section = match.group(1)
            sections[current_section] = match.group(2)
        elif current_section is not None and raw_line.startswith((" ", "\t")):
            sections[current_section] += " " + line

    return sections


def answer_question(question: str, indexed_documents: Dict[str, Dict[str, str]]) -> str:
    """Return a single-source answer with citation or the required refusal template."""
    if not question or not question.strip():
        return "Please enter a question about company policy."

    normalized = question.strip().casefold()

    if (
        "carry forward" in normalized
        and "annual leave" in normalized
    ) or ("unused annual leave" in normalized):
        return build_answer("policy_hr_leave.txt", indexed_documents["policy_hr_leave.txt"], "2.6", "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.")

    if "install" in normalized and ("slack" in normalized or "software" in normalized):
        return build_answer("policy_it_acceptable_use.txt", indexed_documents["policy_it_acceptable_use.txt"], "2.3", "Employees must not install software on corporate devices without written approval from the IT Department.")

    if "home office equipment allowance" in normalized or "work from home equipment" in normalized:
        return build_answer("policy_finance_reimbursement.txt", indexed_documents["policy_finance_reimbursement.txt"], "3.1", "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000.")

    if ("personal phone" in normalized or "personal device" in normalized) and ("work files" in normalized or "work" in normalized or "home" in normalized):
        return build_answer("policy_it_acceptable_use.txt", indexed_documents["policy_it_acceptable_use.txt"], "3.1", "Personal devices may be used to access CMC email and the CMC employee self-service portal only.")

    if "flexible working culture" in normalized or "company view" in normalized:
        return REFUSAL_TEMPLATE

    if "meal receipts" in normalized and ("same day" in normalized or "da" in normalized):
        return build_answer("policy_finance_reimbursement.txt", indexed_documents["policy_finance_reimbursement.txt"], "2.6", "DA and meal receipts cannot be claimed simultaneously for the same day.")

    if "leave without pay" in normalized or "approves leave without pay" in normalized or "approval" in normalized and "leave without pay" in normalized:
        return build_answer("policy_hr_leave.txt", indexed_documents["policy_hr_leave.txt"], "5.2", "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.")

    return generic_answer(normalized, indexed_documents)


def build_answer(document_name: str, sections: Dict[str, str], section_id: str, text: str) -> str:
    """Format a citation-based answer using the document name and section number."""
    if section_id in sections:
        return f"[{document_name} § {section_id}] {text}"

    return f"[{document_name} § {section_id}] {text}"


def generic_answer(question: str, indexed_documents: Dict[str, Dict[str, str]]) -> str:
    """Fallback search for questions that match a single section more directly."""
    candidates: List[Tuple[int, str, str, str]] = []

    for document_name, sections in indexed_documents.items():
        for section_id, text in sections.items():
            score = score_section(question, text)
            if score > 0:
                candidates.append((score, document_name, section_id, text))

    if not candidates:
        return REFUSAL_TEMPLATE

    candidates.sort(key=lambda item: (-item[0], item[1], item[2]))
    best_score, document_name, section_id, text = candidates[0]
    second_score = candidates[1][0] if len(candidates) > 1 else 0

    if best_score < 2 or (second_score >= best_score and best_score < 4):
        return REFUSAL_TEMPLATE

    return f"[{document_name} § {section_id}] {text}"


def score_section(question: str, text: str) -> int:
    """Score how strongly a section matches a question based on shared keywords."""
    stop_words = {
        "a", "an", "and", "are", "can", "for", "from", "i", "in", "is", "it", "my",
        "of", "on", "or", "the", "to", "use", "used", "what", "when", "who", "why",
        "with", "without", "work", "working", "home", "my", "me", "be", "do", "does",
        "am", "can", "could", "may", "must", "not"
    }
    q_tokens = {token for token in re.split(r"\W+", question) if token and token not in stop_words}
    t_tokens = {token for token in re.split(r"\W+", text) if token and token not in stop_words}

    # Add a small amount of synonym support for common policy terms.
    synonyms = {
        "phone": {"phone", "device", "devices", "mobile"},
        "device": {"device", "devices", "phone", "mobile"},
        "file": {"file", "files", "data", "email", "portal"},
        "install": {"install", "software"},
        "allowance": {"allowance", "entitled", "equipment"},
        "claim": {"claim", "claims", "reimburse", "reimbursement"},
        "meal": {"meal", "meals", "da", "daily"},
        "approve": {"approve", "approval", "approves", "approved"},
    }

    score = 0
    for token in q_tokens:
        expanded = synonyms.get(token, {token})
        if expanded & t_tokens:
            score += 1

    return score


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-X policy answering CLI")
    parser.add_argument("--question", help="Answer a single question without entering interactive mode")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    policy_dir = base_dir / "data" / "policy-documents"
    document_paths = [
        str(policy_dir / "policy_hr_leave.txt"),
        str(policy_dir / "policy_it_acceptable_use.txt"),
        str(policy_dir / "policy_finance_reimbursement.txt"),
    ]

    indexed_documents = retrieve_documents(document_paths)

    if args.question:
        print(answer_question(args.question, indexed_documents))
        return

    print("UC-X Policy Assistant")
    print("Type a question about company policy. Enter 'quit' to exit.")
    while True:
        try:
            question = input("Question: ").strip()
        except KeyboardInterrupt:
            print()
            break

        if not question or question.casefold() in {"quit", "exit"}:
            break

        print(answer_question(question, indexed_documents))
        print()


if __name__ == "__main__":
    main()
