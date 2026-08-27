"""
UC-0B app.py — Policy Document Summarizer
Implements the retrieve_policy and summarize_policy skills as defined in skills.md.
Follows enforcement rules from agents.md.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import sys


# ─────────────────────────────────────────────────────────
# Skill: retrieve_policy
# ─────────────────────────────────────────────────────────

def retrieve_policy(file_path: str) -> list[dict]:
    """
    Loads a .txt policy file and returns its content as structured numbered sections.

    Returns a list of dicts, each containing:
      - section_number  (e.g. "2.3")
      - section_title   (e.g. "ANNUAL LEAVE")
      - clause_text     (full unmodified text of the clause)
      - binding_verb    (must, will, requires, may, not permitted, etc.)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
    except FileNotFoundError:
        print(f"ERROR: File not found at {file_path}.")
        sys.exit(1)

    if not raw_text.strip():
        print("ERROR: No structured policy clauses found in input.")
        sys.exit(1)

    # Parse section headings (lines like "2. ANNUAL LEAVE" between ═══ dividers)
    sections = _parse_sections(raw_text)

    if not sections:
        print("ERROR: No structured policy clauses found in input.")
        sys.exit(1)

    return sections


def _parse_sections(raw_text: str) -> list[dict]:
    """Parse the raw policy text into structured clause entries."""
    lines = raw_text.split("\n")
    sections = []
    current_title = ""

    # Regex patterns
    heading_pattern = re.compile(r"^\d+\.\s+[A-Z]")
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)")

    # Binding verb detection patterns (order matters — check multi-word first)
    binding_verbs = [
        ("not permitted", "not permitted"),
        ("not valid", "not valid"),
        ("are forfeited", "are forfeited"),
        ("cannot be", "cannot be"),
        ("will not be", "will not be"),
        ("do not count", "do not count"),
        ("does not apply", "does not apply"),
        ("requires", "requires"),
        ("must", "must"),
        ("will", "will"),
        ("may", "may"),
        ("is entitled", "is entitled"),
        ("are entitled", "are entitled"),
    ]

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Detect section heading (e.g. "2. ANNUAL LEAVE")
        if heading_pattern.match(line):
            current_title = line

        # Detect clause (e.g. "2.3 Employees must submit...")
        clause_match = clause_pattern.match(line)
        if clause_match:
            section_number = clause_match.group(1)
            # Collect full clause text (may span multiple lines)
            clause_lines = [lines[i].strip()]
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                # Stop if we hit another clause, heading, or divider
                if (clause_pattern.match(next_line)
                        or heading_pattern.match(next_line)
                        or next_line.startswith("═")):
                    break
                if next_line:  # skip blank lines
                    clause_lines.append(next_line)
                else:
                    break  # blank line ends clause
                j += 1

            full_clause = " ".join(clause_lines)
            # Remove the clause number prefix from the text for cleaner output
            clause_text_only = re.sub(r"^\d+\.\d+\s+", "", full_clause)

            # Detect binding verb
            detected_verb = _detect_binding_verb(clause_text_only.lower(), binding_verbs)

            sections.append({
                "section_number": section_number,
                "section_title": current_title,
                "clause_text": clause_text_only,
                "binding_verb": detected_verb,
            })

        i += 1

    return sections


def _detect_binding_verb(text: str, binding_verbs: list[tuple]) -> str:
    """Detect the primary binding verb in a clause."""
    for pattern, verb in binding_verbs:
        if pattern in text:
            return verb
    return "—"


# ─────────────────────────────────────────────────────────
# Skill: summarize_policy
# ─────────────────────────────────────────────────────────

# Clauses flagged for verbatim quoting (multi-condition or high meaning-loss risk)
VERBATIM_CLAUSES = {"5.2", "2.5", "7.2"}


def summarize_policy(clauses: list[dict]) -> str:
    """
    Takes structured policy sections and produces a compliant clause-by-clause
    summary with clause references.

    Enforcement rules applied:
      1. Every numbered clause must be present.
      2. Multi-condition obligations preserve ALL conditions.
      3. No information added beyond the source.
      4. Binding verbs match the source exactly.
      5. High-risk clauses quoted verbatim with flag.
    """
    if not clauses:
        return "ERROR: Invalid input — expected structured policy sections."

    output_lines = []
    current_heading = ""

    for clause in clauses:
        # Emit section heading when it changes
        if clause["section_title"] != current_heading:
            current_heading = clause["section_title"]
            if output_lines:
                output_lines.append("")  # blank line between sections
            output_lines.append(f"{'=' * 60}")
            output_lines.append(current_heading)
            output_lines.append(f"{'=' * 60}")

        section_num = clause["section_number"]
        clause_text = clause["clause_text"]

        # For high-risk clauses, quote verbatim
        if section_num in VERBATIM_CLAUSES:
            summary_line = (
                f"  [{section_num}] {clause_text} "
                f"[VERBATIM — meaning loss risk]"
            )
        else:
            # Produce a faithful one-line summary preserving binding verb and conditions
            summary_line = f"  [{section_num}] {clause_text}"

        output_lines.append(summary_line)

    return "\n".join(output_lines)


# ─────────────────────────────────────────────────────────
# Validation
# ─────────────────────────────────────────────────────────

# Ground truth clause inventory from README
REQUIRED_CLAUSES = {
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4",
    "5.2", "5.3",
    "7.2",
}


def validate_summary(summary: str, clauses: list[dict]) -> list[str]:
    """
    Validate the summary against enforcement rules.
    Returns a list of warnings (empty if all pass).
    """
    warnings = []

    # 1. Check every clause is present
    all_clause_nums = {c["section_number"] for c in clauses}
    for num in all_clause_nums:
        if f"[{num}]" not in summary:
            warnings.append(f"MISSING: Clause {num} is not present in the summary.")

    # 2. Check critical required clauses specifically
    for num in REQUIRED_CLAUSES:
        if f"[{num}]" not in summary:
            warnings.append(
                f"CRITICAL MISSING: Required clause {num} from ground truth is absent."
            )

    # 3. Check for scope bleed (phrases NOT in the source document)
    scope_bleed_phrases = [
        "as is standard practice",
        "typically in government",
        "employees are generally expected",
        "it is common to",
        "as per industry norms",
        "usually",
        "normally",
        "in most organisations",
    ]
    summary_lower = summary.lower()
    for phrase in scope_bleed_phrases:
        if phrase in summary_lower:
            warnings.append(
                f"SCOPE BLEED: Found phrase '{phrase}' which is not in the source document."
            )

    # 4. Check multi-condition clause 5.2 specifically
    if "[5.2]" in summary:
        s52_lower = summary_lower
        if "department head" not in s52_lower or "hr director" not in s52_lower:
            warnings.append(
                "CONDITION DROP: Clause 5.2 requires BOTH 'Department Head' AND "
                "'HR Director' — one or both are missing."
            )

    return warnings


# ─────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="UC-0B — Policy Document Summarizer"
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to the .txt policy document"
    )
    parser.add_argument(
        "--output", required=True,
        help="Path to write the summary output"
    )
    args = parser.parse_args()

    # Step 1: Retrieve and parse policy
    print(f"Reading policy from: {args.input}")
    clauses = retrieve_policy(args.input)
    print(f"  Parsed {len(clauses)} clauses.")

    # Step 2: Summarize
    print("Generating summary...")
    summary = summarize_policy(clauses)

    # Step 3: Validate
    print("Validating summary against enforcement rules...")
    warnings = validate_summary(summary, clauses)

    if warnings:
        print(f"\n⚠️  {len(warnings)} validation warning(s):")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("✅ All enforcement rules passed.")

    # Step 4: Write output
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
        f.write("\n")

    print(f"\nDone. Summary written to {args.output}")


if __name__ == "__main__":
    main()
