"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
from typing import Dict, List

REQUIRED_CLAUSES: List[str] = [
    "2.3",
    "2.4",
    "2.5",
    "2.6",
    "2.7",
    "3.2",
    "3.4",
    "5.2",
    "5.3",
    "7.2",
]


def _normalize_spaces(s: str) -> str:
    # Keep punctuation, but normalize line-wrap spaces.
    return re.sub(r"\s+", " ", s).strip()


def retrieve_policy(input_path: str) -> Dict[str, str]:
    """
    Load policy text and extract required clause texts.

    The policy is formatted with clause lines starting at column 1 like:
      2.3 Employees must submit ...
    and potentially wrapped across indented lines.
    """
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Precompute starting line indices for every clause header-like line.
    clause_header_re = re.compile(r"^(?P<num>\d+\.\d+)\s+")
    # Section headers like: "3. SICK LEAVE"
    section_header_re = re.compile(r"^\d+\.\s+[A-Z]")
    indices_by_clause: Dict[str, int] = {}
    for i, line in enumerate(lines):
        m = clause_header_re.match(line)
        if m:
            indices_by_clause[m.group("num")] = i

    clauses: Dict[str, str] = {}
    for clause_id in REQUIRED_CLAUSES:
        start_idx = indices_by_clause.get(clause_id)
        if start_idx is None:
            continue

        # Read until the next clause header line (another number.number) or EOF.
        j = start_idx + 1
        chunk_lines = [lines[start_idx]]
        while j < len(lines):
            # Policy divider lines look like: "══════════════════════════ 3. SICK LEAVE ..."
            # Those are not part of any clause text.
            if lines[j].lstrip().startswith("═"):
                break
            if clause_header_re.match(lines[j]) or section_header_re.match(lines[j]):
                break
            chunk_lines.append(lines[j])
            j += 1

        clause_text = _normalize_spaces(" ".join(chunk_lines))
        clauses[clause_id] = clause_text

    return clauses


def summarize_policy(policy_clauses: Dict[str, str]) -> str:
    """
    Emit a compliant summary file containing all required clauses.

    We quote the clause text verbatim (aside from whitespace normalization) to
    guarantee condition preservation and avoid scope bleed.
    """
    missing = [c for c in REQUIRED_CLAUSES if c not in policy_clauses]
    if missing:
        raise ValueError(f"Missing required clauses in policy: {', '.join(missing)}")

    out_lines: List[str] = []
    out_lines.append("HR Leave Policy Summary (verbatim clause-preserving)")
    out_lines.append("")
    for clause_id in REQUIRED_CLAUSES:
        out_lines.append(f"Clause {clause_id}: {policy_clauses[clause_id]}")
    return "\n".join(out_lines).strip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Summary That Changes Meaning")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    policy_clauses = retrieve_policy(args.input)
    summary = summarize_policy(policy_clauses)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

if __name__ == "__main__":
    main()
