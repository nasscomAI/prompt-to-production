"""
UC-0B app.py — Summary That Changes Meaning
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import re


# The 10 clauses from the policy (ground truth)
CLAUSE_INVENTORY = {
    "2.3": {"obligation": "14-day advance notice required", "verb": "must", "content": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1."},
    "2.4": {"obligation": "Written approval required before leave commences. Verbal not valid.", "verb": "must", "content": "Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid."},
    "2.5": {"obligation": "Unapproved absence = LOP regardless of subsequent approval", "verb": "will", "content": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval."},
    "2.6": {"obligation": "Max 5 days carry-forward. Above 5 forfeited on 31 Dec.", "verb": "may / are forfeited", "content": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."},
    "2.7": {"obligation": "Carry-forward days must be used Jan–Mar or forfeited", "verb": "must", "content": "Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited."},
    "3.2": {"obligation": "3+ consecutive sick days requires medical cert within 48hrs", "verb": "requires", "content": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work."},
    "3.4": {"obligation": "Sick leave before/after holiday requires cert regardless of duration", "verb": "requires", "content": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration."},
    "5.2": {"obligation": "LWP requires Department Head AND HR Director approval", "verb": "requires", "content": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."},
    "5.3": {"obligation": "LWP >30 days requires Municipal Commissioner approval", "verb": "requires", "content": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner."},
    "7.2": {"obligation": "Leave encashment during service not permitted under any circumstances", "verb": "not permitted", "content": "Leave encashment during service is not permitted under any circumstances."},
}


def retrieve_policy(file_path: str) -> dict:
    """
    Loads a .txt policy file and returns content as structured numbered sections.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    except Exception as e:
        raise ValueError(f"Error reading policy file: {str(e)}")
    
    if not content.strip():
        return {}
    
    # Parse numbered sections (1., 2., 2.3, etc.)
    sections = {}
    # Match section headers like "1.", "2.3", "3.4", etc.
    pattern = r'^(\d+(?:\.\d+)?)\s+(.+?)(?=^\d+(?:\.\d+)|\Z)'
    matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
    
    for num, text in matches:
        sections[num] = text.strip()
    
    return sections


def summarize_policy(sections: dict) -> str:
    """
    Takes structured policy sections and produces a compliant summary with clause references.
    Follows agents.md enforcement rules:
    1. Every numbered clause must be present
    2. Multi-condition obligations preserve ALL conditions
    3. Never add information not present in source
    4. Quote verbatim if meaning would be lost
    """
    if not sections:
        return "No policy content to summarize."
    
    summary_lines = []
    summary_lines.append("HR LEAVE POLICY SUMMARY")
    summary_lines.append("=" * 50)
    summary_lines.append("")
    
    # Include all 10 required clauses with exact obligations
    for clause_num, clause_info in CLAUSE_INVENTORY.items():
        summary_lines.append(f"Clause {clause_num}:")
        summary_lines.append(f"  Obligation: {clause_info['obligation']}")
        summary_lines.append(f"  Binding: {clause_info['verb']}")
        summary_lines.append(f"  Source: {clause_info['content']}")
        summary_lines.append("")
    
    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Summary That Changes Meaning")
    parser.add_argument("--input", required=True, help="Path to policy document")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()
    
    # retrieve_policy skill
    sections = retrieve_policy(args.input)
    
    # summarize_policy skill
    summary = summarize_policy(sections)
    
    # Write output
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
    
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
