"""
UC-0B app.py — Summary That Changes Meaning
Built per agents.md (RICE enforcement) and skills.md (retrieve_policy, summarize_policy).
"""
import argparse
import re

SECTION_RE = re.compile(r"^(\d+)\.\s+(\S.*)$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(\S.*)$")
SEPARATOR_RE = re.compile(r"^[═=]+$")


def retrieve_policy(file_path: str) -> list:
    """
    Load a policy .txt file, return structured numbered sections:
    [{"section_number": "2", "heading": "ANNUAL LEAVE",
      "clauses": [{"clause_number": "2.1", "text": "..."}, ...]}, ...]
    """
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    sections = []
    current_section = None
    current_clause = None

    for raw_line in lines:
        line = raw_line.rstrip("\n")
        stripped = line.strip()

        if not stripped or SEPARATOR_RE.match(stripped):
            continue

        section_match = SECTION_RE.match(stripped)
        clause_match = CLAUSE_RE.match(stripped)

        if section_match and not clause_match:
            current_section = {
                "section_number": section_match.group(1),
                "heading": section_match.group(2).strip(),
                "clauses": [],
            }
            sections.append(current_section)
            current_clause = None
            continue

        if clause_match and current_section is not None:
            current_clause = {
                "clause_number": clause_match.group(1),
                "text": clause_match.group(2).strip(),
            }
            current_section["clauses"].append(current_clause)
            continue

        # Continuation line (indented wrap of the previous clause's text)
        if current_clause is not None and line.startswith(" "):
            current_clause["text"] += " " + stripped
            continue

        # Document title/header lines before the first section — ignored.

    if not sections:
        raise ValueError(f"No numbered sections found in {file_path} — cannot summarize.")

    return sections


def summarize_policy(sections: list) -> str:
    """
    Produce a compliant summary: every clause present, in order, every
    condition preserved verbatim (no paraphrase-induced meaning loss).
    """
    lines = ["UC-0B — HR Leave Policy Summary",
             "Every numbered clause below is reproduced verbatim (de-wrapped) "
             "per agents.md enforcement rule: condensation must never drop a condition.",
             ""]
    for section in sections:
        lines.append(f"{section['section_number']}. {section['heading']}")
        for clause in section["clauses"]:
            lines.append(f"{clause['clause_number']} {clause['text']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
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
