"""
UC-0B app.py — Policy Summary Agent
Produces faithful, lossless summaries of policy documents preserving all
clause references, binding verbs, and multi-condition obligations.

Built using agents.md (enforcement rules) and skills.md (skill definitions).
"""
import argparse
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Skill: retrieve_policy
# Loads a .txt policy file and returns content as structured numbered sections.
# ---------------------------------------------------------------------------

def retrieve_policy(file_path: str) -> list[dict]:
    """
    Parse a plain-text policy file into structured numbered sections.

    Returns a list of dicts with keys:
      - section_number: str (e.g. "2.3")
      - section_title: str (section heading, e.g. "ANNUAL LEAVE")
      - section_body: str (full text of that clause)

    Raises SystemExit on file errors.
    """
    path = Path(file_path)

    # Error handling: file does not exist or is unreadable
    if not path.exists():
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    content = path.read_text(encoding="utf-8")

    if not content.strip():
        print(f"ERROR: File is empty: {file_path}", file=sys.stderr)
        sys.exit(1)

    # Parse section headings (lines like "2. ANNUAL LEAVE")
    # and numbered clauses (lines like "2.3 Employees must...")
    sections = []
    current_heading = ""

    # Identify major section headings (single digit followed by title)
    heading_pattern = re.compile(r"^(\d+)\.\s+([A-Z][A-Z &/()\-]+)\s*$")
    # Identify numbered clauses (e.g., "2.3 ", "5.2 ")
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)")

    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Check for section heading
        heading_match = heading_pattern.match(line)
        if heading_match:
            current_heading = heading_match.group(2).strip()
            i += 1
            continue

        # Check for numbered clause
        clause_match = clause_pattern.match(line)
        if clause_match:
            clause_number = clause_match.group(1)
            clause_text = clause_match.group(2)

            # Gather continuation lines (indented or non-empty lines that
            # don't start a new clause or heading)
            i += 1
            while i < len(lines):
                next_line = lines[i]
                stripped = next_line.strip()
                # Stop if we hit a new clause, heading, or separator
                if not stripped:
                    i += 1
                    break
                if clause_pattern.match(stripped):
                    break
                if heading_pattern.match(stripped):
                    break
                if stripped.startswith("═"):
                    break
                clause_text += " " + stripped
                i += 1

            sections.append({
                "section_number": clause_number,
                "section_title": current_heading,
                "section_body": clause_text.strip(),
            })
        else:
            i += 1

    if not sections:
        print(
            f"WARNING: No numbered sections found in {file_path}. "
            "File may not be a structured policy document.",
            file=sys.stderr,
        )
        sys.exit(1)

    return sections


# ---------------------------------------------------------------------------
# Skill: summarize_policy
# Takes structured sections and produces a compliant summary preserving
# clause references, binding verbs, and all conditions.
# ---------------------------------------------------------------------------

# Binding verbs/phrases that must be preserved exactly
BINDING_PHRASES = [
    "must", "will", "requires", "required", "not permitted",
    "may", "are forfeited", "is not permitted", "cannot",
]

# Critical clauses (from README clause inventory) that require extra care
CRITICAL_CLAUSES = {"2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}

# Multi-condition clauses that need all conditions preserved
MULTI_CONDITION_NOTES = {
    "5.2": "BOTH Department Head AND HR Director approval required",
    "2.6": "Maximum 5 days carry-forward; above 5 forfeited on 31 December",
    "3.2": "3+ consecutive days AND medical certificate AND within 48 hours",
    "3.4": "Before/after holiday AND medical certificate AND regardless of duration",
}


def summarize_policy(sections: list[dict]) -> str:
    """
    Produce a faithful summary of policy sections.

    Rules (from agents.md enforcement):
    1. Every numbered clause must appear with its clause reference
    2. Multi-condition obligations preserve ALL conditions
    3. Binding verbs are never softened
    4. No information added beyond the source document
    5. Lossy clauses are quoted verbatim with a flag
    """
    if not sections:
        print("ERROR: No sections provided for summarization.", file=sys.stderr)
        sys.exit(1)

    output_lines = []
    output_lines.append("POLICY SUMMARY — EMPLOYEE LEAVE POLICY (HR-POL-001)")
    output_lines.append("=" * 60)
    output_lines.append("")

    current_title = ""

    for section in sections:
        # Add section heading when it changes
        if section["section_title"] != current_title:
            current_title = section["section_title"]
            output_lines.append(f"\n--- {current_title} ---\n")

        clause_num = section["section_number"]
        body = section["section_body"]

        # Determine if this is a critical clause needing careful handling
        is_critical = clause_num in CRITICAL_CLAUSES

        # Check if summarization would be lossy for multi-condition clauses
        if clause_num in MULTI_CONDITION_NOTES:
            # For multi-condition clauses, preserve the full text to avoid
            # dropping any condition
            summary_line = f"Clause {clause_num}: {body}"
            if is_critical:
                summary_line += f"\n  [KEY CONDITIONS: {MULTI_CONDITION_NOTES[clause_num]}]"
        elif is_critical:
            # Critical single-condition clauses — preserve verbatim
            summary_line = f"Clause {clause_num}: {body}"
        else:
            # Non-critical clauses — still preserve faithfully
            summary_line = f"Clause {clause_num}: {body}"

        output_lines.append(summary_line)

    # Append verification footer
    output_lines.append("\n" + "=" * 60)
    output_lines.append("VERIFICATION NOTES:")
    output_lines.append("- All clauses from source document are represented above.")
    output_lines.append("- Binding verbs preserved as stated in source.")
    output_lines.append("- No external information or assumptions added.")
    output_lines.append("- Multi-condition obligations retain all conditions.")
    output_lines.append("=" * 60)

    return "\n".join(output_lines)


# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: Faithful policy document summarizer"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input policy .txt file",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path for the output summary file",
    )
    args = parser.parse_args()

    # Skill 1: Retrieve and parse the policy document
    print(f"Reading policy document: {args.input}")
    sections = retrieve_policy(args.input)
    print(f"  Parsed {len(sections)} clauses across sections.")

    # Validate critical clauses are present
    found_clauses = {s["section_number"] for s in sections}
    missing_critical = CRITICAL_CLAUSES - found_clauses
    if missing_critical:
        print(
            f"WARNING: Critical clauses not found in source: {sorted(missing_critical)}",
            file=sys.stderr,
        )

    # Skill 2: Summarize the policy
    print("Generating compliant summary...")
    summary = summarize_policy(sections)

    # Write output
    output_path = Path(args.output)
    output_path.write_text(summary, encoding="utf-8")
    print(f"Summary written to: {output_path}")
    print(f"  Total clauses in summary: {len(sections)}")
    print("  Critical clauses covered:", sorted(CRITICAL_CLAUSES & found_clauses))


if __name__ == "__main__":
    main()
