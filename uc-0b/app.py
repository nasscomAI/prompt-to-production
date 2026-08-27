"""
UC-0B app.py — Summary That Changes Meaning
"""
import argparse
import os

REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]


def retrieve_policy(input_path: str):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    clauses = []
    with open(input_path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]

    cur_clause = None
    cur_text = []
    for line in lines:
        if line.startswith("2.") or line.startswith("3.") or line.startswith("5.") or line.startswith("7."):
            # commit previous clause
            if cur_clause:
                clauses.append({"clause": cur_clause, "text": " ".join(cur_text)})
            parts = line.split(" ", 1)
            cur_clause = parts[0].strip()
            cur_text = [parts[1].strip()] if len(parts) > 1 else []
        elif cur_clause:
            cur_text.append(line)

    if cur_clause:
        clauses.append({"clause": cur_clause, "text": " ".join(cur_text)})

    return clauses


def summarize_policy(clauses):
    summary_lines = []
    found = {c: False for c in REQUIRED_CLAUSES}
    for c in clauses:
        clnum = c.get("clause")
        txt = c.get("text", "")
        if clnum in found:
            found[clnum] = True
            summary_lines.append(f"{clnum}: {txt}")

    missing = [c for c, ok in found.items() if not ok]
    if missing:
        summary_lines.append("MISSING_CLAUSES: " + ", ".join(missing))

    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Summary That Changes Meaning")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to summary_hr_leave.txt")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as out:
        out.write(summary)

    print(f"Done. summary written to {args.output}")


if __name__ == "__main__":
    main()
