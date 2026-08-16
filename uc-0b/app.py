import argparse
import re


def retrieve_policy(input_file):
    """Load the policy and return only its numbered clauses."""
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    clauses = {}
    current = None

    for line in text.splitlines():
        line = line.strip()

        # Ignore decorative separator lines
        if not line or set(line) <= set("═-=_ "):
            continue

        # Match actual clauses such as 2.3, 3.2, 5.2
        match = re.match(r"^(\d+\.\d+)\s+(.*)$", line)

        if match:
            current = match.group(1)
            clauses[current] = match.group(2)
            continue

        # Ignore section headings such as "3. SICK LEAVE"
        if re.match(r"^\d+\.\s+", line):
            current = None
            continue

        # Continue multi-line clause text
        if current:
            clauses[current] += " " + line

    return clauses


def summarize_policy(clauses):
    """Create a summary while preserving the required clauses."""
    required = [
        "2.3", "2.4", "2.5", "2.6", "2.7",
        "3.2", "3.4", "5.2", "5.3", "7.2"
    ]

    lines = [
        "HR Leave Policy Summary",
        "Document Reference: HR-POL-001",
        ""
    ]

    for clause in required:
        if clause not in clauses:
            lines.append(
                f"{clause}: [FLAGGED - clause missing from source]"
            )
        else:
            lines.append(f"{clause}: {clauses[clause]}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()