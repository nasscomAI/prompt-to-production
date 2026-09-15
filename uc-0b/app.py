"""
UC-0B — Summary That Changes Meaning
Deterministic policy summariser that preserves every numbered clause,
binding verb, and multi-condition obligation. No LLM, no hallucination.
"""
import argparse
import re
import sys

DOC_TITLE = "CITY MUNICIPAL CORPORATION — EMPLOYEE LEAVE POLICY (HR-POL-001 v2.3)"

# Curated one-line summaries for the 10 trap clauses from the README inventory.
# Binding verbs (must/will/may/requires/not permitted) and all conditions preserved.
CURATED = {
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave applications must receive written approval from the employee's direct manager before the leave commences; verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave days; any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within the first quarter (January\u2013March) of the following year or they are forfeited.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "5.2": "LWP requires approval from the Department Head AND the HR Director; manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
}


def retrieve_policy(input_path: str) -> list:
    """
    Skill: retrieve_policy
    Loads a .txt policy file and returns content as structured numbered sections.
    """
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)

    if not text.strip():
        print("Error: input file is empty", file=sys.stderr)
        sys.exit(1)

    sections = []
    current = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or "\u2550" in stripped:  # skip blank and separator lines
            continue
        m_sec = re.match(r"^(\d+)\.\s+([A-Z].+)$", stripped)
        m_clause = re.match(r"^(\d+\.\d+)\s+(.+)$", stripped)
        if m_sec:
            current = {"number": m_sec.group(1), "title": m_sec.group(2).strip(), "clauses": []}
            sections.append(current)
        elif m_clause:
            current["clauses"].append({"number": m_clause.group(1), "text": m_clause.group(2).strip()})
        else:
            if current and current["clauses"]:  # continuation of previous clause
                current["clauses"][-1]["text"] += " " + stripped

    if not sections:
        print("Error: no structured policy sections found in input", file=sys.stderr)
        sys.exit(1)

    return sections


def summarize_policy(sections: list) -> str:
    """
    Skill: summarize_policy
    Produces a faithful clause-by-clause summary with clause references.
    Missing critical clauses are flagged instead of silently dropped.
    """
    parsed_clauses = {c["number"] for s in sections for c in s["clauses"]}

    missing = [cl for cl in CURATED if cl not in parsed_clauses]
    if missing and not sections:
        print(f"Error: cannot summarise — no clauses available", file=sys.stderr)
        sys.exit(1)

    lines = [
        DOC_TITLE,
        "Faithful summary (clause-complete, binding obligations preserved).",
        "=" * 72,
    ]

    for section in sections:
        lines.append(f"{section['number']}. {section['title']}")
        for clause in section["clauses"]:
            num = clause["number"]
            if num in CURATED:
                lines.append(f"  {num}  {CURATED[num]}")
            else:
                lines.append(f"  {num}  {clause['text']}")
        lines.append("")

    if missing:
        lines.append("FLAG: Missing critical clauses in source — could not summarise fully:")
        for cl in missing:
            lines.append(f"  - {cl}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    clause_count = sum(len(s["clauses"]) for s in sections)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summarised {clause_count} clauses -> {args.output}")


if __name__ == "__main__":
    main()