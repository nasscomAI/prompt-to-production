import argparse
import re

def retrieve_policy(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        raise Exception(f"Error reading file: {e}")

    clauses = re.findall(r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)', content, re.DOTALL)

    if not clauses:
        raise Exception("Invalid structure: No numbered clauses found")

    return [{"clause": num.strip(), "text": text.strip()} for num, text in clauses]


def summarize_policy(clauses):
    if not clauses:
        raise Exception("No clauses to summarize")

    summary = []
    for clause in clauses:
        summary.append(f"{clause['clause']}: {clause['text']}")

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)

    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)

        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)

        print("Summary generated successfully!")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()