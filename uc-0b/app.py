import argparse
import os
import re

def retrieve_policy(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError("Invalid file path")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        raise ValueError("Policy file is empty")

    # Split into clauses like 2.3, 2.4 etc.
    pattern = r'(\d+\.\d+.*?)((?=\n\d+\.\d+)|$)'
    matches = re.findall(pattern, content, re.DOTALL)

    if not matches:
        raise ValueError("Could not parse clauses properly")

    clauses = []
    for match in matches:
        clause_text = match[0].strip()
        clause_number = clause_text.split()[0]
        # Skip invalid lines like "Effective: ..."
        if "Effective:" in clause_text:
            continue
        clauses.append({
            "number": clause_number,
            "text": clause_text
            })

    return clauses


def summarize_policy(clauses):
    if not clauses:
        raise ValueError("No clauses to summarize")

    summary = []

    for clause in clauses:
        number = clause["number"]
        text = clause["text"]

        # Remove duplicate numbering like "2.3 2.3"
        text = re.sub(r'^(\d+\.\d+)\s+\1', '', text).strip()

        # Remove numbering from text if already used
        text = re.sub(r'^\d+\.\d+\s*', '', text).strip()

        # Clean format
        summary.append(f"{number}: {text}")

    if len(summary) != len(clauses):
        raise ValueError("Clause missing in summary")

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)
        result = summarize_policy(clauses)

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)

        print("✅ Summary generated successfully")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()