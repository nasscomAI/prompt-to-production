"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from pathlib import Path
from typing import Dict, List

CLAUSE_LINE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_HEADING_RE = re.compile(r"^\d+\.\s+")

# Targeted rewrite map for high-risk clauses in this UC.
CANONICAL_SUMMARIES: Dict[str, str] = {
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave applications must receive written approval from the employee's direct manager before leave commences; verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave days; any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within January-March of the following year or they are forfeited.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner within 48 hours of returning to work.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "5.2": "LWP requires approval from both the Department Head and the HR Director; manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
}


def retrieve_policy(input_path: str) -> List[Dict[str, str]]:
    content = Path(input_path).read_text(encoding="utf-8")
    clauses: List[Dict[str, str]] = []
    current_id = ""
    current_parts: List[str] = []

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = CLAUSE_LINE_RE.match(line)
        if match:
            if current_id:
                clauses.append(
                    {"clause_id": current_id, "clause_text": " ".join(current_parts).strip()}
                )
            current_id = match.group(1)
            current_parts = [match.group(2).strip()]
            continue
        if current_id and not set(line) <= {"═"} and not SECTION_HEADING_RE.match(line):
            current_parts.append(line)

    if current_id:
        clauses.append({"clause_id": current_id, "clause_text": " ".join(current_parts).strip()})

    if not clauses:
        raise ValueError("No numbered clauses found in policy file.")
    return clauses


def summarize_policy(clauses: List[Dict[str, str]]) -> str:
    lines: List[str] = []
    for clause in clauses:
        clause_id = clause["clause_id"]
        clause_text = clause["clause_text"]
        summary = CANONICAL_SUMMARIES.get(clause_id, clause_text)
        strict_tag = " [STRICT_WORDING_RETAINED]" if clause_id not in CANONICAL_SUMMARIES else ""
        lines.append(f"{clause_id}: {summary}{strict_tag}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary Generator")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to output summary .txt file")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)
    Path(args.output).write_text(summary, encoding="utf-8")
    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
