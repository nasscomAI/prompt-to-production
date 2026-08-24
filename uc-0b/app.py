"""
UC-0B app.py — Summary That Changes Meaning
Implements conservative clause-preserving summarization per agents.md/skills.md.
"""
import argparse
import re
from typing import Dict, List, Tuple


REQUIRED_CLAUSES = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4", "5.2", "5.3", "7.2"
]


def retrieve_policy(path: str) -> Dict[str, str]:
    """Parse the policy text and return mapping clause_id -> full clause text.

    This parser looks for lines beginning with a numbered clause like '2.3'
    and captures continuation lines indented below it.
    """
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    clauses: Dict[str, List[str]] = {}
    current_id = None
    for line in lines:
        # Match a clause header like '2.3 ' at start of line
        m = re.match(r'^(\d+\.\d+)\s+(.*\S)', line)
        if m:
            current_id = m.group(1)
            rest = m.group(2).strip()
            clauses[current_id] = [rest]
            continue
        # If line is indented continuation and we have a current clause, append
        if current_id and (line.startswith('    ') or line.startswith('\t') or line.strip() == ''):
            # include non-empty continuation lines
            if line.strip():
                clauses[current_id].append(line.strip())
            continue
        # Other lines ignored

    # Join clause lines into single strings
    return {cid: ' '.join(parts) for cid, parts in clauses.items()}


def summarize_policy(clauses: Dict[str, str], required: List[str]) -> Tuple[List[str], List[str]]:
    """Produce a clause-preserving summary.

    Strategy: For safety, include the original clause text verbatim for each
    required clause if present. Mark VERBATIM when clause is quoted.
    If a required clause is missing, add a clear missing note.
    """
    summary_lines: List[str] = []
    notes: List[str] = []

    for cid in required:
        if cid in clauses:
            text = clauses[cid]
            # Conservative approach: quote verbatim to avoid meaning loss
            summary_lines.append(f"{cid}: \"{text}\"")
            notes.append(f"{cid}: VERBATIM")
        else:
            summary_lines.append(f"{cid}: MISSING from source document")
            notes.append(f"{cid}: MISSING")

    return summary_lines, notes


def write_summary(output_path: str, summary_lines: List[str], notes: List[str]):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('SUMMARY — Clause-preserving output\n')
        f.write('================================\n\n')
        for line in summary_lines:
            f.write(line + '\n')
        if notes:
            f.write('\nNOTES:\n')
            for n in notes:
                f.write('- ' + n + '\n')


def main():
    parser = argparse.ArgumentParser(description='UC-0B Policy Summarizer')
    parser.add_argument('--input', required=True, help='Path to policy .txt file')
    parser.add_argument('--output', required=True, help='Path to write summary file')
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary_lines, notes = summarize_policy(clauses, REQUIRED_CLAUSES)
    write_summary(args.output, summary_lines, notes)
    print(f"Done. Summary written to {args.output}")


if __name__ == '__main__':
    main()
