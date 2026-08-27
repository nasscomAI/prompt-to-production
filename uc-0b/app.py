"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from typing import Dict


def retrieve_policy(input_path: str) -> Dict[str, str]:
    with open(input_path, "r", encoding="utf-8") as infile:
        lines = infile.readlines()

    clauses: Dict[str, str] = {}
    current_clause = ""
    for raw in lines:
        line = raw.rstrip("\n")
        stripped = line.strip()
        match = re.match(r"^(\d+\.\d+)\s+(.*)$", stripped)
        if match:
            current_clause = match.group(1)
            clauses[current_clause] = match.group(2).strip()
            continue

        is_divider = stripped and all(ch == "═" for ch in stripped)
        is_section_title = bool(re.match(r"^\d+\.\s+[A-Z\s&()-]+$", stripped))

        # In source policy files, true clause continuations are indented lines.
        if current_clause and raw.startswith(" ") and stripped and not is_divider and not is_section_title:
            clauses[current_clause] = f"{clauses[current_clause]} {stripped}".strip()

    return clauses


def summarize_policy(clauses: Dict[str, str]) -> str:
    # Preserve legal meaning by staying close to source wording.
    output_lines = ["HR Leave Policy Summary (Clause-Preserving)", ""]
    for clause_no in sorted(clauses.keys(), key=lambda x: tuple(int(p) for p in x.split("."))):
        text = " ".join(clauses[clause_no].split())
        output_lines.append(f"{clause_no}: {text}")
    return "\n".join(output_lines) + "\n"

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to write summary file")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    if not clauses:
        raise ValueError("No numbered clauses found in source policy file.")

    summary = summarize_policy(clauses)
    with open(args.output, "w", encoding="utf-8") as outfile:
        outfile.write(summary)

    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
