"""UC-0B — faithful, clause-by-clause policy summariser."""

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


CLAUSE_START = re.compile(r"^(?P<reference>\d+\.\d+)\s+(?P<text>.+)$")
SECTION_HEADING = re.compile(r"^(?P<number>\d+)\.\s+(?P<title>.+)$")
DIVIDER = re.compile(r"^[═=\-]+$")


@dataclass(frozen=True)
class PolicyClause:
    reference: str
    text: str
    section_number: str
    section_title: str


@dataclass(frozen=True)
class PolicyDocument:
    metadata: tuple[str, ...]
    clauses: tuple[PolicyClause, ...]


def _normalise(parts: list[str]) -> str:
    """Join wrapped source lines without rewriting their wording."""
    return " ".join(part.strip() for part in parts if part.strip())


def retrieve_policy(input_path: str | Path) -> PolicyDocument:
    """Load a UTF-8 text policy as ordered, structured numbered clauses."""
    path = Path(input_path)
    if path.suffix.lower() != ".txt":
        raise ValueError("Input policy must be a .txt file")

    lines = path.read_text(encoding="utf-8-sig").splitlines()
    metadata: list[str] = []
    clauses: list[PolicyClause] = []
    seen_references: set[str] = set()
    section_number = ""
    section_title = ""
    current_reference: str | None = None
    current_text: list[str] = []

    def finish_clause() -> None:
        nonlocal current_reference, current_text
        if current_reference is None:
            return
        text = _normalise(current_text)
        if not text:
            raise ValueError(f"Clause {current_reference} has no text")
        clauses.append(
            PolicyClause(
                reference=current_reference,
                text=text,
                section_number=section_number,
                section_title=section_title,
            )
        )
        current_reference = None
        current_text = []

    for raw_line in lines:
        line = raw_line.strip()
        if not line or DIVIDER.fullmatch(line):
            continue

        clause_match = CLAUSE_START.match(line)
        if clause_match:
            finish_clause()
            reference = clause_match.group("reference")
            if reference in seen_references:
                raise ValueError(f"Duplicate clause reference: {reference}")
            if not section_number or reference.split(".", 1)[0] != section_number:
                raise ValueError(f"Clause {reference} has no matching section heading")
            seen_references.add(reference)
            current_reference = reference
            current_text = [clause_match.group("text")]
            continue

        heading_match = SECTION_HEADING.match(line)
        if heading_match:
            finish_clause()
            section_number = heading_match.group("number")
            section_title = heading_match.group("title")
            continue

        if current_reference is not None:
            current_text.append(line)
        elif not section_number:
            metadata.append(line)
        else:
            raise ValueError(
                f"Unnumbered text inside section {section_number} cannot be assigned safely: {line}"
            )

    finish_clause()
    if not clauses:
        raise ValueError("Policy contains no numbered clauses")

    return PolicyDocument(metadata=tuple(metadata), clauses=tuple(clauses))


def summarize_policy(policy: PolicyDocument) -> str:
    """Render a lossless extractive summary and verify clause coverage."""
    output: list[str] = []
    if policy.metadata:
        output.extend(policy.metadata)
        output.append("")
    output.append("CLAUSE-BY-CLAUSE SUMMARY")
    output.append("")

    rendered_references: list[str] = []
    previous_section: str | None = None
    for clause in policy.clauses:
        if clause.section_number != previous_section:
            if previous_section is not None:
                output.append("")
            output.append(f"{clause.section_number}. {clause.section_title}")
            previous_section = clause.section_number
        output.append(
            f"{clause.reference} [VERBATIM — meaning-sensitive] {clause.text}"
        )
        rendered_references.append(clause.reference)

    source_references = [clause.reference for clause in policy.clauses]
    if rendered_references != source_references:
        raise ValueError("Summary validation failed: clause coverage or order changed")

    return "\n".join(output) + "\n"


def write_summary(input_path: str | Path, output_path: str | Path) -> None:
    """Retrieve, summarise and write the policy using UTF-8 text."""
    policy = retrieve_policy(input_path)
    summary = summarize_policy(policy)
    Path(output_path).write_text(summary, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="UC-0B faithful policy summariser")
    parser.add_argument("--input", required=True, help="Path to the source .txt policy")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    args = parser.parse_args()
    write_summary(args.input, args.output)
    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
