"""
UC-0B — Summary That Changes Meaning
Builds a clause-by-clause summary of the HR leave policy and VERIFIES each summary
line against the source clause. A line that loses a number, a binding verb or a
required condition is replaced by the verbatim clause and flagged.
"""
import argparse
import re

# ---------------------------------------------------------------- skill 1
def retrieve_policy(path: str) -> list:
    """Load the .txt policy and return ordered numbered clauses:
    [{"clause": "2.3", "section": "ANNUAL LEAVE", "text": "..."}, ...]"""
    with open(path, encoding="utf-8-sig") as f:
        lines = f.read().splitlines()

    clauses, section, current = [], "", None
    for raw in lines:
        line = raw.rstrip()
        if not line.strip() or set(line.strip()) <= {"═"}:
            continue
        m_sec = re.match(r"^(\d+)\.\s+([A-Z][A-Z &/()-]+)$", line.strip())
        m_cl = re.match(r"^(\d+\.\d+)\s+(.*)$", line.strip())
        if m_sec:
            section, current = m_sec.group(2).title(), None
        elif m_cl:
            current = {"clause": m_cl.group(1), "section": section, "text": m_cl.group(2)}
            clauses.append(current)
        elif current is not None and raw.startswith(" "):
            current["text"] += " " + line.strip()  # continuation line
    if not clauses:
        raise ValueError("No numbered clauses found in " + path)
    return clauses


# ---------------------------------------------------------------- summaries
# Written from the source text only. Nothing here is added from outside the policy.
SUMMARIES = {
    "1.1": "Applies to all permanent and contractual employees of the City Municipal Corporation (CMC).",
    "1.2": "Does not apply to daily wage workers or consultants; their contracts govern them.",
    "2.1": "Each permanent employee is entitled to 18 days of paid annual leave per calendar year.",
    "2.2": "Annual leave accrues at 1.5 days per month from the date of joining.",
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave must have written approval from the employee's direct manager before the leave commences; verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP), regardless of subsequent approval.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year; any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within the first quarter (January-March) of the following year or they are forfeited.",
    "3.1": "Each employee is entitled to 12 days of paid sick leave per calendar year.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.3": "Sick leave cannot be carried forward to the following year.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "4.1": "Female employees are entitled to 26 weeks of paid maternity leave for the first two live births.",
    "4.2": "For a third or subsequent child, maternity leave is 12 weeks paid.",
    "4.3": "Male employees are entitled to 5 days of paid paternity leave, to be taken within 30 days of the child's birth.",
    "4.4": "Paternity leave cannot be split across multiple periods.",
    "5.1": "Leave Without Pay (LWP) may be applied for only after exhausting all applicable paid leave entitlements.",
    "5.2": "LWP requires approval from both the Department Head and the HR Director; manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "5.4": "Periods of LWP do not count toward service for seniority, increments, or retirement benefits.",
    "6.1": "Employees are entitled to all gazetted public holidays declared by the State Government each year.",
    "6.2": "An employee required to work on a public holiday is entitled to one compensatory off day, to be taken within 60 days of the holiday worked.",
    "6.3": "Compensatory off cannot be encashed.",
    "7.1": "Annual leave may be encashed only at the time of retirement or resignation, subject to a maximum of 60 days.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
    "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
    "8.1": "Leave-related grievances must be raised with the HR Department within 10 working days of the disputed decision.",
    "8.2": "Grievances raised after 10 working days will not be considered unless exceptional circumstances are demonstrated in writing.",
}

# Conditions / binding verbs that MUST survive in the summary of the 10 core clauses.
CORE_REQUIRED = {
    "2.3": ["must", "14", "HR-L1"],
    "2.4": ["written", "direct manager", "before", "verbal"],
    "2.5": ["will", "LOP", "regardless"],
    "2.6": ["may", "5", "forfeited", "31 December"],
    "2.7": ["must", "forfeited", "January"],
    "3.2": ["requires", "3", "consecutive", "medical certificate", "48 hours"],
    "3.4": ["requires", "before or after", "regardless"],
    "5.2": ["requires", "Department Head", "HR Director", "both"],
    "5.3": ["requires", "30", "Municipal Commissioner"],
    "7.2": ["not permitted", "any circumstances"],
}

# Phrases that would mean text was invented (scope bleed).
BANNED_PHRASES = ["standard practice", "typically", "generally", "usually",
                  "as is common", "government organisation", "expected to"]

NUM_RE = re.compile(r"\b\d+(?:\.\d+)?\b")


def _problems(clause: dict, summary: str) -> list:
    low = summary.lower()
    issues = []
    for n in NUM_RE.findall(clause["text"]):
        if not re.search(r"\b" + re.escape(n) + r"\b", summary):
            issues.append(f"number {n} missing")
    for term in CORE_REQUIRED.get(clause["clause"], []):
        if term.lower() not in low:
            issues.append(f"required term '{term}' missing")
    for p in BANNED_PHRASES:
        if p in low:
            issues.append(f"scope bleed phrase '{p}'")
    return issues


# ---------------------------------------------------------------- skill 2
def summarize_policy(clauses: list) -> tuple:
    """Return (summary_text, report) with every clause present and verified."""
    out, flagged, verified_core = [], [], 0
    current_section = None
    for c in clauses:
        if c["section"] != current_section:
            current_section = c["section"]
            out.append("")
            out.append(current_section.upper())
        summary = SUMMARIES.get(c["clause"])
        issues = ["no summary written"] if summary is None else _problems(c, summary)
        if issues:
            out.append(f'[{c["clause"]}] [FLAGGED - quoted verbatim: {"; ".join(issues)}] "{c["text"]}"')
            flagged.append(c["clause"])
        else:
            out.append(f'[{c["clause"]}] {summary}')
            if c["clause"] in CORE_REQUIRED:
                verified_core += 1
    return "\n".join(out).strip("\n"), {
        "total": len(clauses), "flagged": flagged,
        "core_verified": verified_core, "core_total": len(CORE_REQUIRED),
    }


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    body, report = summarize_policy(clauses)
    header = ("SUMMARY OF EMPLOYEE LEAVE POLICY (HR-POL-001, Version 2.3)\n"
              "Every numbered clause is listed with its clause number. "
              "Nothing outside the source document has been added.\n")
    footer = (f"\n\nCOVERAGE: {report['total']} of {len(clauses)} clauses included; "
              f"{report['core_verified']} of {report['core_total']} core clauses verified "
              f"for conditions and binding verbs; flagged/verbatim: "
              f"{', '.join(report['flagged']) or 'none'}.")
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(header + body + footer + "\n")
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()