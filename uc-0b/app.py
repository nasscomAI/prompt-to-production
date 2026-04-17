import argparse


def retrieve_policy(input_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    lines = text.split("\n")

    clauses = []
    current_clause = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect clause IDs like 2.3, 5.2 etc.
        if line[:3].replace('.', '').isdigit():
            if current_clause:
                clauses.append(current_clause)

            parts = line.split(" ", 1)
            clause_id = parts[0]
            clause_text = parts[1] if len(parts) > 1 else ""

            current_clause = {"id": clause_id, "text": clause_text}
        else:
            if current_clause:
                current_clause["text"] += " " + line

    if current_clause:
        clauses.append(current_clause)

    return clauses


def summarize_policy(clauses):
    summary_lines = []

    for clause in clauses:
        cid = clause["id"]
        text = clause["text"].strip()

        # IMPORTANT: Do NOT over-summarize
        # Keep full meaning intact
        summary = text

        summary_lines.append(f"{cid}: {summary}")

    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to output summary file")

    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)

    print(f"Summary generated: {args.output}")


if __name__ == "__main__":
    main()