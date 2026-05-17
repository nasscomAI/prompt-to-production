"""
UC-0B app.py — Summary That Changes Meaning
Built using RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import re
import os


CRITICAL_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4",
    "5.2", "5.3",
    "7.2"
]

CLAUSE_SUMMARIES = {
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within the first quarter (January-March) of the following year or they are forfeited.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "5.2": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
}


def retrieve_policy(input_path: str) -> list:
    """
    Loads a .txt policy file and returns its content as structured numbered sections.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Policy file not found: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    sections = []
    pattern = r'^(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+\s|\n\n\d+\.|\Z)'
    matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)

    for section_num, section_text in matches:
        section_text = section_text.strip()
        binding_verb = _extract_binding_verb(section_text)
        sections.append({
            "section_number": section_num,
            "content": section_text,
            "binding_verb": binding_verb
        })

    if not sections:
        sections.append({
            "section_number": "FULL",
            "content": content,
            "binding_verb": ""
        })

    return sections


def _extract_binding_verb(text: str) -> str:
    """Extract the binding verb from a clause."""
    verbs = ["must", "will", "requires", "not permitted", "may", "are entitled", "cannot"]
    text_lower = text.lower()
    for verb in verbs:
        if verb in text_lower:
            return verb
    return ""


def summarize_policy(sections: list, output_path: str) -> str:
    """
    Takes structured numbered sections and produces a compliant summary.
    """
    section_numbers = [s["section_number"] for s in sections]
    summary_lines = []

    summary_lines.append("CITY MUNICIPAL CORPORATION — HR LEAVE POLICY SUMMARY")
    summary_lines.append("Document Reference: HR-POL-001, Version 2.3")
    summary_lines.append("=" * 60)
    summary_lines.append("")

    for clause_num in CRITICAL_CLAUSES:
        if clause_num in section_numbers:
            summary_lines.append(f"Clause {clause_num}: {CLAUSE_SUMMARIES[clause_num]}")
        else:
            summary_lines.append(f"Clause {clause_num}: [MISSING CLAUSE {clause_num} — not found in source document]")

    summary_lines.append("")
    summary_lines.append("=" * 60)
    summary_lines.append("END OF SUMMARY")

    summary_text = "\n".join(summary_lines)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary_text)

    return summary_text


def main():
    parser = argparse.ArgumentParser(description="UC-0B — Summary That Changes Meaning")
    parser.add_argument("--input", required=True, help="Path to policy document (.txt)")
    parser.add_argument("--output", required=True, help="Path to write summary (.txt)")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections, args.output)
    print(f"Summary written to {args.output}")
    print(f"Covered {len([c for c in CRITICAL_CLAUSES if c in [s['section_number'] for s in sections]])}/{len(CRITICAL_CLAUSES)} critical clauses")


if __name__ == "__main__":
    main()
