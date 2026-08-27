"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from typing import Dict


REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]


def retrieve_policy(input_path: str) -> Dict[str, object]:
    """Load policy text and return numbered sections as structured data."""
    with open(input_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    clause_pattern = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")
    sections: Dict[str, str] = {}
    current_clause = None

    for raw_line in full_text.splitlines():
        line = raw_line.rstrip()
        match = clause_pattern.match(line)
        if match:
            current_clause = match.group(1)
            sections[current_clause] = match.group(2).strip()
            continue
        # Only keep indented continuation lines for a clause.
        if current_clause and raw_line.startswith("    ") and line.strip():
            sections[current_clause] = (sections[current_clause] + " " + line.strip()).strip()

    missing = [c for c in REQUIRED_CLAUSES if c not in sections]
    if missing:
        raise ValueError(f"Missing required clauses in source policy: {', '.join(missing)}")

    return {"full_text": full_text, "sections": sections}


def summarize_policy(structured_policy: Dict[str, object]) -> str:
    """
    Build a clause-referenced summary preserving obligations and key conditions.
    """
    sections: Dict[str, str] = structured_policy["sections"]  # type: ignore[assignment]
    s = sections

    summary_lines = [
        "Policy summary:",
        f"- [2.3] {s['2.3']}",
        f"- [2.4] {s['2.4']}",
        f"- [2.5] {s['2.5']}",
        f"- [2.6] {s['2.6']}",
        f"- [2.7] {s['2.7']}",
        f"- [3.2] {s['3.2']}",
        f"- [3.4] {s['3.4']}",
        f"- [5.2] {s['5.2']}",
        f"- [5.3] {s['5.3']}",
        f"- [7.2] {s['7.2']}",
    ]

    summary = "\n".join(summary_lines) + "\n"

    # Guardrail for the common trap: clause 5.2 must keep both approvers.
    clause_52 = s["5.2"].lower()
    if ("department head" not in clause_52) or ("hr director" not in clause_52):
        raise ValueError("Clause 5.2 missing mandatory dual approvers in source parse.")

    return summary

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy input .txt file")
    parser.add_argument("--output", required=True, help="Path to output summary .txt file")
    args = parser.parse_args()

    structured = retrieve_policy(args.input)
    summary = summarize_policy(structured)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
