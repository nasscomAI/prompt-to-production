"""UC-X — single-source, citation-first policy document assistant."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence


POLICY_FILENAMES = (
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
)

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""


@dataclass(frozen=True)
class Clause:
    document: str
    section: str
    text: str


DocumentIndex = Mapping[str, Mapping[str, Clause]]


# Each supported intent resolves to sections in exactly one document.
INTENT_ROUTES: tuple[tuple[tuple[str, ...], str, tuple[str, ...]], ...] = (
    (("carry forward", "annual leave"), "policy_hr_leave.txt", ("2.6", "2.7")),
    (("carry-forward", "annual leave"), "policy_hr_leave.txt", ("2.6", "2.7")),
    (("unused", "annual leave"), "policy_hr_leave.txt", ("2.6", "2.7")),
    (("install", "slack"), "policy_it_acceptable_use.txt", ("2.3", "2.4")),
    (("install", "software"), "policy_it_acceptable_use.txt", ("2.3", "2.4")),
    (("home office", "allowance"), "policy_finance_reimbursement.txt", ("3.1", "3.4", "3.5")),
    (("equipment", "allowance"), "policy_finance_reimbursement.txt", ("3.1", "3.2", "3.3", "3.4", "3.5")),
    (("personal phone", "work files"), "policy_it_acceptable_use.txt", ("3.1", "3.2")),
    (("personal phone", "work file"), "policy_it_acceptable_use.txt", ("3.1", "3.2")),
    (("personal device", "work files"), "policy_it_acceptable_use.txt", ("3.1", "3.2")),
    (("personal device", "work file"), "policy_it_acceptable_use.txt", ("3.1", "3.2")),
    (("da", "meal"), "policy_finance_reimbursement.txt", ("2.5", "2.6")),
    (("daily allowance", "meal"), "policy_finance_reimbursement.txt", ("2.5", "2.6")),
    (("approves", "leave without pay"), "policy_hr_leave.txt", ("5.1", "5.2", "5.3")),
    (("approve", "leave without pay"), "policy_hr_leave.txt", ("5.1", "5.2", "5.3")),
    (("approval", "leave without pay"), "policy_hr_leave.txt", ("5.1", "5.2", "5.3")),
    (("approves", "lwp"), "policy_hr_leave.txt", ("5.1", "5.2", "5.3")),
)


def _parse_clauses(document: str, content: str) -> dict[str, Clause]:
    """Parse numbered clauses while preserving wrapped lines and punctuation."""

    matches = list(re.finditer(r"(?m)^(\d+\.\d+)\s+", content))
    if not matches:
        raise ValueError(f"{document}: no numbered policy clauses found")

    clauses: dict[str, Clause] = {}
    for position, match in enumerate(matches):
        section = match.group(1)
        end = matches[position + 1].start() if position + 1 < len(matches) else len(content)
        raw_text = content[match.end() : end]
        raw_text = re.split(r"\n[═]{3,}", raw_text, maxsplit=1)[0]
        text = " ".join(raw_text.split())
        if not text:
            raise ValueError(f"{document} section {section}: empty clause")
        if section in clauses:
            raise ValueError(f"{document}: duplicate section {section}")
        clauses[section] = Clause(document=document, section=section, text=text)
    return clauses


def retrieve_documents(policy_directory: Path) -> dict[str, dict[str, Clause]]:
    """Load and validate exactly the three policy files approved for UC-X."""

    index: dict[str, dict[str, Clause]] = {}
    for filename in POLICY_FILENAMES:
        path = policy_directory / filename
        if not path.is_file():
            raise FileNotFoundError(f"Required policy document not found: {path}")
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise ValueError(f"Could not read {path} as UTF-8: {exc}") from exc
        index[filename] = _parse_clauses(filename, content)
    return index


def _resolve_route(question: str) -> tuple[str, tuple[str, ...]] | None:
    normalized = " ".join(question.casefold().split())
    matches = [
        (document, sections)
        for required_terms, document, sections in INTENT_ROUTES
        if all(term in normalized for term in required_terms)
    ]
    documents = {document for document, _ in matches}
    if len(documents) != 1:
        return None

    document = next(iter(documents))
    sections = tuple(
        sorted(
            {section for _, route_sections in matches for section in route_sections},
            key=lambda value: tuple(int(part) for part in value.split(".")),
        )
    )
    return document, sections


def answer_question(question: str, index: DocumentIndex) -> str:
    """Return complete clauses from one document, or the exact refusal."""

    if not question.strip():
        return REFUSAL_TEMPLATE

    route = _resolve_route(question)
    if route is None:
        return REFUSAL_TEMPLATE

    document, sections = route
    document_clauses = index.get(document)
    if document_clauses is None:
        return REFUSAL_TEMPLATE

    selected: list[Clause] = []
    for section in sections:
        clause = document_clauses.get(section)
        if clause is None:
            return REFUSAL_TEMPLATE
        selected.append(clause)

    return "\n".join(
        f"[{clause.document} section {clause.section}] {clause.text}"
        for clause in selected
    )


def run_cli(index: DocumentIndex) -> None:
    print("CMC Policy Assistant — type a question, or 'quit' to exit.")
    while True:
        try:
            question = input("\nQuestion: ").strip()
        except EOFError:
            print()
            return
        if question.casefold() in {"quit", "exit"}:
            return
        print(answer_question(question, index))


def main(argv: Sequence[str] | None = None) -> int:
    del argv  # Reserved for a future non-interactive interface.
    policy_directory = Path(__file__).resolve().parent.parent / "data" / "policy-documents"
    try:
        index = retrieve_documents(policy_directory)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1
    run_cli(index)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
