import argparse
import os
import re
import sys

REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

class PolicyError(Exception):
    pass


def retrieve_policy(file_path):
    if not os.path.exists(file_path):
        raise PolicyError("File not found")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(r"(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)", re.DOTALL)
    matches = pattern.findall(content)

    if not matches:
        raise PolicyError("No clauses found")

    clauses = {}
    for cid, text in matches:
        clauses[cid.strip()] = text.strip()

    return clauses


def summarize_policy(clauses):
    for c in REQUIRED_CLAUSES:
        if c not in clauses:
            raise PolicyError(f"Missing clause {c}")

    result = []
    for c in REQUIRED_CLAUSES:
        result.append(f"{c}: {clauses[c]} [VERBATIM]")

    return "\n".join(result)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)

        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)

        print("✅ Done")

    except Exception as e:
        print("❌ ERROR:", e)


if __name__ == "__main__":
    main()