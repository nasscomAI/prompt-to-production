import argparse
import re


def retrieve_policy(file_path):
    clauses = {}
    current_clause = None

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # Skip empty lines and section headers (==== or ALL CAPS lines)
            if not line or re.match(r"^=+", line) or line.isupper():
                continue

            # Match clause numbers like 2.3, 3.2 etc.
            match = re.match(r"^(\d+\.\d+)\s+(.*)", line)
            if match:
                current_clause = match.group(1)
                clauses[current_clause] = match.group(2).strip()
            elif current_clause:
                # Append continuation lines properly
                clauses[current_clause] += " " + line.strip()

    return clauses


def summarize_policy(clauses):
    summary_lines = []

    REQUIRED_CLAUSES = [
        "2.3", "2.4", "2.5", "2.6", "2.7",
        "3.2", "3.4", "5.2", "5.3", "7.2"
    ]

    for clause in REQUIRED_CLAUSES:
        text = clauses.get(clause, "").strip()

        if not text:
            summary_lines.append(f"{clause}: MISSING CLAUSE [NEEDS_REVIEW]")
            continue

        # ---------------- MULTI-CONDITION CHECK ----------------
        if clause == "5.2":
            if "department head" not in text.lower() or "hr director" not in text.lower():
                summary_lines.append(f"{clause}: {text} [NEEDS_REVIEW]")
                continue

        # ---------------- MEANING PRESERVATION ----------------
        # Use VERBATIM only when needed (long/complex clauses)
        if len(text.split()) > 25:
            line = f"{clause}: {text} [VERBATIM]"
        else:
            line = f"{clause}: {text}"

        summary_lines.append(line)

    # ---------------- CLEAN FORMATTING ----------------
    return "\n\n".join(summary_lines)


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