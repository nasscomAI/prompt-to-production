import argparse
import re


def retrieve_policy(path):
    with open(path, "r") as f:
        text = f.read()

    clauses = re.findall(r"\d+\.\d+.*", text)

    structured = []
    for c in clauses:
        parts = c.split(" ", 1)
        if len(parts) == 2:
            structured.append({"clause": parts[0], "text": parts[1]})
        else:
            structured.append({"clause": parts[0], "text": ""})

    return structured


def summarize_policy(clauses):

    summary_lines = []

    for c in clauses:
        clause_number = c["clause"]
        clause_text = c["text"]

        summary_lines.append(f"{clause_number} — {clause_text}")

    return "\n".join(summary_lines)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    clauses = retrieve_policy(args.input)

    summary = summarize_policy(clauses)

    with open(args.output, "w") as f:
        f.write(summary)

    print("Summary written to", args.output)


if __name__ == "__main__":
    main()