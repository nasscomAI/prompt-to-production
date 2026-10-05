"""UC-0B policy-preserving summarizer.

The summary is deliberately source-faithful: every numbered clause remains
traceable to its original wording so approvals, thresholds, deadlines, and
prohibitions cannot be silently softened or omitted.
"""

import argparse
import re
from pathlib import Path
from typing import Dict, List


SECTION_PATTERN = re.compile(r"^(?P<number>\d+)\.\s+(?P<title>.+?)\s*$")
CLAUSE_PATTERN = re.compile(r"^(?P<reference>\d+\.\d+)\s+(?P<text>.+?)\s*$")


def retrieve_policy(input_path: str) -> List[Dict[str, str]]:
    """Load a policy text file into ordered, complete numbered clauses.

    Each result contains the section title, the original clause reference, and
    the clause's normalized source text. Text outside numbered clauses is not
    treated as policy content, preventing invented references in the summary.
    """
    path = Path(input_path)
    try:
        raw_text = path.read_text(encoding="utf-8-sig")
    except OSError as error:
        raise OSError(f"Unable to read policy file '{input_path}': {error}") from error

    if not raw_text.strip():
        raise ValueError("Policy file is empty.")

    clauses: List[Dict[str, str]] = []
    current_clause = None
    current_section = ""

    for raw_line in raw_text.splitlines():
        line = raw_line.strip()
        # Divider lines use decorative Unicode characters. Treat any line with
        # no ASCII letters or digits as a divider, even when terminal encoding
        # renders those characters differently.
        if not line or not re.search(r"[A-Za-z0-9]", line):
            continue

        section_match = SECTION_PATTERN.match(line)
        if section_match:
            current_section = (
                f"{section_match.group('number')}. {section_match.group('title')}"
            )
            current_clause = None
            continue

        clause_match = CLAUSE_PATTERN.match(line)
        if clause_match:
            current_clause = {
                "section": current_section,
                "reference": clause_match.group("reference"),
                "text": clause_match.group("text"),
            }
            clauses.append(current_clause)
            continue

        # Wrapped source lines belong only to the preceding numbered clause.
        if current_clause is not None:
            current_clause["text"] = f"{current_clause['text']} {line}"

    if not clauses:
        raise ValueError("No numbered policy clauses were found in the input file.")

    return clauses


def summarize_policy(sections: List[Dict[str, str]]) -> str:
    """Create a complete, clause-referenced, source-only policy summary.

    Using the normalized source wording as the summary prevents a material
    condition from being lost. It is intentionally concise only in formatting,
    not at the expense of policy meaning.
    """
    if not sections:
        raise ValueError("Cannot summarize an empty policy clause inventory.")

    summary_lines = ["POLICY SUMMARY", ""]
    previous_section = None
    seen_references = set()

    for clause in sections:
        reference = str(clause.get("reference", "")).strip()
        text = " ".join(str(clause.get("text", "")).split())
        section = str(clause.get("section", "")).strip()
        if not reference or not text:
            raise ValueError("Each policy clause must include a reference and source text.")
        if reference in seen_references:
            raise ValueError(f"Duplicate clause reference found: {reference}.")
        seen_references.add(reference)

        if section and section != previous_section:
            if previous_section is not None:
                summary_lines.append("")
            summary_lines.append(section)
            previous_section = section
        summary_lines.append(f"{reference} {text}")

    return "\n".join(summary_lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0B Policy-Preserving Summarizer")
    parser.add_argument("--input", required=True, help="Path to the policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write the policy summary")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary, encoding="utf-8")
    print(f"Done. Summary written to {output_path}")


if __name__ == "__main__":
    main()
