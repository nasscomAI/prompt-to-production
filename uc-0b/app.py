"""
UC-0B app.py — Policy summarization agent.
Implements retrieve_policy and summarize_policy skills per skills.md and agents.md.
"""
import argparse
import re
import sys
from pathlib import Path

# Clause inventory from README.md — binding verbs and required clause IDs
CLAUSE_INVENTORY = {
    "2.3": "must",
    "2.4": "must",
    "2.5": "will",
    "2.6": "may / are forfeited",
    "2.7": "must",
    "3.2": "requires",
    "3.4": "requires",
    "5.2": "requires",
    "5.3": "requires",
    "7.2": "not permitted",
}
REQUIRED_CLAUSES = list(CLAUSE_INVENTORY.keys())

SECTION_HEADINGS = {
    "2.3": "ANNUAL LEAVE",
    "2.4": "ANNUAL LEAVE",
    "2.5": "ANNUAL LEAVE",
    "2.6": "ANNUAL LEAVE",
    "2.7": "ANNUAL LEAVE",
    "3.2": "SICK LEAVE",
    "3.4": "SICK LEAVE",
    "5.2": "LEAVE WITHOUT PAY (LWP)",
    "5.3": "LEAVE WITHOUT PAY (LWP)",
    "7.2": "LEAVE ENCASHMENT",
}


def retrieve_policy(filepath):
    """
    Skill: retrieve_policy
    Loads a .txt policy file and returns its content as structured numbered sections.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {filepath}")
    if path.suffix.lower() != ".txt":
        raise ValueError(f"Expected a .txt file, got: {path.suffix}")

    text = path.read_text(encoding="utf-8")
    if not text.strip():
        print("Warning: Policy file is empty.", file=sys.stderr)
        return {}

    sections = {}
    lines = text.splitlines()
    current_label = None
    current_lines = []

    section_header_re = re.compile(r"^\d+\.\s+\w")
    clause_header_re = re.compile(r"^(\d+\.\d+)\s")
    separator_re = re.compile(r"^═+$")

    for line in lines:
        stripped = line.strip()
        if not stripped or separator_re.match(stripped) or section_header_re.match(stripped):
            if section_header_re.match(stripped) and current_label:
                sections[current_label] = " ".join(current_lines)
                current_label = None
                current_lines = []
            continue

        m = clause_header_re.match(stripped)
        if m:
            if current_label:
                sections[current_label] = " ".join(current_lines)
            current_label = m.group(1)
            current_lines = [stripped]
        elif current_label:
            current_lines.append(stripped)

    if current_label:
        sections[current_label] = " ".join(current_lines)

    return sections


def summarize_policy(sections):
    """
    Skill: summarize_policy
    Takes structured policy sections and produces a compliant summary
    referencing every clause in the inventory, preserving all conditions
    and binding verbs.
    """
    missing = [c for c in REQUIRED_CLAUSES if c not in sections]
    if missing:
        return (
            "ERROR: Cannot produce compliant summary — "
            f"the following required clauses were not found in the source: {', '.join(missing)}"
        )

    parts = [
        "SUMMARY OF LEAVE POLICY (HR-POL-001)",
        "This summary covers every mandatory clause from the policy. "
        "Each clause preserves its full conditions and binding verb. "
        "No information has been added beyond what the source document states.",
        "",
    ]

    current_section = None
    for clause_id in REQUIRED_CLAUSES:
        section_label = SECTION_HEADINGS[clause_id]
        if section_label != current_section:
            current_section = section_label
            parts.append(f"--- {current_section} ---")

        binding_verb = CLAUSE_INVENTORY[clause_id]
        clause_text = sections[clause_id]
        parts.append(f"Clause {clause_id} ({binding_verb}): {clause_text}")

    parts.extend([
        "",
        "--- END OF COMPLIANT SUMMARY ---",
        "All 10 mandatory clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) "
        "are present with their complete conditions.",
    ])

    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Policy summarization agent (UC-0B)")
    parser.add_argument("--input", required=True, help="Path to the .txt policy document")
    parser.add_argument("--output", required=True, help="Path to write the summary output")
    args = parser.parse_args()

    try:
        sections = retrieve_policy(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    summary = summarize_policy(sections)

    output_path = Path(args.output)
    output_path.write_text(summary, encoding="utf-8")
    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()
