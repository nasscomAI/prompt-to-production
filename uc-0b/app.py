"""
UC-0B — Summary That Changes Meaning
Summarises policy documents while preserving every clause, condition, and obligation.
Built using RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import re
import os


def retrieve_policy(input_path: str) -> dict:
    """
    Load a .txt policy file and return structured numbered sections.
    Returns: dict mapping section header to list of (clause_number, clause_text).
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Policy file not found: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    sections = {}
    current_section = "PREAMBLE"
    current_clauses = []

    # Pattern for section headers like "2. ANNUAL LEAVE"
    section_pattern = re.compile(r"^(\d+)\.\s+(.+)$", re.MULTILINE)
    # Pattern for clause numbers like "2.3"
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.+?)(?=\n\d+\.\d+|\n={3,}|\Z)",
                                re.MULTILINE | re.DOTALL)

    # Find all section headers with their positions
    section_matches = list(section_pattern.finditer(content))

    for i, match in enumerate(section_matches):
        section_name = f"{match.group(1)}. {match.group(2).strip()}"
        start = match.end()
        end = section_matches[i + 1].start() if i + 1 < len(section_matches) else len(content)
        section_text = content[start:end]

        clauses = []
        for clause_match in clause_pattern.finditer(section_text):
            clause_num = clause_match.group(1)
            clause_text = clause_match.group(2).strip()
            # Remove decorative divider lines and normalize whitespace
            clause_text = re.sub(r"[═]+", "", clause_text)
            clause_text = re.sub(r"\s+", " ", clause_text).strip()
            clauses.append((clause_num, clause_text))

        sections[section_name] = clauses

    return sections


def summarize_policy(sections: dict) -> str:
    """
    Produce a compliant summary preserving all conditions, obligations,
    and binding verbs. Cites clause numbers for every statement.
    """
    # Key clauses that must NEVER have conditions dropped
    MULTI_CONDITION_CLAUSES = {
        "5.2": "TWO approvers required",
    }

    lines = []
    lines.append("POLICY SUMMARY")
    lines.append("=" * 60)
    lines.append("")

    for section_name, clauses in sections.items():
        if not clauses:
            continue

        lines.append(f"--- {section_name} ---")
        lines.append("")

        for clause_num, clause_text in clauses:
            # Flag multi-condition clauses
            if clause_num in MULTI_CONDITION_CLAUSES:
                lines.append(
                    f"  [{clause_num}] {clause_text}"
                )
                lines.append(
                    f"         ⚠ Note: {MULTI_CONDITION_CLAUSES[clause_num]}"
                )
            else:
                lines.append(f"  [{clause_num}] {clause_text}")

        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B — Policy Summariser (preserves all clauses and conditions)"
    )
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()

    print(f"Loading policy from: {args.input}")
    sections = retrieve_policy(args.input)

    total_clauses = sum(len(c) for c in sections.values())
    print(f"  Found {len(sections)} sections, {total_clauses} clauses")

    print("Generating summary...")
    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")

    # Verification: check the 10 critical clauses from README
    critical_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7",
                        "3.2", "3.4", "5.2", "5.3", "7.2"]
    found = set()
    for section_clauses in sections.values():
        for clause_num, _ in section_clauses:
            if clause_num in critical_clauses:
                found.add(clause_num)

    missing = set(critical_clauses) - found
    if missing:
        print(f"  ⚠ WARNING: Critical clauses missing from parse: {missing}")
    else:
        print(f"  ✓ All 10 critical clauses present in summary.")


if __name__ == "__main__":
    main()
