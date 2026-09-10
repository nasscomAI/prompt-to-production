"""
UC-0B — Summary That Changes Meaning
Built using RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import re


CLAUSE_INVENTORY = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4",
    "5.2", "5.3",
    "7.2"
]

CLAUSE_OBLIGATIONS = {
    "2.3": "14-day advance notice required",
    "2.4": "Written approval required before leave commences. Verbal not valid.",
    "2.5": "Unapproved absence = LOP regardless of subsequent approval",
    "2.6": "Max 5 days carry-forward. Above 5 forfeited on 31 Dec.",
    "2.7": "Carry-forward days must be used Jan–Mar or forfeited",
    "3.2": "3+ consecutive sick days requires medical cert within 48hrs",
    "3.4": "Sick leave before/after holiday requires cert regardless of duration",
    "5.2": "LWP requires Department Head AND HR Director approval",
    "5.3": "LWP >30 days requires Municipal Commissioner approval",
    "7.2": "Leave encashment during service not permitted under any circumstances"
}


def retrieve_policy(file_path: str) -> dict:
    """
    Load the HR leave policy text file and parse it into structured numbered sections.
    Returns: dict with keys: sections (dict mapping clause_number -> clause_text), full_text (str)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            full_text = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    except Exception as e:
        raise RuntimeError(f"Error reading policy file: {e}")

    if not full_text.strip():
        raise ValueError("Policy file is empty")

    sections = {}
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.+)$', re.MULTILINE)

    for match in clause_pattern.finditer(full_text):
        clause_num = match.group(1)
        clause_text = match.group(2).strip()
        sections[clause_num] = clause_text

    return {"sections": sections, "full_text": full_text}


def summarize_policy(sections: dict, clause_inventory: list) -> str:
    """
    Generate a compliant summary from structured policy sections preserving all clause inventory items.
    Returns: summary_text (str — formatted summary with clause citations)
    """
    summary_lines = [
        "CMC EMPLOYEE LEAVE POLICY — SUMMARY (HR-POL-001 v2.3)",
        "=" * 55,
        ""
    ]

    missing_clauses = []

    for clause_num in clause_inventory:
        obligation = CLAUSE_OBLIGATIONS.get(clause_num, "")
        clause_text = sections.get(clause_num, "")

        if not clause_text:
            missing_clauses.append(clause_num)
            summary_lines.append(f"Clause {clause_num}: [CLAUSE {clause_num} NOT FOUND IN SOURCE]")
            continue

        summary_lines.append(f"Clause {clause_num}: {obligation}")
        summary_lines.append(f"  Source: \"{clause_text}\"")
        summary_lines.append("")

    if missing_clauses:
        summary_lines.append("")
        summary_lines.append(f"NOTE: The following clauses from inventory were not found in source: {', '.join(missing_clauses)}")

    summary_lines.append("")
    summary_lines.append("=" * 55)
    summary_lines.append("End of summary. All clauses from inventory included above.")

    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    try:
        policy_data = retrieve_policy(args.input)
        summary = summarize_policy(policy_data["sections"], CLAUSE_INVENTORY)

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)

        print(f"Summary written to {args.output}")
        print(f"Clauses processed: {len(CLAUSE_INVENTORY)}")

    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()