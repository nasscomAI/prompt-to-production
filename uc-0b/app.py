"""
UC-0B app.py — Summary That Changes Meaning
Built via RICE -> agents.md -> skills.md -> CRAFT workflow.
"""
import argparse
import re

REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

CLAUSE_PATTERN = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_HEADER_PATTERN = re.compile(r"^\d+\.\s+[A-Z][A-Z\s()]+$")


def retrieve_policy(file_path: str):
    """
    Loads the .txt policy file and returns structured numbered sections.
    Returns: list of {clause, text} dicts, one per numbered clause found.
    """
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    sections = []
    current_clause = None
    current_lines = []

    for line in lines:
        stripped = line.strip()
        match = CLAUSE_PATTERN.match(stripped)
        if match:
            if current_clause is not None:
                sections.append({
                    "clause": current_clause,
                    "text": " ".join(current_lines).strip(),
                })
            current_clause = match.group(1)
            current_lines = [match.group(2)]
        elif (
            current_clause is not None
            and stripped
            and not stripped.startswith("═")
            and not SECTION_HEADER_PATTERN.match(stripped)
        ):
            current_lines.append(stripped)

    if current_clause is not None:
        sections.append({
            "clause": current_clause,
            "text": " ".join(current_lines).strip(),
        })

    if not sections:
        return [{"clause": None, "text": "".join(lines)}]
    return sections


def summarize_policy(sections):
    """
    Takes structured sections and produces a compliant summary with clause references.
    Preserves original wording per clause so no condition or binding verb is lost.
    """
    by_clause = {s["clause"]: s["text"] for s in sections}

    missing = [c for c in REQUIRED_CLAUSES if c not in by_clause]
    if missing:
        raise ValueError(f"Required clauses missing from source document: {missing}")

    lines = ["CMC HR LEAVE POLICY — CLAUSE SUMMARY", ""]
    for section in sections:
        if section["clause"] is None:
            continue
        marker = " [REQUIRED]" if section["clause"] in REQUIRED_CLAUSES else ""
        lines.append(f"{section['clause']}{marker}: {section['text']}")

    lines.append("")
    lines.append(
        "All 10 required clauses (" + ", ".join(REQUIRED_CLAUSES) + ") are present above, "
        "verbatim in substance, with every condition and binding verb preserved from the source."
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary text")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary + "\n")

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
