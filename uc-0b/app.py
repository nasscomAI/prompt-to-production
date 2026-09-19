"""UC-0B clause-preserving HR policy summarizer."""
import argparse
import re
from pathlib import Path

REQUIRED = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

def retrieve_policy(input_path):
    text = Path(input_path).read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError("Policy file is empty")
    clauses = {}
    markers = list(re.finditer(r"(?m)^(?:(\d+\.\d+)|(\d+\.))\s+", text))
    for index, marker in enumerate(markers):
        number = marker.group(1)
        if not number:
            continue
        end = markers[index + 1].start() if index + 1 < len(markers) else len(text)
        clauses[number] = " ".join(text[marker.end():end].split())
    return clauses

def summarize_policy(clauses):
    missing = [number for number in REQUIRED if number not in clauses]
    if missing:
        raise ValueError("Required clauses missing: " + ", ".join(missing))
    lines = ["CMC Employee Leave Policy — Required Clause Summary", "", "This summary is limited to the supplied policy document.", ""]
    for number in REQUIRED:
        lines.append(f"Clause {number}: {clauses[number]}")
    return "\n".join(lines) + "\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    Path(args.output).write_text(summarize_policy(retrieve_policy(args.input)), encoding="utf-8")
    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
