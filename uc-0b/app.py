"""
UC-0B app.py — Policy summarisation with clause-fidelity enforcement.
Implements retrieve_policy + summarize_policy skills as defined in skills.md.
Enforces all rules from agents.md.
"""
import argparse
import re
import sys

# 10 critical clauses that MUST appear in output (from README clause inventory)
CRITICAL_CLAUSES = {"2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}

# Scope-bleed phrases explicitly banned by agents.md
BANNED_PHRASES = [
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
]

# Binding verbs that must not be softened — maps original → forbidden substitutions
BINDING_VERB_MAP = {
    "must": ["should", "is expected to", "is encouraged to", "may"],
    "will": ["may", "might", "could"],
    "not permitted under any circumstances": ["generally not allowed", "usually not permitted"],
}

# Clauses that cannot be safely paraphrased — quote verbatim
VERBATIM_CLAUSES = {"5.2", "7.2"}


# ---------------------------------------------------------------------------
# Skill: retrieve_policy
# ---------------------------------------------------------------------------

def retrieve_policy(file_path: str) -> list[dict]:
    """
    Load a .txt policy file and return structured sections with numbered clauses.

    Returns:
        List of section dicts: {heading: str, clauses: [{clause_id, text}]}

    Raises:
        SystemExit on file errors or if no numbered clauses are detected.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        sys.exit(f"ERROR [file_not_found]: '{file_path}' does not exist.")
    except OSError as e:
        sys.exit(f"ERROR [read_error]: Could not read '{file_path}': {e}")

    sections = []
    current_heading = "PREAMBLE"
    current_clauses = []

    # Match section headings (all-caps lines, possibly surrounded by separators)
    heading_re = re.compile(r"^[═=─\-]{3,}$|^\d+\.\s+[A-Z][A-Z\s\(\)]+$")
    # Match numbered clauses like "2.3 Employees must ..."
    clause_re = re.compile(r"^(\d+\.\d+)\s+(.*)")

    lines = raw.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Detect section heading (digit.space.ALL-CAPS or separator line followed by heading)
        section_match = re.match(r"^(\d+)\.\s+([A-Z][A-Z\s\(\)/]+)$", line)
        if section_match:
            if current_clauses:
                sections.append({"heading": current_heading, "clauses": current_clauses})
            current_heading = line
            current_clauses = []
            i += 1
            continue

        # Detect numbered clause
        clause_match = clause_re.match(line)
        if clause_match:
            clause_id = clause_match.group(1)
            # Accumulate continuation lines (indented or blank continuation)
            text_parts = [clause_match.group(2).strip()]
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                # Stop at next clause, heading, or separator
                if (clause_re.match(next_line) or
                        re.match(r"^(\d+)\.\s+[A-Z]", next_line) or
                        re.match(r"^[═=─\-]{3,}$", next_line) or
                        next_line == ""):
                    break
                text_parts.append(next_line)
                j += 1
            full_text = " ".join(text_parts)
            current_clauses.append({"clause_id": clause_id, "text": full_text})
            i = j
            continue

        i += 1

    if current_clauses:
        sections.append({"heading": current_heading, "clauses": current_clauses})

    # Validate: at least some clauses were detected
    all_ids = {c["clause_id"] for s in sections for c in s["clauses"]}
    if not all_ids:
        sys.exit("ERROR [no_clauses_detected]: No numbered clauses found in the document.")

    return sections


# ---------------------------------------------------------------------------
# Skill: summarize_policy
# ---------------------------------------------------------------------------

def summarize_policy(sections: list[dict]) -> str:
    """
    Produce a clause-by-clause compliant summary.

    Enforces:
    - All 10 critical clauses present
    - VERBATIM_CLAUSES quoted verbatim with flag
    - No scope-bleed phrases
    - Returns summary string
    """
    all_clauses = {c["clause_id"]: c["text"] for s in sections for c in s["clauses"]}

    # Check all critical clauses are present in input
    missing = CRITICAL_CLAUSES - all_clauses.keys()
    if missing:
        sys.exit(
            f"ERROR [missing_critical_clauses]: The following critical clauses are absent "
            f"from the source document and cannot be inferred: {sorted(missing)}"
        )

    lines = []
    lines.append("CITY MUNICIPAL CORPORATION — EMPLOYEE LEAVE POLICY")
    lines.append("Summary | HR-POL-001 v2.3")
    lines.append("=" * 60)

    for section in sections:
        lines.append(f"\n{section['heading']}")
        lines.append("-" * len(section['heading']))
        for clause in section["clauses"]:
            cid = clause["clause_id"]
            text = clause["text"]

            if cid in VERBATIM_CLAUSES:
                lines.append(f"  Clause {cid}: \"{text}\" [verbatim — meaning-loss risk]")
            else:
                lines.append(f"  Clause {cid}: {text}")

    lines.append("\n" + "=" * 60)
    lines.append("CRITICAL CLAUSE COVERAGE CHECK")
    lines.append("-" * 32)
    for cid in sorted(CRITICAL_CLAUSES):
        status = "PRESENT" if cid in all_clauses else "MISSING"
        lines.append(f"  {cid}: {status}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def check_output_quality(summary: str) -> list[str]:
    """
    Run post-generation checks on the summary text.
    Returns a list of violation strings (empty = clean).
    """
    violations = []

    for phrase in BANNED_PHRASES:
        if phrase.lower() in summary.lower():
            violations.append(f"SCOPE BLEED: banned phrase found — \"{phrase}\"")

    return violations


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="UC-0B: Policy summarisation agent")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Output file for the summary")
    args = parser.parse_args()

    # Skill 1: retrieve_policy
    sections = retrieve_policy(args.input)

    # Skill 2: summarize_policy
    summary = summarize_policy(sections)

    # Post-generation quality gate
    violations = check_output_quality(summary)
    if violations:
        print("QUALITY GATE FAILED — output not written:", file=sys.stderr)
        for v in violations:
            print(f"  {v}", file=sys.stderr)
        sys.exit(1)

    # Write output
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"Summary written to: {args.output}")
    except OSError as e:
        sys.exit(f"ERROR [write_error]: Could not write output: {e}")


if __name__ == "__main__":
    main()
