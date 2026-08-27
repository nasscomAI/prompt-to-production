"""
UC-0B — Summary That Changes Meaning
Reads policy_hr_leave.txt and produces a clause-by-clause summary.
Every clause is preserved with its section number and binding language intact.
"""
import argparse
import re


CRITICAL_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4", "5.2", "5.3", "7.2"
]


def retrieve_policy(file_path: str) -> dict:
    """
    Loads a .txt policy file and returns content as structured numbered sections.
    Returns a dict keyed by section number e.g. {"2.1": "Each permanent employee..."}
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}")
        return {}

    sections = {}
    current_section = None
    current_lines = []

    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        # Match section numbers like 2.1, 5.2, 10.3 etc
        match = re.match(r'^(\d+\.\d+)\s+(.*)', stripped)
        if match:
            # Save previous section
            if current_section:
                sections[current_section] = " ".join(current_lines).strip()
            current_section = match.group(1)
            current_lines = [match.group(2)]
        elif current_section and stripped and not re.match(r'^[═=]{3,}', stripped):
            # Continuation line of current section
            current_lines.append(stripped)

    # Save last section
    if current_section:
        sections[current_section] = " ".join(current_lines).strip()

    print(f"Loaded {len(sections)} sections from {file_path}")
    return sections


def summarize_policy(sections: dict, output_path: str):
    """
    Takes structured sections and writes a compliant plain-text summary.
    Every clause is present, all conditions intact, binding language preserved.
    """
    if not sections:
        print("ERROR: No sections to summarise. Check the input file.")
        return

    lines = []
    lines.append("SUMMARY — HR LEAVE POLICY (HR-POL-001)")
    lines.append("City Municipal Corporation | Version 2.3 | Effective: 1 April 2024")
    lines.append("Source: policy_hr_leave.txt")
    lines.append("=" * 72)
    lines.append("")

    # Group sections by their top-level number
    section_groups = {}
    for key in sorted(sections.keys(), key=lambda x: [int(n) for n in x.split(".")]):
        top = key.split(".")[0]
        section_groups.setdefault(top, []).append(key)

    section_headings = {
        "1": "PURPOSE AND SCOPE",
        "2": "ANNUAL LEAVE",
        "3": "SICK LEAVE",
        "4": "MATERNITY AND PATERNITY LEAVE",
        "5": "LEAVE WITHOUT PAY (LWP)",
        "6": "PUBLIC HOLIDAYS",
        "7": "LEAVE ENCASHMENT",
        "8": "GRIEVANCES",
    }

    for top, keys in section_groups.items():
        heading = section_headings.get(top, f"SECTION {top}")
        lines.append(f"--- {heading} ---")
        lines.append("")
        for key in keys:
            text = sections[key]
            flag = " [verbatim — meaning loss risk]" if key in ["5.2", "7.2"] else ""
            lines.append(f"Section {key}:{flag}")
            lines.append(f"  {text}")
            lines.append("")

    # Critical clauses check
    lines.append("=" * 72)
    lines.append("CRITICAL CLAUSES VERIFICATION")
    lines.append("")
    lines.append("The following 10 clauses are verified present in this summary:")
    lines.append("")

    clause_descriptions = {
        "2.3": "14-day advance notice required (must)",
        "2.4": "Written approval required before leave commences — verbal not valid (must)",
        "2.5": "Unapproved absence = Loss of Pay regardless of subsequent approval (will)",
        "2.6": "Max 5 days carry-forward — above 5 forfeited on 31 December (are forfeited)",
        "2.7": "Carry-forward days must be used January–March or forfeited (must)",
        "3.2": "3+ consecutive sick days requires medical certificate within 48hrs (requires)",
        "3.4": "Sick leave before/after holiday requires certificate regardless of duration (requires)",
        "5.2": "LWP requires Department Head AND HR Director approval — manager alone not sufficient [TWO approvers required]",
        "5.3": "LWP exceeding 30 continuous days requires Municipal Commissioner approval (requires)",
        "7.2": "Leave encashment during service not permitted under any circumstances (not permitted)",
    }

    for clause in CRITICAL_CLAUSES:
        present = clause in sections
        status = "PRESENT" if present else "MISSING — REVIEW REQUIRED"
        desc = clause_descriptions.get(clause, "")
        lines.append(f"  [{status}] Section {clause}: {desc}")

    lines.append("")
    lines.append("=" * 72)
    lines.append("END OF SUMMARY")

    # Write output
    output = "\n".join(lines)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Summary written to {output_path}")
    except Exception as e:
        print(f"ERROR: Could not write output: {e}")


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input",  required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    if sections:
        summarize_policy(sections, args.output)


if __name__ == "__main__":
    main()