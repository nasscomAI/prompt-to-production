"""
UC-0B Policy Summarizer
Reads a policy document and produces a structured summary
while preserving clause references and obligations.
"""
import argparse
import re

def retrieve_policy(file_path: str):
    clauses = []
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    pattern = r"(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)"
    matches = re.findall(pattern, content, re.DOTALL)
    for number, text in matches:
        clauses.append((number.strip(), text.strip()))
    return clauses

def summarize_policy(clauses):
    summary_lines = []
    for number, text in clauses:
        sentence = text.replace("\n", " ").strip()
        if len(sentence.split()) > 35:
            summary = f'Clause {number}: "{sentence}"'
        else:
            summary = f"Clause {number}: {sentence}"
        summary_lines.append(summary)
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to output summary file")
    args = parser.parse_args()
    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"Summary written to {args.output}")

if __name__ == "__main__":
    main()