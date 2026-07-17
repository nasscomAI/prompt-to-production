"""
UC-0B app.py
Built using the RICE (agents.md) -> skills.md -> CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

DIVIDER_RE = re.compile(r"^═+$")
SECTION_HEADER_PREFIX_RE = re.compile(r"^\d+\.\s")
CLAUSE_PREFIX_RE = re.compile(r"^\d+\.\d+\s")


def retrieve_policy(file_path: str) -> list:
    """
    Load a .txt policy file and return its content as structured numbered clauses.
    Returns: list of dicts with keys: section, clause, text
    """
    with open(file_path, encoding="utf-8") as f:
        raw_lines = [line.rstrip("\n") for line in f]

    clauses = []
    current_section = None
    current_clause = None
    current_text = []

    def flush():
        if current_clause is not None:
            clauses.append({
                "section": current_section,
                "clause": current_clause,
                "text": " ".join(current_text).strip(),
            })

    for raw_line in raw_lines:
        line = raw_line.strip()
        if not line or DIVIDER_RE.match(line):
            continue

        clause_match = CLAUSE_PREFIX_RE.match(line)
        if clause_match:
            flush()
            current_clause = line[:clause_match.end()].split()[0]
            current_text = [line[clause_match.end():].strip()]
            continue

        section_match = SECTION_HEADER_PREFIX_RE.match(line)
        if section_match:
            flush()
            current_clause = None
            current_text = []
            current_section = line
            continue

        if current_clause is not None:
            current_text.append(line)

    flush()

    if not clauses:
        raise ValueError(f"No numbered clauses found in {file_path}")

    return clauses


def summarize_policy(clauses: list) -> str:
    """
    Produce the compliant summary from structured clauses.
    Every clause is carried through verbatim (only whitespace/line-wrap is
    normalized) so no obligation, condition, or restriction can be dropped
    or softened, and section headers group clauses in document order.
    """
    lines = []
    current_section = None
    for entry in clauses:
        if entry["section"] != current_section:
            current_section = entry["section"]
            if lines:
                lines.append("")
            lines.append(current_section)
            lines.append("-" * len(current_section))
        lines.append(f"Clause {entry['clause']}: {entry['text']}")
    return "\n".join(lines).strip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_[name].txt")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
