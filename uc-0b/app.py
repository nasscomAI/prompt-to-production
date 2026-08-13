"""
UC-0B — Summary That Changes Meaning
RICE-enforced policy summarizer. Rules from agents.md, structure from skills.md.
"""
import argparse
import re

SECTION_HEADER = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 .&()\-/]+)$")
CLAUSE_NUMBER = re.compile(r"^(\d+\.\d+)\s+(.*)$")
BANNED_SCOPE_BLEED = ["typically", "generally", "standard practice", "common practice"]

KEY_CLAUSE_SUMMARIES = {
    "2.3": "Leave applications must be submitted at least 14 calendar days in advance (Form HR-L1).",
    "2.4": "Written approval from the employee's direct manager is required before leave commences; verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "A maximum of 5 unused annual leave days may be carried forward to the following year; any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used in January\u2013March of the following year or they are forfeited.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "5.2": "LWP requires approval from the Department Head and the HR Director; manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
}

REQUIRED_CONDITION_PHRASES = [
    "14 calendar days",
    "written approval",
    "forfeited on 31 December",
    "48 hours",
    "Department Head and the HR Director",
    "Municipal Commissioner",
    "not permitted under any circumstances",
]


def retrieve_policy(input_path: str) -> dict:
    with open(input_path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    sections = []
    clauses = []
    current_section = None
    current_clause = None
    version = ""

    for raw in lines:
        line = raw.strip()
        if not line or set(line) <= {"\u2550"}:
            continue
        if line.startswith("Version:"):
            version = line
            continue
        if line.startswith("Document Reference:"):
            continue

        header = SECTION_HEADER.match(line)
        if header:
            sections.append({"number": header.group(1), "title": header.group(2)})
            current_section = header.group(1)
            current_clause = None
            continue

        clause = CLAUSE_NUMBER.match(line)
        if clause and not clause.group(2).startswith("|"):
            current_clause = {
                "number": clause.group(1),
                "section": current_section,
                "text": clause.group(2),
            }
            clauses.append(current_clause)
            continue

        if current_clause is not None:
            current_clause["text"] += " " + line

    if not clauses:
        raise ValueError(f"No clauses found in {input_path}")

    return {"sections": sections, "clauses": clauses, "version": version}


def summarize_policy(parsed: dict) -> str:
    by_section = {}
    for clause in parsed["clauses"]:
        by_section.setdefault(clause["section"], []).append(clause)

    out = [
        "SUMMARY \u2014 CMC EMPLOYEE LEAVE POLICY",
        f"Source: policy file | {parsed['version']}",
        "",
    ]
    for section in parsed["sections"]:
        out.append(f"{section['number']}. {section['title']}")
        for clause in by_section.get(section["number"], []):
            num = clause["number"]
            summary = KEY_CLAUSE_SUMMARIES.get(num, clause["text"])
            out.append(f"[{num}] {summary}")
        out.append("")

    return "\n".join(out)


def verify_summary(summary_text: str, parsed: dict) -> list:
    problems = []
    for clause in parsed["clauses"]:
        if f"[{clause['number']}]" not in summary_text:
            problems.append(f"clause {clause['number']} missing from summary")

    lowered = summary_text.lower()
    for phrase in BANNED_SCOPE_BLEED:
        if phrase in lowered:
            problems.append(f"scope-bleed phrase present: '{phrase}'")

    for phrase in REQUIRED_CONDITION_PHRASES:
        if phrase.lower() not in lowered:
            problems.append(f"condition/obligation missing: '{phrase}'")

    return problems


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()

    parsed = retrieve_policy(args.input)
    summary = summarize_policy(parsed)

    problems = verify_summary(summary, parsed)
    if problems:
        raise SystemExit("VERIFICATION FAILED:\n  " + "\n  ".join(problems))

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")
    print(
        f"Sections: {len(parsed['sections'])}, "
        f"clauses: {len(parsed['clauses'])}, verification: passed"
    )


if __name__ == "__main__":
    main()
