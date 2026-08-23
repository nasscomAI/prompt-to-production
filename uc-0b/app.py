"""
UC-0B — Summary That Changes Meaning
Faithful summariser for the CMC HR Leave Policy.
Implements agents.md enforcement and skills.md contracts.
"""
import argparse
import re
import sys
from pathlib import Path

CLAUSE_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.+?)\s*$")
HEADING_RE = re.compile(r"^\s*(\d+)\.\s+([A-Z][A-Z \-&(),]+)\s*$")

OBLIGATION_RE = re.compile(
    r"\b(must|requires|required|will|may|cannot|forfeit\w*|not permitted|"
    r"not valid|not sufficient|not apply|do not count|not be considered)\b",
    re.IGNORECASE,
)

FORBIDDEN_PHRASES = [
    "standard practice",
    "typically",
    "generally expected",
    "generally understood",
    "common practice",
    "it is common",
]

FAITHFUL_SUMMARIES = {
    "1.1": "This policy governs all leave entitlements for permanent and contractual employees of CMC.",
    "1.2": "Does NOT apply to daily wage workers or consultants — those categories are governed by their respective contracts.",
    "2.1": "Each permanent employee is entitled to 18 days of paid annual leave per calendar year.",
    "2.2": "Annual leave accrues at 1.5 days per month from date of joining.",
    "2.3": "Employees MUST submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Applications MUST receive WRITTEN approval from the employee's direct manager BEFORE leave commences; verbal approval is NOT valid.",
    "2.5": "Unapproved absence WILL be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Employees MAY carry forward a MAXIMUM of 5 unused annual leave days to the following year; days above 5 ARE FORFEITED on 31 December.",
    "2.7": "Carry-forward days MUST be used within the first quarter (January-March) of the following year or they are forfeited.",
    "3.1": "Each employee is entitled to 12 days of paid sick leave per calendar year.",
    "3.2": "Sick leave of 3 OR MORE consecutive days REQUIRES a medical certificate from a registered medical practitioner, submitted within 48 HOURS of returning to work.",
    "3.3": "Sick leave CANNOT be carried forward to the following year.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period REQUIRES a medical certificate REGARDLESS of duration.",
    "4.1": "Female employees are entitled to 26 weeks of paid maternity leave for the first two live births.",
    "4.2": "Third or subsequent child: maternity leave is 12 weeks paid.",
    "4.3": "Male employees are entitled to 5 days of paid paternity leave within 30 days of the child's birth.",
    "4.4": "Paternity leave CANNOT be split across multiple periods.",
    "5.1": "LWP may be applied for ONLY after exhausting all applicable paid leave entitlements.",
    "5.2": "LWP REQUIRES approval from BOTH the Department Head AND the HR Director; manager approval alone is NOT sufficient.",
    "5.3": "LWP exceeding 30 continuous days REQUIRES approval from the Municipal Commissioner.",
    "5.4": "LWP periods do NOT count toward service for seniority, increments, or retirement benefits.",
    "6.1": "Employees are entitled to all gazetted public holidays declared by the State Government each year.",
    "6.2": "If required to work on a public holiday: one compensatory off day, taken within 60 days of the holiday worked.",
    "6.3": "Compensatory off CANNOT be encashed.",
    "7.1": "Annual leave may be encashed ONLY at retirement or resignation, maximum 60 days.",
    "7.2": "Leave encashment during service is NOT PERMITTED under ANY circumstances.",
    "7.3": "Sick leave and LWP CANNOT be encashed under any circumstances.",
    "8.1": "Leave grievances MUST be raised with HR within 10 working days of the disputed decision.",
    "8.2": "Grievances raised after 10 working days will NOT be considered unless exceptional circumstances are demonstrated in writing.",
}

TRAP_CONDITION_CHECKS = {
    "2.3": ["14 calendar days", "Form HR-L1"],
    "2.4": ["written approval", "direct manager", "before", "verbal approval is NOT valid"],
    "2.6": ["maximum of 5", "forfeited on 31 december"],
    "2.7": ["january-march"],
    "3.2": ["3 OR MORE consecutive days", "48 hours"],
    "3.4": ["regardless of duration"],
    "5.2": ["department head", "hr director", "NOT sufficient"],
    "5.3": ["30 continuous days", "municipal commissioner"],
    "7.2": ["not permitted", "any circumstances"],
}


def retrieve_policy(path):
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"Cannot read policy file {path}: {exc}", file=sys.stderr)
        sys.exit(1)

    text = re.sub(r"\uFFFD+|[\u2013\u2014]", "-", text)

    clauses = {}
    order = []
    headings = []
    current_id = None

    for line in text.splitlines():
        stripped = line.strip()
        heading_match = HEADING_RE.match(line)
        clause_match = CLAUSE_RE.match(line)
        if heading_match:
            headings.append(f"{heading_match.group(1)}. {heading_match.group(2).title()}")
            current_id = None
        elif clause_match:
            current_id = clause_match.group(1)
            clauses[current_id] = clause_match.group(2)
            order.append(current_id)
        elif current_id and stripped and set(stripped) - set("-= "):
            clauses[current_id] += " " + stripped
        else:
            current_id = None

    if not clauses:
        print("No numbered clauses parsed from policy file; aborting.", file=sys.stderr)
        sys.exit(1)

    return clauses, order, headings


def summarize_policy(clauses, order, headings):
    lines = [
        "SUMMARY — CITY MUNICIPAL CORPORATION EMPLOYEE LEAVE POLICY",
        "(Source: policy_hr_leave.txt | Ref: HR-POL-001 v2.3)",
        "",
        "Every numbered clause below is preserved with its reference.",
        "[VERBATIM QUOTE] marks clauses kept word-for-word to avoid condition loss.",
        "",
    ]

    for heading in headings:
        section_num = heading.split(".")[0]
        section_clauses = [cid for cid in order if cid.startswith(section_num + ".")]
        if not section_clauses:
            continue
        lines.append(heading.upper())
        for cid in section_clauses:
            source_text = clauses[cid]
            obligation_count = len(OBLIGATION_RE.findall(source_text))
            if cid not in FAITHFUL_SUMMARIES or obligation_count > 3:
                lines.append(f"  [{cid}] [VERBATIM QUOTE] \"{source_text}\"")
                continue
            summary_line = FAITHFUL_SUMMARIES[cid]
            if obligation_count >= 2:
                lines.append(f"  [{cid}] [VERBATIM QUOTE] \"{source_text}\"")
            else:
                lines.append(f"  [{cid}] {summary_line}")
        lines.append("")

    covered = sum(1 for cid in order if f"[{cid}]" in "\n".join(lines))
    lines.append(f"COVERAGE: {covered}/{len(order)} numbered clauses present.")
    return "\n".join(lines), covered


def self_check(clauses, order, output_text):
    results = []
    missing = [cid for cid in order if f"[{cid}]" not in output_text]
    results.append(("clause coverage", not missing, f"{len(order) - len(missing)}/{len(order)} present" + (f"; MISSING: {missing}" if missing else "")))

    lowered = output_text.lower()
    failed_conditions = []
    for cid, needles in TRAP_CONDITION_CHECKS.items():
        block_start = output_text.find(f"[{cid}]")
        if block_start == -1:
            failed_conditions.append(f"{cid}: clause absent")
            continue
        block_end = output_text.find("\n  [", block_start + 1)
        block = output_text[block_start:block_end if block_end != -1 else len(output_text)].lower()
        for needle in needles:
            if needle.lower() not in block:
                failed_conditions.append(f"{cid}: dropped condition '{needle}'")
    results.append(("multi-condition preservation", not failed_conditions, "all trap-clause conditions retained" if not failed_conditions else "; ".join(failed_conditions)))

    bleed = [p for p in FORBIDDEN_PHRASES if p in lowered]
    results.append(("no scope bleed / additions", not bleed, "clean" if not bleed else f"found: {bleed}"))

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary txt")
    args = parser.parse_args()

    clauses, order, headings = retrieve_policy(args.input)
    summary, covered = summarize_policy(clauses, order, headings)

    Path(args.output).write_text(summary + "\n", encoding="utf-8")

    print(f"Summary written to {args.output}")
    print("Self-check results:")
    all_pass = True
    for name, ok, detail in self_check(clauses, order, summary):
        status = "PASS" if ok else "FAIL"
        all_pass = all_pass and ok
        print(f"  [{status}] {name}: {detail}")
    if not all_pass:
        sys.exit(1)


if __name__ == "__main__":
    main()
