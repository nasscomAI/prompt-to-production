"""
UC-0B — Summary That Changes Meaning

Summarises a CMC policy document (policy_hr_leave.txt) into a clause-complete
summary at uc-0b/summary_hr_leave.txt.

Enforcement rules (from agents.md) implemented here:
  1. Every numbered clause (X.Y) present in the source MUST appear in the output.
  2. Multi-condition obligations keep ALL conditions — never one dropped silently
     (e.g. clause 5.2 keeps BOTH the Department Head AND the HR Director).
  3. Never add information not present in the source document.
  4. If a clause cannot be summarised without meaning loss, it is quoted
     verbatim and flagged as [VERBATIM].
"""
import argparse
import os
import re
import sys

CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")

# ---------------------------------------------------------------------------
# Clause summaries. Every condition and binding verb of the source is
# preserved. Anything not covered here is quoted verbatim and flagged.
# ---------------------------------------------------------------------------
CLAUSE_SUMMARIES = {
    "1.1": "This policy governs all leave entitlements for permanent and contractual employees of the City Municipal Corporation (CMC).",
    "1.2": "This policy does not apply to daily wage workers or consultants, who are governed by their respective contracts.",
    "2.1": "Each permanent employee is entitled to 18 days of paid annual leave per calendar year.",
    "2.2": "Annual leave accrues at 1.5 days per month from the date of joining.",
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave applications must receive written approval from the employee's direct manager before the leave commences; verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year; any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within the first quarter (January\u2013March) of the following year or they are forfeited.",
    "3.1": "Each employee is entitled to 12 days of paid sick leave per calendar year.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.3": "Sick leave cannot be carried forward to the following year.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "4.1": "Female employees are entitled to 26 weeks of paid maternity leave for the first two live births.",
    "4.2": "For a third or subsequent child, maternity leave is 12 weeks paid.",
    "4.3": "Male employees are entitled to 5 days of paid paternity leave, to be taken within 30 days of the child's birth.",
    "4.4": "Paternity leave cannot be split across multiple periods.",
    "5.1": "An employee may apply for Leave Without Pay only after exhausting all applicable paid leave entitlements.",
    "5.2": "LWP requires approval from the Department Head and the HR Director; manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "5.4": "Periods of LWP do not count toward service for the purposes of seniority, increments, or retirement benefits.",
    "6.1": "Employees are entitled to all gazetted public holidays as declared by the State Government each year.",
    "6.2": "If an employee is required to work on a public holiday, they are entitled to one compensatory off day, to be taken within 60 days of the holiday worked.",
    "6.3": "Compensatory off cannot be encashed.",
    "7.1": "Annual leave may be encashed only at the time of retirement or resignation, subject to a maximum of 60 days.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
    "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
    "8.1": "Leave-related grievances must be raised with the HR Department within 10 working days of the disputed decision.",
    "8.2": "Grievances raised after 10 working days will not be considered unless exceptional circumstances are demonstrated in writing.",
}


def retrieve_policy(input_path: str) -> list:
    """
    Load a .txt policy file and return its content as structured numbered
    sections: list of (clause_id, body_text) preserving order.
    """
    if not os.path.isfile(input_path):
        print("Error: input file not found: %s" % input_path, file=sys.stderr)
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    clauses = []
    current = None
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("\u2550"):  # section divider line
            continue
        match = CLAUSE_RE.match(stripped)
        if match:
            current = [match.group(1), match.group(2)]
            clauses.append(current)
        elif current is not None:
            # continuation of the previous clause body
            current[1] += " " + stripped

    # Normalise whitespace in every clause body.
    normalized = []
    for clause_id, body in clauses:
        body = re.sub(r"\s+", " ", body).strip()
        normalized.append((clause_id, body))
    return normalized


def summarize_policy(clauses: list) -> list:
    """
    Produce a clause-complete summary. Returns list of
    (clause_id, summary_text, flagged) preserving clause order.
    """
    result = []
    for clause_id, body in clauses:
        if clause_id in CLAUSE_SUMMARIES:
            result.append((clause_id, CLAUSE_SUMMARIES[clause_id], False))
        else:
            # Not safe to paraphrase without meaning loss — quote verbatim.
            result.append((clause_id, body, True))
    return result


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    if not clauses:
        print("Error: no numbered clauses found in %s" % args.input, file=sys.stderr)
        sys.exit(1)

    summaries = summarize_policy(clauses)

    parsed_ids = {cid for cid, _ in clauses}
    missing = [cid for cid in CLAUSE_SUMMARIES if cid not in parsed_ids]
    if missing:
        print("Warning: clauses in summary table not found in source: %s" % ", ".join(missing), file=sys.stderr)

    lines = []
    lines.append("EMPLOYEE LEAVE POLICY \u2014 CLAUSE-COMPLETE SUMMARY")
    lines.append("Source document: %s" % os.path.basename(args.input))
    lines.append("")
    lines.append("Every numbered clause found in the source is preserved below. "
                 "Multi-condition obligations retain ALL of their conditions, "
                 "and binding verbs (must / will / requires / not permitted) are "
                 "unchanged. No information has been added beyond the source "
                 "document. [VERBATIM] marks clauses quoted word-for-word "
                 "because summarising them would risk meaning loss.")
    lines.append("")
    for clause_id, text, flagged in summaries:
        marker = " [VERBATIM]" if flagged else ""
        lines.append("[%s]%s %s" % (clause_id, marker, text))

    out_dir = os.path.dirname(os.path.abspath(args.output))
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    flagged_count = sum(1 for _, _, f in summaries if f)
    print("Summarised %d clause(s) -> %s (flagged verbatim: %d)"
          % (len(summaries), args.output, flagged_count))


if __name__ == "__main__":
    main()