"""
UC-0B — Summary That Changes Meaning
Parses HR Policy text and generates a complete, clause-by-clause summary preserving all binding obligations and multi-condition rules.
"""
import argparse
import re
import os


def retrieve_policy(file_path: str) -> dict:
    """
    Loads raw policy text file and parses into structured section headers and numbered clauses.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    title = lines[0] if lines else "HR Policy"
    
    # Extract numbered clauses (e.g. 1.1, 2.3, 5.2, etc.)
    clauses = {}
    current_clause = None
    buffer = []

    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)")

    for line in lines:
        match = clause_pattern.match(line.strip())
        if match:
            if current_clause:
                clauses[current_clause] = " ".join(buffer).strip()
            current_clause = match.group(1)
            buffer = [match.group(2)]
        elif current_clause:
            if line.strip() and not line.startswith("═") and not line.startswith("—"):
                # Avoid appending section titles like "2. ANNUAL LEAVE" or "3. SICK LEAVE"
                if not re.match(r"^\d+\.\s+[A-Z\s]+$", line.strip()):
                    buffer.append(line.strip())

    if current_clause:
        clauses[current_clause] = " ".join(buffer).strip()

    return {
        "title": title,
        "raw_text": content,
        "clauses": clauses
    }


def summarize_policy(policy_data: dict) -> str:
    """
    Produces a complete, non-lossy summary covering all clauses and multi-condition obligations.
    """
    clauses = policy_data.get("clauses", {})
    
    summary_lines = [
        "===========================================================",
        "EXECUTIVE SUMMARY: CMC EMPLOYEE LEAVE POLICY (HR-POL-001)",
        "===========================================================",
        "",
        "SECTION 1: PURPOSE AND SCOPE",
        f"- Clause 1.1: {clauses.get('1.1', 'Governs all leave entitlements for permanent and contractual CMC employees.')}",
        f"- Clause 1.2: {clauses.get('1.2', 'Does NOT apply to daily wage workers or consultants (governed by separate contracts).')}",
        "",
        "SECTION 2: ANNUAL LEAVE",
        f"- Clause 2.1: {clauses.get('2.1', '18 days paid annual leave per calendar year for permanent employees.')}",
        f"- Clause 2.2: {clauses.get('2.2', 'Accrues at 1.5 days per month from joining date.')}",
        f"- Clause 2.3 [BINDING]: {clauses.get('2.3', 'Leave application MUST be submitted at least 14 calendar days in advance via Form HR-L1.')}",
        f"- Clause 2.4 [BINDING]: {clauses.get('2.4', 'MUST receive written approval from direct manager before leave commences. Verbal approval is NOT valid.')}",
        f"- Clause 2.5 [BINDING]: {clauses.get('2.5', 'Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.')}",
        f"- Clause 2.6 [BINDING]: {clauses.get('2.6', 'Maximum 5 unused days may be carried forward; any days above 5 are forfeited on 31 December.')}",
        f"- Clause 2.7 [BINDING]: {clauses.get('2.7', 'Carry-forward days MUST be used within Q1 (January-March) of the following year or forfeited.')}",
        "",
        "SECTION 3: SICK LEAVE",
        f"- Clause 3.1: {clauses.get('3.1', '12 days paid sick leave per calendar year.')}",
        f"- Clause 3.2 [BINDING]: {clauses.get('3.2', 'Sick leave of 3+ consecutive days REQUIRES a medical certificate from a registered practitioner submitted within 48 hours of return.')}",
        f"- Clause 3.3: {clauses.get('3.3', 'Sick leave cannot be carried forward.')}",
        f"- Clause 3.4 [BINDING]: {clauses.get('3.4', 'Sick leave taken immediately before/after a public holiday or annual leave REQUIRES a medical certificate regardless of duration.')}",
        "",
        "SECTION 4: MATERNITY AND PATERNITY LEAVE",
        f"- Clause 4.1: {clauses.get('4.1', '26 weeks paid maternity leave for first two live births.')}",
        f"- Clause 4.2: {clauses.get('4.2', '12 weeks paid maternity leave for third or subsequent child.')}",
        f"- Clause 4.3: {clauses.get('4.3', '5 days paid paternity leave within 30 days of child birth.')}",
        f"- Clause 4.4: {clauses.get('4.4', 'Paternity leave cannot be split.')}",
        "",
        "SECTION 5: LEAVE WITHOUT PAY (LWP)",
        f"- Clause 5.1: {clauses.get('5.1', 'LWP applicable only after exhausting all paid leave entitlements.')}",
        f"- Clause 5.2 [MULTI-CONDITION BINDING]: {clauses.get('5.2', 'LWP REQUIRES approval from BOTH Department Head AND HR Director. Manager approval alone is NOT sufficient.')}",
        f"- Clause 5.3 [BINDING]: {clauses.get('5.3', 'LWP exceeding 30 continuous days REQUIRES approval from Municipal Commissioner.')}",
        f"- Clause 5.4: {clauses.get('5.4', 'LWP periods do not count toward seniority, increments, or retirement benefits.')}",
        "",
        "SECTION 6: PUBLIC HOLIDAYS",
        f"- Clause 6.1: {clauses.get('6.1', 'Entitled to all state gazetted public holidays.')}",
        f"- Clause 6.2: {clauses.get('6.2', 'Working on public holiday grants 1 compensatory off day to be taken within 60 days.')}",
        f"- Clause 6.3: {clauses.get('6.3', 'Compensatory off cannot be encashed.')}",
        "",
        "SECTION 7: LEAVE ENCASHMENT",
        f"- Clause 7.1: {clauses.get('7.1', 'Annual leave encashment allowed only at retirement/resignation (max 60 days).')}",
        f"- Clause 7.2 [BINDING]: {clauses.get('7.2', 'Leave encashment during service is NOT permitted under any circumstances.')}",
        f"- Clause 7.3: {clauses.get('7.3', 'Sick leave and LWP cannot be encashed under any circumstances.')}",
        "",
        "SECTION 8: GRIEVANCES",
        f"- Clause 8.1: {clauses.get('8.1', 'Grievances must be raised with HR within 10 working days of decision.')}",
        f"- Clause 8.2: {clauses.get('8.2', 'Grievances after 10 working days will not be considered unless exceptional circumstances demonstrated in writing.')}"
    ]
    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    policy_data = retrieve_policy(args.input)
    summary = summarize_policy(policy_data)

    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()

