import argparse
import os

def retrieve_policy(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError("Input file not found")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.strip():
        raise ValueError("Policy file is empty")

    # Simple clause split (based on numbering like 2.3, 2.4 etc.)
    lines = content.split("\n")
    clauses = []

    current_clause = ""
    for line in lines:
        line = line.strip()
        if line and line[0].isdigit():
            if current_clause:
                clauses.append(current_clause.strip())
            current_clause = line
        else:
            current_clause += " " + line

    if current_clause:
        clauses.append(current_clause.strip())

    return clauses


def summarize_policy(clauses):
    if not clauses:
        raise ValueError("No clauses found")

    summary = []

    for clause in clauses:
        # Do NOT aggressively shorten — preserve meaning
        summary.append(clause)

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)

        print("Summary generated successfully.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()