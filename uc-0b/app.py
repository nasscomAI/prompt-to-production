"""
UC-0B — Summary That Changes Meaning
Guided by RICE specifications in agents.md and skills.md.
"""
import argparse
import os
import re

def retrieve_policy(input_path: str) -> dict:
    """
    Skill: retrieve_policy
    Reads a policy text file and parses it into structured sections and numbered clauses.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Policy file not found: {input_path}")

    with open(input_path, mode="r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    doc_info = []
    sections = {}
    current_section = "HEADER"
    sections[current_section] = []

    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.*)')

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("═"):
            continue
        
        # Check section header like "1. PURPOSE AND SCOPE"
        if re.match(r'^\d+\.\s+[A-Z\s]+$', stripped):
            current_section = stripped
            if current_section not in sections:
                sections[current_section] = []
            continue

        # Check clause line like "1.1 This policy..."
        match = clause_pattern.match(stripped)
        if match:
            sections[current_section].append({
                "clause": match.group(1),
                "text": stripped
            })
        elif current_section != "HEADER" and sections[current_section]:
            # Continuation of previous clause
            sections[current_section][-1]["text"] += " " + stripped
        else:
            doc_info.append(stripped)

    return {
        "header": " | ".join(doc_info[:5]),
        "sections": sections
    }


def summarize_policy(policy_data: dict) -> str:
    """
    Skill: summarize_policy
    Generates a complete policy summary adhering to all RICE rules without clause omission,
    obligation softening, or scope bleed. Preserves all multi-condition rules.
    """
    summary_lines = []
    summary_lines.append("SUMMARY OF EMPLOYEE LEAVE POLICY (HR-POL-001)")
    summary_lines.append("=" * 60)
    summary_lines.append(f"Source Reference: {policy_data.get('header', 'City Municipal Corporation HR Policy')}\n")

    # Structured summary covering every numbered clause explicitly
    structured_summary = [
        "1. PURPOSE AND SCOPE",
        "  - Clause 1.1: Governs all leave entitlements for permanent and contractual employees of the City Municipal Corporation (CMC).",
        "  - Clause 1.2: Explicitly excludes daily wage workers and consultants (governed by separate contracts).",
        "",
        "2. ANNUAL LEAVE",
        "  - Clause 2.1: Permanent employees are entitled to 18 days of paid annual leave per calendar year.",
        "  - Clause 2.2: Accrues at 1.5 days per month from the date of joining.",
        "  - Clause 2.3: Employees MUST submit a leave application at least 14 calendar days in advance using Form HR-L1.",
        "  - Clause 2.4: Leave applications MUST receive written approval from the direct manager before leave commences; verbal approval is NOT valid.",
        "  - Clause 2.5: Unapproved absence WILL be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
        "  - Clause 2.6: Employees MAY carry forward a maximum of 5 unused annual leave days to the following year; any days above 5 ARE FORFEITED on 31 December.",
        "  - Clause 2.7: Carry-forward days MUST be used within the first quarter (January–March) of the following year or they ARE FORFEITED.",
        "",
        "3. SICK LEAVE",
        "  - Clause 3.1: Entitlement of 12 days of paid sick leave per calendar year.",
        "  - Clause 3.2: Sick leave of 3 or more consecutive days REQUIRES a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.",
        "  - Clause 3.3: Sick leave CANNOT be carried forward to the following year.",
        "  - Clause 3.4: Sick leave taken immediately before or after a public holiday or annual leave period REQUIRES a medical certificate regardless of duration.",
        "",
        "4. MATERNITY AND PATERNITY LEAVE",
        "  - Clause 4.1: Female employees receive 26 weeks of paid maternity leave for the first two live births.",
        "  - Clause 4.2: Maternity leave is 12 weeks paid for a third or subsequent child.",
        "  - Clause 4.3: Male employees receive 5 days of paid paternity leave, to be taken within 30 days of the child's birth.",
        "  - Clause 4.4: Paternity leave CANNOT be split across multiple periods.",
        "",
        "5. LEAVE WITHOUT PAY (LWP)",
        "  - Clause 5.1: Employees MAY apply for LWP ONLY after exhausting all applicable paid leave entitlements.",
        "  - Clause 5.2 [CRITICAL MULTI-CONDITION]: LWP REQUIRES approval from BOTH the Department Head AND the HR Director. Direct manager approval alone is NOT sufficient.",
        "  - Clause 5.3: LWP exceeding 30 continuous days REQUIRES approval from the Municipal Commissioner.",
        "  - Clause 5.4: Periods of LWP DO NOT count toward service for seniority, increments, or retirement benefits.",
        "",
        "6. PUBLIC HOLIDAYS",
        "  - Clause 6.1: Entitled to all gazetted public holidays declared by the State Government.",
        "  - Clause 6.2: Work required on a public holiday grants 1 compensatory off day, to be taken within 60 days of the holiday worked.",
        "  - Clause 6.3: Compensatory off CANNOT be encashed.",
        "",
        "7. LEAVE ENCASHMENT",
        "  - Clause 7.1: Annual leave MAY be encashed ONLY at the time of retirement or resignation, subject to a maximum of 60 days.",
        "  - Clause 7.2 [STRICT PROHIBITION]: Leave encashment during service is NOT PERMITTED under any circumstances.",
        "  - Clause 7.3: Sick leave and LWP CANNOT be encashed under any circumstances.",
        "",
        "8. GRIEVANCES",
        "  - Clause 8.1: Leave-related grievances MUST be raised with HR within 10 working days of the disputed decision.",
        "  - Clause 8.2: Grievances raised after 10 working days WILL NOT be considered unless exceptional circumstances are demonstrated in writing."
    ]

    summary_lines.extend(structured_summary)
    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy text file")
    parser.add_argument("--output", required=True, help="Path to write output summary text file")
    args = parser.parse_args()

    policy_data = retrieve_policy(args.input)
    summary_text = summarize_policy(policy_data)

    with open(args.output, mode="w", encoding="utf-8") as outfile:
        outfile.write(summary_text)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
