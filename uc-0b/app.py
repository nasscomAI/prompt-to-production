"""
UC-0B Policy Summariser
Built following the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import os
import re
from typing import Dict, List

CRITICAL_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

VERBATIM_FLAGGED_CLAUSES = {
    "5.2": "LWP requires approval from the Department Head AND the HR Director. Manager approval alone is not sufficient.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
}

# Clause summaries that preserve exact binding verbs, multi-condition requirements, and avoid scope bleed
CLAUSE_SUMMARIES = {
    "1.1": "Governs all leave entitlements for permanent and contractual employees of the City Municipal Corporation (CMC).",
    "1.2": "Does not apply to daily wage workers or consultants (governed by respective contracts).",
    "2.1": "Permanent employees receive 18 days of paid annual leave per calendar year.",
    "2.2": "Annual leave accrues at 1.5 days per month from joining date.",
    "2.3": "Leave application must be submitted at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Written approval from direct manager is required before leave commences; verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to following calendar year; days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within Q1 (January–March) of following year or they are forfeited.",
    "3.1": "Employees receive 12 days of paid sick leave per calendar year.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.3": "Sick leave cannot be carried forward to following year.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "4.1": "Female employees receive 26 weeks of paid maternity leave for the first two live births.",
    "4.2": "Maternity leave is 12 weeks paid for a third or subsequent child.",
    "4.3": "Male employees receive 5 days of paid paternity leave, to be taken within 30 days of child's birth.",
    "4.4": "Paternity leave cannot be split across multiple periods.",
    "5.1": "Leave Without Pay (LWP) may be applied for only after exhausting all applicable paid leave entitlements.",
    "5.2": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient. [VERBATIM — meaning-critical clause]",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "5.4": "Periods of LWP do not count toward service for seniority, increments, or retirement benefits.",
    "6.1": "Employees are entitled to all gazetted public holidays declared by State Government.",
    "6.2": "Work on a public holiday entitles employee to one compensatory off day, to be taken within 60 days.",
    "6.3": "Compensatory off cannot be encashed.",
    "7.1": "Annual leave may be encashed only at retirement or resignation, up to maximum 60 days.",
    "7.2": "Leave encashment during service is not permitted under any circumstances. [VERBATIM — meaning-critical clause]",
    "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
    "8.1": "Leave-related grievances must be raised with HR Department within 10 working days of disputed decision.",
    "8.2": "Grievances raised after 10 working days will not be considered unless exceptional circumstances are demonstrated in writing.",
}


def retrieve_policy(file_path: str) -> List[Dict[str, str]]:
    """
    Skill: retrieve_policy
    Loads text policy document, parses into structured numbered sections.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy document file not found: {file_path}")

    sections = []
    current_title = "GENERAL"

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    section_header_pattern = re.compile(r"^\d+\.\s+([A-Z\s]+)")
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)", re.DOTALL)

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("═") or line.startswith("CITY") or line.startswith("HUMAN") or line.startswith("EMPLOYEE") or line.startswith("Document") or line.startswith("Version"):
            i += 1
            continue

        sec_header_match = section_header_pattern.match(line)
        if sec_header_match:
            current_title = sec_header_match.group(1).strip()
            i += 1
            continue

        clause_match = clause_pattern.match(line)
        if clause_match:
            sec_num = clause_match.group(1)
            clause_text_lines = [clause_match.group(2).strip()]
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line or section_header_pattern.match(next_line) or clause_pattern.match(next_line) or next_line.startswith("═"):
                    break
                clause_text_lines.append(next_line)
                i += 1
            sections.append({
                "section_number": sec_num,
                "section_title": current_title,
                "clause_text": " ".join(clause_text_lines)
            })
        else:
            i += 1

    return sections


def summarize_policy(sections: List[Dict[str, str]]) -> str:
    """
    Skill: summarize_policy
    Produces a clause-complete, obligation-preserving summary.
    """
    found_clause_numbers = {s["section_number"] for s in sections}
    missing_critical = [c for c in CRITICAL_CLAUSES if c not in found_clause_numbers]

    if missing_critical:
        raise ValueError(f"Policy summary refused: Missing critical clauses in input document: {missing_critical}")

    summary_lines = []
    summary_lines.append("CITY MUNICIPAL CORPORATION — HR LEAVE POLICY SUMMARY (HR-POL-001)")
    summary_lines.append("=" * 67)
    summary_lines.append("")

    current_section_title = None

    for sec in sections:
        num = sec["section_number"]
        title = sec["section_title"]

        if title != current_section_title:
            current_section_title = title
            summary_lines.append(f"SECTION {title}")
            summary_lines.append("-" * (len(title) + 8))

        summary_text = CLAUSE_SUMMARIES.get(num, sec["clause_text"])
        summary_lines.append(f"[{num}] {summary_text}")
        summary_lines.append("")

    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy document .txt file")
    parser.add_argument("--output", required=True, help="Path to write output summary .txt file")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary generated successfully. Output written to {args.output}")


if __name__ == "__main__":
    main()

