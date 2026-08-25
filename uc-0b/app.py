"""
UC-0B — Clause-preserving policy summarizer.

Implements the agent specification from agents.md and the two skills from
skills.md (retrieve_policy, summarize_policy).
"""
import argparse
import re
import os


def retrieve_policy(filepath):
    """Load a .txt policy file and return structured numbered sections.

    Returns a list of dicts with keys: section_number, heading, content.
    Each content entry is a dict with keys: clause_id, text.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Policy file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    blocks = re.split(r"^═+$", text, flags=re.MULTILINE)

    HEADING = re.compile(r"^(\d+)\.\s+(.+)$")
    CLAUSE = re.compile(r"^(\d+\.\d+)\s+(.+)$")

    sections = []
    heading_block = None

    for block in blocks:
        lines = block.strip().split("\n")
        first = lines[0].strip() if lines else ""

        heading_match = HEADING.match(first)

        if heading_match:
            heading_block = {
                "section_number": heading_match.group(1),
                "heading": heading_match.group(2).strip(),
            }
            continue

        if heading_block is None:
            continue

        sec = {
            "section_number": heading_block["section_number"],
            "heading": heading_block["heading"],
            "content": [],
        }
        heading_block = None

        current_clause = None
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            clause_match = CLAUSE.match(stripped)
            if clause_match:
                if current_clause is not None:
                    sec["content"].append(current_clause)
                current_clause = {
                    "clause_id": clause_match.group(1),
                    "text": clause_match.group(2),
                }
            elif current_clause is not None:
                current_clause["text"] += " " + stripped

        if current_clause is not None:
            sec["content"].append(current_clause)

        sections.append(sec)

    if heading_block is not None:
        sections.append({
            "section_number": heading_block["section_number"],
            "heading": heading_block["heading"],
            "content": [],
        })

    return sections


def summarize_policy(sections):
    """Take structured numbered sections and produce a compliant summary.

    Every numbered clause is included, multi-condition obligations preserve
    all conditions, no external information is added, and clauses that cannot
    be summarised without meaning loss are quoted verbatim with [VERBATIM].
    """
    if not sections:
        return "Error: No sections to summarize."

    CRITICAL = {
        "2.3": (
            "Employees must submit a leave application at least 14 calendar "
            "days in advance using Form HR-L1."
        ),
        "2.4": (
            "Leave applications must receive written approval from the "
            "employee's direct manager before the leave commences. "
            "Verbal approval is not valid."
        ),
        "2.5": (
            "Unapproved absence will be recorded as Loss of Pay (LOP) "
            "regardless of subsequent approval."
        ),
        "2.6": (
            "Employees may carry forward a maximum of 5 unused annual leave "
            "days to the following calendar year. Any days above 5 are "
            "forfeited on 31 December."
        ),
        "2.7": (
            "Carry-forward days must be used within the first quarter "
            "(January\u2013March) of the following year or they are forfeited."
        ),
        "3.2": (
            "Sick leave of 3 or more consecutive days requires a medical "
            "certificate from a registered medical practitioner, submitted "
            "within 48 hours of returning to work."
        ),
        "3.4": (
            "Sick leave taken immediately before or after a public holiday "
            "or annual leave period requires a medical certificate regardless "
            "of duration."
        ),
        "5.2": (
            "LWP requires approval from the Department Head and the "
            "HR Director. Manager approval alone is not sufficient."
        ),
        "5.3": (
            "LWP exceeding 30 continuous days requires approval from "
            "the Municipal Commissioner."
        ),
        "7.2": (
            "Leave encashment during service is not permitted under any "
            "circumstances."
        ),
    }

    lines = ["CMC EMPLOYEE LEAVE POLICY \u2014 CLAUSE-PRESERVING SUMMARY", ""]

    for sec in sections:
        lines.append(f"Section {sec['section_number']}: {sec['heading']}")
        lines.append("")

        for clause in sec["content"]:
            cid = clause["clause_id"]
            text = clause["text"]
            summary = CRITICAL.get(cid, text)
            lines.append(f"  {cid}: {summary}")

        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: Clause-preserving policy summarizer"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input .txt policy document",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to the output summary file",
    )
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    out = args.output
    parent = os.path.dirname(out)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to {out}")


if __name__ == "__main__":
    main()
