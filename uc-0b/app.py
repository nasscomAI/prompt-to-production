import argparse
import re

def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Leave Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary text")
    args = parser.parse_args()

    required = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    # FIX: Changed \\s and \\d to standard single backslashes \s and \d inside the raw string r"..."
    clause_start = re.compile(r"(?m)^\s*(?P<num>\d+\.\d+)\b")
    tokens = list(clause_start.finditer(text))

    clause_map = {}
    for i, t in enumerate(tokens):
        num = t.group("num")
        start = t.start()
        # Find where the next clause block starts, or slice to the end of the file
        end = tokens[i + 1].start() if i + 1 < len(tokens) else len(text)
        
        if num in required and num not in clause_map:
            clause_map[num] = text[start:end].strip()

    lines = []
    for num in required:
        if num not in clause_map:
            lines.append(f"MISSING CLAUSE {num}")
            continue

        snippet = clause_map[num]
        
        # Output layout adhering to the workshop enforcement guidelines
        lines.append(f"Clause {num}:")
        lines.append(snippet)
        lines.append("")

    out_text = "\n".join(lines).rstrip() + "\n"
    with open(args.output, "w", encoding="utf-8") as out_f:
        out_f.write(out_text)

    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
