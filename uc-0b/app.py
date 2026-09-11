"""
UC-0B — Summary That Changes Meaning
Summarizes the HR leave policy document while preserving every decimal-
numbered clause (e.g. 2.3, 5.2) and every condition attached to each
obligation. Implements the two skills defined in skills.md:
retrieve_policy, summarize_policy.
"""

import argparse
import re
import sys

# Matches clause headers like "2.3", "5.2", "3.4" at the start of a line
CLAUSE_PATTERN = re.compile(r"^\s*(\d+\.\d+)\b[\.\)\s]*", re.MULTILINE)

CONDITION_MARKERS = [
    " and ", " unless ", " provided that ", " except ",
    " both ", " regardless of ", " within ",
]

BINDING_VERBS = ["must", "will", "requires", "requires", "not permitted", "are forfeited", "may"]


def retrieve_policy(input_path):
    """Load the policy file and split it into decimal-numbered clauses."""
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if not text.strip():
        print(f"ERROR: input file is empty: {input_path}", file=sys.stderr)
        sys.exit(1)

    matches = list(CLAUSE_PATTERN.finditer(text))
    sections = []

    if not matches:
        print("WARNING: no decimal-numbered clauses (e.g. 2.3) detected; treating file as a single section.")
        sections.append({"clause_id": "1", "text": text.strip()})
        return sections

    for i, m in enumerate(matches):
        clause_id = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        clause_text = text[start:end].strip()
        sections.append({"clause_id": clause_id, "text": clause_text})

    return sections


def _count_conditions(text_lower):
    return sum(text_lower.count(m.strip()) for m in CONDITION_MARKERS)


def summarize_clause(clause_id, text):
    """Condense a single clause, preserving every condition. Falls back to
    verbatim + flag if the clause can't be safely condensed."""
    clean = re.sub(r"\s+", " ", text).strip()
    clean_lower = clean.lower()

    marker_count = _count_conditions(clean_lower)
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", clean) if s]

    if not sentences:
        return f"[VERBATIM — FLAGGED] {clean}"

    if marker_count == 0 or len(sentences) == 1:
        return sentences[0]

    # Multi-condition clause: keep sentences until all condition markers are covered
    kept = []
    covered = 0
    for s in sentences:
        kept.append(s)
        covered += _count_conditions(s.lower())
        if covered >= marker_count:
            break

    combined = " ".join(kept)

    # Safety check: if combining still seems to drop an "and"-joined dual
    # requirement (e.g. two named approvers), fall back to verbatim + flag
    if " and " in clean_lower and " and " not in combined.lower():
        return f"[VERBATIM — FLAGGED] {clean}"

    return combined


def summarize_policy(sections, output_path):
    lines = []
    for section in sections:
        summary = summarize_clause(section["clause_id"], section["text"])
        lines.append(f'{section["clause_id"]}: {summary}')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return lines


def main():
    parser = argparse.ArgumentParser(description="UC-0B HR leave policy summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary_lines = summarize_policy(sections, args.output)

    print(f"Read {len(sections)} clause(s) from {args.input}")
    print(f"Wrote {len(summary_lines)} summary line(s) to {args.output}")


if __name__ == "__main__":
    main()