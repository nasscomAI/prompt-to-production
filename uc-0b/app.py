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
    """Load the policy .txt file and return its numbered sections."""

    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Policy file not found: {input_path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Input path is not a file: {input_path}"
        )

    if path.suffix.lower() != ".txt":
        raise ValueError(
            "Input policy must be a .txt file."
        )

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(
            "Policy file could not be decoded as UTF-8."
        ) from exc

    if not text.strip():
        raise ValueError("Policy file is empty.")

    sections = {}
    current_clause = None
    current_lines = []

    clause_pattern = re.compile(
        r"^\s*(?:Clause\s+)?(\d+\.\d+)\b[\s:.-]*(.*)$",
        re.IGNORECASE
    )

    for line in text.splitlines():
        match = clause_pattern.match(line)

        if match:
            if current_clause is not None:
                sections[current_clause] = (
                    "\n".join(current_lines).strip()
                )

            current_clause = match.group(1)

            first_text = match.group(2).strip()

            if first_text:
                current_lines = [first_text]
            else:
                current_lines = []

        elif current_clause is not None:
            current_lines.append(line)

    if current_clause is not None:
        sections[current_clause] = (
            "\n".join(current_lines).strip()
        )

    return {
        "text": text,
        "sections": sections
    }


def find_clause_content(policy, clause):
    """Find a clause in the structured policy."""

    sections = policy["sections"]

    if clause in sections:
        content = sections[clause].strip()

        if content:
            return content

    return None


def validate_clause(clause, content):
    """Check that important conditions have been preserved."""

    if not content:
        return False

    text = content.lower()

    if clause == "2.3":
        return (
            "14" in text
            and "notice" in text
        )

    if clause == "2.4":
        return (
            "written" in text
            and "approval" in text
            and "before" in text
            and "verbal" in text
        )

    if clause == "2.5":
        return (
            "unapproved" in text
            and "absence" in text
            and "lop" in text
            and "approval" in text
        )

    if clause == "2.6":
        return (
            "5" in text
            and "carry" in text
            and "forfeit" in text
        )

    if clause == "2.7":
        return (
            "carry" in text
            and (
                "jan" in text
                or "january" in text
            )
            and (
                "mar" in text
                or "march" in text
            )
            and "forfeit" in text
        )

    if clause == "3.2":
        return (
            (
                "3" in text
                or "three" in text
            )
            and "sick" in text
            and "medical" in text
            and "48" in text
        )

    if clause == "3.4":
        return (
            "sick" in text
            and "holiday" in text
            and "cert" in text
            and "duration" in text
        )

    if clause == "5.2":
        return (
            "lwp" in text
            and "department head" in text
            and "hr director" in text
            and "approval" in text
        )

    if clause == "5.3":
        return (
            "lwp" in text
            and "30" in text
            and "municipal commissioner" in text
            and "approval" in text
        )

    if clause == "7.2":
        return (
            "leave" in text
            and "encashment" in text
            and "not permitted" in text
        )

    return True


def summarize_policy(policy):
    """
    Create a conservative summary.

    The original policy wording is retained wherever possible
    to avoid changing the meaning of obligations.
    """

    results = []

    for clause in REQUIRED_CLAUSES:

        content = find_clause_content(
            policy,
            clause
        )

        if content is None:
            results.append(
                f"[Clause {clause}] "
                "ERROR: Required clause could not be found "
                "in the source document."
            )
            continue

        if not validate_clause(
            clause,
            content
        ):
            results.append(
                f"[Clause {clause}] "
                "FLAG: The clause could not be safely "
                "summarized without possible meaning loss.\n"
                f"Verbatim source: \"{content}\""
            )
            continue

        results.append(
            f"[Clause {clause}] {content}"
        )

    return "\n\n".join(results)


def main():

    parser = argparse.ArgumentParser(
        description="UC-0B HR Policy Summarizer"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the HR policy .txt file"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path for the generated summary"
    )

    args = parser.parse_args()

    try:

        policy = retrieve_policy(
            args.input
        )

        summary = summarize_policy(
            policy
        )

        output_path = Path(
            args.output
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        output_path.write_text(
            summary + "\n",
            encoding="utf-8"
        )

        print(
            f"Summary successfully written to: "
            f"{output_path}"
        )

    except FileNotFoundError as error:

        print(f"ERROR: {error}")
        raise SystemExit(1)

    except ValueError as error:

        print(f"ERROR: {error}")
        raise SystemExit(1)

    except OSError as error:

        print(f"ERROR: Could not access file: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()