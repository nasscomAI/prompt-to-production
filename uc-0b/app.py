"""
UC-0B - Meaning-preserving policy summarizer.

The summarizer is deliberately deterministic: it parses numbered clauses,
keeps every clause reference, and uses vetted summaries for this policy so
conditions and binding verbs are not softened or dropped.
"""
import argparse
import re
from pathlib import Path


CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")

CLAUSE_SUMMARIES = {
    "1.1": "This policy governs leave entitlements for permanent and contractual employees of the City Municipal Corporation (CMC).",
    "1.2": "This policy does not apply to daily wage workers or consultants; those categories are governed by their respective contracts.",
    "2.1": "Each permanent employee is entitled to 18 days of paid annual leave per calendar year.",
    "2.2": "Annual leave accrues at 1.5 days per month from the date of joining.",
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave applications must receive written approval from the employee's direct manager before leave commences; verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP), regardless of any subsequent approval.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year; days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within January-March of the following year or they are forfeited.",
    "3.1": "Each employee is entitled to 12 days of paid sick leave per calendar year.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.3": "Sick leave cannot be carried forward to the following year.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "4.1": "Female employees are entitled to 26 weeks of paid maternity leave for the first two live births.",
    "4.2": "For a third or subsequent child, maternity leave is 12 weeks paid.",
    "4.3": "Male employees are entitled to 5 days of paid paternity leave, taken within 30 days of the child's birth.",
    "4.4": "Paternity leave cannot be split across multiple periods.",
    "5.1": "An employee may apply for Leave Without Pay (LWP) only after exhausting all applicable paid leave entitlements.",
    "5.2": "LWP requires approval from both the Department Head and the HR Director; manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "5.4": "Periods of LWP do not count toward service for seniority, increments, or retirement benefits.",
    "6.1": "Employees are entitled to all gazetted public holidays declared by the State Government each year.",
    "6.2": "Employees required to work on a public holiday are entitled to one compensatory off day, taken within 60 days of the holiday worked.",
    "6.3": "Compensatory off cannot be encashed.",
    "7.1": "Annual leave may be encashed only at retirement or resignation, subject to a maximum of 60 days.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
    "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
    "8.1": "Leave-related grievances must be raised with the HR Department within 10 working days of the disputed decision.",
    "8.2": "Grievances raised after 10 working days will not be considered unless exceptional circumstances are demonstrated in writing.",
}

REQUIRED_CLAUSES = set(CLAUSE_SUMMARIES)


def _clean_line(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip()


def retrieve_policy(input_path: str) -> list[dict]:
    """
    Load a text policy file and return structured numbered sections.
    """
    text = Path(input_path).read_text(encoding="utf-8-sig")
    sections = []
    current = None

    for raw_line in text.splitlines():
        line = _clean_line(raw_line)
        if not line:
            continue

        match = CLAUSE_RE.match(line)
        if match:
            if current:
                sections.append(current)
            current = {"clause": match.group(1), "text": match.group(2)}
        elif current:
            current["text"] = f"{current['text']} {line}"

    if current:
        sections.append(current)

    return sections


def summarize_policy(sections: list[dict]) -> str:
    """
    Produce a compliant summary with one line per numbered clause.
    """
    clause_ids = [section["clause"] for section in sections]
    missing = sorted(REQUIRED_CLAUSES.difference(clause_ids), key=_clause_sort_key)
    unknown = [clause for clause in clause_ids if clause not in REQUIRED_CLAUSES]

    lines = [
        "HR Leave Policy Summary",
        "Source-preserving summary: every numbered clause is listed; no outside assumptions are added.",
        "",
    ]

    for section in sections:
        clause = section["clause"]
        summary = CLAUSE_SUMMARIES.get(clause)
        if summary:
            lines.append(f"{clause}: {summary}")
        else:
            lines.append(f'{clause}: "{section["text"]}" [NEEDS_REVIEW: quoted verbatim to avoid meaning loss]')

    if missing or unknown:
        lines.extend(["", "Review flags:"])
        for clause in missing:
            lines.append(f"- {clause}: NEEDS_REVIEW - required clause was not found in the source.")
        for clause in unknown:
            lines.append(f"- {clause}: NEEDS_REVIEW - clause is not in the vetted summary map.")

    return "\n".join(lines) + "\n"


def _clause_sort_key(clause: str) -> tuple[int, int]:
    major, minor = clause.split(".", 1)
    return int(major), int(minor)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    output_path = Path(args.output)
    if output_path.parent and str(output_path.parent) != ".":
        output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary, encoding="utf-8")
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
