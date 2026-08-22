"""
UC-0B app.py — Policy summariser.
Design choice per agents.md rule 4: clauses are reproduced verbatim rather than paraphrased.
A hand-written summariser has no reliable way to compress a sentence without risking exactly
the condition-dropping bug this exercise exists to catch, so "safe compression" here means
"quote it" — every clause survives, formatted and grouped, never reworded.
"""
import argparse
import re

SECTION_PATTERN = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 /,&()]*)$")
CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")


def retrieve_policy(path: str) -> list:
    """Parse a policy .txt file into ordered sections of numbered clauses."""
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    sections = []
    current_clause = None  # [number, [text_parts]]

    def flush_clause():
        if current_clause and sections:
            sections[-1]["clauses"].append({
                "number": current_clause[0],
                "text": " ".join(current_clause[1]),
            })

    for raw_line in lines:
        line = raw_line.strip()
        if not line or set(line) == {"═"}:
            continue

        section_match = SECTION_PATTERN.match(line)
        clause_match = CLAUSE_PATTERN.match(line)

        if clause_match:
            flush_clause()
            current_clause = [clause_match.group(1), [clause_match.group(2).strip()]]
        elif section_match:
            flush_clause()
            current_clause = None
            sections.append({
                "section_number": section_match.group(1),
                "section_title": section_match.group(2).strip(),
                "clauses": [],
            })
        elif current_clause:
            current_clause[1].append(line)
        # else: document title/version metadata before section 1 — not a clause, skip.

    flush_clause()
    return sections


def summarize_policy(sections: list) -> str:
    """Render every section heading and every clause, verbatim, in document order."""
    lines = []
    for section in sections:
        lines.append(f"{section['section_number']}. {section['section_title']}")
        if not section["clauses"]:
            lines.append("  [No clauses parsed for this section — needs manual check.]")
        for clause in section["clauses"]:
            lines.append(f"{clause['number']} {clause['text']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
