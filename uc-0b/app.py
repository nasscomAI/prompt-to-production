import argparse
import re

def retrieve_policy(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        raise Exception("Invalid file path")

    if not content.strip():
        raise Exception("Empty file")

    clauses = re.split(r'\n(?=\d+\.\d+)', content)
    structured: list[dict[str, str]] = []

    for clause in clauses:
        match = re.match(r'(\d+\.\d+)\s*(.*)', clause, re.DOTALL)
        if match:
            structured.append({
                "clause": match.group(1),
                "text": match.group(2).strip()
            })

    if not structured:
        raise Exception("Parsing error")

    return structured

def summarize_policy(clauses):
    summary: list[str] = []

    for clause in clauses:
        text = clause["text"]

        if len(text) < 120:
            summary.append(f"{clause['clause']}: {text}")
        else:
            summary.append(f"{clause['clause']}: {text} (quoted due to risk of meaning loss)")

    if len(summary) != len(clauses):
        raise Exception("Clause missing in summary")

    return "\n".join(summary)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, 'w', encoding='utf-8') as file:
        file.write(summary)

    print("Summary generated successfully!")

if __name__ == "__main__":
    main()
