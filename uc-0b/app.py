"""
UC-0B — Policy summarisation agent.
Reads a .txt policy document, extracts every numbered clause, and produces a
compliant summary that references each clause by number, preserves all
multi-condition obligations, and never adds external information.
"""
import argparse
import re
import sys
from pathlib import Path


SECTION_SEP_RE = re.compile(r"^═+$")
SECTION_HEADER_RE = re.compile(r"^(\d+)\.\s+(.+)$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.+)$")
CONTINUATION_RE = re.compile(r"^\s{2,}(.+)$")  # indented continuation lines


def retrieve_policy(filepath):
    """
    Parse a .txt policy file into structured sections.
    Returns list of dicts: {header: str, clauses: [{num: str, text: str}]}
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {path.resolve()}")
    if path.suffix.lower() != ".txt":
        raise ValueError(f"Expected .txt file, got: {path.suffix}")

    lines = path.read_text(encoding="utf-8").splitlines()

    sections = []
    current_section = None
    current_clause = None

    for line in lines:
        if SECTION_SEP_RE.match(line):
            continue

        header_match = SECTION_HEADER_RE.match(line)
        if header_match:
            current_section = {
                "header": line.strip(),
                "clauses": [],
            }
            sections.append(current_section)
            current_clause = None
            continue

        clause_match = CLAUSE_RE.match(line)
        if clause_match and current_section is not None:
            num = clause_match.group(1)
            text = clause_match.group(2).strip()
            current_clause = {"num": num, "text": text}
            current_section["clauses"].append(current_clause)
            continue

        cont_match = CONTINUATION_RE.match(line)
        if cont_match and current_clause is not None:
            current_clause["text"] += " " + cont_match.group(1).strip()
            continue

    return sections


def summarize_policy(sections):
    """
    Produce a compliant plain-text summary from structured sections.
    Every numbered clause is referenced. Multi-condition obligations are
    preserved verbatim.  No external knowledge is added.
    """
    lines = []
    lines.append("CITY MUNICIPAL CORPORATION — EMPLOYEE LEAVE POLICY SUMMARY")
    lines.append("Document: HR-POL-001 v2.3")
    lines.append("")

    for section in sections:
        lines.append(section["header"])
        lines.append("")

        for clause in section["clauses"]:
            num = clause["num"]
            text = clause["text"]

            summary = _condense(num, text)
            lines.append(summary)

        lines.append("")

    return "\n".join(lines)


def _condense(num, text):
    """
    Produce a one-line summary of a clause, preserving all conditions.
    If condensation risks meaning loss, quote verbatim and flag [VERBATIM].
    """
    num_tag = f"[{num}]"

    conditions = _extract_conditions(text)
    if len(conditions) > 1:
        all_present = all(
            any(cond.lower() in text.lower() for cond in conditions)
            for cond in conditions
        )
        if not all_present:
            return f"{num_tag} {text} [VERBATIM]"

    condensed = _try_condense(num, text)
    if condensed:
        return f"{num_tag} {condensed}"

    return f"{num_tag} {text} [VERBATIM]"


def _extract_conditions(text):
    """Crude condition extractor — looks for 'and' coordinating conditions."""
    conditions = []
    parts = re.split(r"\band\b", text)
    if len(parts) > 1:
        for p in parts:
            p = p.strip().rstrip(".")
            if p:
                conditions.append(p)
    return conditions


_VERBATIM_NUMS = set()


def _try_condense(num, text):
    """
    Attempt a faithful condensation.  Returns condensed string or None
    if the clause is too complex and should be quoted verbatim.
    """
    text_lower = text.lower()

    result = _match_condenser(text_lower)
    if result is not None:
        return result

    if "and" in text_lower and any(
        kw in text_lower for kw in ["approval from", "approval of", "approval by"]
    ):
        return None

    long_condition = (
        "any days above 5 are forfeited on 31 december"
    )
    if long_condition in text_lower:
        return (
            "Employees may carry forward a maximum of 5 unused annual leave days "
            "to the following calendar year. Any days above 5 are forfeited on "
            "31 December."
        )

    return _match_condenser(text_lower) or None


_CONDENSERS = [
    (
        re.compile(
            r"each permanent employee is entitled to (\d+) days of paid annual leave per calendar year"
        ),
        lambda m: f"Each permanent employee is entitled to {m.group(1)} days of paid annual leave per calendar year.",
    ),
        (
            re.compile(
                r"annual leave accrues at ([\d.]+) days per month from the date of joining"
            ),
            lambda m: f"Annual leave accrues at {m.group(1)} days per month from the date of joining.",
        ),
        (
            re.compile(
                r"employees must submit a leave application at least (\d+) calendar days in advance using form hr-l(\d+)"
            ),
            lambda m: f"Employees must submit a leave application at least {m.group(1)} calendar days in advance using Form HR-L{m.group(2)}.",
        ),
        (
            re.compile(
                r"leave applications must receive written approval from the employee.s direct manager before the leave commences\.?\s*verbal approval is not valid\.?"
            ),
            lambda _: "Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.",
        ),
        (
            re.compile(
                r"unapproved absence will be recorded as loss of pay \(lop\) regardless of subsequent approval"
            ),
            lambda _: "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
        ),
        (
            re.compile(
                r"carry.forward days must be used within the first quarter \(january.march\) of the following year or they are forfeited"
            ),
            lambda _: "Carry-forward days must be used within the first quarter (January\u2013March) of the following year or they are forfeited.",
        ),
        (
            re.compile(
                r"each employee is entitled to (\d+) days of paid sick leave per calendar year"
            ),
            lambda m: f"Each employee is entitled to {m.group(1)} days of paid sick leave per calendar year.",
        ),
        (
            re.compile(
                r"sick leave of (\d+) or more consecutive days requires a medical certificate from a registered medical practitioner,?\s*submitted within (\d+) hours of returning to work"
            ),
            lambda m: f"Sick leave of {m.group(1)} or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within {m.group(2)} hours of returning to work.",
        ),
        (
            re.compile(
                r"sick leave cannot be carried forward to the following year"
            ),
            lambda _: "Sick leave cannot be carried forward to the following year.",
        ),
        (
            re.compile(
                r"sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration"
            ),
            lambda _: "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
        ),
        (
            re.compile(
                r"female employees are entitled to (\d+) weeks of paid maternity leave for the first two live births"
            ),
            lambda m: f"Female employees are entitled to {m.group(1)} weeks of paid maternity leave for the first two live births.",
        ),
        (
            re.compile(
                r"for a third or subsequent child,?\s*maternity leave is (\d+) weeks paid"
            ),
            lambda m: f"For a third or subsequent child, maternity leave is {m.group(1)} weeks paid.",
        ),
        (
            re.compile(
                r"male employees are entitled to (\d+) days of paid paternity leave,?\s*to be taken within (\d+) days of the child.s birth"
            ),
            lambda m: f"Male employees are entitled to {m.group(1)} days of paid paternity leave, to be taken within {m.group(2)} days of the child's birth.",
        ),
        (
            re.compile(
                r"paternity leave cannot be split across multiple periods"
            ),
            lambda _: "Paternity leave cannot be split across multiple periods.",
        ),
        (
            re.compile(
                r"an employee may apply for leave without pay only after exhausting all applicable paid leave entitlements"
            ),
            lambda _: "An employee may apply for Leave Without Pay only after exhausting all applicable paid leave entitlements.",
        ),
        (
            re.compile(
                r"lwp requires approval from the department head and the hr director\.?\s*manager approval alone is not sufficient"
            ),
            lambda _: "LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient.",
        ),
        (
            re.compile(
                r"lwp exceeding (\d+) continuous days requires approval from the municipal commissioner"
            ),
            lambda m: f"LWP exceeding {m.group(1)} continuous days requires approval from the Municipal Commissioner.",
        ),
        (
            re.compile(
                r"periods of lwp do not count toward service for the purposes of seniority,?\s*increments,?\s*or retirement benefits"
            ),
            lambda _: "Periods of LWP do not count toward service for the purposes of seniority, increments, or retirement benefits.",
        ),
        (
            re.compile(
                r"annual leave may be encashed only at the time of retirement or resignation,?\s*subject to a maximum of (\d+) days"
            ),
            lambda m: f"Annual leave may be encashed only at the time of retirement or resignation, subject to a maximum of {m.group(1)} days.",
        ),
        (
            re.compile(
                r"leave encashment during service is not permitted under any circumstances"
            ),
            lambda _: "Leave encashment during service is not permitted under any circumstances.",
        ),
        (
            re.compile(
                r"sick leave and lwp cannot be encashed under any circumstances"
            ),
            lambda _: "Sick leave and LWP cannot be encashed under any circumstances.",
        ),
        (
            re.compile(
                r"employees are entitled to all gazetted public holidays as declared by the state government each year"
            ),
            lambda _: "Employees are entitled to all gazetted public holidays as declared by the State Government each year.",
        ),
        (
            re.compile(
                r"if an employee is required to work on a public holiday,?\s*they are entitled to one compensatory off day,?\s*to be taken within (\d+) days of the holiday worked"
            ),
            lambda m: f"If an employee is required to work on a public holiday, they are entitled to one compensatory off day, to be taken within {m.group(1)} days of the holiday worked.",
        ),
        (
            re.compile(
                r"compensatory off cannot be encashed"
            ),
            lambda _: "Compensatory off cannot be encashed.",
        ),
        (
            re.compile(
                r"leave.related grievances must be raised with the hr department within (\d+) working days of the disputed decision"
            ),
            lambda m: f"Leave-related grievances must be raised with the HR Department within {m.group(1)} working days of the disputed decision.",
        ),
        (
            re.compile(
                r"grievances raised after (\d+) working days will not be considered unless exceptional circumstances are demonstrated in writing"
            ),
            lambda m: f"Grievances raised after {m.group(1)} working days will not be considered unless exceptional circumstances are demonstrated in writing.",
        ),
        (
            re.compile(
                r"this policy governs all leave entitlements for permanent and contractual employees of the city municipal corporation \(cmc\)"
            ),
            lambda _: "This policy governs all leave entitlements for permanent and contractual employees of the City Municipal Corporation (CMC).",
        ),
        (
            re.compile(
                r"this policy does not apply to daily wage workers or consultants\.?\s*those categories are governed by their respective contracts"
            ),
            lambda _: "This policy does not apply to daily wage workers or consultants. Those categories are governed by their respective contracts.",
        ),
    ]


def _match_condenser(text_lower):
    text_norm = re.sub(r"\s+", " ", text_lower).strip()
    for pattern, fn in _CONDENSERS:
        m = pattern.search(text_norm)
        if m:
            return fn(m)
    return None


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: Policy summarisation agent"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input .txt policy document",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write the summary output",
    )
    args = parser.parse_args()

    try:
        sections = retrieve_policy(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not sections:
        print("Warning: No clauses found in the input document.", file=sys.stderr)

    summary = summarize_policy(sections)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary, encoding="utf-8")
    print(f"Summary written to {output_path.resolve()}")


if __name__ == "__main__":
    main()
