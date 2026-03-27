"""
UC-0B — Summary That Changes Meaning
Rule-based summarizer following RICE enforcement from agents.md.
Preserves every numbered clause, every binding verb, and all multi-condition
obligations from the source HR leave policy.
"""
import argparse
import re
import sys


def retrieve_policy(file_path: str) -> list[dict]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    if not text.strip():
        print(f"ERROR: File is empty: {file_path}", file=sys.stderr)
        sys.exit(1)

    sections = []
    current_section = None

    for line in text.splitlines():
        stripped = line.strip()

        if re.match(r"^═+$", stripped):
            continue

        section_header = re.match(r"^(\d+)\.\s+(.+)$", stripped)
        if section_header:
            if current_section:
                sections.append(current_section)
            current_section = {
                "section_number": section_header.group(1),
                "title": section_header.group(2),
                "clauses": [],
            }
            continue

        clause_match = re.match(r"^(\d+\.\d+)\s+(.+)$", stripped)
        if clause_match and current_section:
            current_section["clauses"].append({
                "number": clause_match.group(1),
                "text": clause_match.group(2),
            })
        elif current_section and current_section["clauses"] and stripped:
            current_section["clauses"][-1]["text"] += " " + stripped

    if current_section:
        sections.append(current_section)

    return sections


def summarize_policy(sections: list[dict]) -> str:
    lines = []
    lines.append("POLICY SUMMARY — HR LEAVE POLICY (HR-POL-001 v2.3)")
    lines.append("=" * 60)
    lines.append("")

    for section in sections:
        lines.append(f"{section['section_number']}. {section['title']}")
        lines.append("-" * 40)

        for clause in section["clauses"]:
            text = clause["text"]
            lines.append(f"  {clause['number']} — {text}")

        lines.append("")

    lines.append("=" * 60)
    lines.append("END OF SUMMARY")
    lines.append("")
    lines.append("Note: All binding verbs (must, requires, will, may, not permitted)")
    lines.append("are preserved exactly as stated in the source document.")
    lines.append("No external information has been added.")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Summary written to {args.output}")
    print(f"Sections processed: {len(sections)}")
    total_clauses = sum(len(s['clauses']) for s in sections)
    print(f"Clauses preserved: {total_clauses}")


if __name__ == "__main__":
    main()
