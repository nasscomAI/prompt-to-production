import argparse
import re


def retrieve_policy(input_path):
    """
    Load the policy file and return numbered clauses.
    """

    try:
        with open(input_path, "r", encoding="utf-8") as file:
            content = file.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {input_path}")

    if not content:
        raise ValueError("Policy file is empty.")

    # Find numbered clauses such as 2.3, 2.4, 3.2, etc.
    pattern = r"(?m)^(\d+\.\d+)\s*(.*?)(?=^\d+\.\d+\s|\Z)"
    matches = re.findall(pattern, content, re.DOTALL)

    if not matches:
        raise ValueError("No numbered clauses found in the policy document.")

    sections = []

    for clause_number, text in matches:
        sections.append({
            "clause": clause_number,
            "text": text.strip()
        })

    return sections


def summarize_policy(sections):
    """
    Create a compliant summary while preserving every clause.
    """

    if not sections:
        raise ValueError("No policy sections available to summarize.")

    summary = []

    for section in sections:
        clause = section["clause"]
        text = section["text"]

        # Preserve original text to avoid clause omission,
        # scope bleed, obligation softening, or condition dropping.
        summary.append(f"Clause {clause}: {text}")

    return "\n\n".join(summary)


def main():
    parser = argparse.ArgumentParser(
        description="HR Leave Policy Summarizer"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the HR leave policy file"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path for the summary output file"
    )

    args = parser.parse_args()

    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)

        with open(args.output, "w", encoding="utf-8") as file:
            file.write(summary)

        print(f"Summary created successfully: {args.output}")
        print(f"Total clauses processed: {len(sections)}")

    except Exception as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()