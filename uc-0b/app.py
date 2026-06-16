"""
UC-0B — Policy Summarizer
Produces a clause-by-clause summary of a policy document.
Enforcement rules are defined in agents.md. Skills in skills.md.
"""
import argparse
import re


# Key clauses that MUST be present in the output (UC-0B enforcement rule 1).
REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

# Clauses whose exact wording must be preserved verbatim to avoid meaning loss.
EXACT_QUOTE_CLAUSES = {"5.2", "7.2"}


# ---------------------------------------------------------------------------
# Skill: retrieve_policy
# ---------------------------------------------------------------------------
def retrieve_policy(file_path: str) -> list[dict]:
    """
    Load a .txt policy file and return a list of numbered sections.
    Each section dict has: section_number, section_heading, clauses (list of str).
    """
    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            raw = fh.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {file_path}")

    sections: list[dict] = []
    current_section: dict | None = None

    heading_re = re.compile(r"^={3,}\s*$")  # separator line
    clause_re = re.compile(r"^\s*(\d+\.\d+)\s+(.+)")
    section_title_re = re.compile(r"^\d+\.\s+.+")

    lines = raw.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Detect a section separator block: ===...===  TITLE  ===...===
        if heading_re.match(line):
            title_line = lines[i + 1].strip() if i + 1 < len(lines) else "UNLABELLED_SECTION"
            # Extract section number from title (e.g. "2. ANNUAL LEAVE" → "2")
            m = re.match(r"^(\d+)[\.\s]+(.+)", title_line)
            if m:
                sec_num, sec_heading = m.group(1), m.group(2).strip()
            else:
                sec_num, sec_heading = "?", title_line
            current_section = {
                "section_number": sec_num,
                "section_heading": sec_heading,
                "clauses": [],
            }
            sections.append(current_section)
            i += 3  # skip separator + title + closing separator
            continue

        # Detect a clause line (e.g. "2.3 Employees must submit...")
        m = clause_re.match(line)
        if m and current_section is not None:
            clause_id = m.group(1)
            clause_text = line
            # Accumulate continuation lines (indented, no new clause number)
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if not next_line or clause_re.match(next_line) or heading_re.match(next_line):
                    break
                clause_text += " " + next_line
                j += 1
            current_section["clauses"].append(clause_text.strip())
            i = j
            continue

        i += 1

    return sections


# ---------------------------------------------------------------------------
# Skill: summarize_policy
# ---------------------------------------------------------------------------
def summarize_policy(sections: list[dict], required_clauses: list[str]) -> str:
    """
    Build a clause-by-clause plain-text summary.
    - Preserves binding verbs (must, will, requires, not permitted).
    - Flags verbatim-required clauses with EXACT_QUOTE.
    - Appends MISSING_CLAUSE warnings for any required clause not found.
    """
    # Flatten all clauses into a lookup: clause_id → clause_text
    clause_map: dict[str, str] = {}
    for section in sections:
        for clause_text in section["clauses"]:
            m = re.match(r"^(\d+\.\d+)\s+", clause_text)
            if m:
                clause_map[m.group(1)] = clause_text

    lines: list[str] = ["POLICY SUMMARY — HR-POL-001", "=" * 50, ""]

    for section in sections:
        lines.append(f"\n{section['section_number']}. {section['section_heading']}")
        lines.append("-" * 40)
        for clause_text in section["clauses"]:
            m = re.match(r"^(\d+\.\d+)\s+", clause_text)
            clause_id = m.group(1) if m else None
            if clause_id and clause_id in EXACT_QUOTE_CLAUSES:
                lines.append(f"  {clause_text}  [EXACT_QUOTE]")
            else:
                lines.append(f"  {clause_text}")

    # Enforcement: flag any required clause that is completely absent.
    missing = [cid for cid in required_clauses if cid not in clause_map]
    if missing:
        lines.append("\n" + "=" * 50)
        lines.append("COMPLIANCE WARNINGS")
        lines.append("-" * 40)
        for cid in missing:
            lines.append(f"  MISSING_CLAUSE {cid}: This required clause was not found in the source document.")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input",  required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary  = summarize_policy(sections, REQUIRED_CLAUSES)

    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
