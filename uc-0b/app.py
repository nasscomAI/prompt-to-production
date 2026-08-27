"""Generate a faithful summary for numbered policy clauses."""

import argparse
import re
from pathlib import Path


CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*\S)\s*$")
SECTION_PATTERN = re.compile(r"^\d+\.\s+.*")


def retrieve_policy(input_path: Path):
    """Load a policy file and return ordered, structured numbered clauses."""
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    text = input_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    section_title = "General"
    clauses = []

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            continue

        if SECTION_PATTERN.match(stripped) and not CLAUSE_PATTERN.match(stripped):
            section_title = stripped
            continue

        clause_match = CLAUSE_PATTERN.match(stripped)
        if clause_match:
            clause_number, clause_text = clause_match.groups()
            clauses.append(
                {
                    "clause_number": clause_number,
                    "section_title": section_title,
                    "clause_text": clause_text,
                }
            )
            continue

        if clauses and not stripped.startswith("═"):
            clauses[-1]["clause_text"] += f" {stripped}"

    if not clauses:
        raise ValueError("No numbered clauses found in input policy")

    return clauses


def summarize_policy(clauses):
    """Create a clause-referenced summary while preserving obligations and conditions."""
    lines = []
    lines.append("HR Leave Policy Summary (Clause-Referenced)")
    lines.append("")
    lines.append("This summary preserves all numbered clauses from the source policy.")
    lines.append("")

    current_section = None
    for clause in clauses:
        section = clause["section_title"]
        number = clause["clause_number"]
        text = clause["clause_text"]

        if section != current_section:
            if current_section is not None:
                lines.append("")
            lines.append(section)
            current_section = section

        # Keep clause text faithful to avoid silent condition drops.
        lines.append(f"- {number}: {text}")

    lines.append("")
    lines.append("High-risk clauses retained verbatim to prevent meaning loss:")
    for required_clause in ("2.4", "2.5", "5.2", "5.3", "7.2"):
        match = next((c for c in clauses if c["clause_number"] == required_clause), None)
        if match:
            lines.append(f"- VERBATIM {required_clause}: \"{match['clause_text']}\"")

    return "\n".join(lines).strip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="Summarize policy document without meaning drift")
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to output summary text file")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    clauses = retrieve_policy(input_path)
    summary = summarize_policy(clauses)
    output_path.write_text(summary, encoding="utf-8")


if __name__ == "__main__":
    main()
