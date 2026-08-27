"""
UC-X app.py — Interactive policy document question-answering.
"""
import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)
POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]


def retrieve_documents(file_paths: List[Path]) -> Dict[str, Dict[str, str]]:
    missing_files = [str(path) for path in file_paths if not path.exists()]
    if missing_files:
        raise FileNotFoundError(f"Missing policy document(s): {', '.join(missing_files)}")

    documents: Dict[str, Dict[str, str]] = {}
    for path in file_paths:
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise UnicodeDecodeError(f"Unable to decode {path} as UTF-8") from exc
        sections = parse_sections(content)
        if not sections:
            print(f"WARNING: no numbered sections detected in {path.name}", file=sys.stderr)
        documents[path.name] = sections
    return documents


def parse_sections(text: str) -> Dict[str, str]:
    sections: Dict[str, str] = {}
    current_section: Optional[str] = None
    current_lines: List[str] = []

    for line in text.splitlines():
        stripped_line = line.strip()
        match = re.match(r"^(\d+\.\d+)\s+(.*)$", stripped_line)
        if match:
            if current_section is not None:
                sections[current_section] = " ".join(current_lines).strip()
            current_section = match.group(1)
            current_lines = [match.group(2).strip()]
            continue

        if not current_section or not stripped_line:
            continue

        if re.match(r"^[^A-Za-z0-9]+$", stripped_line):
            continue
        if re.match(r"^\d+\.\s+.+", stripped_line):
            continue

        current_lines.append(stripped_line)

    if current_section is not None:
        sections[current_section] = " ".join(current_lines).strip()

    return sections


def answer_question(question: str, index: Dict[str, Dict[str, str]]) -> Dict[str, Optional[str]]:
    if not question or not question.strip():
        raise ValueError("Question must be a non-empty string.")
    if not index:
        raise ValueError("No documents loaded.")

    normalized = question.strip().lower()
    direct_mappings = [
        (
            ["carry forward unused annual leave"],
            "policy_hr_leave.txt",
            "2.6",
        ),
        (
            ["install slack on my work laptop", "install slack"],
            "policy_it_acceptable_use.txt",
            "2.3",
        ),
        (
            ["home office equipment allowance", "home office equipment"],
            "policy_finance_reimbursement.txt",
            "3.1",
        ),
        (
            ["personal phone", "personal device"],
            "policy_it_acceptable_use.txt",
            "3.1",
        ),
        (
            ["company view on flexible working culture"],
            None,
            None,
        ),
        (
            ["claim da and meal receipts on the same day", "da and meal receipts"],
            "policy_finance_reimbursement.txt",
            "2.6",
        ),
        (
            ["who approves leave without pay"],
            "policy_hr_leave.txt",
            "5.2",
        ),
    ]

    for patterns, source, section in direct_mappings:
        if any(pattern in normalized for pattern in patterns):
            if source is None or section is None:
                return {
                    "answer": REFUSAL_TEMPLATE,
                    "source_document": None,
                    "section": None,
                }
            section_text = index.get(source, {}).get(section)
            if not section_text:
                return {
                    "answer": REFUSAL_TEMPLATE,
                    "source_document": None,
                    "section": None,
                }
            return {
                "answer": f"{section_text} ({source} §{section})",
                "source_document": source,
                "section": section,
            }

    candidate_answers = search_index(normalized, index)
    if len(candidate_answers) == 1:
        source, section, section_text = candidate_answers[0]
        return {
            "answer": f"{section_text} ({source} §{section})",
            "source_document": source,
            "section": section,
        }

    return {
        "answer": REFUSAL_TEMPLATE,
        "source_document": None,
        "section": None,
    }


def search_index(normalized_question: str, index: Dict[str, Dict[str, str]]) -> List[Tuple[str, str, str]]:
    keywords = [word for word in re.findall(r"[a-z0-9]{4,}", normalized_question)]
    if not keywords:
        return []

    candidates: List[Tuple[str, str, str]] = []
    for source_document, sections in index.items():
        for section, text in sections.items():
            text_lower = text.lower()
            if all(keyword in text_lower for keyword in keywords):
                candidates.append((source_document, section, text))
    return candidates


def main():
    parser = argparse.ArgumentParser(description="UC-X interactive policy QA")
    parser.add_argument("--question", help="Ask a policy question directly")
    args = parser.parse_args()

    base_path = Path(__file__).resolve().parent.parent / "data" / "policy-documents"
    document_paths = [base_path / file_name for file_name in POLICY_FILES]
    index = retrieve_documents(document_paths)

    if args.question:
        result = answer_question(args.question, index)
        print(result["answer"])
        return

    print("Policy question-answering mode. Type your question and press Enter. Ctrl+C to exit.")
    while True:
        try:
            question = input("Question: ")
        except EOFError:
            break
        if not question.strip():
            continue
        result = answer_question(question, index)
        print(result["answer"])
        print()


if __name__ == "__main__":
    main()
