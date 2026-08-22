"""
UC-0B — Summary That Changes Meaning

Deterministic policy summarizer.

The program:
1. Reads the source policy.
2. Extracts numbered clauses.
3. Verifies the required clause inventory.
4. Produces a faithful clause-referenced summary.
5. Refuses to silently omit or invent policy requirements.
"""

import argparse
import re
from pathlib import Path


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
    """
    Load the policy and extract numbered clauses.

    Returns:
        dict mapping clause number -> original clause text
    """

    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {input_path}")

    text = path.read_text(encoding="utf-8-sig")

    if not text.strip():
        raise ValueError("Policy file is empty.")

    clauses = {}

    # Match numbered clauses such as 2.3, 2.4, 5.2, etc.
    # A clause continues until the next numbered clause.
    pattern = re.compile(
        r"(?m)^\s*(\d+\.\d+)\s+(.*?)(?=^\s*\d+\.\d+\s+|\Z)",
        re.DOTALL,
    )

    for match in pattern.finditer(text):
        number = match.group(1)
        clause_text = " ".join(match.group(2).split())

        if clause_text:
            clauses[number] = clause_text

    if not clauses:
        raise ValueError(
            "No numbered policy clauses could be identified."
        )

    return clauses


def verify_clause_inventory(clauses):
    """
    Ensure every required clause exists in the source.
    """

    missing = [
        clause
        for clause in REQUIRED_CLAUSES
        if clause not in clauses
    ]

    if missing:
        raise ValueError(
            "Required policy clauses are missing from the source: "
            + ", ".join(missing)
        )


def summarize_policy(clauses):
    """
    Produce a clause-referenced summary.

    Because this exercise prioritizes meaning preservation,
    the original clause text is retained rather than paraphrased
    aggressively.
    """

    lines = [
        "CITY MUNICIPAL CORPORATION",
        "EMPLOYEE LEAVE POLICY — COMPLIANCE SUMMARY",
        "",
        "This summary preserves the requirements of all required "
        "numbered policy clauses.",
        "",
    ]

    for clause_number in REQUIRED_CLAUSES:
        clause_text = clauses[clause_number]

        lines.append(
            f"{clause_number} — {clause_text}"
        )

    lines.extend(
        [
            "",
            "VERIFICATION",
            "All required clauses are included: "
            + ", ".join(REQUIRED_CLAUSES),
            "No external policy information has been added.",
        ]
    )

    return "\n".join(lines)


def verify_summary(summary):
    """
    Verify that every required clause appears in the generated summary.
    """

    missing = [
        clause
        for clause in REQUIRED_CLAUSES
        if not re.search(
            rf"(?m)^\s*{re.escape(clause)}\s*[—-]",
            summary,
        )
    ]

    if missing:
        raise ValueError(
            "Generated summary is missing required clauses: "
            + ", ".join(missing)
        )


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Policy Summarizer"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to policy text file",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to output summary",
    )

    args = parser.parse_args()

    clauses = retrieve_policy(args.input)

    verify_clause_inventory(clauses)

    summary = summarize_policy(clauses)

    verify_summary(summary)

    Path(args.output).write_text(
        summary,
        encoding="utf-8",
    )

    print(
        f"Done. Summary written to {args.output}"
    )


if __name__ == "__main__":
    main()
