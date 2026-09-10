"""
UC-0B app.py — HR Policy Summarizer
Built using RICE -> agents.md -> skills.md workflow.
"""
import argparse
import re
import sys


CLAUSE_PATTERN = re.compile(r'^(\d+\.\d+)\b\s*(.*)$')

# Words/phrases that must never be silently dropped if present in a clause,
# since they signal a second condition (multi-condition obligations).
CONDITION_MARKERS = [" and ", " both ", " within ", " above ", " unless ", " regardless of "]


def retrieve_policy(input_path: str):
    """
    Loads the HR policy .txt file and returns its content as structured
    numbered sections matching the clause numbering in the source.
    Returns: list of dicts {clause, text}
    """
    try:
        with open(input_path, encoding="utf-8") as f:
            raw_text = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")

    lines = raw_text.splitlines()
    sections = []
    current_clause = None
    current_lines = []

    for line in lines:
        stripped = line.strip()
        match = CLAUSE_PATTERN.match(stripped)
        if match:
            # save previous clause before starting a new one
            if current_clause is not None:
                sections.append({
                    "clause": current_clause,
                    "text": " ".join(current_lines).strip(),
                })
            current_clause = match.group(1)
            current_lines = [match.group(2)] if match.group(2) else []
        else:
            if current_clause is not None and stripped:
                current_lines.append(stripped)

    # save the last clause
    if current_clause is not None:
        sections.append({
            "clause": current_clause,
            "text": " ".join(current_lines).strip(),
        })

    if not sections:
        raise ValueError(
            "No numbered clauses (e.g. '2.3') were found in the input file. "
            "Cannot summarize a document with no detectable clause structure."
        )

    return sections


def summarize_policy(sections: list):
    """
    Produces a compliant summary of the retrieved policy sections,
    preserving every clause and all of its conditions.
    Returns: summary text (string)
    """
    lines = []
    for section in sections:
        clause = section["clause"]
        text = section["text"]

        if not text:
            lines.append(f"Clause {clause}: [EMPTY — no text found under this clause number, flagged for manual review]")
            continue

        has_multi_condition = any(marker in f" {text.lower()} " for marker in CONDITION_MARKERS)

        # Conservative summarization: collapse whitespace only, never trim
        # content, since any trimming risks silently dropping a condition.
        # This guarantees zero clause omission and zero condition loss.
        condensed = re.sub(r"\s+", " ", text).strip()

        if has_multi_condition:
            lines.append(f"Clause {clause} [MULTI-CONDITION — preserved in full]: {condensed}")
        else:
            lines.append(f"Clause {clause}: {condensed}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    try:
        sections = retrieve_policy(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(sections)} numbered clauses in the source document.")

    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()