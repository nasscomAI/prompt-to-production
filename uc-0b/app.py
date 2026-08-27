"""
UC-0B — Policy Summary Tool
Builds on the agent/skill definitions in agents.md and skills.md.
"""
import argparse
import re
import sys


TARGET_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7",
                  "3.2", "3.4", "5.2", "5.3", "7.2"]


def retrieve_policy(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        text = f.read()

    if not text.strip():
        raise ValueError(f"Empty file: {path}")

    sections = {}
    current_section = None
    section_pattern = re.compile(r"^═+\n(\d+\.\s+.+)\n═+", re.MULTILINE)
    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.+)", re.MULTILINE)

    parts = section_pattern.split(text)
    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        body = parts[i + 1].strip()
        clauses = []
        for m in clause_pattern.finditer(body):
            clauses.append({
                "clause_id": m.group(1),
                "text": m.group(2).strip(),
            })
        sections[heading] = clauses

    return sections


def _summarise_clause(clause_id: str, text: str) -> str:
    summaries = {
        "2.3": (
            "Employees must submit a leave application at least "
            "14 calendar days in advance using Form HR‑L1."
        ),
        "2.4": (
            "Leave applications must receive written approval from "
            "the employee's direct manager before the leave commences. "
            "Verbal approval is not valid."
        ),
        "2.5": (
            "Unapproved absence will be recorded as Loss of Pay (LOP) "
            "regardless of subsequent approval."
        ),
        "2.6": (
            "Employees may carry forward a maximum of 5 unused annual "
            "leave days. Any days above 5 are forfeited on 31 December."
        ),
        "2.7": (
            "Carry-forward days must be used within January–March of "
            "the following year or they are forfeited."
        ),
        "3.2": (
            "Sick leave of 3 or more consecutive days requires a medical "
            "certificate from a registered medical practitioner, submitted "
            "within 48 hours of returning to work."
        ),
        "3.4": (
            "Sick leave taken immediately before or after a public holiday "
            "or annual leave period requires a medical certificate "
            "regardless of duration."
        ),
        "5.2": (
            "LWP requires approval from the Department Head AND the "
            "HR Director. Manager approval alone is not sufficient."
        ),
        "5.3": (
            "LWP exceeding 30 continuous days requires approval from "
            "the Municipal Commissioner."
        ),
        "7.2": (
            "Leave encashment during service is not permitted under "
            "any circumstances."
        ),
    }
    if clause_id in summaries:
        return f"{clause_id}: {summaries[clause_id]}"
    return f"{clause_id}: [QUOTED] {text}"


def summarize_policy(sections: dict, target_ids: list) -> str:
    found = set()
    for heading, clauses in sections.items():
        for c in clauses:
            if c["clause_id"] in target_ids:
                found.add(c["clause_id"])

    missing = set(target_ids) - found
    if missing:
        raise ValueError(
            f"Target clauses not found in source: {', '.join(sorted(missing))}"
        )

    lines = ["HR LEAVE POLICY — CLAUSE SUMMARY", ""]
    for heading, clauses in sections.items():
        for c in clauses:
            if c["clause_id"] in target_ids:
                lines.append(_summarise_clause(c["clause_id"], c["text"]))
                lines.append("")

    return "\n".join(lines).strip()


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections, TARGET_CLAUSES)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary + "\n")

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
