"""
UC-0B - Summary That Changes Meaning

Reads the HR leave policy and produces a clause-complete summary.
"""

import argparse
import re


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


def retrieve_policy(input_path):
    """Load the policy document and return numbered clauses."""

    with open(input_path, "r", encoding="utf-8-sig") as file:
        content = file.read()

    clauses = {}

    pattern = re.compile(
        r"(?m)^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+\s+|\Z)",
        re.DOTALL,
    )

    for match in pattern.finditer(content):
        number = match.group(1)
        text = " ".join(match.group(2).split())
        clauses[number] = text

    return clauses


def summarize_policy(clauses):
    """
    Produce a faithful summary.

    Every required clause must be present.
    Multi-condition obligations must preserve every condition.
    No information outside the source policy is added.
    """

    summary = []

    summary.append("CITY MUNICIPAL CORPORATION - EMPLOYEE LEAVE POLICY")
    summary.append("")
    summary.append("Policy Summary")
    summary.append("================")
    summary.append("")

    # ---------------------------------------------------------
    # PURPOSE AND SCOPE
    # ---------------------------------------------------------

    summary.append("1. Purpose and Scope")

    if "1.1" in clauses:
        summary.append(f"Clause 1.1: {clauses['1.1']}")

    if "1.2" in clauses:
        summary.append(f"Clause 1.2: {clauses['1.2']}")

    summary.append("")

    # ---------------------------------------------------------
    # ANNUAL LEAVE
    # ---------------------------------------------------------

    summary.append("2. Annual Leave")

    for clause in ["2.3", "2.4", "2.5", "2.6", "2.7"]:
        if clause in clauses:
            summary.append(f"Clause {clause}: {clauses[clause]}")

    summary.append("")

    # ---------------------------------------------------------
    # SICK LEAVE
    # ---------------------------------------------------------

    summary.append("3. Sick Leave")

    for clause in ["3.2", "3.4"]:
        if clause in clauses:
            summary.append(f"Clause {clause}: {clauses[clause]}")

    summary.append("")

    # ---------------------------------------------------------
    # LEAVE WITHOUT PAY
    # ---------------------------------------------------------

    summary.append("5. Leave Without Pay (LWP)")

    for clause in ["5.2", "5.3"]:
        if clause in clauses:
            summary.append(f"Clause {clause}: {clauses[clause]}")

    summary.append("")

    # ---------------------------------------------------------
    # LEAVE ENCASHMENT
    # ---------------------------------------------------------

    summary.append("7. Leave Encashment")

    if "7.2" in clauses:
        summary.append(f"Clause 7.2: {clauses['7.2']}")

    summary.append("")

    # ---------------------------------------------------------
    # CLAUSE VERIFICATION
    # ---------------------------------------------------------

    summary.append("Clause Verification")
    summary.append("===================")

    missing = []

    for clause in REQUIRED_CLAUSES:
        if clause not in clauses:
            missing.append(clause)

    if missing:
        summary.append(
            "NEEDS_REVIEW: Missing required clauses: "
            + ", ".join(missing)
        )
    else:
        summary.append(
            "All 10 required clauses "
            "(2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) "
            "are included."
        )

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Policy Summary Generator"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the policy text file",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to the summary output file",
    )

    args = parser.parse_args()

    clauses = retrieve_policy(args.input)

    summary = summarize_policy(clauses)

    with open(
        args.output,
        "w",
        encoding="utf-8",
    ) as file:
        file.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
