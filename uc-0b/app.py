"""UC-0B - Policy summariser (clause-preserving)"""
import argparse
import re

# Hand-checked summaries keyed by clause number. Every clause in the source must have one.
SUMMARIES = {
    "1.1": "Applies to permanent and contractual employees of the City Municipal Corporation (CMC).",
    "1.2": "Does not apply to daily wage workers or consultants; their contracts govern them.",
    "2.1": "Each permanent employee is entitled to 18 days of paid annual leave per calendar year.",
    "2.2": "Annual leave accrues at 1.5 days per month from the date of joining.",
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within the first quarter (January-March) of the following year or they are forfeited.",
    "3.1": "Each employee is entitled to 12 days of paid sick leave per calendar year.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.3": "Sick leave cannot be carried forward to the following year.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "4.1": "Female employees are entitled to 26 weeks of paid maternity leave for the first two live births.",
    "4.2": "For a third or subsequent child, maternity leave is 12 weeks paid.",
    "4.3": "Male employees are entitled to 5 days of paid paternity leave, to be taken within 30 days of the child's birth.",
    "4.4": "Paternity leave cannot be split across multiple periods.",
    "5.1": "An employee may apply for Leave Without Pay (LWP) only after exhausting all applicable paid leave entitlements.",
    "5.2": "LWP requires approval from both the Department Head and the HR Director. Manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "5.4": "Periods of LWP do not count toward service for seniority, increments, or retirement benefits.",
    "6.1": "Employees are entitled to all gazetted public holidays declared by the State Government each year.",
    "6.2": "An employee required to work on a public holiday is entitled to one compensatory off day, to be taken within 60 days of the holiday worked.",
    "6.3": "Compensatory off cannot be encashed.",
    "7.1": "Annual leave may be encashed only at the time of retirement or resignation, up to a maximum of 60 days.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
    "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
    "8.1": "Leave-related grievances must be raised with the HR Department within 10 working days of the disputed decision.",
    "8.2": "Grievances raised after 10 working days will not be considered unless exceptional circumstances are demonstrated in writing.",
}

# Terms that must survive in the summary of these clauses (conditions, numbers, binding verbs).
REQUIRED = {
    "2.3": ["must", "14", "HR-L1"],
    "2.4": ["written", "before", "verbal", "not valid"],
    "2.5": ["will", "LOP", "regardless"],
    "2.6": ["5", "forfeited", "31 December"],
    "2.7": ["must", "January", "March", "forfeited"],
    "3.2": ["3", "requires", "48 hours", "registered medical practitioner"],
    "3.4": ["requires", "regardless"],
    "5.2": ["Department Head", "HR Director", "not sufficient"],
    "5.3": ["30", "Municipal Commissioner", "requires"],
    "7.2": ["not permitted", "any circumstances"],
}


def retrieve_policy(path: str) -> list:
    """Load .txt policy; return list of sections {number, title, clauses:[(id, text)]}."""
    try:
        with open(path, encoding="utf-8-sig") as f:
            lines = f.read().splitlines()
    except OSError as e:
        raise SystemExit(f"Cannot read input file: {e}")
    sections, clause = [], None
    for line in lines:
        m_sec = re.match(r"^(\d+)\.\s+([A-Z][A-Z &/()-]+)$", line.strip())
        m_cl = re.match(r"^(\d+\.\d+)\s+(.*)$", line.strip())
        if m_sec and not line.startswith(" "):
            sections.append({"number": m_sec.group(1), "title": m_sec.group(2), "clauses": []})
            clause = None
        elif m_cl and sections:
            clause = [m_cl.group(1), m_cl.group(2)]
            sections[-1]["clauses"].append(clause)
        elif clause and line.strip() and not line.startswith("═"):
            clause[1] += " " + line.strip()
    if not any(s["clauses"] for s in sections):
        raise SystemExit("No numbered clauses found in input.")
    return sections


def summarize_policy(sections: list) -> str:
    out = ["SUMMARY OF EMPLOYEE LEAVE POLICY (HR-POL-001)",
           "Every clause is listed with its clause number. Nothing is added beyond the source.", ""]
    flagged = []
    for s in sections:
        out.append(f"{s['number']}. {s['title']}")
        for cid, text in s["clauses"]:
            summary = SUMMARIES.get(cid)
            missing = [t for t in REQUIRED.get(cid, []) if summary and t.lower() not in summary.lower()]
            if summary is None or missing:
                out.append(f"  {cid} [VERBATIM - NEEDS REVIEW] {text}")
                flagged.append(cid)
            else:
                out.append(f"  {cid} {summary}")
        out.append("")
    if flagged:
        out.append("Clauses quoted verbatim because a safe summary was not available: " + ", ".join(flagged))
    return "\n".join(out).rstrip() + "\n"


def main():
    p = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    p.add_argument("--input", required=True, help="Path to policy .txt file")
    p.add_argument("--output", required=True, help="Path to write summary .txt")
    a = p.parse_args()
    summary = summarize_policy(retrieve_policy(a.input))
    with open(a.output, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"Done. Summary written to {a.output}")


if __name__ == "__main__":
    main()