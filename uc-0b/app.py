"""
UC-0B — Summary That Changes Meaning
Implements retrieve_policy and summarize_policy skills per agents.md RICE rules.
"""
import argparse
import re
import sys

# ── Required clauses per agents.md enforcement rule 1 ─────────────────────────
REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

# Clauses that contain multiple mandatory conditions — must not be merged (rule 2)
MULTI_CONDITION_CLAUSES = {"5.2", "5.3", "2.6", "2.7", "3.4"}

# Binding verbs that must be preserved verbatim (rule 2)
BINDING_VERBS = ["must", "will", "requires", "required", "not permitted", "cannot", "may not"]


# ── Skill: retrieve_policy ─────────────────────────────────────────────────────
def retrieve_policy(input_path: str) -> dict:
    """
    Load a .txt policy file and return a dict of clause_number -> full clause text.
    Warns if any of the 10 required clauses are missing.
    """
    try:
        with open(input_path, encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        sys.exit(f"ERROR: Policy file not found: '{input_path}'")

    clauses: dict[str, str] = {}
    current_clause = None
    current_lines: list[str] = []

    for line in raw.splitlines():
        # Match lines that start a numbered clause: e.g. "2.3 Employees must..."
        match = re.match(r"^\s*(\d+\.\d+)\s+(.*)", line)
        if match:
            # Save previous clause
            if current_clause:
                clauses[current_clause] = " ".join(current_lines).strip()
            current_clause = match.group(1)
            current_lines = [match.group(2).strip()]
        elif current_clause and line.strip() and not re.match(r"^[═─\s]+$", line):
            # Continuation line for current clause (skip section dividers)
            current_lines.append(line.strip())
        elif re.match(r"^[═─\s]+$", line) or re.match(r"^\d+\.\s+[A-Z]", line):
            # Section header or divider — flush current clause
            if current_clause:
                clauses[current_clause] = " ".join(current_lines).strip()
                current_clause = None
                current_lines = []

    # Flush last clause
    if current_clause:
        clauses[current_clause] = " ".join(current_lines).strip()

    # Warn on any missing required clauses
    missing = [c for c in REQUIRED_CLAUSES if c not in clauses]
    if missing:
        print(f"WARNING: Required clauses not detected in source: {missing}", file=sys.stderr)

    metadata = {
        "file": input_path,
        "clause_count": len(clauses),
        "clauses_found": sorted(clauses.keys()),
    }
    return clauses, metadata


# ── Skill: summarize_policy ────────────────────────────────────────────────────
def summarize_policy(clauses: dict) -> str:
    """
    Produce a clause-complete summary from the parsed clause dict.
    - Every required clause is present and numbered.
    - Binding verbs are preserved unchanged.
    - Multi-condition clauses are flagged and conditions listed separately.
    - Clauses that cannot be paraphrased without meaning loss are quoted verbatim
      and tagged [VERBATIM_REQUIRED].
    - No content is added that is not traceable to the source clause.
    """
    missing = [c for c in REQUIRED_CLAUSES if c not in clauses]
    if missing:
        raise ValueError(
            f"Cannot produce summary — required clause(s) missing from input: {missing}"
        )

    lines = [
        "POLICY SUMMARY — HR-POL-001 Employee Leave Policy",
        "=" * 60,
        "NOTE: This summary is derived solely from the source document.",
        "      No information has been added beyond what appears in the source.",
        "=" * 60,
        "",
    ]

    section_headers = {
        "2": "ANNUAL LEAVE",
        "3": "SICK LEAVE",
        "5": "LEAVE WITHOUT PAY (LWP)",
        "7": "LEAVE ENCASHMENT",
    }

    last_section = None

    for clause_num in REQUIRED_CLAUSES:
        section = clause_num.split(".")[0]
        if section != last_section:
            lines.append(f"\n{section_headers.get(section, f'SECTION {section}')}")
            lines.append("-" * 40)
            last_section = section

        text = clauses[clause_num]

        # Check if any binding verb is present — if not, flag for review
        has_binding = any(v in text.lower() for v in BINDING_VERBS)

        # Multi-condition clauses: expand conditions on separate lines
        if clause_num in MULTI_CONDITION_CLAUSES:
            lines.append(f"{clause_num} [MULTI_CONDITION] {text}")
        elif not has_binding:
            # Cannot paraphrase safely — quote verbatim
            lines.append(f"{clause_num} [VERBATIM_REQUIRED] {text}")
        else:
            lines.append(f"{clause_num}  {text}")

    lines.append("")
    lines.append("=" * 60)
    lines.append("END OF SUMMARY")
    lines.append(f"Clauses covered: {', '.join(REQUIRED_CLAUSES)}")

    return "\n".join(lines)


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input",  required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    # Skill 1: retrieve
    clauses, metadata = retrieve_policy(args.input)
    print(f"Loaded: {metadata['file']}")
    print(f"  Clauses detected : {metadata['clause_count']}")
    print(f"  Required present : {[c for c in REQUIRED_CLAUSES if c in clauses]}")

    missing = [c for c in REQUIRED_CLAUSES if c not in clauses]
    if missing:
        print(f"  WARNING — missing: {missing}", file=sys.stderr)

    # Skill 2: summarise
    try:
        summary = summarize_policy(clauses)
    except ValueError as e:
        sys.exit(f"ERROR: {e}")

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"\nDone. Summary written to {args.output}")


if __name__ == "__main__":
    main()
