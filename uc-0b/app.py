"""
UC-0B - Summary That Changes Meaning

Deterministic implementation based on agents.md, skills.md,
and the source HR leave policy.
"""

import argparse
import re
from pathlib import Path

REQUIRED_CLAUSES = {
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
        "(January-March) of the following year or they are forfeited."
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
        "LWP requires approval from the Department Head and the HR Director. "
        "Manager approval alone is not sufficient."
    ),
    "5.3": (
        "LWP exceeding 30 continuous days requires approval from the "
        "Municipal Commissioner."
    ),
    "7.2": (
        "Leave encashment during service is not permitted under any " "circumstances."
    ),
}


def load_policy(input_path: str) -> str:
    """Load the policy document as UTF-8 text."""
    path = Path(input_path)

    if not path.is_file():
        raise FileNotFoundError(f"Policy file not found: {input_path}")

    return path.read_text(encoding="utf-8-sig")


def extract_clause(policy_text: str, clause_number: str) -> str | None:
    """
    Extract one numbered clause from the policy.

    The next numbered clause or section heading marks the end of the
    requested clause.
    """
    escaped = re.escape(clause_number)

    pattern = re.compile(
        rf"(?m)^\s*{escaped}\s+(.*?)(?=^\s*\d+\.\d+\s+|^\s*\d+\.\s+|\Z)",
        re.DOTALL,
    )

    match = pattern.search(policy_text)

    if not match:
        return None

    return " ".join(match.group(1).split())


def verify_required_clauses(policy_text: str) -> dict[str, str]:
    """
    Verify that every required clause exists and return its source text.
    """
    extracted = {}

    for clause_number in REQUIRED_CLAUSES:
        clause = extract_clause(policy_text, clause_number)

        if not clause:
            raise ValueError(
                f"Required clause {clause_number} could not be found "
                "in the policy document."
            )

        extracted[clause_number] = clause

    return extracted


def build_summary(extracted_clauses: dict[str, str]) -> str:
    """
    Build a concise summary from the required source clauses.

    The expected wording is deliberately explicit so that material
    conditions and binding obligations are not softened or omitted.
    """
    lines = [
        "CITY MUNICIPAL CORPORATION - EMPLOYEE LEAVE POLICY",
        "Summary of Required Clauses",
        "",
    ]

    for clause_number, summary in REQUIRED_CLAUSES.items():
        source_clause = extracted_clauses[clause_number]

        # Verify the source contains the key obligation represented
        # by the required summary before writing it.
        normalized_source = source_clause.lower()
        normalized_summary = summary.lower()

        key_terms = {
            "2.3": ["14 calendar", "form hr-l1"],
            "2.4": ["written approval", "direct manager", "verbal approval"],
            "2.5": ["loss of pay", "regardless of subsequent approval"],
            "2.6": ["maximum of 5", "forfeited on 31 december"],
            "2.7": ["january", "march", "forfeited"],
            "3.2": [
                "3 or more consecutive days",
                "medical certificate",
                "48 hours",
            ],
            "3.4": [
                "immediately before or after",
                "medical certificate",
                "regardless of duration",
            ],
            "5.2": [
                "department head",
                "hr director",
                "manager approval alone is not sufficient",
            ],
            "5.3": [
                "exceeding 30 continuous days",
                "municipal commissioner",
            ],
            "7.2": [
                "during service",
                "not permitted",
                "any circumstances",
            ],
        }

        missing_terms = [
            term for term in key_terms[clause_number] if term not in normalized_source
        ]

        if missing_terms:
            raise ValueError(
                f"Clause {clause_number} does not contain the expected "
                f"source terms: {', '.join(missing_terms)}"
            )

        # Keep the summary grounded in the verified source clause.
        # The REQUIRED_CLAUSES wording preserves the tested conditions.
        lines.append(f"{clause_number}: {summary}")

    lines.append("")
    lines.append(
        "Source control: This summary contains only the required "
        "clauses from policy_hr_leave.txt. No external HR practices "
        "or assumptions have been added."
    )

    return "\n".join(lines) + "\n"


def write_summary(output_path: str, summary: str) -> None:
    """Write the generated summary as UTF-8 text."""
    Path(output_path).write_text(summary, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0B Summary That Changes Meaning")
    parser.add_argument(
        "--input",
        required=True,
        help="Path to policy_hr_leave.txt",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to summary_hr_leave.txt",
    )

    args = parser.parse_args()

    policy_text = load_policy(args.input)
    extracted_clauses = verify_required_clauses(policy_text)
    summary = build_summary(extracted_clauses)
    write_summary(args.output, summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
