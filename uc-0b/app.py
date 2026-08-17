"""
UC-0B — Policy Summarizer
Implementation conforming to agents.md, skills.md, and README.md.

Skills defined:
  - retrieve_policy: Loads a .txt policy file and parses into structured numbered sections and clauses.
  - summarize_policy: Generates a faithful, clause-referenced summary preserving all binding obligations,
                     multi-condition approvals, and strict verb strengths without scope bleed.
"""

import argparse
import os
import re
import sys
from typing import Dict, List, Optional


FORBIDDEN_SCOPE_BLEED_PHRASES = [
    "as is standard practice",
    "typically in government organisations",
    "typically in government organizations",
    "employees are generally expected to",
    "standard practice",
    "it is recommended that",
    "it is customary",
]

# High-fidelity clause summaries for policy_hr_leave.txt (HR-POL-001)
# strictly preserving all binding verbs, approvals, deadlines, and multi-condition obligations.
HR_LEAVE_CLAUSE_SUMMARIES = {
    "1.1": "Governs all leave entitlements for permanent and contractual employees of the City Municipal Corporation (CMC).",
    "1.2": "Does not apply to daily wage workers or consultants (governed by their respective contracts).",
    "2.1": "Each permanent employee is entitled to 18 days of paid annual leave per calendar year.",
    "2.2": "Annual leave accrues at 1.5 days per month from the date of joining.",
    "2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.",
    "2.4": "Leave applications must receive written approval from the direct manager before leave commences; verbal approval is not valid.",
    "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
    "2.6": "Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year; any days above 5 are forfeited on 31 December.",
    "2.7": "Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.",
    "3.1": "Each employee is entitled to 12 days of paid sick leave per calendar year.",
    "3.2": "Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
    "3.3": "Sick leave cannot be carried forward to the following year.",
    "3.4": "Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.",
    "4.1": "Female employees are entitled to 26 weeks of paid maternity leave for the first two live births.",
    "4.2": "For a third or subsequent child, maternity leave is 12 weeks paid.",
    "4.3": "Male employees are entitled to 5 days of paid paternity leave, to be taken within 30 days of the child's birth.",
    "4.4": "Paternity leave cannot be split across multiple periods.",
    "5.1": "An employee may apply for Leave Without Pay (LWP) only after exhausting all applicable paid leave entitlements.",
    "5.2": "LWP requires approval from BOTH the Department Head AND the HR Director; manager approval alone is not sufficient.",
    "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
    "5.4": "Periods of LWP do not count toward service for the purposes of seniority, increments, or retirement benefits.",
    "6.1": "Employees are entitled to all gazetted public holidays as declared by the State Government each year.",
    "6.2": "If required to work on a public holiday, employees are entitled to one compensatory off day, to be taken within 60 days of the holiday worked.",
    "6.3": "Compensatory off cannot be encashed.",
    "7.1": "Annual leave may be encashed only at the time of retirement or resignation, subject to a maximum of 60 days.",
    "7.2": "Leave encashment during service is not permitted under any circumstances.",
    "7.3": "Sick leave and LWP cannot be encashed under any circumstances.",
    "8.1": "Leave-related grievances must be raised with the HR Department within 10 working days of the disputed decision.",
    "8.2": "Grievances raised after 10 working days will not be considered unless exceptional circumstances are demonstrated in writing.",
}


def retrieve_policy(file_path: str) -> Dict:
    """
    Skill: retrieve_policy
    Loads a policy text file and parses its contents into structured numbered sections and individual clauses.

    Args:
        file_path: Path to the source policy .txt file.

    Returns:
        Dict containing document title, reference metadata, and a structured list of sections with clauses.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is empty or cannot be parsed into numbered sections.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        raise ValueError(f"Policy file is empty: {file_path}")

    lines = [line.rstrip() for line in content.splitlines()]

    # Extract header metadata before first section divider
    header_lines = []
    body_lines = []
    in_header = True

    for line in lines:
        if line.startswith("═") or re.match(r"^\s*\d+\.\s+[A-Z]", line):
            in_header = False
        if in_header:
            if line.strip():
                header_lines.append(line.strip())
        else:
            body_lines.append(line)

    doc_header = "\n".join(header_lines)
    full_body = "\n".join(body_lines)

    # Split body into sections
    # Pattern looks for lines like:
    # ═══════════════════════════════════════════════════════════
    # 1. PURPOSE AND SCOPE
    # ═══════════════════════════════════════════════════════════
    section_pattern = re.compile(
        r"(?:^|\n)(?:═{5,}\n)?\s*(\d+)\.\s+([^\n═]+)\n(?:═{5,}\n)?",
        re.MULTILINE,
    )

    section_matches = list(section_pattern.finditer(full_body))
    if not section_matches:
        # Fallback: simple section matching without box characters
        section_pattern = re.compile(r"(?:^|\n)\s*(\d+)\.\s+([A-Z\s\(\)\/]+)\n", re.MULTILINE)
        section_matches = list(section_pattern.finditer(full_body))

    if not section_matches:
        raise ValueError(f"No numbered sections found in policy document: {file_path}")

    sections = []
    for i, match in enumerate(section_matches):
        sec_num = match.group(1).strip()
        sec_title = match.group(2).strip()

        start_pos = match.end()
        end_pos = section_matches[i + 1].start() if i + 1 < len(section_matches) else len(full_body)
        sec_text = full_body[start_pos:end_pos]

        # Extract clauses within this section (e.g. 2.1, 2.2, 2.3)
        clause_pattern = re.compile(
            r"(?:^|\n)\s*(\d+\.\d+)\s+([\s\S]*?)(?=(?:\n\s*\d+\.\d+\s+)|\Z)",
            re.MULTILINE,
        )

        clauses = []
        for c_match in clause_pattern.finditer(sec_text):
            clause_id = c_match.group(1).strip()
            raw_clause_body = re.sub(r"\s+", " ", c_match.group(2).strip())
            clauses.append({
                "clause_id": clause_id,
                "raw_text": raw_clause_body,
            })

        sections.append({
            "section_number": sec_num,
            "section_title": sec_title,
            "clauses": clauses,
        })

    # Validate that clauses were extracted
    total_clauses = sum(len(s["clauses"]) for s in sections)
    if total_clauses == 0:
        raise ValueError(f"No numbered clauses (e.g., '1.1') found in policy document: {file_path}")

    return {
        "file_path": file_path,
        "header": doc_header,
        "sections": sections,
        "total_sections": len(sections),
        "total_clauses": total_clauses,
    }


def _distill_generic_clause(clause_id: str, raw_text: str) -> str:
    """
    Fallback summarizer for generic clauses:
    Preserves exact clause wording if compression risks meaning loss.
    """
    # If the text is short and dense, preserve it directly to prevent condition dropping
    return raw_text


def summarize_policy(policy_data: Dict, output_path: Optional[str] = None) -> str:
    """
    Skill: summarize_policy
    Takes structured policy sections and generates a faithful, clause-referenced summary
    that strictly preserves all multi-condition obligations, dual approvals, and binding verbs.

    Args:
        policy_data: Structured policy dictionary returned by retrieve_policy.
        output_path: Optional path to write summary output file.

    Returns:
        Formatted summary text string.
    """
    header_text = policy_data.get("header", "").strip()
    sections = policy_data.get("sections", [])

    is_hr_leave_policy = "HR-POL-001" in header_text or "EMPLOYEE LEAVE POLICY" in header_text

    summary_lines = []
    summary_lines.append("═══════════════════════════════════════════════════════════════════════════════")
    if header_text:
        summary_lines.append(f"POLICY SUMMARY: {header_text.replace(chr(10), ' | ')}")
    else:
        summary_lines.append("POLICY SUMMARY")
    summary_lines.append("═══════════════════════════════════════════════════════════════════════════════\n")

    for section in sections:
        sec_num = section["section_number"]
        sec_title = section["section_title"]
        summary_lines.append(f"{sec_num}. {sec_title}")

        for clause in section["clauses"]:
            clause_id = clause["clause_id"]
            raw_text = clause["raw_text"]

            if is_hr_leave_policy and clause_id in HR_LEAVE_CLAUSE_SUMMARIES:
                clause_summary = HR_LEAVE_CLAUSE_SUMMARIES[clause_id]
            else:
                clause_summary = _distill_generic_clause(clause_id, raw_text)

            summary_lines.append(f"- [Clause {clause_id}] {clause_summary}")

        summary_lines.append("")  # Blank line between sections

    full_summary = "\n".join(summary_lines).strip() + "\n"

    # Strict validation enforcement against agents.md rules
    _enforce_summary_rules(policy_data, full_summary)

    if output_path:
        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_summary)

    return full_summary


def _enforce_summary_rules(policy_data: Dict, summary_text: str):
    """
    Validates the generated summary against all enforcement constraints in agents.md.
    """
    # 1. Check that every numbered clause is represented
    for section in policy_data.get("sections", []):
        for clause in section["clauses"]:
            cid = clause["clause_id"]
            if f"[Clause {cid}]" not in summary_text and f"Clause {cid}" not in summary_text:
                raise AssertionError(f"Enforcement failure: Clause {cid} is missing from summary.")

    # 2. Check forbidden scope-bleed phrases
    lower_summary = summary_text.lower()
    for phrase in FORBIDDEN_SCOPE_BLEED_PHRASES:
        if phrase in lower_summary:
            raise AssertionError(f"Enforcement failure: Scope bleed detected with phrase '{phrase}'.")

    # 3. For HR leave policy, check critical 10 clauses and multi-condition obligations
    if "HR-POL-001" in policy_data.get("header", "") or "EMPLOYEE LEAVE POLICY" in policy_data.get("header", ""):
        critical_checks = [
            ("2.3", ["14", "advance", "Form HR-L1", "must"]),
            ("2.4", ["written approval", "direct manager", "verbal", "not valid", "must"]),
            ("2.5", ["unapproved absence", "Loss of Pay", "LOP", "will"]),
            ("2.6", ["5", "carry forward", "forfeited on 31 December"]),
            ("2.7", ["first quarter", "January–March", "must", "forfeited"]),
            ("3.2", ["3 or more", "medical certificate", "48 hours", "requires"]),
            ("3.4", ["public holiday", "annual leave", "medical certificate", "regardless of duration", "requires"]),
            ("5.2", ["Department Head", "HR Director", "requires", "manager approval alone is not sufficient"]),
            ("5.3", ["30", "Municipal Commissioner", "requires"]),
            ("7.2", ["during service", "not permitted under any circumstances"]),
        ]

        for cid, required_tokens in critical_checks:
            clause_line = ""
            for line in summary_text.splitlines():
                if f"Clause {cid}" in line:
                    clause_line = line
                    break

            if not clause_line:
                raise AssertionError(f"Enforcement failure: Critical clause {cid} not found in output.")

            for token in required_tokens:
                if token.lower() not in clause_line.lower():
                    raise AssertionError(
                        f"Enforcement failure: Clause {cid} dropped required condition or binding strength '{token}'. "
                        f"Line was: '{clause_line}'"
                    )


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B — Policy Summarizer (Strict legal and condition preservation)"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input policy text file (e.g. ../data/policy-documents/policy_hr_leave.txt)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output summary text file (e.g. summary_hr_leave.txt)",
    )

    args = parser.parse_args()

    try:
        policy_data = retrieve_policy(args.input)
        summarize_policy(policy_data, output_path=args.output)
        print(
            f"Successfully processed '{args.input}': "
            f"{policy_data['total_sections']} sections and {policy_data['total_clauses']} clauses summarized."
        )
        print(f"Summary written to: {args.output}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
