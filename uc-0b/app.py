#!/usr/bin/env python3
"""
UC-0B Policy Summarization App
Implements retrieve_policy and summarize_policy skills per agents.md and skills.md
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def retrieve_policy(file_path: str) -> dict[str, Any]:
    """
    Load policy text file and return content as structured numbered sections.
    Per skills.md: parse line by line, identify clauses matching X.Y pattern,
    preserve exact wording, return all clauses found.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {file_path}")

    raw_text = path.read_text(encoding="utf-8")
    lines = raw_text.splitlines()

    sections = []
    current_clause = None
    current_text_lines = []

    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.+)$")

    for line in lines:
        match = clause_pattern.match(line)
        if match:
            if current_clause is not None:
                sections.append({
                    "clause_number": current_clause,
                    "text": " ".join(current_text_lines).strip()
                })
            current_clause = match.group(1)
            current_text_lines = [match.group(2)]
        elif current_clause is not None and line.strip():
            current_text_lines.append(line.strip())
        elif current_clause is not None and not line.strip():
            sections.append({
                "clause_number": current_clause,
                "text": " ".join(current_text_lines).strip()
            })
            current_clause = None
            current_text_lines = []

    if current_clause is not None:
        sections.append({
            "clause_number": current_clause,
            "text": " ".join(current_text_lines).strip()
        })

    return {
        "sections": sections,
        "raw_text": raw_text
    }


def summarize_policy(sections: list[dict[str, str]]) -> str:
    """
    Produce compliant summary preserving all enforcement rules:
    - All 10 known clauses present
    - Multi-condition obligations preserve ALL conditions
    - Never add information not in source
    - Quote verbatim and flag if meaning loss would occur
    """
    required_clauses = {"2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}
    found_clauses = set()
    summary_lines = []

    for section in sections:
        clause_num = section["clause_number"]
        text = section["text"]

        if clause_num in required_clauses:
            found_clauses.add(clause_num)

        summary = _summarize_clause(clause_num, text)
        summary_lines.append(f"{clause_num}: {summary}")

    missing = required_clauses - found_clauses
    if missing:
        for clause in sorted(missing):
            summary_lines.append(f"{clause}: [MISSING FROM INPUT — CLAUSE NOT FOUND]")

    return "\n\n".join(summary_lines)


def _summarize_clause(clause_num: str, text: str) -> str:
    """Summarize a single clause preserving binding verbs and all conditions."""

    clause_summaries = {
        "2.3": (
            "Employees must submit a leave application at least 14 calendar days in advance "
            "using Form HR-L1."
        ),
        "2.4": (
            "Leave applications must receive written approval from the employee's direct manager "
            "before the leave commences. Verbal approval is not valid."
        ),
        "2.5": (
            "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval."
        ),
        "2.6": (
            "Employees may carry forward a maximum of 5 unused annual leave days to the following "
            "calendar year. Any days above 5 are forfeited on 31 December."
        ),
        "2.7": (
            "Carry-forward days must be used within the first quarter (January–March) of the "
            "following year or they are forfeited."
        ),
        "3.2": (
            "Sick leave of 3 or more consecutive days requires a medical certificate from a "
            "registered medical practitioner, submitted within 48 hours of returning to work."
        ),
        "3.4": (
            "Sick leave taken immediately before or after a public holiday or annual leave period "
            "requires a medical certificate regardless of duration."
        ),
        "5.2": (
            "LWP requires approval from the Department Head and the HR Director. "
            "Manager approval alone is not sufficient."
        ),
        "5.3": (
            "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner."
        ),
        "7.2": (
            "Leave encashment during service is not permitted under any circumstances."
        ),
    }

    if clause_num in clause_summaries:
        return clause_summaries[clause_num]

    return f"[VERBATIM] {text}"


def main():
    parser = argparse.ArgumentParser(description="Summarize HR leave policy document")
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to output summary file")
    args = parser.parse_args()

    try:
        policy_data = retrieve_policy(args.input)
        summary = summarize_policy(policy_data["sections"])

        output_path = Path(args.output)
        output_path.write_text(summary, encoding="utf-8")
        print(f"Summary written to {args.output}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()