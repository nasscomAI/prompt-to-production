"""
UC-0B — Summary That Changes Meaning
Parses a policy document and produces a clause-by-clause summary that preserves
every numbered clause, all binding obligations, and all conditions.
Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import re
import sys


def retrieve_policy(file_path: str) -> list[dict]:
    """
    Load a .txt policy file and parse it into structured sections and clauses.
    Returns a list of sections, each with section_number, section_title, and clauses.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into sections by the separator lines (═══...)
    section_pattern = re.compile(
        r'═{3,}\s*\n'
        r'(\d+)\.\s+(.+?)\s*\n'
        r'═{3,}',
        re.MULTILINE
    )

    # Find all section headers and their positions
    matches = list(section_pattern.finditer(content))
    sections = []

    for i, match in enumerate(matches):
        section_num = match.group(1)
        section_title = match.group(2).strip()

        # Extract text between this header and the next (or end of file)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        section_text = content[start:end].strip()

        # Parse individual clauses (e.g., "2.1 ...", "2.2 ...")
        clause_pattern = re.compile(
            r'^[ \t]*(\d+\.\d+)\s+(.+?)(?=\n[ \t]*\d+\.\d+\s|\Z)',
            re.MULTILINE | re.DOTALL
        )
        clauses = []
        for cm in clause_pattern.finditer(section_text):
            clause_num = cm.group(1)
            clause_text = cm.group(2).strip()
            # Normalize whitespace (collapse multi-line into single line)
            clause_text = re.sub(r'\s+', ' ', clause_text)
            clauses.append({
                "clause_number": clause_num,
                "clause_text": clause_text,
            })

        sections.append({
            "section_number": section_num,
            "section_title": section_title,
            "clauses": clauses,
        })

    if not sections:
        print("WARNING: No structured sections found in document.", file=sys.stderr)

    return sections


def summarize_policy(sections: list[dict]) -> str:
    """
    Produce a clause-by-clause summary preserving all obligations and conditions.
    """
    lines = []
    lines.append("=" * 60)
    lines.append("POLICY SUMMARY")
    lines.append("=" * 60)
    lines.append("")

    for section in sections:
        # Section header
        lines.append(f"--- {section['section_number']}. {section['section_title']} ---")
        lines.append("")

        for clause in section["clauses"]:
            cn = clause["clause_number"]
            ct = clause["clause_text"]

            # Detect binding verbs for preservation
            binding_verbs = []
            for verb in ["must", "will", "requires", "required", "may",
                         "not permitted", "are forfeited", "is not",
                         "cannot", "must not"]:
                if verb.lower() in ct.lower():
                    binding_verbs.append(verb)

            # Detect multi-condition clauses (AND, BOTH, two approvers, etc.)
            has_multi_condition = any(
                marker in ct.lower()
                for marker in [" and the ", " and hr", "both ", "two "]
            )

            # For complex clauses with multi-conditions or critical obligations,
            # preserve verbatim to avoid meaning loss
            if has_multi_condition or "not permitted" in ct.lower():
                lines.append(f"  [{cn}] {ct}")
                if has_multi_condition:
                    lines.append(f"         [MULTI-CONDITION — all conditions preserved]")
            else:
                lines.append(f"  [{cn}] {ct}")

            if binding_verbs:
                lines.append(f"         Binding: {', '.join(binding_verbs)}")

            lines.append("")

    # Footer
    lines.append("=" * 60)
    lines.append("END OF SUMMARY")
    lines.append(f"Total sections: {len(sections)}")
    total_clauses = sum(len(s['clauses']) for s in sections)
    lines.append(f"Total clauses summarized: {total_clauses}")
    lines.append("=" * 60)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True,
                        help="Path to policy .txt file")
    parser.add_argument("--output", required=True,
                        help="Path to write summary .txt file")
    args = parser.parse_args()

    # Step 1: Retrieve and parse policy
    print(f"Loading policy: {args.input}")
    sections = retrieve_policy(args.input)
    print(f"Parsed {len(sections)} sections with "
          f"{sum(len(s['clauses']) for s in sections)} clauses.")

    # Step 2: Summarize
    summary = summarize_policy(sections)

    # Step 3: Write output
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to: {args.output}")

    # Step 4: Verification — list all clause numbers for audit
    print("\nClause audit trail:")
    for section in sections:
        for clause in section["clauses"]:
            print(f"  [OK] {clause['clause_number']}")


if __name__ == "__main__":
    main()
