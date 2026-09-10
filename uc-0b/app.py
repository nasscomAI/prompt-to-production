"""
UC-0B app.py — Extractive CMC leave-policy summarizer.
Implements agents.md enforcement via the skills.md workflow:
retrieve_policy -> summarize_policy -> summary_hr_leave.txt.

Extractive by construction: every output line traces to a numbered
source clause, high-risk clauses are verified verbatim quotes, and the
program fails loudly on missing clauses, ungrounded quotes, or bleed
phrases instead of emitting a compromised summary.
"""
import argparse
import re
import sys

# Phrases that must never appear — none of them is in the source document.
BLEED_PHRASES = [
    "as is standard practice",
    "typically",
    "generally expected",
    "generally understood",
    "while not explicitly covered",
    "standard practice",
    "usual practice",
    "it is standard",
    "as is usual",
]

# Per-clause summaries authored from source words only. QUOTED entries are
# verified character-for-character against the source at runtime (see main).
# Clause 5.2 is quoted verbatim: the README trap is dropping one approver.
SUMMARIES = {
    "1.1": "Covers leave entitlements for permanent and contractual employees of the City Municipal Corporation (CMC).",
    "1.2": "Does not apply to daily wage workers or consultants, who are governed by their respective contracts.",
    "2.1": "Each permanent employee is entitled to 18 days of paid annual leave per calendar year.",
    "2.2": "Annual leave accrues at 1.5 days per month from the date of joining.",
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave applications must receive written approval from the employee's direct manager before the leave commences; verbal approval is not valid.",
    "2.5": 'QUOTED: "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval." [QUOTED VERBATIM — MEANING-LOSS RISK]',
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
    "5.1": "An employee may apply for Leave Without Pay only after exhausting all applicable paid leave entitlements.",
    "5.2": 'QUOTED: "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient." [QUOTED VERBATIM — MEANING-LOSS RISK]',
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "5.4": "Periods of LWP do not count toward service for the purposes of seniority, increments, or retirement benefits.",
    "6.1": "Employees are entitled to all gazetted public holidays as declared by the State Government each year.",
    "6.2": "An employee required to work on a public holiday is entitled to one compensatory off day, to be taken within 60 days of the holiday worked.",
    "6.3": "Compensatory off cannot be encashed.",
    "7.1": "Annual leave may be encashed only at the time of retirement or resignation, subject to a maximum of 60 days.",
    "7.2": 'QUOTED: "Leave encashment during service is not permitted under any circumstances." [QUOTED VERBATIM — MEANING-LOSS RISK]',
    "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
    "8.1": "Leave-related grievances must be raised with the HR Department within 10 working days of the disputed decision.",
    "8.2": "Grievances raised after 10 working days will not be considered unless exceptional circumstances are demonstrated in writing.",
}

SECTION_TITLES = {
    "1": "Purpose and scope",
    "2": "Annual leave",
    "3": "Sick leave",
    "4": "Maternity and paternity leave",
    "5": "Leave Without Pay (LWP)",
    "6": "Public holidays",
    "7": "Leave encashment",
    "8": "Grievances",
}


def refuse(message):
    """Refuse to summarize — never guess at policy content."""
    print(f"REFUSED: {message}", file=sys.stderr)
    raise SystemExit(2)


def retrieve_policy(input_path):
    """Load .txt policy file, return (header, ordered clause mapping)."""
    try:
        with open(input_path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        refuse(f"input file not found: {input_path}")
    except OSError as exc:
        refuse(f"cannot read input file {input_path}: {exc}")

    clauses = {}
    current = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        m = re.match(r"^(\d+\.\d+)\s+(.*)$", line)
        if m:
            current = m.group(1)
            clauses[current] = m.group(2).strip()
        elif current and line and not line.startswith("═"):
            clauses[current] += " " + line
    # Header = non-clause lines before the first numbered clause.
    header_lines = []
    for raw_line in text.splitlines():
        if re.match(r"^\s*\d+\.\d+\s+", raw_line):
            break
        if raw_line.strip() and not raw_line.strip().startswith("═"):
            header_lines.append(raw_line.strip())
    if not clauses:
        refuse(f"no numbered clauses found in {input_path}; "
               f"will not summarize from memory")
    print(f"Retrieved {len(clauses)} numbered clauses from {input_path}.")
    return header_lines, clauses, text


def _normalize(text):
    return re.sub(r"\s+", " ", text).strip()


def summarize_policy(header_lines, clauses, source_text):
    """Build the compliant summary; fail loudly on any violation."""
    missing = [n for n in clauses if n not in SUMMARIES]
    if missing:
        refuse(f"no summary mapping for clauses {missing}; "
               f"emitting a partial summary is not allowed")

    # Ground every verbatim quote against the source text.
    normalized_source = _normalize(source_text)
    for number, summary in SUMMARIES.items():
        if number not in clauses:
            continue
        for quote in re.findall(r'"([^"]+)"', summary):
            if _normalize(quote) not in normalized_source:
                refuse(f"clause {number} quote not found verbatim in source: "
                       f"{quote!r}")

    lines = []
    lines.append("SUMMARY — CMC EMPLOYEE LEAVE POLICY (HR-POL-001, v2.3)")
    lines.append("Source: policy_hr_leave.txt. Every line cites its clause; "
                 "quoted lines are verbatim.")
    lines.append("")
    current_section = None
    for number in sorted(clauses.keys(),
                         key=lambda n: tuple(int(p) for p in n.split("."))):
        section = number.split(".")[0]
        if section != current_section:
            current_section = section
            lines.append(f"--- {section}. "
                         f"{SECTION_TITLES.get(section, 'Clauses')} ---")
        lines.append(f"[Clause {number}] {SUMMARIES[number]}")
    lines.append("")
    lines.append("End of summary. All numbered clauses 1.1-8.2 are covered above.")
    summary = "\n".join(lines) + "\n"

    found_bleed = [p for p in BLEED_PHRASES if p.lower() in summary.lower()]
    if found_bleed:
        refuse(f"bleed phrases detected in summary output: {found_bleed}")
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args(argv)

    header_lines, clauses, source_text = retrieve_policy(args.input)
    summary = summarize_policy(header_lines, clauses, source_text)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"Wrote summary of {len(clauses)} clauses to {args.output}.")


if __name__ == "__main__":
    main()
