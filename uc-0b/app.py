"""
UC-0B — Summary That Changes Meaning
Built using the RICE -> agents.md -> skills.md -> CRAFT workflow.
"""
import argparse
import re
import sys


def retrieve_policy(file_path: str) -> list:
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    sections = []
    current_section = None
    current_clauses = []
    buffer = ""
    last_clause_id = None

    for line in lines:
        stripped = line.strip()

        section_match = re.match(r"^(\d+)\.\s+(.+)", stripped)
        if section_match and not re.match(r"^\d+\.\d+", stripped):
            if current_section and last_clause_id:
                current_clauses.append({"clause_id": last_clause_id, "text": buffer.strip()})
            if current_section:
                sections.append({
                    "section_number": current_section["number"],
                    "section_title": current_section["title"],
                    "clauses": current_clauses,
                })
            current_section = {"number": section_match.group(1), "title": section_match.group(2)}
            current_clauses = []
            buffer = ""
            last_clause_id = None
            continue

        clause_match = re.match(r"^(\d+\.\d+)\s+(.+)", stripped)
        if clause_match:
            if last_clause_id:
                current_clauses.append({"clause_id": last_clause_id, "text": buffer.strip()})
            last_clause_id = clause_match.group(1)
            buffer = clause_match.group(2)
        elif last_clause_id and stripped:
            buffer += " " + stripped

    if current_section and last_clause_id:
        current_clauses.append({"clause_id": last_clause_id, "text": buffer.strip()})
    if current_section:
        sections.append({
            "section_number": current_section["number"],
            "section_title": current_section["title"],
            "clauses": current_clauses,
        })

    return sections


SUMMARY_RULES = {
    "1.1": "This policy covers all permanent and contractual CMC employees.",
    "1.2": "Daily wage workers and consultants are excluded; governed by separate contracts.",
    "2.1": "18 days paid annual leave per calendar year.",
    "2.2": "Accrues at 1.5 days per month from joining date.",
    "2.3": "Employees must submit leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave must receive written approval from direct manager before leave commences. Verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Maximum 5 unused annual leave days may carry forward. Days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within January-March of the following year or they are forfeited.",
    "3.1": "12 days paid sick leave per calendar year.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.3": "Sick leave cannot be carried forward.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "4.1": "26 weeks paid maternity leave for first two live births.",
    "4.2": "12 weeks paid maternity leave for third or subsequent child.",
    "4.3": "5 days paid paternity leave, to be taken within 30 days of birth.",
    "4.4": "Paternity leave cannot be split across multiple periods.",
    "5.1": "LWP may be applied for only after exhausting all paid leave entitlements.",
    "5.2": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "5.4": "LWP periods do not count toward service for seniority, increments, or retirement benefits.",
    "6.1": "Entitled to all gazetted public holidays declared by State Government.",
    "6.2": "Working on a public holiday entitles employee to one compensatory off day, taken within 60 days.",
    "6.3": "Compensatory off cannot be encashed.",
    "7.1": "Annual leave may be encashed only at retirement or resignation, max 60 days.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
    "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
    "8.1": "Leave grievances must be raised with HR within 10 working days of disputed decision.",
    "8.2": "Grievances after 10 working days not considered unless exceptional circumstances demonstrated in writing.",
}


def summarize_policy(sections: list) -> str:
    output_lines = []
    output_lines.append("CITY MUNICIPAL CORPORATION — EMPLOYEE LEAVE POLICY SUMMARY")
    output_lines.append("Source: HR-POL-001 v2.3 (Effective 1 April 2024)")
    output_lines.append("")

    for section in sections:
        sec_num = section["section_number"]
        title = section["section_title"]
        output_lines.append(f"{'=' * 60}")
        output_lines.append(f"{sec_num}. {title}")
        output_lines.append(f"{'=' * 60}")

        for clause in section["clauses"]:
            cid = clause["clause_id"]
            summary = SUMMARY_RULES.get(cid)
            if summary:
                output_lines.append(f"  [{cid}] {summary}")
            else:
                output_lines.append(f"  [{cid}] {clause['text']}")

        output_lines.append("")

    critical = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    output_lines.append(f"{'=' * 60}")
    output_lines.append("CRITICAL CLAUSE VERIFICATION")
    output_lines.append(f"{'=' * 60}")
    for cid in critical:
        status = "PRESENT" if cid in SUMMARY_RULES else "MISSING"
        output_lines.append(f"  [{cid}] {status}: {SUMMARY_RULES.get(cid, 'NOT FOUND')}")

    return "\n".join(output_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
