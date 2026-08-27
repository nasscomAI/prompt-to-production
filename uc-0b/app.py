"""
UC-0B app.py — Policy summary generator.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""

import argparse
import re
from typing import Dict, List, Tuple


CRITICAL_CLAUSES = {
    "2.3": {"verb": "must"},
    "2.4": {"verb": "must"},
    "2.5": {"verb": "will"},
    "2.6": {"verb": "may / are forfeited"},
    "2.7": {"verb": "must"},
    "3.2": {"verb": "requires"},
    "3.4": {"verb": "requires"},
    "5.2": {"verb": "requires"},
    "5.3": {"verb": "requires"},
    "7.2": {"verb": "not permitted"},
}

VERBATIM_CLAUSES = {"5.2", "5.3", "7.2", "7.3"}


def normalize_text(text: str) -> str:
    """Normalize whitespace and remove junk encoding artifacts."""
    text = str(text)
    text = text.replace("\ufeff", "")
    text = text.replace("–", "-").replace("—", "-")
    text = text.replace("\r", "\n")

    # Remove obvious mojibake / junk characters
    text = re.sub(r"[^\x00-\x7F\n]+", " ", text)

    # Remove repeated decorative/junk runs like a-a-a-a or dot clusters
    text = re.sub(r"(?:[A-Za-z]\s*-\s*){3,}[A-Za-z]?", " ", text)
    text = re.sub(r"(?:\.\s*){3,}", " ", text)
    text = re.sub(r"(?:-\s*){3,}", " ", text)

    # Clean each line
    cleaned_lines = []
    for line in text.splitlines():
        line = " ".join(line.split()).strip()
        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def retrieve_policy(input_path: str) -> Tuple[str, Dict[str, str]]:
    """
    Read the policy file and return:
    1) raw normalized text
    2) structured numbered clauses like {'2.3': 'text...'}
    """
    with open(input_path, "r", encoding="utf-8-sig") as f:
        raw_text = normalize_text(f.read())

    pattern = re.compile(
        r"(?m)^\s*(\d+\.\d+)\s+(.*?)(?=^\s*\d+\.\d+\s+|^\s*\d+\.\s+[A-Z][A-Z\s]+$|\Z)",
        re.DOTALL,
    )

    clauses: Dict[str, str] = {}
    for match in pattern.finditer(raw_text):
        clause_id = match.group(1).strip()
        clause_text = normalize_text(match.group(2))

        # keep first occurrence only to avoid accidental duplicates
        if clause_id not in clauses and clause_text:
            clauses[clause_id] = clause_text

    return raw_text, clauses


def clause_needs_verbatim(clause_id: str, clause_text: str) -> bool:
    lowered = clause_text.lower()

    if clause_id in VERBATIM_CLAUSES:
        return True

    if "and" in lowered and "approval" in lowered:
        return True

    if "under any circumstances" in lowered:
        return True

    return False


def summarize_single_clause(clause_id: str, clause_text: str) -> Tuple[str, bool]:
    """Return (summary_line, flagged_for_verbatim)."""
    clean_text = " ".join(clause_text.split()).strip()
    flagged = clause_needs_verbatim(clause_id, clean_text)

    if flagged:
        return f'{clause_id}: "{clean_text}" [VERBATIM]', True

    return f"{clause_id}: {clean_text}", False


def summarize_policy(clauses: Dict[str, str]) -> str:
    """Produce a compliant summary with clause references."""
    missing = [clause_id for clause_id in CRITICAL_CLAUSES if clause_id not in clauses]
    if missing:
        raise ValueError(f"Missing critical clauses in source: {', '.join(missing)}")

    ordered_ids = sorted(clauses.keys(), key=lambda x: tuple(map(int, x.split("."))))

    lines: List[str] = []
    lines.append("HR Leave Policy Summary")
    lines.append("Clause-preserving summary with references")
    lines.append("")

    seen = set()
    for clause_id in ordered_ids:
        if clause_id in seen:
            continue
        seen.add(clause_id)

        clause_text = clauses[clause_id]
        summary_line, _ = summarize_single_clause(clause_id, clause_text)
        lines.append(summary_line)

    return "\n".join(lines).strip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    _, clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8", newline="\n") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()