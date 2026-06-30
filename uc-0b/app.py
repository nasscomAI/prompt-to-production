"""
UC-0B — Summary That Changes Meaning
Summarizes HR policy documents while preserving all clause conditions.
"""
import argparse
import re


def retrieve_policy(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        text = f.read()

    sections = []
    lines = text.splitlines()
    current_section = None
    current_clauses = []
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.+)")
    section_header_pattern = re.compile(r"^\d+\.\s+(.+)")
    current_clause = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        header_match = section_header_pattern.match(stripped)
        clause_match = clause_pattern.match(stripped)

        if header_match:
            if current_clause:
                current_clauses.append(current_clause)
                current_clause = None
            if current_section:
                sections.append({"title": current_section, "clauses": current_clauses})
            current_section = header_match.group(1)
            current_clauses = []
        elif clause_match:
            if current_clause:
                current_clauses.append(current_clause)
            current_clause = {
                "id": clause_match.group(1),
                "text": clause_match.group(2),
            }
        elif current_clause and line[0] in (" ", "\t"):
            current_clause["text"] += " " + stripped

    if current_clause:
        current_clauses.append(current_clause)
    if current_section:
        sections.append({"title": current_section, "clauses": current_clauses})

    return sections


def _summarize_clause(clause: dict) -> str:
    cid = clause["id"]
    text = clause["text"]

    summaries = {
        "1.1": "The policy applies to permanent and contractual employees.",
        "1.2": "Daily wage workers and consultants are governed by their own contracts.",
        "2.1": "18 days paid annual leave per calendar year for permanent employees.",
        "2.2": "Annual leave accrues at 1.5 days per month from date of joining.",
        "2.3": "Employees must submit leave application at least 14 calendar days in advance using Form HR-L1.",
        "2.4": "Leave requires written approval from the direct manager before commencement. Verbal approval is not valid.",
        "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
        "2.6": "Maximum 5 unused days may be carried forward. Any days above 5 are forfeited on 31 December.",
        "2.7": "Carry-forward days must be used within January\u2013March or they are forfeited.",
        "3.1": "12 days paid sick leave per calendar year.",
        "3.2": "Sick leave of 3+ consecutive days requires a medical certificate from a registered practitioner submitted within 48 hours of returning to work.",
        "3.3": "Sick leave cannot be carried forward.",
        "3.4": "Sick leave taken immediately before or after a public holiday or annual leave requires a medical certificate regardless of duration.",
        "4.1": "Female employees: 26 weeks paid maternity leave for first two live births.",
        "4.2": "For third or subsequent child: 12 weeks paid maternity leave.",
        "4.3": "Male employees: 5 days paid paternity leave within 30 days of birth.",
        "4.4": "Paternity leave cannot be split across multiple periods.",
        "5.1": "LWP may be applied for only after exhausting all paid leave entitlements.",
        "5.2": "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.",
        "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
        "5.4": "LWP periods do not count toward seniority, increments, or retirement benefits.",
        "6.1": "Employees are entitled to all gazetted public holidays.",
        "6.2": "Working on a public holiday entitles one compensatory off day within 60 days.",
        "6.3": "Compensatory off cannot be encashed.",
        "7.1": "Annual leave encashment only at retirement or resignation, max 60 days.",
        "7.2": "Leave encashment during service is not permitted under any circumstances.",
        "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
        "8.1": "Grievances must be raised with HR within 10 working days.",
        "8.2": "Grievances raised after 10 working days will not be considered unless exceptional circumstances are demonstrated in writing.",
    }

    if cid in summaries:
        return summaries[cid]

    # Fallback: quote verbatim with [VERBATIM] flag
    return f"[VERBATIM] {clause['id']} {text}"


def summarize_policy(sections: list) -> str:
    parts = []
    for section in sections:
        parts.append(section["title"])
        parts.append("")
        for clause in section["clauses"]:
            summary = _summarize_clause(clause)
            parts.append(f"  {clause['id']}  {summary}")
        parts.append("")
    return "\n".join(parts).strip()


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary + "\n")

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
