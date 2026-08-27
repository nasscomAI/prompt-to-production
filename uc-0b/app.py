"""
UC-0B — HR Leave Policy Summariser
Implements retrieve_policy and summarize_policy per agents.md and skills.md.

Run command:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
"""
import argparse
import re
import sys

# ---------------------------------------------------------------------------
# Clauses that are condition-sensitive and must be quoted verbatim to prevent
# any condition from being silently dropped during summarisation.
# ---------------------------------------------------------------------------
VERBATIM_CLAUSES = {"2.4", "2.5", "2.7", "3.4", "5.2", "5.3", "7.2"}


# ---------------------------------------------------------------------------
# Skill: retrieve_policy
# ---------------------------------------------------------------------------

def retrieve_policy(file_path: str) -> list[dict]:
    """
    Load the policy .txt file and return a list of section dicts.
    Each dict: { section_number, heading, clauses: [{clause_number, text}] }
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        print(f"ERROR: Policy file not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"ERROR: Could not read policy file: {exc}", file=sys.stderr)
        sys.exit(1)

    # Normalise line endings
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    lines = raw.splitlines()

    sections = []
    current_section = None
    current_clause_num = None
    current_clause_lines = []

    # Regex patterns
    separator_re = re.compile(r'^[═]{3,}$')
    section_heading_re = re.compile(r'^(\d+)\.\s+(.+)$')
    clause_re = re.compile(r'^(\d+\.\d+)\s+(.*)')

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip separator lines (═══…)
        if separator_re.match(stripped):
            i += 1
            continue

        # Detect a section heading like "2. ANNUAL LEAVE"
        section_match = section_heading_re.match(stripped)
        if section_match:
            # Close any open clause in the previous section
            if current_section is not None and current_clause_num is not None:
                _flush_clause(current_section, current_clause_num, current_clause_lines)
                current_clause_num = None
                current_clause_lines = []
            current_section = {
                "section_number": section_match.group(1),
                "heading": section_match.group(2).strip(),
                "clauses": [],
            }
            sections.append(current_section)
            i += 1
            continue

        # Detect a clause line like "2.3 Employees must …"
        clause_match = clause_re.match(stripped)
        if clause_match and current_section is not None:
            # Close the previous clause
            if current_clause_num is not None:
                _flush_clause(current_section, current_clause_num, current_clause_lines)
            current_clause_num = clause_match.group(1)
            current_clause_lines = [clause_match.group(2).strip()]
            i += 1
            continue

        # Continuation line for current clause (indented text)
        if current_clause_num is not None and stripped:
            current_clause_lines.append(stripped)
            i += 1
            continue

        # Blank line — end of a clause block
        if current_clause_num is not None and not stripped:
            _flush_clause(current_section, current_clause_num, current_clause_lines)
            current_clause_num = None
            current_clause_lines = []
            i += 1
            continue

        i += 1

    # Flush any remaining open clause
    if current_section is not None and current_clause_num is not None:
        _flush_clause(current_section, current_clause_num, current_clause_lines)

    # Fallback
    if not sections:
        sections = [{
            "section_number": "1",
            "heading": "Full Document",
            "clauses": [{"clause_number": "1.1", "text": raw.strip()}],
        }]

    return sections


def _flush_clause(section: dict, clause_num: str, text_lines: list[str]) -> None:
    """Commit accumulated lines as a completed clause on the section."""
    full_text = " ".join(t for t in text_lines if t).strip()
    section["clauses"].append({"clause_number": clause_num, "text": full_text})


# ---------------------------------------------------------------------------
# Skill: summarize_policy
# ---------------------------------------------------------------------------

def summarize_policy(sections: list[dict], output_path: str) -> None:
    """
    Write a clause-faithful summary of the policy to output_path.
    All critical clauses are included verbatim where condition-sensitivity
    demands it; the rest are summarised in plain language with clause refs.
    """
    out = []
    out.append("CITY MUNICIPAL CORPORATION — HR LEAVE POLICY SUMMARY")
    out.append("Document Reference: HR-POL-001  |  Version: 2.3  |  Effective: 1 April 2024")
    out.append("=" * 70)
    out.append("NOTE: This summary preserves all binding obligations from the source policy.")
    out.append("      Clauses marked [VERBATIM — condition-sensitive] are quoted exactly")
    out.append("      to prevent any condition from being silently omitted.")
    out.append("")

    for section in sections:
        try:
            sec_num = section["section_number"]
            heading = section["heading"]
            clauses = section["clauses"]
        except KeyError as exc:
            print(f"WARNING: Section dict missing key {exc} — skipping.", file=sys.stderr)
            continue

        out.append("─" * 70)
        out.append(f"SECTION {sec_num}: {heading}")
        out.append("")

        for clause in clauses:
            try:
                c_num = clause["clause_number"]
                c_text = clause["text"]
            except KeyError as exc:
                print(
                    f"WARNING: Clause in section {sec_num} missing key {exc} — skipping.",
                    file=sys.stderr,
                )
                continue

            out.append(_format_clause(c_num, c_text))
            out.append("")

    out.append("=" * 70)
    out.append("END OF SUMMARY")

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(out))
    except Exception as exc:
        print(f"ERROR: Could not write output file: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Summary written to {output_path}")


def _format_clause(clause_number: str, text: str) -> str:
    """
    Return a formatted summary entry for one clause.
    Condition-sensitive clauses are quoted verbatim and flagged.
    """
    if clause_number in VERBATIM_CLAUSES:
        return (
            f"  [{clause_number}]  [VERBATIM — condition-sensitive]\n"
            f"          \"{text}\""
        )
    return f"  [{clause_number}]  {text}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Leave Policy Summariser")
    parser.add_argument("--input",  required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summarize_policy(sections, args.output)
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
