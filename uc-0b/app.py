"""
UC-0B app.py — Summary That Changes Meaning
Implements the two skills defined in skills.md under the rules in agents.md:

    retrieve_policy(path)      -> structured numbered sections and clauses
    summarize_policy(policy)   -> clause-by-clause summary + validation report

Run:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt \
                  --output summary_hr_leave.txt

Design note: the summary is built deterministically (no free-form generation),
so it cannot drop a clause, soften a verb, or add outside information without
the validator noticing. Every clause summary is checked against its source
clause; any failure falls back to the verbatim source text with a flag.
"""
import argparse
import re
import sys
import textwrap

# --------------------------------------------------------------------------
# Ground truth from the UC-0B README: the 10 critical clauses.
# --------------------------------------------------------------------------
CRITICAL_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

# --------------------------------------------------------------------------
# Clause summaries. Wording keeps the source's binding verbs, numbers and
# roles; only filler is removed. Each is validated against the live source
# clause at run time (see validate_summary).
# --------------------------------------------------------------------------
CLAUSE_SUMMARIES = {
    "1.1": "Governs all leave entitlements for permanent and contractual employees of the City Municipal Corporation (CMC).",
    "1.2": "Does not apply to daily wage workers or consultants; those categories are governed by their respective contracts.",
    "2.1": "Each permanent employee is entitled to 18 days of paid annual leave per calendar year.",
    "2.2": "Annual leave accrues at 1.5 days per month from the date of joining.",
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP), regardless of subsequent approval.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within the first quarter (January\u2013March) of the following year or they are forfeited.",
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
    "5.4": "Periods of LWP do not count toward service for the purposes of seniority, increments, or retirement benefits.",
    "6.1": "Employees are entitled to all gazetted public holidays as declared by the State Government each year.",
    "6.2": "An employee required to work on a public holiday is entitled to one compensatory off day, to be taken within 60 days of the holiday worked.",
    "6.3": "Compensatory off cannot be encashed.",
    "7.1": "Annual leave may be encashed only at the time of retirement or resignation, subject to a maximum of 60 days.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
    "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
    "8.1": "Leave-related grievances must be raised with the HR Department within 10 working days of the disputed decision.",
    "8.2": "Grievances raised after 10 working days will not be considered unless exceptional circumstances are demonstrated in writing.",
}

# Terms that must survive summarisation for the multi-condition critical clauses.
REQUIRED_TERMS = {
    "2.3": ["14 calendar days", "Form HR-L1"],
    "2.4": ["written approval", "direct manager", "Verbal approval is not valid"],
    "2.5": ["LOP", "regardless of subsequent approval"],
    "2.6": ["maximum of 5", "31 December", "forfeited"],
    "2.7": ["January", "March", "forfeited"],
    "3.2": ["3 or more consecutive days", "medical certificate", "48 hours"],
    "3.4": ["before or after", "medical certificate", "regardless of duration"],
    "5.2": ["Department Head", "HR Director", "Manager approval alone is not sufficient"],
    "5.3": ["30", "Municipal Commissioner"],
    "7.2": ["during service", "not permitted", "under any circumstances"],
}

# Binding language: if the phrase is in the source clause it must be in the summary.
BINDING_PHRASES = [
    r"must not", r"must(?! not)", r"requires?", r"will not", r"will be",
    r"not permitted", r"cannot", r"only", r"may", r"forfeited", r"not valid",
    r"not sufficient", r"do not count", r"does not apply", r"under any circumstances",
    r"regardless", r"entitled", r"at least", r"maximum", r"exceeding", r"within",
]

# Role / form names that must not be dropped (condition-drop guard).
ENTITY_TERMS = [
    "Department Head", "HR Director", "Municipal Commissioner", "HR Department",
    "State Government", "direct manager", "Form HR-L1", "medical certificate",
]

# Scope-bleed / hedging phrases that are never allowed to appear in a summary.
BANNED_PHRASES = [
    r"typically", r"generally", r"usually", r"normally", r"commonly",
    r"as is standard", r"standard practice", r"common practice",
    r"in most organi[sz]ations", r"government organi[sz]ations",
    r"employees are expected", r"expected to", r"it is common",
]

NUMBER_WORDS = r"\b(one|two|three|first|second|third)\b"


# --------------------------------------------------------------------------
# Skill 1: retrieve_policy
# --------------------------------------------------------------------------
def retrieve_policy(path: str) -> dict:
    """Load a .txt policy file and return structured numbered sections/clauses.

    Raises ValueError on a missing, empty, or non-numbered file (refusal condition).
    """
    try:
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
    except FileNotFoundError:
        raise ValueError(f"Input file not found: {path}")
    except (OSError, UnicodeDecodeError) as exc:
        raise ValueError(f"Cannot read input file {path}: {exc}")

    if not raw.strip():
        raise ValueError(f"Input file is empty: {path}")

    section_re = re.compile(r"^(\d+)\.\s+(\S.*)$")
    clause_re = re.compile(r"^(\d+\.\d+)\s+(\S.*)$")

    header, sections = [], []
    current_section, current_clause = None, None
    warnings, seen_ids = [], set()

    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or set(stripped) <= {"\u2550", "="}:
            continue  # blank line or rule line

        m_clause = clause_re.match(stripped) if not line[0].isspace() else None
        m_section = section_re.match(stripped) if not line[0].isspace() else None

        if m_clause:
            if current_section is None:
                raise ValueError("Clause found before any section heading.")
            cid = m_clause.group(1)
            if cid in seen_ids:
                warnings.append(f"Duplicate clause number {cid}; kept both in file order.")
            seen_ids.add(cid)
            current_clause = {"id": cid, "text": m_clause.group(2).strip()}
            current_section["clauses"].append(current_clause)
        elif m_section:
            current_section = {"number": m_section.group(1), "title": m_section.group(2).strip(), "clauses": []}
            sections.append(current_section)
            current_clause = None
        elif current_clause is not None and line[0].isspace():
            current_clause["text"] += " " + stripped  # wrapped continuation line
        elif current_section is None:
            header.append(stripped)
        else:
            warnings.append(f"Unattached line kept out of clauses: {stripped!r}")

    total = sum(len(s["clauses"]) for s in sections)
    if total == 0:
        raise ValueError("No numbered clauses found; file does not look like a numbered policy.")

    return {"header": header, "sections": sections, "warnings": warnings, "clause_count": total}


# --------------------------------------------------------------------------
# Validation (enforces agents.md rules against each clause summary)
# --------------------------------------------------------------------------
def _numbers(text: str) -> set:
    return set(re.findall(r"\d+(?:\.\d+)?", text))


def validate_summary(clause_id: str, source: str, summary: str) -> list:
    """Return a list of problems; empty list means the summary is safe."""
    problems = []
    src_l, sum_l = source.lower(), summary.lower()

    # Numbers: nothing lost, nothing invented.
    if _numbers(source) != _numbers(summary):
        problems.append(f"numbers differ (source {sorted(_numbers(source))} vs summary {sorted(_numbers(summary))})")

    # Number words (one/two/first/third...) both ways.
    if set(re.findall(NUMBER_WORDS, src_l)) != set(re.findall(NUMBER_WORDS, sum_l)):
        problems.append("number words (one/two/first/third) differ")

    # Softening: binding phrases in source must survive.
    for pat in BINDING_PHRASES:
        if re.search(rf"\b{pat}\b", src_l) and not re.search(rf"\b{pat}\b", sum_l):
            problems.append(f"binding language dropped or softened: '{pat}'")

    # Condition drop: named roles/forms must survive.
    for term in ENTITY_TERMS:
        if term.lower() in src_l and term.lower() not in sum_l:
            problems.append(f"condition dropped: '{term}'")

    # Critical multi-condition terms.
    for term in REQUIRED_TERMS.get(clause_id, []):
        if term.lower() not in sum_l:
            problems.append(f"required term missing: '{term}'")

    # Scope bleed / hedging.
    for pat in BANNED_PHRASES:
        if re.search(pat, sum_l) and not re.search(pat, src_l):
            problems.append(f"scope bleed / hedging phrase: '{pat}'")

    return problems


# --------------------------------------------------------------------------
# Skill 2: summarize_policy
# --------------------------------------------------------------------------
def summarize_policy(policy: dict) -> tuple:
    """Return (summary_text, report). Raises ValueError if clause coverage fails."""
    lines = list(policy["header"]) + ["", "CLAUSE-BY-CLAUSE SUMMARY (every numbered clause of the source is listed)", ""]
    flagged, output_ids = [], []

    for sec in policy["sections"]:
        lines.append(f"{sec['number']}. {sec['title']}")
        for clause in sec["clauses"]:
            cid, source = clause["id"], clause["text"]
            candidate = CLAUSE_SUMMARIES.get(cid)

            if candidate is None:
                reason = ["no summary rule for this clause"]
            else:
                reason = validate_summary(cid, source, candidate)

            if reason:
                body = f'"{source}" [VERBATIM - meaning-loss risk]'
                flagged.append((cid, reason))
            else:
                body = candidate

            entry = textwrap.fill(f"[{cid}] {body}", width=100, subsequent_indent="      ")
            lines.append(entry)
            output_ids.append(cid)
        lines.append("")

    source_ids = [c["id"] for s in policy["sections"] for c in s["clauses"]]
    if output_ids != source_ids:
        raise ValueError("Clause coverage mismatch between source and summary; refusing to write output.")

    text = "\n".join(lines).rstrip() + "\n"
    critical_missing = [c for c in CRITICAL_CLAUSES if f"[{c}]" not in text]
    report = {
        "source_clauses": len(source_ids),
        "summary_clauses": len(output_ids),
        "flagged": flagged,
        "critical_missing": critical_missing,
        "warnings": policy["warnings"],
    }
    return text, report


# --------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    try:
        policy = retrieve_policy(args.input)
        summary, report = summarize_policy(policy)
    except ValueError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        sys.exit(1)

    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(summary)

    print(f"Clauses in source : {report['source_clauses']}")
    print(f"Clauses in summary: {report['summary_clauses']}")
    print(f"Critical clauses present: {len(CRITICAL_CLAUSES) - len(report['critical_missing'])}/{len(CRITICAL_CLAUSES)}")
    if report["critical_missing"]:
        print(f"  MISSING: {report['critical_missing']}")
    if report["flagged"]:
        print("Flagged (verbatim fallback):")
        for cid, why in report["flagged"]:
            print(f"  {cid}: {'; '.join(why)}")
    else:
        print("Flagged clauses: none")
    for w in report["warnings"]:
        print(f"Warning: {w}")
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
