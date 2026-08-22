"""
UC-0B app.py — Deterministic policy summariser.

Implements the two skills defined in skills.md:
  - retrieve_policy: loads a .txt policy file into structured numbered sections
  - summarize_policy: produces a clause-tagged summary enforcing agents.md rules

Run:
  python app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
"""
import argparse
import re
import sys

CRITICAL_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

SECTION_RE = re.compile(r"^(\d+)\.\s+\S")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")

SOFTENERS = [
    "typically", "generally", "as is standard practice", "standard practice",
    "where possible", "is expected to", "should ideally", "usually",
]

CONDITION_REQUIREMENTS = {
    "2.3": ["14"],
    "2.4": ["written approval", "verbal approval is not valid"],
    "2.5": ["loss of pay", "regardless of subsequent approval"],
    "2.6": ["maximum of 5", "forfeited on 31 december"],
    "2.7": ["january", "march", "forfeited"],
    "3.2": ["3 or more consecutive days", "within 48 hours of returning to work"],
    "3.4": ["regardless of duration"],
    "5.2": ["department head", "hr director"],
    "5.3": ["30 continuous days", "municipal commissioner"],
    "7.2": ["not permitted under any circumstances"],
}

SUMMARY_TEXT = {
    "1.1": "This policy governs all leave entitlements for permanent and contractual employees of the City Municipal Corporation (CMC).",
    "1.2": "This policy does not apply to daily wage workers or consultants; those categories are governed by their respective contracts.",
    "2.1": "Each permanent employee is entitled to 18 days of paid annual leave per calendar year.",
    "2.2": "Annual leave accrues at 1.5 days per month from the date of joining.",
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave applications must receive written approval from the employee's direct manager before the leave commences; verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
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


def retrieve_policy(path):
    try:
        raw = open(path, encoding="utf-8").read()
    except FileNotFoundError:
        raise SystemExit(f"ERROR: input file not found: {path}")
    except UnicodeDecodeError as e:
        raise SystemExit(f"ERROR: cannot decode {path} as UTF-8: {e}")

    sections = []
    current_section = None
    current_clause = None
    unrecognised = []

    for lineno, line in enumerate(raw.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or set(stripped) == {"═"}:
            continue

        clause_match = CLAUSE_RE.match(stripped)
        section_match = SECTION_RE.match(stripped)
        if clause_match:
            num, first = clause_match.group(1), clause_match.group(2).strip()
            existing = next((c for s in sections for c in s["clauses"] if c["number"] == num), None)
            if existing:
                raise SystemExit(f"ERROR: duplicate clause number {num} at line {lineno}")
            current_clause = {"number": num, "text": [first]}
            current_section["clauses"].append(current_clause)
        elif section_match:
            num, heading = stripped.split(".", 1)
            current_section = {"section_number": num.strip(), "heading": heading.strip(), "clauses": []}
            current_clause = None
            sections.append(current_section)
        elif current_section and current_clause is not None:
            current_clause["text"].append(stripped)
        elif current_section is None:
            continue
        else:
            unrecognised.append((lineno, stripped))

    if unrecognised:
        details = "; ".join(f"line {ln}: '{tx}'" for ln, tx in unrecognised[:10])
        raise SystemExit(f"ERROR: unrecognised lines outside any numbered clause: {details}")

    for sec in sections:
        for c in sec["clauses"]:
            c["text"] = " ".join(c["text"])

    return sections


def render_clause(clause):
    num = clause["number"]
    if num in SUMMARY_TEXT:
        return f"[{num}] {SUMMARY_TEXT[num]}"
    return f'[{num}] "{clause["text"]}" [VERBATIM QUOTE]'


def verify(sections, output_text):
    errors = []
    source_numbers = {c["number"] for s in sections for c in s["clauses"]}
    cited = set(re.findall(r"\[(\d+\.\d+)\]", output_text))

    missing_critical = [n for n in CRITICAL_CLAUSES if n not in cited]
    if missing_critical:
        errors.append(f"critical clauses omitted from summary: {missing_critical}")

    uncovered = source_numbers - cited
    if uncovered:
        errors.append(f"source clauses not covered in summary: {sorted(uncovered)}")

    low = output_text.lower()
    for softener in SOFTENERS:
        if softener in low:
            errors.append(f"forbidden softener present: '{softener}'")

    by_num = {c["number"]: c["text"].lower() for s in sections for c in s["clauses"]}
    rendered_lines = {m.group(1): m.group(2).lower()
                      for m in re.finditer(r"\[(\d+\.\d+)\]\s*(.*)", output_text)}
    for num in CRITICAL_CLAUSES:
        rendered = rendered_lines.get(num, "")
        for token in CONDITION_REQUIREMENTS.get(num, []):
            if token.lower() not in rendered:
                errors.append(f"clause {num}: required condition '{token}' missing from rendered text")
            elif token.lower() not in by_num.get(num, ""):
                errors.append(f"clause {num}: condition '{token}' not traceable to source text")

    if errors:
        raise SystemExit("VERIFICATION FAILED:\n  - " + "\n  - ".join(errors))


def summarize_policy(sections):
    if not any(c["number"] in CRITICAL_CLAUSES for s in sections for c in s["clauses"]):
        raise SystemExit("ERROR: none of the required critical clauses found in input; refusing to summarise the wrong document.")

    lines = ["CITY MUNICIPAL CORPORATION - EMPLOYEE LEAVE POLICY - SUMMARY",
             "(Every line is tagged with its source clause reference.)", ""]
    for sec in sections:
        heading = f"{sec['section_number']}. {sec['heading']}"
        lines.append(heading.upper())
        for clause in sec["clauses"]:
            lines.append(render_clause(clause))
        lines.append("")
    output_text = "\n".join(lines).rstrip() + "\n"

    verify(sections, output_text)
    return output_text


def main():
    parser = argparse.ArgumentParser(description="Summarise a CMC leave-policy .txt file with clause-level fidelity.")
    parser.add_argument("--input", required=True, help="Path to the source policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write the summary .txt file")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    output_text = summarize_policy(sections)
    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(output_text)
    print(f"Wrote summary to {args.output} ({len(output_text.splitlines())} lines)")


if __name__ == "__main__":
    main()
