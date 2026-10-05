"""UC-X single-source policy question-answering CLI."""

import argparse
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


CLAUSE_PATTERN = re.compile(r"^(?P<section>\d+\.\d+)\s+(?P<text>.+?)\s*$")
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)
DEFAULT_DOCUMENTS = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)
STOP_WORDS = {
    "a", "an", "and", "are", "can", "company", "do", "for", "from", "i", "in",
    "is", "it", "me", "my", "of", "on", "the", "to", "use", "what", "when", "with",
    "work", "working", "yes", "you",
}


def _read_clauses(path: Path) -> Dict[str, str]:
    """Read one policy file into complete numbered clauses."""
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as error:
        raise OSError(f"Unable to read policy document '{path}': {error}") from error
    if not text.strip():
        raise ValueError(f"Policy document '{path.name}' is empty.")

    clauses: Dict[str, str] = {}
    current_reference: Optional[str] = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        # The policy files contain decorative divider lines. Ignore any line
        # without ordinary letters or digits, regardless of terminal encoding.
        if not line or not re.search(r"[A-Za-z0-9]", line):
            continue
        match = CLAUSE_PATTERN.match(line)
        if match:
            current_reference = match.group("section")
            if current_reference in clauses:
                raise ValueError(f"Duplicate section {current_reference} in {path.name}.")
            clauses[current_reference] = match.group("text")
        elif current_reference:
            clauses[current_reference] = f"{clauses[current_reference]} {line}"

    if not clauses:
        raise ValueError(f"No numbered clauses found in '{path.name}'.")
    return {reference: " ".join(clause.split()) for reference, clause in clauses.items()}


def retrieve_documents(document_paths: Iterable[str]) -> Dict[str, Dict[str, str]]:
    """Load approved documents, keeping every clause within its document boundary."""
    documents: Dict[str, Dict[str, str]] = {}
    for raw_path in document_paths:
        path = Path(raw_path)
        if path.name not in DEFAULT_DOCUMENTS:
            raise ValueError(f"Unapproved policy document: {path.name}.")
        documents[path.name] = _read_clauses(path)
    if set(documents) != set(DEFAULT_DOCUMENTS):
        raise ValueError("All three approved policy documents are required.")
    return documents


def _citation(document_name: str, section: str) -> str:
    return f"Source: {document_name}, section {section}."


def _answer_from_clause(
    documents: Dict[str, Dict[str, str]], document_name: str, section: str
) -> str:
    clause = documents[document_name].get(section)
    if not clause:
        return REFUSAL_TEMPLATE
    return f"{clause}\n{_citation(document_name, section)}"


def _targeted_match(question: str) -> Optional[Tuple[str, str]]:
    """Recognize policy topics that have one unambiguous source clause."""
    words = set(re.findall(r"[a-z]+", question.lower()))
    if {"carry", "forward"} <= words and ("leave" in words or "annual" in words):
        return "policy_hr_leave.txt", "2.6"
    if "install" in words and ({"slack", "software"} & words):
        return "policy_it_acceptable_use.txt", "2.3"
    if {"home", "office", "equipment", "allowance"} <= words:
        return "policy_finance_reimbursement.txt", "3.1"
    if {"personal", "phone"} <= words or ({"personal", "device"} <= words):
        # Do not incorporate HR remote-work language: IT 3.1 alone limits the
        # allowed personal-device access to email and the self-service portal.
        return "policy_it_acceptable_use.txt", "3.1"
    if "da" in words and ("meal" in words or "receipts" in words):
        return "policy_finance_reimbursement.txt", "2.6"
    if "lwp" in words or ({"leave", "without", "pay"} <= words):
        return "policy_hr_leave.txt", "5.2"
    return None


def _single_source_search(
    question: str, documents: Dict[str, Dict[str, str]]
) -> Optional[Tuple[str, str]]:
    """Find a clearly dominant clause without mixing document claims."""
    query_words = {
        word for word in re.findall(r"[a-z0-9]+", question.lower()) if word not in STOP_WORDS
    }
    if len(query_words) < 2:
        return None

    candidates: List[Tuple[int, str, str]] = []
    for document_name, clauses in documents.items():
        for section, text in clauses.items():
            clause_words = set(re.findall(r"[a-z0-9]+", text.lower()))
            score = len(query_words & clause_words)
            if score:
                candidates.append((score, document_name, section))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    best_score, document_name, section = candidates[0]
    tied_best = [candidate for candidate in candidates if candidate[0] == best_score]
    # Require a strong, unique lexical match. Ambiguous searches refuse instead
    # of selecting a second document or inventing a combined answer.
    if best_score < 2 or len(tied_best) != 1:
        return None
    return document_name, section


def answer_question(question: str, documents: Dict[str, Dict[str, str]]) -> str:
    """Return one cited, source-supported answer or the exact refusal template."""
    if not question or not question.strip():
        return REFUSAL_TEMPLATE
    selected = _targeted_match(question) or _single_source_search(question, documents)
    if not selected:
        return REFUSAL_TEMPLATE
    return _answer_from_clause(documents, *selected)


def _default_document_paths() -> List[str]:
    data_directory = Path(__file__).resolve().parent.parent / "data" / "policy-documents"
    return [str(data_directory / name) for name in DEFAULT_DOCUMENTS]


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument(
        "--documents-dir",
        help="Directory containing the three approved policy .txt files",
    )
    parser.add_argument("--question", help="Answer one question without starting the interactive CLI")
    args = parser.parse_args()

    if args.documents_dir:
        document_paths = [str(Path(args.documents_dir) / name) for name in DEFAULT_DOCUMENTS]
    else:
        document_paths = _default_document_paths()
    documents = retrieve_documents(document_paths)

    if args.question:
        print(answer_question(args.question, documents))
        return

    print("Ask a question about the available policy documents. Type 'exit' to quit.")
    while True:
        try:
            question = input("\nquestion> ").strip()
        except EOFError:
            print()
            break
        if question.lower() in {"exit", "quit"}:
            break
        print(answer_question(question, documents))


if __name__ == "__main__":
    main()
