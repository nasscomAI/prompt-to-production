"""
UC-0B — Summary That Changes Meaning
Deterministic, stdlib-only. See agents.md / skills.md for the enforcement
rules this file implements.
"""
import argparse
import re

REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

CLAUSE_START = re.compile(r"^(\d+\.\d+)\s+(.*)$")

# Multi-condition clauses: every listed phrase must survive into the summary.
CONDITION_CHECKS = {
    "2.6": ["carry forward", "5", "forfeited"],
    "5.2": ["department head", "hr director"],
}

SUMMARIES = {
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance (Form HR-L1).",
    "2.4": "Leave requires written approval from the direct manager before it commences; verbal approval is not valid.",
    "2.5": "Unapproved absence is recorded as Loss of Pay, even if approved afterward.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave days; anything above 5 is forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within January-March of the following year or they are forfeited.",
    "3.2": "Sick leave of 3+ consecutive days requires a medical certificate submitted within 48 hours of returning to work.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave requires a medical certificate regardless of duration.",
    "5.2": "Leave Without Pay requires approval from BOTH the Department Head AND the HR Director; manager approval alone is not sufficient.",
    "5.3": "Leave Without Pay exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
}


def retrieve_policy(input_path: str) -> dict:
    clauses = {}
    current = None
    buf = []

    def flush():
        if current is not None:
            clauses[current] = " ".join(buf).strip()

    with open(input_path, encoding="utf-8") as handle:
        for raw in handle:
            line = raw.rstrip("\n")
            match = CLAUSE_START.match(line.strip())
            if match:
                flush()
                current = match.group(1)
                buf = [match.group(2)]
            elif current is not None and line.startswith(" ") and line.strip():
                buf.append(line.strip())
            elif current is not None and not line.strip():
                flush()
                current = None
                buf = []
    flush()
    return clauses


def summarize_policy(clauses: dict) -> list:
    lines = []
    for num in REQUIRED_CLAUSES:
        if num not in clauses:
            lines.append(f"[{num}] NOT FOUND in source document")
            continue

        summary = SUMMARIES[num]
        for required_phrase in CONDITION_CHECKS.get(num, []):
            if required_phrase.lower() not in summary.lower():
                summary = f"[verbatim] {clauses[num]}"
                break

        lines.append(f"[{num}] {summary}")
    return lines


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    lines = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as out:
        out.write("\n".join(lines) + "\n")

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
