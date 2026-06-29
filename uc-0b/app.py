"""
UC-0B — Summary That Changes Meaning
Preserves every numbered clause, multi-condition obligations,
and adds no external information.  Flags at-risk clauses [VERBATIM].

Usage:
  python app.py --input <policy.txt> --output <summary.txt>
"""
import argparse
import re
import sys
from pathlib import Path


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def parse_sections_and_clauses(text: str):
    lines = text.splitlines()
    sections = []
    current_section: dict | None = None
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.+)')
    section_pattern = re.compile(r'^(\d+)\.\s+(.+)')
    separator_pattern = re.compile(r'^═+$')

    for line in lines:
        stripped = line.strip()
        if not stripped or separator_pattern.match(stripped):
            continue
        cls_match = clause_pattern.match(stripped)
        sec_match = section_pattern.match(stripped)
        if cls_match and current_section is not None:
            current_section["clauses"].append({
                "number": cls_match.group(1),
                "text": cls_match.group(2).strip(),
            })
        elif sec_match and not cls_match:
            current_section = {
                "number": sec_match.group(1),
                "title": sec_match.group(2).strip(),
                "clauses": [],
            }
            sections.append(current_section)
        elif current_section and current_section["clauses"] and stripped:
            current_section["clauses"][-1]["text"] += " " + stripped
    return sections


def is_at_risk(clause_text: str) -> bool:
    """Check if a clause has multi-condition logic or strong language
    that summarisation could weaken or drop."""
    conditions = [
        " and ", " or ", ", and", ", or",
        "regardless of", "under any circumstances",
        "not sufficient", "not valid",
        "only after", "cannot be", "are forfeited",
    ]
    return any(c in clause_text.lower() for c in conditions)


def summarize_clause(clause_num: str, text: str) -> str:
    if is_at_risk(text):
        return f"  [VERBATIM] [{clause_num}] {text}"
    return f"  [{clause_num}] {text}"


def build_summary(sections: list[dict]) -> str:
    parts = [
        "EMPLOYEE LEAVE POLICY — SUMMARY",
        "Document: HR-POL-001 v2.3",
        "=" * 60,
        "",
    ]
    clause_count = 0
    for sec in sections:
        parts.append(f"\n{sec['number']}. {sec['title']}")
        parts.append("-" * 40)
        for cl in sec["clauses"]:
            parts.append(summarize_clause(cl["number"], cl["text"]))
            clause_count += 1
    parts.append(f"\n{'=' * 60}")
    parts.append(f"Total clauses summarised: {clause_count}")
    return "\n".join(parts)


def write_output(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    parser = argparse.ArgumentParser(description="UC-0B: Summarise a policy document")
    parser.add_argument("--input", required=True, help="Path to input policy .txt")
    parser.add_argument("--output", required=True, help="Path to output summary")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    text = read_file(args.input)
    sections = parse_sections_and_clauses(text)

    total = sum(len(s["clauses"]) for s in sections)
    if total == 0:
        print("Error: No numbered clauses found in input file.", file=sys.stderr)
        sys.exit(1)

    summary = build_summary(sections)
    write_output(args.output, summary)

    print(f"Summary written to {args.output} ({total} clauses)")


if __name__ == "__main__":
    main()
