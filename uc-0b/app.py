"""
UC-0B — Policy Compliance Summarization
Reads a numbered HR policy document, extracts required clauses,
and writes a clause-preserving summary to an output file.
"""
import argparse
import re

# Clauses that MUST appear in the summary (from agents.md enforcement)
REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

# Clauses where multi-condition obligations must be preserved verbatim
# (summarization risks dropping a condition)
VERBATIM_CLAUSES = {"2.4", "2.5", "5.2", "5.3", "7.2", "3.4"}


# ---------------------------------------------------------------------------
# Skill: retrieve_policy
# ---------------------------------------------------------------------------

def retrieve_policy(path: str) -> dict[str, str]:
    """
    Load the policy document and extract all numbered clauses.
    Returns a dict mapping clause number (e.g. "2.3") to its full text.
    Raises SystemExit on file read / parse failure.
    """
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as exc:
        raise SystemExit(f"Error: cannot read policy file '{path}': {exc}")

    clauses: dict[str, str] = {}
    current_key: str | None = None
    current_lines: list[str] = []

    clause_start = re.compile(r"^(\d+\.\d+)\s+(.*)")

    for line in lines:
        match = clause_start.match(line)
        if match:
            # Save previous clause
            if current_key:
                clauses[current_key] = " ".join(current_lines).strip()
            current_key = match.group(1)
            current_lines = [match.group(2).strip()]
        elif current_key and line.startswith((" ", "\t")) and line.strip():
            # Continuation line: indented text belonging to the current clause
            current_lines.append(line.strip())
        elif line.startswith("═") or (line.strip() and not line.startswith((" ", "\t"))):
            # Section divider or a non-indented non-clause line — close current clause
            if current_key:
                clauses[current_key] = " ".join(current_lines).strip()
                current_key = None
                current_lines = []

    # Flush last clause
    if current_key:
        clauses[current_key] = " ".join(current_lines).strip()

    if not clauses:
        raise SystemExit("Error: no numbered clauses found in the policy document.")

    return clauses


# ---------------------------------------------------------------------------
# Skill: summarize_policy
# ---------------------------------------------------------------------------

# Human-readable section titles for grouping output
SECTION_TITLES = {
    "2": "ANNUAL LEAVE",
    "3": "SICK LEAVE",
    "5": "LEAVE WITHOUT PAY (LWP)",
    "7": "LEAVE ENCASHMENT",
}

def summarize_policy(clauses: dict[str, str]) -> str:
    """
    Generate a clause-preserving summary for all REQUIRED_CLAUSES.
    Multi-condition clauses are quoted VERBATIM.
    Returns the summary as a string.
    """
    missing = [c for c in REQUIRED_CLAUSES if c not in clauses]
    if missing:
        raise SystemExit(
            f"Error: the following required clauses were not found in the document: "
            f"{', '.join(missing)}"
        )

    lines: list[str] = []
    lines.append("CITY MUNICIPAL CORPORATION — HR LEAVE POLICY")
    lines.append("CLAUSE-PRESERVING SUMMARY (HR-POL-001 v2.3)")
    lines.append("=" * 60)
    lines.append(
        "Scope: This summary covers the required enforcement clauses only.\n"
        "Source: policy_hr_leave.txt — no external information has been added."
    )
    lines.append("=" * 60)

    current_section: str | None = None

    for clause_num in REQUIRED_CLAUSES:
        section = clause_num.split(".")[0]
        if section != current_section:
            current_section = section
            title = SECTION_TITLES.get(section, f"SECTION {section}")
            lines.append(f"\n{title}\n" + "-" * len(title))

        text = clauses[clause_num]

        if clause_num in VERBATIM_CLAUSES:
            lines.append(f"\nClause {clause_num} [VERBATIM]:")
            lines.append(f'  "{text}"')
        else:
            lines.append(f"\nClause {clause_num}:")
            lines.append(f"  {text}")

    lines.append("\n" + "=" * 60)
    lines.append("END OF SUMMARY")
    lines.append(
        f"Required clauses covered: {', '.join(REQUIRED_CLAUSES)}"
    )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Compliance Summarizer")
    parser.add_argument("--input",  required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary + "\n")
    except OSError as exc:
        raise SystemExit(f"Error: cannot write output file '{args.output}': {exc}")

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
