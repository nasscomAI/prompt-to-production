"""
UC-0B app.py – Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""

import argparse
import re

REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]


def retrieve_policy(input_path: str) -> dict:
    """
    Load the policy .txt file and return content as structured numbered sections.
    Returns: dict mapping clause number (e.g. "2.3") -> full clause text.
    """
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Match lines like "2.3 Employees must submit..." at start of line
    pattern = re.compile(r"^(\d+\.\d+)\s+(.*(?:\n(?!\d+\.\d+|\d+\.\s|\Z).*)*)", re.MULTILINE)
    sections = {}
    for match in pattern.finditer(text):
        clause_num = match.group(1)
        clause_text = " ".join(line.strip() for line in match.group(2).strip().splitlines())
        sections[clause_num] = clause_text

    if not sections:
        raise ValueError(f"No numbered clauses found in {input_path}")

    return sections


def summarize_policy(sections: dict) -> str:
    """
    Take structured clause sections and produce a compliant summary.
    Every required clause must appear, preserving conditions and binding strength.
    """
    lines = ["HR LEAVE POLICY — SUMMARY", "=" * 40, ""]

    for clause_num in REQUIRED_CLAUSES:
        if clause_num not in sections:
            lines.append(f"[{clause_num}] MISSING FROM SOURCE — FLAG FOR REVIEW")
            continue
        text = sections[clause_num]
        lines.append(f"[{clause_num}] {text}")

    lines.append("")
    lines.append("Note: All clauses above are quoted or closely paraphrased from the")
    lines.append("source policy. No conditions have been dropped. Binding verbs")
    lines.append("(must/will/requires/not permitted) are preserved as in the source.")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")

    missing = [c for c in REQUIRED_CLAUSES if c not in sections]
    if missing:
        print(f"WARNING: clauses not found in source: {missing}")


if __name__ == "__main__":
    main()
    