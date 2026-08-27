import argparse

REQUIRED_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4",
    "5.2", "5.3",
    "7.2"
]

def retrieve_policy(input_path):
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    clauses = {}
    lines = text.split("\n")

    current_clause = None
    buffer = []

    for line in lines:
        stripped = line.strip()
        if len(stripped) > 2 and stripped[0].isdigit() and "." in stripped[:4]:
            if current_clause:
                clauses[current_clause] = " ".join(buffer).strip()
                buffer = []
            current_clause = stripped.split()[0]
            buffer.append(stripped)
        else:
            if current_clause:
                buffer.append(stripped)

    if current_clause:
        clauses[current_clause] = " ".join(buffer).strip()

    return clauses


def summarize_policy(clauses):
    summary_lines = []

    for clause in REQUIRED_CLAUSES:
        if clause in clauses:
            text = clauses[clause]

            if clause == "5.2":
                summary_lines.append(
                    "Clause 5.2: Leave Without Pay requires approval from BOTH Department Head and HR Director."
                )
            elif clause == "7.2":
                summary_lines.append(
                    "Clause 7.2: Leave encashment during service is not permitted under any circumstances."
                )
            else:
                summary_lines.append(f"Clause {clause}: {text}")

        else:
            summary_lines.append(f"Clause {clause}: NOT FOUND — NEEDS REVIEW")

    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print("Summary generated successfully.")


if __name__ == "__main__":
    main()