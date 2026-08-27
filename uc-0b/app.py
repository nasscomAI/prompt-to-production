import argparse

def retrieve_policy(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.readlines()
    except Exception as e:
        raise Exception(f"Error loading file: {e}")

    clauses = {}
    current_clause = None

    for line in content:
        line = line.strip()
        if line and line[0].isdigit():
            parts = line.split(" ", 1)
            clause_id = parts[0]
            clause_text = parts[1] if len(parts) > 1 else ""

            current_clause = clause_id
            clauses[current_clause] = clause_text
        elif current_clause:
            clauses[current_clause] += " " + line

    return clauses


def summarize_policy(clauses):
    summary_lines = []

    for clause_id, text in clauses.items():
        # Strict preservation
        summary_lines.append(f"{clause_id} {text.strip()}")

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

    print(f"✅ Summary saved to {args.output}")


if __name__ == "__main__":
    main()