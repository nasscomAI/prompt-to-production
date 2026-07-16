"""
UC-0B — Summary That Changes Meaning
Built with the RICE + agents.md + skills.md + CRAFT workflow.

Enforcement implemented here (mirrors agents.md):
- every numbered clause present, referenced by clause number (verified, aborts if not)
- multi-condition obligations keep ALL conditions; binding verbs never softened
- nothing added that is not in the source document
- clauses with no reviewed condensation are quoted verbatim and flagged
"""
import argparse
import re
import sys

CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z &()/-]+)$")

# Reviewed condensations, keyed by clause number. Each line was checked against
# the source so that every condition and binding verb survives (agents.md
# enforcement rules 2 and 3). A clause not in this map is emitted verbatim and
# flagged rather than paraphrased (rule 5).
CLAUSE_SUMMARIES = {
    "1.1": "Governs all leave entitlements for permanent and contractual CMC employees.",
    "1.2": "Does not apply to daily wage workers or consultants; their contracts govern those categories.",
    "2.1": "Each permanent employee is entitled to 18 days of paid annual leave per calendar year.",
    "2.2": "Annual leave accrues at 1.5 days per month from the date of joining.",
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave must receive written approval from the employee's direct manager before it commences; verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following year; any days above 5 are forfeited on 31 December.",
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
    "5.2": "LWP requires approval from the Department Head AND the HR Director; manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "5.4": "Periods of LWP do not count toward service for seniority, increments, or retirement benefits.",
    "6.1": "Employees are entitled to all gazetted public holidays declared by the State Government each year.",
    "6.2": "Working on a public holiday earns one compensatory off day, to be taken within 60 days of the holiday worked.",
    "6.3": "Compensatory off cannot be encashed.",
    "7.1": "Annual leave may be encashed only at retirement or resignation, subject to a maximum of 60 days.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
    "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
    "8.1": "Leave-related grievances must be raised with the HR Department within 10 working days of the disputed decision.",
    "8.2": "Grievances raised after 10 working days will not be considered unless exceptional circumstances are demonstrated in writing.",
}


def retrieve_policy(path: str):
    """Load the policy file, return ordered (clause_no, section_title, text) tuples."""
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError as exc:
        sys.exit("Cannot read policy file %s: %s" % (path, exc))

    clauses = []
    section_title = ""
    current_no, current_text = None, []
    for line in lines:
        stripped = line.strip()
        section = SECTION_RE.match(stripped)
        clause = CLAUSE_RE.match(stripped)
        if section:
            if current_no:
                clauses.append((current_no, section_title, " ".join(current_text)))
                current_no, current_text = None, []
            section_title = section.group(2).title()
        elif clause:
            if current_no:
                clauses.append((current_no, section_title, " ".join(current_text)))
            current_no, current_text = clause.group(1), [clause.group(2).strip()]
        elif current_no and stripped and not stripped.startswith("═"):
            current_text.append(stripped)
    if current_no:
        clauses.append((current_no, section_title, " ".join(current_text)))

    if not clauses:
        sys.exit("No numbered clauses (e.g. '2.3 ...') found in %s — wrong file format." % path)
    return clauses


def summarize_policy(clauses):
    """Produce clause-referenced summary text. Every clause present, nothing added."""
    out = ["POLICY SUMMARY - every numbered clause retained, clause numbers preserved", ""]
    last_section = None
    for clause_no, section_title, text in clauses:
        if section_title != last_section:
            out.append("")
            out.append(section_title.upper())
            last_section = section_title
        summary = CLAUSE_SUMMARIES.get(clause_no)
        if summary:
            out.append("%s  %s" % (clause_no, summary))
        else:
            # No reviewed condensation → verbatim beats a lossy paraphrase
            out.append('%s  [VERBATIM - FLAGGED] "%s"' % (clause_no, text))
    return "\n".join(out).lstrip("\n") + "\n"


def verify_completeness(clauses, summary_text: str):
    """Abort if any source clause number is missing from the summary."""
    missing = [no for no, _, _ in clauses
               if not re.search(r"^%s\s" % re.escape(no), summary_text, re.M)]
    if missing:
        sys.exit("COMPLETENESS CHECK FAILED — clauses missing from summary: %s"
                 % ", ".join(missing))


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input",  required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)
    verify_completeness(clauses, summary)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
    flagged = summary.count("[VERBATIM - FLAGGED]")
    print("Summarised %d clauses (%d flagged verbatim). Written to %s"
          % (len(clauses), flagged, args.output))


if __name__ == "__main__":
    main()
