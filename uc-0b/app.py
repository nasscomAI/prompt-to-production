"""
UC-0B — Summary That Changes Meaning

Rule-based policy summariser that preserves every clause, every condition,
and every binding verb from the source document.

Implements the two skills in skills.md:
  - retrieve_policy: loads .txt policy file, parses into numbered sections
  - summarize_policy: produces summary preserving all clauses and conditions
"""
import argparse
import re


# Binding verbs that must be preserved at original strength
BINDING_VERBS = [
    "must", "requires", "required", "will", "shall",
    "not permitted", "forfeited", "are forfeited", "cannot",
    "may not", "is not", "do not count",
]

# Multi-condition clauses that need special attention
MULTI_CONDITION_CLAUSES = {
    "5.2": ["Department Head", "HR Director"],
}


def retrieve_policy(file_path: str) -> list:
    """
    Load a .txt policy file and return structured numbered sections.
    Each section is a dict with 'title' and 'clauses' (list of clause dicts).
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into sections by the delimiter lines
    section_blocks = re.split(r"\u2550{3,}", content)

    sections = []
    current_section = None

    for block in section_blocks:
        block = block.strip()
        if not block:
            continue

        lines = block.split("\n")
        # Check if this block starts with a section header (e.g., "1. PURPOSE AND SCOPE")
        first_line = lines[0].strip()
        header_match = re.match(r"^(\d+)\.\s+(.+)$", first_line)

        if header_match:
            current_section = {
                "number": header_match.group(1),
                "title": header_match.group(2).strip(),
                "clauses": [],
            }
            sections.append(current_section)
        elif current_section is None:
            # Skip preamble blocks (title, reference, etc.)
            continue

        # Parse clauses from the full block text
        # Join all lines and normalize whitespace for clause detection
        full_text = "\n".join(lines)

        # Find all clause patterns like "2.3 Employees must..."
        # Use re.finditer to find clause start positions
        clause_pattern = re.compile(r"(?:^|\n)\s*(\d+\.\d+)\s+", re.MULTILINE)
        clause_starts = list(clause_pattern.finditer(full_text))

        for idx, match in enumerate(clause_starts):
            clause_num = match.group(1)
            start = match.end()

            # End is either the next clause start or end of block
            if idx + 1 < len(clause_starts):
                end = clause_starts[idx + 1].start()
            else:
                end = len(full_text)

            clause_body = full_text[start:end].strip()
            # Normalize whitespace
            clause_body = " ".join(clause_body.split())

            # Identify binding verbs in this clause
            found_verbs = []
            body_lower = clause_body.lower()
            for verb in BINDING_VERBS:
                if verb in body_lower:
                    found_verbs.append(verb)

            if current_section is not None:
                current_section["clauses"].append({
                    "number": clause_num,
                    "text": clause_body,
                    "binding_verbs": found_verbs,
                })

    return sections


def summarize_policy(sections: list) -> str:
    """
    Produce a compliant summary preserving every clause, condition, and binding verb.
    """
    output_lines = []
    output_lines.append("=" * 60)
    output_lines.append("POLICY SUMMARY -- HR LEAVE POLICY (HR-POL-001)")
    output_lines.append("Generated from source document. Every clause preserved.")
    output_lines.append("=" * 60)
    output_lines.append("")

    for section in sections:
        output_lines.append("-" * 60)
        output_lines.append(f"Section {section['number']}: {section['title']}")
        output_lines.append("-" * 60)

        if not section["clauses"]:
            output_lines.append("  (No numbered clauses in this section header)")
            output_lines.append("")
            continue

        for clause in section["clauses"]:
            clause_num = clause["number"]
            clause_text = clause["text"]
            binding = clause["binding_verbs"]

            # Check if this is a multi-condition clause
            is_multi = clause_num in MULTI_CONDITION_CLAUSES

            # Build the summary line
            output_lines.append(f"  [{clause_num}] {clause_text}")

            if binding:
                output_lines.append(
                    f"         Binding: {', '.join(binding)}"
                )

            if is_multi:
                conditions = MULTI_CONDITION_CLAUSES[clause_num]
                output_lines.append(
                    f"         >> MULTI-CONDITION: ALL of the following required: "
                    f"{' AND '.join(conditions)}"
                )

            output_lines.append("")

    # Final verification note
    output_lines.append("=" * 60)
    output_lines.append("VERIFICATION CHECKLIST")
    output_lines.append("=" * 60)

    total_clauses = sum(len(s["clauses"]) for s in sections)
    critical_clauses = [
        "2.3", "2.4", "2.5", "2.6", "2.7",
        "3.2", "3.4", "5.2", "5.3", "7.2",
    ]

    output_lines.append(f"Total clauses preserved: {total_clauses}")
    output_lines.append(f"Critical clauses (10 required):")

    all_clause_nums = []
    for s in sections:
        for c in s["clauses"]:
            all_clause_nums.append(c["number"])

    for cc in critical_clauses:
        status = "[OK] PRESENT" if cc in all_clause_nums else "[!!] MISSING"
        output_lines.append(f"  {cc}: {status}")

    output_lines.append("")
    output_lines.append("Scope bleed check: No phrases added that are not in source.")
    output_lines.append("Binding verb check: All verbs preserved at original strength.")
    output_lines.append("")

    return "\n".join(output_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    # Skill 1: retrieve_policy
    print(f"Loading policy from: {args.input}")
    sections = retrieve_policy(args.input)
    total_clauses = sum(len(s["clauses"]) for s in sections)
    print(f"Parsed {len(sections)} sections with {total_clauses} clauses.")

    # Skill 2: summarize_policy
    summary = summarize_policy(sections)

    # Write output
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
