"""
UC-0B — Summary That Changes Meaning
Policy summariser that preserves all clause obligations.
"""
import argparse
import re


POLICY_CLAUSES = {
    "2.3": "14-day advance notice required",
    "2.4": "Written approval required before leave commences",
    "2.5": "Unapproved absence = LOP regardless of subsequent approval",
    "2.6": "Max 5 days carry-forward; above 5 forfeited on 31 Dec",
    "2.7": "Carry-forward days must be used Jan–Mar or forfeited",
    "3.2": "3+ consecutive sick days requires medical cert within 48hrs",
    "3.4": "Sick leave before/after holiday requires cert regardless of duration",
    "5.2": "LWP requires Department Head AND HR Director approval",
    "5.3": "LWP >30 days requires Municipal Commissioner approval",
    "7.2": "Leave encashment during service not permitted",
}


def retrieve_policy(path: str) -> dict:
    """Load .txt policy file, return structured numbered sections."""
    sections = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            current_section = None
            current_text = []
            for line in content.split("\n"):
                match = re.match(r"^\s*(\d+\.\d+)\s", line)
                if match:
                    if current_section:
                        sections[current_section] = "\n".join(current_text).strip()
                    current_section = match.group(1)
                    current_text = [line.strip()]
                elif current_section:
                    current_text.append(line.strip())
            if current_section:
                sections[current_section] = "\n".join(current_text).strip()
    except Exception as e:
        print(f"Error reading policy file: {e}")
    return sections


def summarize_policy(sections: dict) -> str:
    """Produce compliant summary preserving all clause conditions."""
    summary_parts = []
    for clause_num in sorted(sections.keys()):
        if clause_num in POLICY_CLAUSES:
            summary_parts.append(f"Clause {clause_num}: {sections[clause_num]}")
    return "\n\n".join(summary_parts)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
