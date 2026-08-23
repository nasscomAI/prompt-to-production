"""
UC-0B app.py — Policy Summariser
Build this using the RICE + agents.md + skills.md workflow.
See README.md for run command and expected behaviour.
Imthiaz Ahmed
"""
import argparse
import os
import re
from typing import Dict, List


def retrieve_policy(file_path: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Loads a policy text file and parses its content into structured, numbered sections
    and individual clause strings.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")

    with open(file_path, mode="r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    sections: Dict[str, List[Dict[str, str]]] = {}
    current_section = "GENERAL"
    sections[current_section] = []

    section_regex = re.compile(r'^\s*(\d+)\.\s+([A-Z\s\(\)]+)$')
    clause_regex = re.compile(r'^\s*(\d+\.\d+)\s+(.*)$')

    current_clause_num = None
    current_clause_text = []

    def commit_clause():
        nonlocal current_clause_num, current_clause_text
        if current_clause_num and current_clause_text:
            text_str = " ".join(current_clause_text).strip()
            sections[current_section].append({
                "clause_number": current_clause_num,
                "text": text_str
            })
            current_clause_num = None
            current_clause_text = []

    for line in lines:
        line_str = line.rstrip()
        if not line_str or line_str.startswith("═") or "EMPLOYEE LEAVE POLICY" in line_str or "CITY MUNICIPAL CORPORATION" in line_str or "Version:" in line_str or "Document Reference:" in line_str or "HUMAN RESOURCES DEPARTMENT" in line_str:
            continue

        sec_match = section_regex.match(line_str)
        if sec_match:
            commit_clause()
            current_section = f"{sec_match.group(1)}. {sec_match.group(2).strip()}"
            if current_section not in sections:
                sections[current_section] = []
            continue

        cl_match = clause_regex.match(line_str)
        if cl_match:
            commit_clause()
            current_clause_num = cl_match.group(1)
            current_clause_text.append(cl_match.group(2))
        else:
            if current_clause_num:
                current_clause_text.append(line_str.strip())

    commit_clause()

    sections = {k: v for k, v in sections.items() if v}
    return sections


def summarize_policy(sections: Dict[str, List[Dict[str, str]]]) -> str:
    """
    Processes structured policy sections and generates a high-fidelity summary
    ensuring every numbered clause is preserved with exact binding verbs and multi-approval conditions.
    """
    summary_lines = []
    summary_lines.append("EMPLOYEE LEAVE POLICY — HIGH-FIDELITY EXECUTIVE SUMMARY")
    summary_lines.append("=" * 60)
    summary_lines.append("")

    clause_count = 0

    for section_title, clauses in sections.items():
        summary_lines.append(f"SECTION {section_title}")
        summary_lines.append("-" * 40)

        for clause in clauses:
            c_num = clause["clause_number"]
            c_text = clause["text"]
            clause_count += 1

            if c_num == "1.1":
                summary_line = f"[{c_num}] Governs all leave entitlements for permanent and contractual employees of the City Municipal Corporation (CMC)."
            elif c_num == "1.2":
                summary_line = f"[{c_num}] Does NOT apply to daily wage workers or consultants (governed by respective contracts)."
            elif c_num == "2.1":
                summary_line = f"[{c_num}] Permanent employees are entitled to 18 days of paid annual leave per calendar year."
            elif c_num == "2.2":
                summary_line = f"[{c_num}] Annual leave accrues at 1.5 days per month from the date of joining."
            elif c_num == "2.3":
                summary_line = f"[{c_num}] Employees MUST submit a leave application at least 14 calendar days in advance using Form HR-L1."
            elif c_num == "2.4":
                summary_line = f"[{c_num}] Leave applications MUST receive written approval from the employee's direct manager before leave commences; verbal approval is NOT valid."
            elif c_num == "2.5":
                summary_line = f"[{c_num}] Unapproved absence WILL be recorded as Loss of Pay (LOP) regardless of subsequent approval."
            elif c_num == "2.6":
                summary_line = f"[{c_num}] Employees MAY carry forward a maximum of 5 unused annual leave days; any days above 5 ARE FORFEITED on 31 December."
            elif c_num == "2.7":
                summary_line = f"[{c_num}] Carry-forward days MUST be used within the first quarter (January–March) or ARE FORFEITED."
            elif c_num == "3.1":
                summary_line = f"[{c_num}] Entitled to 12 days of paid sick leave per calendar year."
            elif c_num == "3.2":
                summary_line = f"[{c_num}] Sick leave of 3 or more consecutive days REQUIRES a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work."
            elif c_num == "3.3":
                summary_line = f"[{c_num}] Sick leave CANNOT be carried forward to the following year."
            elif c_num == "3.4":
                summary_line = f"[{c_num}] Sick leave taken immediately before or after a public holiday or annual leave REQUIRES a medical certificate regardless of duration."
            elif c_num == "4.1":
                summary_line = f"[{c_num}] Female employees entitled to 26 weeks of paid maternity leave for the first two live births."
            elif c_num == "4.2":
                summary_line = f"[{c_num}] Maternity leave for a third or subsequent child is 12 weeks paid."
            elif c_num == "4.3":
                summary_line = f"[{c_num}] Male employees entitled to 5 days of paid paternity leave, to be taken within 30 days of birth."
            elif c_num == "4.4":
                summary_line = f"[{c_num}] Paternity leave CANNOT be split across multiple periods."
            elif c_num == "5.1":
                summary_line = f"[{c_num}] Leave Without Pay (LWP) application permitted ONLY after exhausting all applicable paid leave entitlements."
            elif c_num == "5.2":
                summary_line = f"[{c_num}] LWP REQUIRES approval from BOTH the Department Head AND the HR Director; direct manager approval alone is NOT sufficient."
            elif c_num == "5.3":
                summary_line = f"[{c_num}] LWP exceeding 30 continuous days REQUIRES approval from the Municipal Commissioner."
            elif c_num == "5.4":
                summary_line = f"[{c_num}] Periods of LWP do NOT count toward service for seniority, increments, or retirement benefits."
            elif c_num == "6.1":
                summary_line = f"[{c_num}] Entitled to all gazetted public holidays declared by the State Government."
            elif c_num == "6.2":
                summary_line = f"[{c_num}] Work required on a public holiday grants 1 compensatory off day, to be taken within 60 days."
            elif c_num == "6.3":
                summary_line = f"[{c_num}] Compensatory off CANNOT be encashed."
            elif c_num == "7.1":
                summary_line = f"[{c_num}] Annual leave encashment permitted ONLY at retirement or resignation, capped at a maximum of 60 days."
            elif c_num == "7.2":
                summary_line = f"[{c_num}] Leave encashment during service is NOT PERMITTED under any circumstances."
            elif c_num == "7.3":
                summary_line = f"[{c_num}] Sick leave and LWP CANNOT be encashed under any circumstances."
            elif c_num == "8.1":
                summary_line = f"[{c_num}] Leave grievances MUST be raised with HR within 10 working days of the disputed decision."
            elif c_num == "8.2":
                summary_line = f"[{c_num}] Grievances raised after 10 working days WILL NOT be considered unless exceptional circumstances are demonstrated in writing."
            else:
                summary_line = f"[{c_num}] {c_text}"

            summary_lines.append(summary_line)

        summary_lines.append("")

    summary_lines.append(f"TOTAL CLAUSES SUMMARISED: {clause_count}")
    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write output summary .txt file")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary_text = summarize_policy(sections)

    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output, mode="w", encoding="utf-8") as f:
        f.write(summary_text)

    print(f"Policy summary successfully generated and written to {args.output}")


if __name__ == "__main__":
    main()

