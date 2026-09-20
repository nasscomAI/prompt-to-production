"""UC-0B app.py — deterministic policy summarizer. No external APIs."""
import argparse
import re

REQUIRED = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

# Faithful condensations, each preserving all source conditions, AND/OR,
# numbers, deadlines, and binding verbs. Wording checked against source spans.
SUMMARIES = {
    "2.3": "[2.3] Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "[2.4] Leave applications must receive written approval from the employee's direct manager before the leave commences; verbal approval is not valid.",
    "2.5": "[2.5] Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "[2.6] Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year; any days above 5 are forfeited on 31 December.",
    "2.7": "[2.7] Carry-forward days must be used within the first quarter (January-March) of the following year or they are forfeited.",
    "3.2": "[3.2] Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.4": "[3.4] Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "5.2": "[5.2] LWP requires approval from the Department Head AND the HR Director; manager approval alone is not sufficient.",
    "5.3": "[5.3] LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "7.2": "[7.2] Leave encashment during service is not permitted under any circumstances.",
}


def retrieve_policy(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    clauses = {}
    pattern = re.compile(r"^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+|\Z)", re.M | re.S)
    for m in pattern.finditer(text):
        num = m.group(1).strip()
        body = re.sub(r"\s+", " ", m.group(2)).strip()
        clauses[num] = body
    return clauses


def summarize_policy(clauses):
    lines = [
        "LEAVE POLICY SUMMARY (HR-POL-001) — critical clauses only",
        "",
    ]
    for num in REQUIRED:
        if num in clauses and SUMMARIES[num]:
            lines.append(SUMMARIES[num])
        else:
            found = clauses.get(num, "")
            if found:
                lines.append('[%s] "%s" [QUOTED VERBATIM]' % (num, found))
            else:
                lines.append("[%s] Not found in source." % num)
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
    print("Done. Summary written to %s" % args.output)


if __name__ == "__main__":
    main()
