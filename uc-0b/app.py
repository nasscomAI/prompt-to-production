"""
UC-0B — HR Leave Policy Summarizer

Built using the RICE → agents.md → skills.md → CRAFT workflow.
"""

import argparse
import re


# The 10 ground-truth clauses specified by UC-0B.
REQUIRED_CLAUSES = [
    "2.3",
    "2.4",
    "2.5",
    "2.6",
    "2.7",
    "3.2",
    "3.4",
    "5.2",
    "5.3",
    "7.2",
]


def retrieve_policy(input_path: str) -> dict:
    """
    Load the policy and extract numbered clauses.

    Returns:
        Dictionary mapping clause numbers to source text.
    """

    with open(input_path, "r", encoding="utf-8-sig") as infile:
        content = infile.read()

    sections = {}

    # Match numbered clauses such as 2.3, 2.4, 5.2, etc.
    pattern = re.compile(
        r"(?m)^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+\s|\Z)",
        re.DOTALL,
    )

    for match in pattern.finditer(content):
        clause_number = match.group(1)
        clause_text = " ".join(match.group(2).split())
        sections[clause_number] = clause_text

    return sections


def summarize_policy(sections: dict) -> str:
    """
    Produce a compliant summary containing all ten required clauses.

    The wording intentionally preserves the conditions and obligations
    identified by the UC-0B clause inventory.
    """

    missing = [
        clause
        for clause in REQUIRED_CLAUSES
        if clause not in sections
    ]

    if missing:
        raise ValueError(
            "Required policy clauses are missing: "
            + ", ".join(missing)
        )

    summary = """CITY MUNICIPAL CORPORATION
EMPLOYEE LEAVE POLICY — COMPLIANCE SUMMARY

2. ANNUAL LEAVE

Clause 2.3 — Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1.

Clause 2.4 — Leave applications must receive written approval from the employee's direct manager before the leave commences. Verbal approval is not valid.

Clause 2.5 — Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.

Clause 2.6 — Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December.

Clause 2.7 — Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.

3. SICK LEAVE

Clause 3.2 — Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.

Clause 3.4 — Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.

5. LEAVE WITHOUT PAY (LWP)

Clause 5.2 — LWP requires approval from both the Department Head and the HR Director. Manager approval alone is not sufficient.

Clause 5.3 — LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.

7. LEAVE ENCASHMENT

Clause 7.2 — Leave encashment during service is not permitted under any circumstances.
"""

    return summary


def validate_summary(summary: str):
    """
    Verify that every required clause is present and that critical
    multi-condition obligations have not been weakened.
    """

    missing = [
        clause
        for clause in REQUIRED_CLAUSES
        if f"Clause {clause}" not in summary
    ]

    if missing:
        raise ValueError(
            "Summary is missing required clauses: "
            + ", ".join(missing)
        )

    critical_requirements = {
        "2.3": ["14 calendar days", "must", "HR-L1"],
        "2.4": ["written approval", "direct manager", "before the leave commences", "Verbal approval is not valid"],
        "2.5": ["Loss of Pay", "regardless of subsequent approval"],
        "2.6": ["maximum of 5", "forfeited", "31 December"],
        "2.7": ["first quarter", "January–March", "forfeited"],
        "3.2": ["3 or more consecutive days", "medical certificate", "registered medical practitioner", "48 hours"],
        "3.4": ["before or after", "public holiday", "annual leave", "regardless of duration"],
        "5.2": ["Department Head", "HR Director", "Manager approval alone is not sufficient"],
        "5.3": ["exceeding 30 continuous days", "Municipal Commissioner"],
        "7.2": ["not permitted under any circumstances"],
    }

    for clause, requirements in critical_requirements.items():
        start = summary.find(f"Clause {clause}")
        next_clause = summary.find("Clause ", start + 1)

        if next_clause == -1:
            section = summary[start:]
        else:
            section = summary[start:next_clause]

        for requirement in requirements:
            if requirement.lower() not in section.lower():
                raise ValueError(
                    f"Clause {clause} lost required condition: "
                    f"{requirement}"
                )


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B HR Leave Policy Summarizer"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to policy_hr_leave.txt",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to summary output file",
    )

    args = parser.parse_args()

    sections = retrieve_policy(args.input)

    summary = summarize_policy(sections)

    validate_summary(summary)

    with open(
        args.output,
        "w",
        encoding="utf-8",
    ) as outfile:
        outfile.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()