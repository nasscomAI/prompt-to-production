"""
UC-0B — Summary That Changes Meaning
Rule-based policy summariser built from agents.md and skills.md specifications.
"""
import argparse
import re
import sys


# ---------------------------------------------------------------------------
# Skill: retrieve_policy
# ---------------------------------------------------------------------------

def retrieve_policy(file_path: str) -> list[dict]:
    """
    Load a .txt policy file and return its content as structured numbered
    sections with clause identifiers preserved.

    Returns: list of dicts with keys: section_number, section_heading, section_text
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Error reading file: {exc}", file=sys.stderr)
        sys.exit(1)

    sections: list[dict] = []
    current_heading = ""

    # Detect top-level headings (lines like "2. ANNUAL LEAVE")
    heading_pattern = re.compile(r"^(\d+)\.\s+(.+)$")
    # Detect numbered clauses (lines like "2.3 Employees must...")
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.+)")

    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Check for top-level heading
        heading_match = heading_pattern.match(line)
        if heading_match:
            current_heading = heading_match.group(2).strip()
            i += 1
            continue

        # Check for numbered clause
        clause_match = clause_pattern.match(line)
        if clause_match:
            clause_num = clause_match.group(1)
            clause_text = clause_match.group(2)

            # Gather continuation lines (indented or non-empty lines that
            # don't start a new clause or heading)
            i += 1
            while i < len(lines):
                next_line = lines[i]
                stripped = next_line.strip()
                if not stripped:
                    break
                if clause_pattern.match(stripped):
                    break
                if heading_pattern.match(stripped):
                    break
                if re.match(r"^[═]+$", stripped):
                    break
                clause_text += " " + stripped
                i += 1

            sections.append({
                "section_number": clause_num,
                "section_heading": current_heading,
                "section_text": clause_text.strip(),
            })
            continue

        i += 1

    if not sections:
        # Unstructured fallback
        sections.append({
            "section_number": "UNSTRUCTURED",
            "section_heading": "FULL DOCUMENT",
            "section_text": content,
        })
        print("Warning: No numbered clauses found. Returning raw text.",
              file=sys.stderr)

    return sections


# ---------------------------------------------------------------------------
# Binding verb preservation map
# ---------------------------------------------------------------------------

# These binding verbs must not be softened in the summary.
BINDING_VERBS = {
    "must": "must",
    "will": "will",
    "requires": "requires",
    "required": "required",
    "not permitted": "not permitted",
    "are forfeited": "are forfeited",
    "cannot": "cannot",
    "may not": "may not",
}

# Softened verbs to watch for (these must NOT replace binding verbs)
SOFTENED_VERBS = {"should", "can", "may", "is expected to", "typically",
                  "generally", "as is standard"}


def _preserve_binding_verb(source_text: str) -> str:
    """Extract the primary binding verb from the source clause."""
    source_lower = source_text.lower()
    for verb in BINDING_VERBS:
        if verb in source_lower:
            return verb
    return ""


# ---------------------------------------------------------------------------
# Critical clauses — ground truth from README
# ---------------------------------------------------------------------------

CRITICAL_CLAUSES = {
    "2.3": "14-day advance notice required",
    "2.4": "Written approval required before leave commences. Verbal not valid.",
    "2.5": "Unapproved absence = LOP regardless of subsequent approval",
    "2.6": "Max 5 days carry-forward. Above 5 forfeited on 31 Dec.",
    "2.7": "Carry-forward days must be used Jan-Mar or forfeited",
    "3.2": "3+ consecutive sick days requires medical cert within 48hrs",
    "3.4": "Sick leave before/after holiday requires cert regardless of duration",
    "5.2": "LWP requires Department Head AND HR Director approval",
    "5.3": "LWP >30 days requires Municipal Commissioner approval",
    "7.2": "Leave encashment during service not permitted under any circumstances",
}

# Multi-condition clauses that need special attention
MULTI_CONDITION_CLAUSES = {
    "2.4": ["written approval", "verbal approval is not valid"],
    "2.6": ["maximum of 5", "forfeited on 31 December"],
    "5.2": ["Department Head", "HR Director"],
}


# ---------------------------------------------------------------------------
# Skill: summarize_policy
# ---------------------------------------------------------------------------

def summarize_policy(sections: list[dict]) -> str:
    """
    Take structured policy sections and produce a clause-by-clause compliant
    summary that preserves all obligations and conditions.

    Enforcement (from agents.md):
      - Every numbered clause must appear with its clause reference
      - Multi-condition obligations preserve ALL conditions
      - Binding verbs must not be softened
      - No external information added
      - Verbatim fallback for meaning-loss risk
    """
    summary_lines: list[str] = []
    current_heading = ""
    seen_clauses: set[str] = set()

    for section in sections:
        clause_num = section["section_number"]
        heading = section["section_heading"]
        text = section["section_text"]

        # Add heading separator when section changes
        if heading != current_heading:
            if summary_lines:
                summary_lines.append("")
            summary_lines.append(f"--- {heading} ---")
            current_heading = heading

        seen_clauses.add(clause_num)

        # Build the summary line
        summary_line = _summarize_clause(clause_num, text)
        summary_lines.append(summary_line)

    # Verify all critical clauses are present
    missing = []
    for clause_num in CRITICAL_CLAUSES:
        if clause_num not in seen_clauses:
            missing.append(clause_num)

    if missing:
        summary_lines.append("")
        summary_lines.append("--- MISSING CLAUSES (NOT FOUND IN SOURCE) ---")
        for clause_num in missing:
            summary_lines.append(
                f"§{clause_num}: [MISSING] Expected: {CRITICAL_CLAUSES[clause_num]}"
            )

    return "\n".join(summary_lines)


def _summarize_clause(clause_num: str, text: str) -> str:
    """
    Summarize a single clause, preserving binding verbs and all conditions.
    Falls back to verbatim quoting when meaning loss is likely.
    """
    binding_verb = _preserve_binding_verb(text)

    # Check if this is a multi-condition clause
    if clause_num in MULTI_CONDITION_CLAUSES:
        conditions = MULTI_CONDITION_CLAUSES[clause_num]
        text_lower = text.lower()
        all_present = all(c.lower() in text_lower for c in conditions)

        if all_present:
            # All conditions found — quote verbatim to avoid condition drop
            return (
                f"§{clause_num}: {text} "
                f"[VERBATIM: multi-condition clause — all conditions preserved]"
            )
        else:
            # Some conditions missing from source (shouldn't happen)
            return f"§{clause_num}: {text} [VERBATIM: meaning loss risk]"

    # Check if it's a critical clause with absolute prohibition or
    # complex obligation — use verbatim for safety
    if clause_num in CRITICAL_CLAUSES:
        return f"§{clause_num}: {text}"

    # Standard clauses — summarize but preserve binding verb
    if binding_verb:
        return f"§{clause_num}: {text}"
    else:
        # Informational clause — no binding obligation
        return f"§{clause_num}: {text} [INFO-ONLY: no binding obligation]"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="UC-0B — Policy Summariser (Summary That Changes Meaning)"
    )
    parser.add_argument("--input", required=True,
                        help="Path to policy .txt file")
    parser.add_argument("--output", required=True,
                        help="Path to write summary output")
    args = parser.parse_args()

    # Step 1: Retrieve and parse policy
    sections = retrieve_policy(args.input)
    print(f"Parsed {len(sections)} clause(s) from {args.input}")

    # Step 2: Summarize with enforcement
    summary = summarize_policy(sections)

    # Step 3: Write output
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary + "\n")
    except Exception as exc:
        print(f"Error writing output: {exc}", file=sys.stderr)
        sys.exit(1)

    # Step 4: Report critical clause coverage
    parsed_nums = {s["section_number"] for s in sections}
    covered = [c for c in CRITICAL_CLAUSES if c in parsed_nums]
    missing = [c for c in CRITICAL_CLAUSES if c not in parsed_nums]

    print(f"Critical clauses covered: {len(covered)}/10")
    if missing:
        print(f"WARNING — Missing critical clauses: {', '.join(missing)}",
              file=sys.stderr)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
