import argparse


def retrieve_policy(file_path: str) -> dict:
    sections = {}
    current_clause = None

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            # Detect clause numbers like 2.3, 3.2 etc.
            if line[0].isdigit() and "." in line[:4]:
                parts = line.split(" ", 1)
                clause_id = parts[0]

                if len(parts) > 1:
                    sections[clause_id] = parts[1]
                else:
                    sections[clause_id] = ""

                current_clause = clause_id
            else:
                if current_clause:
                    sections[current_clause] += " " + line

    return sections


def summarize_policy(sections: dict) -> str:
    REQUIRED_CLAUSES = [
        "2.3", "2.4", "2.5", "2.6", "2.7",
        "3.2", "3.4", "5.2", "5.3", "7.2"
    ]

    summary_lines = []

    for clause in REQUIRED_CLAUSES:
        text = sections.get(clause, "").strip()

        # Missing clause handling
        if not text:
            summary_lines.append(f"{clause} [MISSING — NEEDS_REVIEW]")
            continue

        # Detect risky clauses (multi-condition)
        lower_text = text.lower()
        risky = any(word in lower_text for word in ["and", "or"])

        if risky:
            summary_lines.append(f"{clause} {text} [REVIEW]")
        else:
            summary_lines.append(f"{clause} {text}")

    return "\n\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to {args.output}")


if __name__ == "__main__":
    main()
