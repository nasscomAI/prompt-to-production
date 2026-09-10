"""
UC-0B app.py — Summary That Changes Meaning
Built using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z][A-Z0-9 ()&/,'-]*)$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
BAR_RE = re.compile(r"^[═=]+$")


def retrieve_policy(path: str):
    """
    Load a .txt policy file and parse it into structured sections/clauses.
    Returns: list of {number, title, clauses: [{number, text}]}
    """
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as exc:
        raise IOError(f"Could not read policy file '{path}': {exc}") from exc

    sections = []
    current_section = None
    current_clause = None

    for raw_line in lines:
        line = raw_line.rstrip("\n").rstrip()
        if not line or BAR_RE.match(line.strip()):
            continue

        section_match = SECTION_RE.match(line.strip())
        clause_match = CLAUSE_RE.match(line.strip())

        if section_match:
            current_section = {
                "number": section_match.group(1),
                "title": section_match.group(2).strip(),
                "clauses": [],
            }
            sections.append(current_section)
            current_clause = None
        elif clause_match and current_section is not None:
            current_clause = {
                "number": clause_match.group(1),
                "text": clause_match.group(2).strip(),
            }
            current_section["clauses"].append(current_clause)
        elif current_clause is not None:
            current_clause["text"] += " " + line.strip()
        # else: line before any recognised section/clause (document title block) — ignored

    total_clauses = sum(len(s["clauses"]) for s in sections)
    if total_clauses == 0:
        raise ValueError(
            f"No numbered clauses (format 'N.N text') found in '{path}'. "
            "Check the document follows the expected policy format."
        )

    return sections


def summarize_policy(sections) -> str:
    """
    Turn parsed sections into a clause-referenced summary.
    Every clause is preserved near-verbatim (whitespace-normalized only)
    so no condition or clause can be silently dropped or softened.
    """
    lines = []
    for section in sections:
        if not section["clauses"]:
            continue
        lines.append(f"## {section['number']}. {section['title']}")
        for clause in section["clauses"]:
            lines.append(f"- {clause['number']} {clause['text']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to a policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write the clause-referenced summary")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    total_clauses = sum(len(s["clauses"]) for s in sections)
    print(f"Done. {total_clauses} clauses across {len(sections)} sections written to {args.output}")


if __name__ == "__main__":
    main()
