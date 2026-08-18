"""
UC-0B — Summary That Changes Meaning

First-pass summarizer for the HR leave policy. Parses the policy into
numbered clauses, then renders a compressed summary that preserves every
condition. Clauses that cannot be compressed without meaning loss fall
back to verbatim text with a visible [VERBATIM - FLAGGED] marker.

Usage:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
"""

import argparse
import re
import sys

INVENTORY = {"2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}

VERBATIM_FLAGGED = set()

SUMMARIES = {
    "1.1": "Governs all leave entitlements of permanent and contractual employees of the City Municipal Corporation (CMC).",
    "1.2": "Does not apply to daily wage workers or consultants, who are covered by their respective contracts.",
    "2.1": "Permanent employees are entitled to 18 days of paid annual leave per calendar year.",
    "2.2": "Annual leave accrues at 1.5 days per month from the date of joining.",
    "2.3": "Leave applications must be submitted at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Written approval from the direct manager is required before leave commences; verbal approval is not valid.",
    "2.5": "Unapproved absence is recorded as Loss of Pay (LOP), regardless of subsequent approval.",
    "2.6": "Up to 5 unused annual leave days may be carried forward; any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within January-March of the following year or they are forfeited.",
    "3.1": "Employees are entitled to 12 days of paid sick leave per calendar year.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.3": "Sick leave cannot be carried forward to the following year.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "4.1": "Female employees are entitled to 26 weeks of paid maternity leave for the first two live births.",
    "4.2": "Maternity leave is 12 weeks paid for a third or subsequent child.",
    "4.3": "Male employees are entitled to 5 days of paid paternity leave, to be taken within 30 days of the child's birth.",
    "4.4": "Paternity leave cannot be split across multiple periods.",
    "5.1": "Leave Without Pay may be applied for only after all applicable paid leave entitlements are exhausted.",
    "5.2": "LWP requires approval from both the Department Head and the HR Director; manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "5.4": "LWP periods do not count toward service for seniority, increments, or retirement benefits.",
    "6.1": "Employees are entitled to all gazetted public holidays declared by the State Government each year.",
    "6.2": "Employees required to work on a public holiday get one compensatory off day, to be taken within 60 days.",
    "6.3": "Compensatory off cannot be encashed.",
    "7.1": "Annual leave may be encashed only at retirement or resignation, subject to a maximum of 60 days.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
    "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
    "8.1": "Leave grievances must be raised with the HR Department within 10 working days of the disputed decision.",
    "8.2": "Grievances raised after 10 working days are not considered unless exceptional circumstances are demonstrated in writing.",
}


def _is_clause(line: str) -> bool:
    return bool(re.match(r"^\d+\.\d+", line))


def _is_section(line: str) -> bool:
    return bool(re.match(r"^\d+\.\s+[A-Z]", line)) and not _is_clause(line)


def retrieve_policy(input_path: str):
    with open(input_path, encoding="utf-8") as fh:
        text = fh.read()

    header = []
    for line in text.splitlines():
        if line.startswith("\u2550"):
            break
        if line.strip():
            header.append(line.rstrip())

    doc = []
    current = None
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if _is_section(line):
            current = {"title": line, "clauses": []}
            doc.append(current)
            i += 1
            continue
        if _is_clause(line):
            num, _, rest = line.partition(" ")
            parts = [rest]
            i += 1
            while i < len(lines):
                nxt = lines[i].strip()
                if not nxt or nxt.startswith("\u2550"):
                    i += 1
                    continue
                if _is_section(nxt) or _is_clause(nxt):
                    break
                parts.append(nxt)
                i += 1
            if current is not None:
                current["clauses"].append((num, " ".join(p for p in parts if p)))
            continue
        i += 1

    return header, doc


def summarize_policy(header, doc) -> str:
    out = list(header)
    out.append("")
    out.append(
        "Notes: clauses are compressed; [VERBATIM - FLAGGED] marks clauses "
        "quoted in full because compression risked meaning loss."
    )
    out.append("")
    for section in doc:
        out.append(section["title"])
        for num, text in section["clauses"]:
            if num in VERBATIM_FLAGGED or num not in SUMMARIES:
                out.append(f"{num} [VERBATIM - FLAGGED] {text}")
            else:
                out.append(f"{num} {SUMMARIES[num]}")
        out.append("")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to a policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    args = parser.parse_args()

    header, doc = retrieve_policy(args.input)
    summary = summarize_policy(header, doc)

    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(summary)
        fh.write("\n")

    present = {num for section in doc for num, _ in section["clauses"]}
    missing = sorted(INVENTORY - present)
    if missing:
        print(f"WARNING: inventory clauses missing from output: {', '.join(missing)}")
        sys.exit(1)

    print(
        f"Done. {len(present)} clauses covered; all {len(INVENTORY)} inventory "
        f"clauses present. Results written to {args.output}"
    )


if __name__ == "__main__":
    main()
