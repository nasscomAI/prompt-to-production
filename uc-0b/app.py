"""
UC-0B app.py — Policy Summarisation Agent
Implements retrieve_policy and summarize_policy per agents.md (R.I.C.E)
and skills.md specifications.
"""
import argparse
import re
import sys


# ---------------------------------------------------------------------------
# Enforcement constants (from agents.md)
# ---------------------------------------------------------------------------

# Binding verbs that must be preserved exactly as they appear in the source.
BINDING_VERBS = [
    "must", "will", "requires", "may", "not permitted",
    "are forfeited", "is not valid", "cannot", "are entitled",
    "is entitled", "do not count", "is not permitted",
]

# Scope-bleed phrases that must NEVER appear in the summary (agents.md context).
SCOPE_BLEED_PHRASES = [
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
    "as is common",
    "generally",
    "in line with standard norms",
    "as per industry practice",
    "it is customary",
]


# ---------------------------------------------------------------------------
# Skill: retrieve_policy
# ---------------------------------------------------------------------------

def retrieve_policy(input_path: str) -> list[dict]:
    """
    Load a plain-text policy file and return structured, numbered sections.

    Input : file path (string) pointing to a .txt policy document.
    Output: list of section dicts, each with:
              - section_number (str): clause number e.g. "2.3"
              - section_heading (str): parent section title e.g. "ANNUAL LEAVE"
              - section_body (str): full verbatim text of the clause.

    Error handling (skills.md):
      - File not found / unreadable → error message, never partial output.
      - Empty file → error message.
      - No numbered clauses detected → error message.
    """

    # --- Guard: read the file ------------------------------------------------
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"ERROR: File not found — '{input_path}'", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"ERROR: Cannot read file '{input_path}': {exc}", file=sys.stderr)
        sys.exit(1)

    # --- Guard: empty file ---------------------------------------------------
    if not content.strip():
        print("ERROR: Empty file — no content to process.", file=sys.stderr)
        sys.exit(1)

    # --- Parse sections and clauses ------------------------------------------
    # Section headings look like:
    #   ═══════════════════════════════════════════════════════════
    #   2. ANNUAL LEAVE
    #   ═══════════════════════════════════════════════════════════
    # Clauses look like:
    #   2.3 Employees must submit a leave application ...

    sections: list[dict] = []
    current_heading = ""

    # Pattern for major section headers: "1. PURPOSE AND SCOPE", "2. ANNUAL LEAVE"
    heading_pattern = re.compile(r"^\d+\.\s+[A-Z][A-Z\s()]+$")

    # Pattern for numbered clauses: "2.3 ...", "5.2 ..."
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.+)")

    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Detect section heading
        if heading_pattern.match(line):
            # Extract just the title part (strip leading number + dot)
            current_heading = re.sub(r"^\d+\.\s+", "", line).strip()
            i += 1
            continue

        # Detect clause start
        clause_match = clause_pattern.match(line)
        if clause_match:
            clause_num = clause_match.group(1)
            clause_text = clause_match.group(2)

            # Collect continuation lines (indented or non-clause, non-heading,
            # non-separator lines that follow)
            i += 1
            while i < len(lines):
                next_line = lines[i]
                stripped = next_line.strip()
                # Stop if we hit another clause, heading, separator, or blank line
                if not stripped:
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
                "section_number": clause_num,
                "section_heading": current_heading,
                "section_body": clause_text.strip(),
            })
            continue

        i += 1

    # --- Guard: no clauses found ---------------------------------------------
    if not sections:
        print(
            "ERROR: No numbered clauses detected in the document.",
            file=sys.stderr,
        )
        sys.exit(1)

    return sections


# ---------------------------------------------------------------------------
# Skill: summarize_policy
# ---------------------------------------------------------------------------

def summarize_policy(sections: list[dict], output_path: str):
    """
    Generate a clause-complete, faithful summary from structured sections.

    Input : list of section dicts from retrieve_policy.
    Output: plain-text summary file at output_path.

    Enforcement rules (agents.md):
      1. Every numbered clause must be present.
      2. Multi-condition obligations preserve ALL conditions.
      3. Binding verbs preserved exactly.
      4. Zero information not in the source.
      5. Verbatim flag when summarisation would alter meaning.
      6. Refuse on empty/malformed input.
    """

    # --- Guard: empty or malformed input -------------------------------------
    if not sections:
        print("ERROR: No sections provided — cannot produce summary.", file=sys.stderr)
        sys.exit(1)

    for idx, sec in enumerate(sections):
        if "section_number" not in sec or "section_body" not in sec:
            print(
                f"ERROR: Malformed section object at index {idx} — "
                f"missing 'section_number' or 'section_body'.",
                file=sys.stderr,
            )
            sys.exit(1)

    # --- Build summary -------------------------------------------------------
    summary_lines: list[str] = []
    current_heading = ""

    for sec in sections:
        # Insert heading separator when the section changes
        if sec["section_heading"] != current_heading:
            current_heading = sec["section_heading"]
            if summary_lines:
                summary_lines.append("")  # blank line between sections
            summary_lines.append(f"── {current_heading} ──")

        clause_num = sec["section_number"]
        body = sec["section_body"]

        # --- Summarise the clause --------------------------------------------
        summarised = _summarise_clause(clause_num, body)
        summary_lines.append(f"{clause_num}: {summarised}")

    # --- Scope-bleed check (enforcement rule 4) ------------------------------
    full_summary = "\n".join(summary_lines)
    for phrase in SCOPE_BLEED_PHRASES:
        if phrase.lower() in full_summary.lower():
            print(
                f"WARNING: Scope-bleed phrase detected — '{phrase}'. "
                f"Removing it from the summary.",
                file=sys.stderr,
            )
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            full_summary = pattern.sub("", full_summary)

    # --- Write output --------------------------------------------------------
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_summary.rstrip() + "\n")
    except Exception as exc:
        print(f"ERROR: Cannot write output file '{output_path}': {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Summary written to {output_path} ({len(sections)} clauses).")


# ---------------------------------------------------------------------------
# Summarisation logic
# ---------------------------------------------------------------------------

def _summarise_clause(clause_num: str, body: str) -> str:
    """
    Produce a faithful one-line summary of a single clause.

    Strategy:
      - Condense obvious boilerplate (e.g., "Each permanent employee is
        entitled to ...") into shorter phrasing — BUT preserve every
        binding verb, numeric value, condition, and named entity exactly.
      - If the clause has multi-condition obligations (AND / BOTH),
        preserve ALL conditions.
      - If shortening would lose meaning, return verbatim with flag.
    """

    # Check for multi-condition obligations — these are high-risk for
    # condition-drop failures, so we quote verbatim by default.
    multi_condition_markers = [" and the ", " AND ", " BOTH "]
    has_multi_condition = any(m in body or m.lower() in body.lower()
                              for m in multi_condition_markers)

    # Check for absolute prohibitions — also high-risk for softening.
    absolute_markers = [
        "not permitted under any circumstances",
        "cannot be encashed under any circumstances",
        "cannot be carried forward",
        "cannot be split",
    ]
    has_absolute = any(m.lower() in body.lower() for m in absolute_markers)

    # If the clause is short enough already (< 120 chars), keep verbatim.
    if len(body) <= 120:
        return body

    # For multi-condition or absolute-prohibition clauses, keep verbatim
    # with flag to avoid condition-drop or obligation-softening errors.
    if has_multi_condition or has_absolute:
        return f"{body} [VERBATIM — summarisation would alter meaning]"

    # --- Safe to condense: apply rule-based shortening ----------------------
    summarised = body

    # Remove "Each permanent employee" / "Each employee" boilerplate
    summarised = re.sub(
        r"^Each (permanent )?employee is entitled to ",
        "Entitled to ",
        summarised,
    )

    # Remove "An employee may" → "May"
    summarised = re.sub(r"^An employee may ", "May ", summarised)

    # Remove "Employees are entitled to" → "Entitled to"
    summarised = re.sub(
        r"^Employees are entitled to ",
        "Entitled to ",
        summarised,
    )

    # "Female employees are entitled to" → "Female employees: entitled to"
    summarised = re.sub(
        r"^Female employees are entitled to ",
        "Female employees: entitled to ",
        summarised,
    )

    # "Male employees are entitled to" → "Male employees: entitled to"
    summarised = re.sub(
        r"^Male employees are entitled to ",
        "Male employees: entitled to ",
        summarised,
    )

    # "Employees must" stays "Employees must" (binding verb preserved)
    # "Employees may" stays "Employees may" (binding verb preserved)

    # If the result is still long (> 200 chars), flag as verbatim to be safe.
    if len(summarised) > 200:
        return f"{body} [VERBATIM — summarisation would alter meaning]"

    return summarised


# ---------------------------------------------------------------------------
# CLI entry point (per README.md run command)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="UC-0B — Policy Summarisation Agent"
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to the policy .txt file (e.g., ../data/policy-documents/policy_hr_leave.txt)",
    )
    parser.add_argument(
        "--output", required=True,
        help="Path to write the summary output file (e.g., summary_hr_leave.txt)",
    )
    args = parser.parse_args()

    # Step 1: retrieve_policy
    sections = retrieve_policy(args.input)

    # Step 2: summarize_policy
    summarize_policy(sections, args.output)

    print(f"Done. Summary written to {args.output}")
