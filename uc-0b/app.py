import argparse
import re


def retrieve_policy(input_path):
    """Read the policy and extract every numbered clause."""

    with open(input_path, "r", encoding="utf-8-sig") as f:
        text = f.read()

    # Remove decorative separator lines.
    lines = []
    for line in text.splitlines():
        stripped = line.strip()

        # Ignore lines made mainly from box/separator characters.
        if stripped and not re.search(r"\d+\.\d+", stripped):
            if not re.search(r"[A-Za-z]{3,}", stripped):
                continue

        lines.append(line)

    text = "\n".join(lines)

    # Normalize encoding artifacts without deleting useful words.
    text = text.replace("ΓÇô", "-")
    text = text.replace("ΓÇö", "-")
    text = text.replace("ΓÇÉ", "-")

    # Collapse whitespace.
    text = re.sub(r"[ \t]+", " ", text)

    # Extract numbered clauses.
    # Example: 2.3 Employees must submit...
    pattern = re.compile(
        r"(?m)^\s*(\d+\.\d+)\s+(.*?)(?=^\s*\d+\.\d+\s+|\Z)",
        re.DOTALL
    )

    clauses = []

    for match in pattern.finditer(text):
        number = match.group(1)
        clause_text = match.group(2)

        # Remove blank lines and normalize spaces.
        clause_text = " ".join(clause_text.split())

        # Remove accidental section headings/decorative text.
        clause_text = re.sub(
            r"\s+\d+\.\s+[A-Z][A-Z\s()&-]+$",
            "",
            clause_text
        ).strip()

        if clause_text:
            clauses.append({
                "number": number,
                "text": clause_text
            })

    if not clauses:
        raise ValueError("No numbered policy clauses found.")

    return clauses


def summarize_policy(clauses):
    """Create a compliant clause-preserving summary."""

    output = []

    output.append("CITY MUNICIPAL CORPORATION")
    output.append("EMPLOYEE LEAVE POLICY - COMPLIANT SUMMARY")
    output.append("")
    output.append(
        "This summary preserves every numbered clause from the source policy."
    )
    output.append(
        "Only information contained in the source policy is included."
    )
    output.append("")

    for clause in clauses:
        output.append(
            f"{clause['number']}: {clause['text']}"
        )
        output.append("")

    return "\n".join(output).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B policy summarization agent"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to policy_hr_leave.txt"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to summary output file"
    )

    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)

        summary = summarize_policy(clauses)

        with open(
            args.output,
            "w",
            encoding="utf-8"
        ) as outfile:
            outfile.write(summary)

        print(
            f"Done. Summary written to {args.output}"
        )
        print(
            f"Clauses processed: {len(clauses)}"
        )

    except Exception as exc:
        print(f"ERROR: {exc}")
        raise


if __name__ == "__main__":
    main()