import argparse
import re


def retrieve_policy(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Remove divider lines
    text = re.sub(r'═+', '', text)

    # Remove Effective date
    text = re.sub(r'\|\s*Effective:.*', '', text)

    # Remove section titles like "7. LEAVE ENCASHMENT"
    text = re.sub(r'\n\s*\d+\.\s+[A-Z\s()]+\n', '\n', text)

    # Extract numbered clauses
    pattern = r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)'
    matches = re.findall(pattern, text, re.DOTALL)

    clauses = []

    for num, clause in matches:

        # Remove clause numbers accidentally captured inside text
        clause = re.sub(r'^\d+\.\d+\s*', '', clause)

        # Clean whitespace
        clean_clause = " ".join(clause.split())

        clauses.append((num, clean_clause))

    return clauses


def summarize_policy(clauses):
    summary_lines = []

    for num, clause in clauses:
        summary_lines.append(f"Clause {num}: {clause}")

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

    print("✅ Summary generated:", args.output)


if __name__ == "__main__":
    main()