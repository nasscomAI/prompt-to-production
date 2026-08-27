"""
UC-0B — Summary That Changes Meaning

Policy summarizer for the City Municipal Corporation
Employee Leave Policy.

Workflow:
retrieve_policy -> summarize_policy
"""

import argparse
import re
from pathlib import Path


def retrieve_policy(input_path: str) -> list[dict]:
    """
    Read the policy file and extract numbered clauses.

    Section headings such as:
        2. ANNUAL LEAVE
        3. SICK LEAVE

    are ignored and are not merged into the previous clause.

    Clauses such as:
        2.1 Each permanent employee...
        2.2 Annual leave accrues...

    are extracted and returned.
    """

    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Input policy file not found: {input_path}"
        )

    with path.open("r", encoding="utf-8-sig") as file:
        content = file.read()

    # Remove empty and decorative lines
    lines = []

    for line in content.splitlines():
        stripped = line.strip()

        if not stripped:
            continue

        # Ignore decorative separator lines
        if all(char in "═─-_=*" for char in stripped):
            continue

        lines.append(stripped)

    clauses = []

    current_number = None
    current_text = []

    # Matches clauses such as:
    # 1.1 This policy governs...
    # 2.3 Employees must...
    # 7.2 Leave encashment...
    clause_pattern = re.compile(
        r"^(\d+\.\d+)\s+(.*)$"
    )

    # Matches section headings such as:
    # 1. PURPOSE
    # 2. ANNUAL LEAVE
    # 3. SICK LEAVE
    #
    # These are NOT clauses.
    section_pattern = re.compile(
        r"^\d+\.\s+[A-Z][A-Z\s&\-()]*$"
    )

    for line in lines:

        # -----------------------------------------------------
        # Check for a numbered clause
        # -----------------------------------------------------

        clause_match = clause_pattern.match(line)

        if clause_match:

            # Save previous clause
            if current_number is not None:
                clauses.append(
                    {
                        "number": current_number,
                        "text": " ".join(current_text).strip()
                    }
                )

            current_number = clause_match.group(1)
            current_text = [clause_match.group(2)]

            continue

        # -----------------------------------------------------
        # Check for a section heading
        # -----------------------------------------------------

        section_match = section_pattern.match(line)

        if section_match:
            # Section headings are intentionally ignored.
            continue

        # -----------------------------------------------------
        # Continuation of current clause
        # -----------------------------------------------------

        if current_number is not None:
            current_text.append(line)

    # Save final clause
    if current_number is not None:
        clauses.append(
            {
                "number": current_number,
                "text": " ".join(current_text).strip()
            }
        )

    if not clauses:
        raise ValueError(
            "No numbered policy clauses were found."
        )

    return clauses


def summarize_policy(clauses: list[dict]) -> str:
    """
    Produce a faithful clause-referenced summary.

    The summary is based only on the retrieved policy clauses.
    No external information is added.
    """

    output = []

    # ASCII-safe heading to avoid Windows CMD encoding issues
    output.append(
        "EMPLOYEE LEAVE POLICY - CLAUSE SUMMARY"
    )

    output.append("=" * 48)
    output.append("")

    for clause in clauses:

        number = clause["number"]
        text = clause["text"]

        output.append(
            f"Clause {number}: {text}"
        )

        output.append("")

    return "\n".join(output).rstrip() + "\n"


def save_summary(output_path: str, summary: str) -> None:
    """
    Save the generated summary to the output file.
    """

    output_file = Path(output_path)

    # Create output directory if necessary
    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with output_file.open(
        "w",
        encoding="utf-8"
    ) as file:
        file.write(summary)


def main():
    """
    Command-line entry point.
    """

    parser = argparse.ArgumentParser(
        description="UC-0B Policy Summarizer"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to policy_hr_leave.txt"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to write summary_hr_leave.txt"
    )

    args = parser.parse_args()

    try:

        # Step 1: Retrieve policy clauses
        clauses = retrieve_policy(
            args.input
        )

        # Step 2: Generate summary
        summary = summarize_policy(
            clauses
        )

        # Step 3: Save summary
        save_summary(
            args.output,
            summary
        )

        print(
            f"Done. Summary written to {args.output}"
        )

        print(
            f"Total clauses processed: {len(clauses)}"
        )

    except FileNotFoundError as exc:

        print(f"Error: {exc}")

    except PermissionError as exc:

        print(f"Permission error: {exc}")

    except OSError as exc:

        print(f"File error: {exc}")

    except ValueError as exc:

        print(f"Invalid policy file: {exc}")


if __name__ == "__main__":
    main()