import re
import argparse


def retrieve_policy(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    clauses = re.findall(r"(\\d+\\.\\d+.*?)(?=\\n\\d+\\.\\d+|$)", text, re.S)
    return [c.strip() for c in clauses]


def summarize_policy(clauses):
    summary = []

    for clause in clauses:
        clause_no = re.match(r"(\\d+\\.\\d+)", clause)
        clause_id = clause_no.group(1) if clause_no else "UNKNOWN"

        # Safe strategy: keep clause text mostly intact
        summary.append(f"{clause_id}: {clause}")

    return "\\n".join(summary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)


if __name__ == "__main__":
    main()