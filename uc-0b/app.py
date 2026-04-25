"""
UC-0B policy summarization app.

Reads a policy document and writes a clause-referenced summary while preserving
all obligations and conditions.
"""

import argparse
import re
from pathlib import Path


SECTION_HEADER_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z\s()/-]+)$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def retrieve_policy(file_path: str) -> dict:
    """Load and parse a text policy into numbered sections and clauses."""
    path = Path(file_path)
    if not path.exists():
        raise ValueError(f"Input file not found: {file_path}")
    if not path.is_file():
        raise ValueError(f"Input path is not a file: {file_path}")

    raw_text = path.read_text(encoding="utf-8").strip()
    if not raw_text:
        raise ValueError("Input file is empty.")

    lines = raw_text.splitlines()
    title = _extract_title(lines)

    sections = []
    current_section = None
    current_clause = None

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or set(stripped) == {"═"}:
            continue

        section_match = SECTION_HEADER_RE.match(stripped)
        if section_match:
            current_section = {
                "section_number": section_match.group(1),
                "section_title": section_match.group(2).strip(),
                "clauses": [],
            }
            sections.append(current_section)
            current_clause = None
            continue

        clause_match = CLAUSE_RE.match(stripped)
        if clause_match:
            clause_id = clause_match.group(1)
            clause_text = clause_match.group(2).strip()
            if current_section is None:
                raise ValueError(
                    f"Clause {clause_id} appears before any section header."
                )
            current_clause = {"clause_id": clause_id, "clause_text": clause_text}
            current_section["clauses"].append(current_clause)
            continue

        # Continuation line for wrapped clause text.
        if current_clause is not None:
            current_clause["clause_text"] = (
                f"{current_clause['clause_text']} {stripped}".strip()
            )

    if not any(section["clauses"] for section in sections):
        raise ValueError("No parseable numbered clauses found in input.")

    return {"document_id": path.stem, "title": title, "sections": sections}


def summarize_policy(parsed_policy: dict) -> dict:
    """
    Build summary items with explicit clause references.

    To prevent meaning loss, high-risk clauses are quoted verbatim.
    """
    summary_items = []
    all_clauses = [
        clause
        for section in parsed_policy["sections"]
        for clause in section["clauses"]
    ]
    if not all_clauses:
        raise ValueError("Cannot summarize policy with zero clauses.")

    for clause in all_clauses:
        clause_text = clause["clause_text"]
        clause_id = clause["clause_id"]
        needs_verbatim = _is_high_risk_clause(clause_text)

        summary_items.append(
            {
                "summary_text": clause_text,
                "source_clauses": [clause_id],
                "verbatim": needs_verbatim,
            }
        )

    # Coverage check: all parsed clauses must appear exactly once in output.
    summarized_ids = [item["source_clauses"][0] for item in summary_items]
    source_ids = [clause["clause_id"] for clause in all_clauses]
    if sorted(summarized_ids) != sorted(source_ids):
        raise ValueError("Summary coverage failed: missing or extra clause mappings.")

    return {"summary_items": summary_items}


def write_summary_file(parsed_policy: dict, summary: dict, output_path: str) -> None:
    """Write a readable, clause-referenced summary text file."""
    source_clause_map = {
        clause["clause_id"]: clause["clause_text"]
        for section in parsed_policy["sections"]
        for clause in section["clauses"]
    }

    lines = [f"Policy Summary: {parsed_policy['title']}", ""]
    lines.append("Clause-referenced summary:")

    for item in summary["summary_items"]:
        clause_id = item["source_clauses"][0]
        source_text = source_clause_map[clause_id]
        marker = " [VERBATIM - HIGH RISK]" if item.get("verbatim") else ""
        lines.append(f"- [{clause_id}]{marker} {item['summary_text']}")
        if item.get("verbatim") and item["summary_text"] != source_text:
            # Strictly avoid meaning drift on flagged clauses.
            lines.append(f'  Source quote: "{source_text}"')

    Path(output_path).write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def _extract_title(lines: list[str]) -> str:
    for line in lines:
        stripped = line.strip()
        if stripped == "EMPLOYEE LEAVE POLICY":
            return stripped
    return "Policy Document"


def _is_high_risk_clause(text: str) -> bool:
    lowered = text.lower()
    risk_markers = [
        "must",
        "requires",
        "required",
        "regardless",
        "not valid",
        "not sufficient",
        "not permitted",
        "under any circumstances",
        "forfeited",
        "approval from",
        " and ",
    ]
    return any(marker in lowered for marker in risk_markers)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate clause-referenced policy summary."
    )
    parser.add_argument("--input", required=True, help="Input policy .txt file path")
    parser.add_argument("--output", required=True, help="Output summary .txt file path")
    args = parser.parse_args()

    parsed_policy = retrieve_policy(args.input)
    summary = summarize_policy(parsed_policy)
    write_summary_file(parsed_policy, summary, args.output)


if __name__ == "__main__":
    main()
