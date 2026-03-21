"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

def extract_clauses(text):
    pattern = r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)'
    matches = re.findall(pattern, text, re.DOTALL)

    clauses = []
    for number, content in matches:
        clean = " ".join(content.split())
        clauses.append(f"{number} {clean}")

    return clauses


def main(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    clauses = extract_clauses(text)

    with open(output_path, "w", encoding="utf-8") as f:
        for c in clauses:
            f.write(c + "\n")

    print("Done. Output written to", output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args()
    main(args.input, args.output)
