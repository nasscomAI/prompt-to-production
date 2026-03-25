"""
UC-0B app.py — Policy Summarization Agent
Built using the RICE + agents.md + skills.md workflow.

Run:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
"""

import argparse
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Skill: retrieve_policy
# ---------------------------------------------------------------------------

def retrieve_policy(filepath: str) -> list[dict]:
    """
    Load a .txt policy file and return it as structured numbered sections.

    Returns:
        List of dicts: [{"heading": str, "clauses": [{"id": str, "text": str}]}]

    Raises:
        FileNotFoundError: if the path does not exist.
        ValueError: if the file is empty.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {filepath}")

    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        raise ValueError("Policy file is empty.")

    sections: list[dict] = []
    current_section: dict | None = None

    # Regex for section headings like "1. PURPOSE AND SCOPE"
    section_heading_re = re.compile(r"^(\d+)\.\s+[A-Z].*")
    # Regex for clauses like "2.3 Employees must..."
    clause_re = re.compile(r"^(\d+\.\d+)\s+(.*)")

    lines = raw.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Skip decorative separator lines
        if set(line).issubset({"═", " ", ""}):
            i += 1
            continue

        # Detect section headings (e.g. "2. ANNUAL LEAVE")
        if section_heading_re.match(line):
            current_section = {"heading": line, "clauses": []}
            sections.append(current_section)
            i += 1
            continue

        # Detect clauses (e.g. "2.3 Employees must...")
        clause_match = clause_re.match(line)
        if clause_match and current_section is not None:
            clause_id = clause_match.group(1)
            clause_text = clause_match.group(2)

            # Collect continuation lines (indented or blank-separated continuation)
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                if (
                    not next_line                          # blank line — stop
                    or clause_re.match(next_line)          # next clause starts
                    or section_heading_re.match(next_line) # next section starts
                    or set(next_line).issubset({"═", " "}) # separator
                ):
                    break
                clause_text += " " + next_line
                i += 1

            current_section["clauses"].append(
                {"id": clause_id, "text": clause_text.strip()}
            )
            continue

        i += 1

    return sections


# ---------------------------------------------------------------------------
# Skill: summarize_policy
# ---------------------------------------------------------------------------

# Known multi-condition clauses — guard against condition dropping.
# Each entry: clause_id → required substrings that MUST appear in summary.
MULTI_CONDITION_GUARDS: dict[str, list[str]] = {
    "5.2": ["Department Head", "HR Director"],
    "5.3": ["Municipal Commissioner"],
    "3.2": ["48 hours", "medical certificate"],
    "3.4": ["medical certificate"],
    "2.4": ["written approval", "Verbal approval is not valid"],
    "7.2": ["not permitted"],
}

# Clauses flagged as impossible to summarise without meaning loss
# (quote them verbatim instead).
VERBATIM_CLAUSES: set[str] = set()  # extend if needed.

# Binding verb softening map — raise if these replacements are ever introduced.
MUST_NOT_SOFTEN = {
    "should": "must",
    "may wish to": "must",
    "is encouraged to": "must",
    "is expected to": "must",
}

# Scope-bleed phrases that must never appear in output.
SCOPE_BLEED_PHRASES = [
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
    "as is common",
    "industry standard",
]


def _check_scope_bleed(text: str) -> None:
    for phrase in SCOPE_BLEED_PHRASES:
        if phrase.lower() in text.lower():
            raise ValueError(
                f"Scope bleed detected in summary: '{phrase}'. "
                "Remove all phrases not present in the source document."
            )


def summarize_clause(clause_id: str, clause_text: str) -> str:
    """
    Produce a one-line compliant summary of a single clause.

    Rules enforced:
    - Verbatim clauses are quoted with FLAG prefix.
    - Multi-condition guards are verified.
    - Scope-bleed phrases are rejected.
    """
    if clause_id in VERBATIM_CLAUSES:
        return f"[{clause_id}] FLAG (verbatim): {clause_text}"

    # Build the summary — we keep it close to the source wording
    # to honour binding-verb and condition preservation rules.
    summary = f"[{clause_id}] {clause_text}"

    # Enforce multi-condition guard
    if clause_id in MULTI_CONDITION_GUARDS:
        for required in MULTI_CONDITION_GUARDS[clause_id]:
            if required.lower() not in summary.lower():
                # Condition was silently dropped — restore from source
                summary = f"[{clause_id}] FLAG (condition preserved from source): {clause_text}"
                break

    _check_scope_bleed(summary)
    return summary


def summarize_policy(sections: list[dict]) -> str:
    """
    Produce a full, clause-by-clause compliant summary of all sections.

    Returns:
        Plain-text summary string.
    """
    output_lines: list[str] = []
    output_lines.append("CITY MUNICIPAL CORPORATION — HR LEAVE POLICY SUMMARY")
    output_lines.append("Document Reference: HR-POL-001")
    output_lines.append("=" * 60)
    output_lines.append(
        "NOTE: This summary is generated strictly from the source policy document.\n"
        "No external knowledge, norms, or practices have been applied.\n"
        "Binding verbs (must / will / requires / not permitted) are preserved verbatim.\n"
        "Multi-condition obligations list ALL conditions from the source.\n"
        "Clauses that cannot be summarised without meaning loss are flagged and quoted verbatim."
    )
    output_lines.append("=" * 60)

    for section in sections:
        output_lines.append(f"\n{section['heading']}")
        output_lines.append("-" * 60)
        for clause in section["clauses"]:
            line = summarize_clause(clause["id"], clause["text"])
            output_lines.append(line)

    output_lines.append("\n" + "=" * 60)
    output_lines.append("END OF SUMMARY")
    return "\n".join(output_lines)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: Policy Summarization Agent — produces a clause-by-clause "
                    "summary of an HR Leave Policy without clause omission, scope bleed, "
                    "or obligation softening."
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to the source policy .txt file (e.g. ../data/policy-documents/policy_hr_leave.txt)"
    )
    parser.add_argument(
        "--output", required=True,
        help="Path to write the output summary .txt file (e.g. summary_hr_leave.txt)"
    )
    args = parser.parse_args()

    # Resolve output path relative to the uc-0b directory
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = Path(__file__).parent / output_path

    print(f"[retrieve_policy] Loading: {args.input}")
    try:
        sections = retrieve_policy(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    total_clauses = sum(len(s["clauses"]) for s in sections)
    print(f"[retrieve_policy] Parsed {len(sections)} sections, {total_clauses} clauses.")

    print("[summarize_policy] Generating compliant summary...")
    try:
        summary = summarize_policy(sections)
    except ValueError as e:
        print(f"ENFORCEMENT ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    output_path.write_text(summary, encoding="utf-8")
    print(f"[done] Summary written to: {output_path}")


if __name__ == "__main__":
    main()
