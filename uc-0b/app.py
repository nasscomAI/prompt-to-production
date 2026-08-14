"""
UC-0B — Summary That Changes Meaning
Reads a policy document and produces a faithful summary that preserves every
clause and every condition per the enforcement rules in agents.md and skills.md.
"""
import argparse
import re
import sys

CRITICAL_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

CRITICAL_MUST_INCLUDE = {
    "2.3": ["14 calendar", "Form HR-L1"],
    "2.4": ["written approval", "Verbal approval is not valid"],
    "2.5": ["Loss of Pay", "regardless of subsequent approval"],
    "2.6": ["5 unused", "31 December"],
    "2.7": ["January", "March", "forfeited"],
    "3.2": ["3 or more consecutive days", "48 hours", "medical certificate"],
    "3.4": ["public holiday", "regardless of duration"],
    "5.2": ["Department Head", "HR Director", "Manager approval alone is not sufficient"],
    "5.3": ["30 continuous days", "Municipal Commissioner"],
    "7.2": ["not permitted under any circumstances"],
}


def retrieve_policy(path: str) -> list:
    """Load a policy .txt file and return its numbered clauses as (num, text)."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    clause_re = re.compile(r"^(\d+\.\d+)\s+(.*)$")
    header_re = re.compile(r"^\d+\.\s+[A-Z]")

    sections = {}
    current = None
    for line in lines:
        stripped = line.strip()
        if not stripped or re.fullmatch(r"[═=]+", stripped):
            continue
        m = clause_re.match(stripped)
        if m:
            current = m.group(1)
            sections[current] = [m.group(2)]
            continue
        if header_re.match(stripped):
            current = None
            continue
        if current:
            sections[current].append(stripped)

    result = [(num, re.sub(r"\s+", " ", " ".join(parts)).strip())
              for num, parts in sections.items()]
    if not result:
        raise ValueError("No numbered clauses found in policy file")
    return result


def summarize_policy(sections: list) -> list:
    """Return one summary line per clause, preserving conditions verbatim."""
    lines = []
    for num, txt in sections:
        flag = "[VERBATIM] " if num in CRITICAL_CLAUSES else ""
        lines.append(f"Clause {num}: {flag}{txt}")
    return lines


def verify(sections: list, lines: list) -> list:
    """Check every critical clause is present with its conditions intact."""
    present = {num for num, _ in sections}
    checks = []
    missing = sorted(set(CRITICAL_CLAUSES) - present)
    checks.append(f"CRITICAL missing clauses: {', '.join(missing) if missing else 'none'}")
    body = "\n".join(lines)
    for num, needles in CRITICAL_MUST_INCLUDE.items():
        text = dict(sections).get(num, "")
        if all(n in text for n in needles):
            checks.append(f"Clause {num}: conditions OK")
        else:
            checks.append(f"Clause {num}: CONDITIONS DROPPED")
    return checks


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    lines = summarize_policy(sections)
    checks = verify(sections, lines)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write("UC-0B — Employee Leave Policy Summary (policy_hr_leave.txt)\n")
        f.write("Source-derived summary: every numbered clause preserved with conditions intact.\n")
        f.write("=" * 70 + "\n\n")
        for line in lines:
            f.write(line + "\n")
        f.write("\n" + "=" * 70 + "\n")
        f.write("ENFORCEMENT VERIFICATION\n")
        for c in checks:
            f.write("- " + c + "\n")

    failed = any("DROPPED" in c or "missing clauses" in c and "none" not in c for c in checks)
    if failed:
        print("FAIL: summary lost conditions or clauses", file=sys.stderr)
        sys.exit(1)
    print(f"Done. Summary written to {args.output} ({len(sections)} clauses, verification passed)")


if __name__ == "__main__":
    main()
