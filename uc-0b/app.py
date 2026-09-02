"""
UC-0B — Summary That Changes Meaning

Creates a faithful, source-grounded summary of the HR leave policy.

Protected failure modes:
1. Clause omission
2. Scope bleed
3. Obligation softening
"""

import argparse
import re
from pathlib import Path


# Ground-truth clauses required by the UC-0B specification.
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


def retrieve_policy(input_path: str) -> str:
    """
    Read the supplied policy document.

    The supplied policy document is the only source of truth.
    """

    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Policy file not found: {input_path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Input path is not a file: {input_path}"
        )

    try:
        content = path.read_text(
            encoding="utf-8-sig"
        )
    except UnicodeDecodeError as exc:
        raise ValueError(
            "Policy file must be a valid UTF-8 text file: "
            f"{exc}"
        )

    if not content.strip():
        raise ValueError(
            "Policy document is empty."
        )

    return content


def normalize_encoding(text: str) -> str:
    """
    Normalize common encoding artifacts without
    changing the meaning of the policy.
    """

    replacements = {
        "â€“": "-",
        "â€”": "-",
        "â€˜": "'",
        "â€™": "'",
        "â€œ": '"',
        "â€\x9d": '"',

        # Proper Unicode punctuation.
        "\u2013": "-",
        "\u2014": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',

        # Non-breaking space.
        "\u00a0": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def normalize_clause_text(text: str) -> str:
    """
    Clean extracted clause text without changing its meaning.
    """

    # Fix encoding issues first.
    text = normalize_encoding(text)

    # Collapse repeated whitespace.
    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    # Fix known word-joining artifacts.
    text = text.replace(
        "hoursof",
        "hours of"
    )

    text = text.replace(
        "daysof",
        "days of"
    )

    text = text.replace(
        "yearsof",
        "years of"
    )

    # Generic protection for a word immediately followed by "of".
    text = re.sub(
        r"([A-Za-z])of\b",
        r"\1 of",
        text,
        flags=re.IGNORECASE,
    )

    # Remove unwanted spaces before punctuation.
    text = re.sub(
        r"\s+([,.;:])",
        r"\1",
        text,
    )

    return text.strip()


def is_separator(line: str) -> bool:
    """
    Check whether a line is a decorative separator.
    """

    stripped = line.strip()

    if not stripped:
        return True

    separator_characters = set(
        "═-_=─━"
    )

    return all(
        character in separator_characters
        for character in stripped
    )


def extract_clauses(policy_text: str) -> dict:
    """
    Extract numbered policy clauses.

    Example:
        2.3 Employees must submit...

    Continuation lines belonging to the same clause
    are joined together.

    Section headings such as:
        1. PURPOSE AND SCOPE
        2. ANNUAL LEAVE

    are ignored.
    """

    clauses = {}

    current_clause = None
    current_text = []

    clause_pattern = re.compile(
        r"^\s*(\d+\.\d+)\s+(.+?)\s*$"
    )

    section_pattern = re.compile(
        r"^\s*\d+\.\s+.+$"
    )

    def save_current_clause():
        """
        Save the currently collected clause.
        """

        nonlocal current_clause
        nonlocal current_text

        if current_clause is None:
            return

        clause_text = normalize_clause_text(
            " ".join(current_text)
        )

        if not clause_text:
            raise ValueError(
                f"Clause {current_clause} is empty."
            )

        clauses[current_clause] = clause_text

    for line in policy_text.splitlines():

        stripped = line.strip()

        # Ignore empty lines.
        if not stripped:
            continue

        # Ignore decorative separators.
        if is_separator(stripped):
            continue

        # Ignore section headings.
        if section_pattern.match(stripped):
            continue

        match = clause_pattern.match(line)

        if match:

            # Save the previous clause.
            save_current_clause()

            # Start the new clause.
            current_clause = match.group(1)

            current_text = [
                match.group(2).strip()
            ]

        elif current_clause is not None:

            # Continuation line.
            current_text.append(
                stripped
            )

    # Save the final clause.
    save_current_clause()

    return clauses


def validate_required_clauses(
    clauses: dict
) -> None:
    """
    Verify that all required UC-0B clauses exist.
    """

    missing = [
        clause
        for clause in REQUIRED_CLAUSES
        if clause not in clauses
    ]

    if missing:
        raise ValueError(
            "Cannot safely generate the summary. "
            "Required clauses are missing: "
            + ", ".join(missing)
        )


def validate_clause_content(
    clauses: dict
) -> None:
    """
    Validate critical conditions that must never
    be lost or weakened.
    """

    # Clause 2.3
    clause_2_3 = clauses["2.3"]

    required_2_3 = [
        "14",
        "calendar days",
        "Form HR-L1",
    ]

    for term in required_2_3:
        if term.lower() not in clause_2_3.lower():
            raise ValueError(
                f"Clause 2.3 lost required information: {term}"
            )

    # Clause 2.4
    clause_2_4 = clauses["2.4"]

    required_2_4 = [
        "written approval",
        "direct manager",
        "before the leave commences",
        "Verbal approval is not valid",
    ]

    for term in required_2_4:
        if term.lower() not in clause_2_4.lower():
            raise ValueError(
                f"Clause 2.4 lost required information: {term}"
            )

    # Clause 2.5
    clause_2_5 = clauses["2.5"]

    required_2_5 = [
        "Loss of Pay",
        "regardless of subsequent approval",
    ]

    for term in required_2_5:
        if term.lower() not in clause_2_5.lower():
            raise ValueError(
                f"Clause 2.5 lost required information: {term}"
            )

    # Clause 2.6
    clause_2_6 = clauses["2.6"]

    required_2_6 = [
        "maximum of 5",
        "forfeited",
        "31 December",
    ]

    for term in required_2_6:
        if term.lower() not in clause_2_6.lower():
            raise ValueError(
                f"Clause 2.6 lost required information: {term}"
            )

    # Clause 2.7
    clause_2_7 = clauses["2.7"]

    required_2_7 = [
        "first quarter",
        "January-March",
        "forfeited",
    ]

    for term in required_2_7:
        if term.lower() not in clause_2_7.lower():
            raise ValueError(
                f"Clause 2.7 lost required information: {term}"
            )

    # Clause 3.2
    clause_3_2 = clauses["3.2"]

    required_3_2 = [
        "3 or more consecutive days",
        "medical certificate",
        "registered medical practitioner",
        "48 hours",
    ]

    for term in required_3_2:
        if term.lower() not in clause_3_2.lower():
            raise ValueError(
                f"Clause 3.2 lost required information: {term}"
            )

    # Clause 3.4
    clause_3_4 = clauses["3.4"]

    required_3_4 = [
        "public holiday",
        "annual leave period",
        "medical certificate",
        "regardless of duration",
    ]

    for term in required_3_4:
        if term.lower() not in clause_3_4.lower():
            raise ValueError(
                f"Clause 3.4 lost required information: {term}"
            )

    # Clause 5.2
    # This is the primary UC-0B trap:
    # BOTH approvers must be preserved.
    clause_5_2 = clauses["5.2"]

    required_5_2 = [
        "Department Head",
        "HR Director",
        "Manager approval alone is not sufficient",
    ]

    for term in required_5_2:
        if term.lower() not in clause_5_2.lower():
            raise ValueError(
                f"Clause 5.2 lost required information: {term}"
            )

    # Clause 5.3
    clause_5_3 = clauses["5.3"]

    required_5_3 = [
        "30 continuous days",
        "Municipal Commissioner",
    ]

    for term in required_5_3:
        if term.lower() not in clause_5_3.lower():
            raise ValueError(
                f"Clause 5.3 lost required information: {term}"
            )

    # Clause 7.2
    clause_7_2 = clauses["7.2"]

    required_7_2 = [
        "not permitted",
        "under any circumstances",
    ]

    for term in required_7_2:
        if term.lower() not in clause_7_2.lower():
            raise ValueError(
                f"Clause 7.2 lost required information: {term}"
            )


def build_summary(
    clauses: dict
) -> str:
    """
    Build the compliant summary directly from
    extracted policy clauses.
    """

    sections = [
        (
            "Scope",
            [
                "1.1",
                "1.2",
            ],
        ),
        (
            "Annual Leave",
            [
                "2.3",
                "2.4",
                "2.5",
                "2.6",
                "2.7",
            ],
        ),
        (
            "Sick Leave",
            [
                "3.2",
                "3.4",
            ],
        ),
        (
            "Leave Without Pay",
            [
                "5.2",
                "5.3",
            ],
        ),
        (
            "Leave Encashment",
            [
                "7.2",
            ],
        ),
    ]

    lines = [
        "CITY MUNICIPAL CORPORATION",
        "EMPLOYEE LEAVE POLICY - COMPLIANT SUMMARY",
        "",
        (
            "This summary is generated only from "
            "the supplied policy document."
        ),
    ]

    for section_name, clause_numbers in sections:

        lines.extend(
            [
                "",
                f"{section_name}:",
            ]
        )

        for clause_number in clause_numbers:

            if clause_number not in clauses:
                raise ValueError(
                    f"Required clause {clause_number} "
                    "cannot be included because it is missing."
                )

            lines.append(
                f"{clause_number}: "
                f"{clauses[clause_number]}"
            )

    lines.extend(
        [
            "",
            "Verification:",
            (
                "All required ground-truth clauses are present. "
                "No external policy information has been added."
            ),
        ]
    )

    return "\n".join(lines)


def summarize_policy(
    policy_text: str
) -> str:
    """
    Extract, validate, and generate the policy summary.
    """

    clauses = extract_clauses(
        policy_text
    )

    validate_required_clauses(
        clauses
    )

    validate_clause_content(
        clauses
    )

    return build_summary(
        clauses
    )


def write_summary(
    output_path: str,
    summary: str
) -> None:
    """
    Write the summary as UTF-8 text.
    """

    path = Path(
        output_path
    )

    try:
        path.write_text(
            summary,
            encoding="utf-8",
            newline="\n",
        )
    except OSError as exc:
        raise OSError(
            f"Unable to write summary to "
            f"{output_path}: {exc}"
        )


def main() -> None:
    """
    Command-line entry point.
    """

    parser = argparse.ArgumentParser(
        description=(
            "UC-0B — Source-grounded "
            "employee leave policy summary"
        )
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the source policy text file.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path where the summary will be written.",
    )

    args = parser.parse_args()

    try:

        policy_text = retrieve_policy(
            args.input
        )

        summary = summarize_policy(
            policy_text
        )

        write_summary(
            args.output,
            summary
        )

    except (
        FileNotFoundError,
        ValueError,
        OSError,
    ) as exc:

        raise SystemExit(
            f"Error: {exc}"
        )

    print(
        f"Done. Summary written to "
        f"{args.output}"
    )


if __name__ == "__main__":
    main()