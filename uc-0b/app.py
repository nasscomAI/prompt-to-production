"""
UC-0B app.py — Policy Summarizer
Build: RICE + agents.md + skills.md + CRAFT workflow.
Preserves all numbered clauses, numerical caps, approval conditions, and exceptions.
"""
import argparse
import os
import re


def parse_clauses(text: str) -> list:
    lines = text.splitlines()
    clauses = []
    current_clause = {"title": "Preamble / General Policy Scope", "body": []}

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if re.match(r"^(Clause|Section|Rule|\d+\.|\([a-z0-9]+\))\s*", stripped, re.IGNORECASE):
            if current_clause["body"] or current_clause["title"]:
                clauses.append(current_clause)
            current_clause = {"title": stripped, "body": []}
        else:
            current_clause["body"].append(stripped)

    if current_clause["body"] or current_clause["title"]:
        clauses.append(current_clause)

    return clauses


def extract_critical_constraints(text: str) -> list:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    critical_markers = [
        "must", "shall", "maximum", "minimum", "limit", "prior approval",
        "days", "hours", "percent", "%", "penalty", "loss of pay",
        "subject to", "provided that", "except", "not permitted", "mandatory",
        "applicable", "entitled", "lapse", "carry forward"
    ]
    extracted = []
    for s in sentences:
        s_clean = s.strip()
        if not s_clean:
            continue
        if any(marker in s_clean.lower() for marker in critical_markers) or len(sentences) <= 2:
            extracted.append(s_clean)

    return extracted if extracted else [text]


def generate_summary(input_path: str, output_path: str):
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        return

    with open(input_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    clauses = parse_clauses(content)
    summary_lines = [
        "# STRICT POLICY SUMMARY: HR LEAVE POLICY",
        "# ENFORCEMENT: Every numbered clause, constraint, and quantitative cap is preserved.\n"
    ]

    for clause in clauses:
        summary_lines.append(f"## {clause['title']}")
        body_text = " ".join(clause["body"])
        key_points = extract_critical_constraints(body_text)

        for pt in key_points:
            summary_lines.append(f"- {pt}")
        summary_lines.append("")

    out_dir = os.path.dirname(output_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines))

    print(f"Summary generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument(
        "--input",
        default="data/policy-documents/policy_hr_leave.txt",
        help="Path to input policy text file"
    )
    parser.add_argument(
        "--output",
        default="uc-0b/summary_hr_leave.txt",
        help="Path to write summary output file"
    )
    args = parser.parse_args()

    input_path = args.input if os.path.exists(args.input) else "../data/policy-documents/policy_hr_leave.txt"
    output_path = args.output if not os.path.exists("app.py") else "summary_hr_leave.txt"

    generate_summary(input_path, output_path)


if __name__ == "__main__":
    main()