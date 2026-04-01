"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse


def summarize_policy(text: str) -> str:
    """
    Create a safe summary that preserves important rules and numbers.
    """

    lines = text.splitlines()
    summary = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        lower = line.lower()

        # Preserve numbered clauses
        if line[0].isdigit():
            summary.append(line)

        # Preserve critical rule words
        elif any(word in lower for word in [
            "must", "shall", "required", "approval",
            "days", "leave", "policy"
        ]):
            summary.append(line)

    if not summary:
        return "FULL_TEXT_REQUIRED"

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy document")
    parser.add_argument("--output", required=True, help="Output summary file")

    args = parser.parse_args()

    # Read policy
    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    # Generate summary
    summary = summarize_policy(text)

    # Write summary
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()