"""
UC-0B — Summary That Changes Nothing
"""
import argparse
import re


def retrieve_policy(input_path: str) -> dict:
    with open(input_path, encoding="utf-8") as f:
        text = f.read()

    sections = {}
    current_section = None
    current_clauses = []

    for line in text.splitlines():
        line = line.strip()
        header_match = re.match(r"^[═]+$", line)
        if header_match and current_section:
            continue
        section_match = re.match(r"^(\d+)\.\s+(.+)$", line)
        if section_match:
            if current_section:
                sections[current_section] = list(current_clauses)
            current_section = line
            current_clauses = []
            continue
        clause_match = re.match(r"^(\d+\.\d+)\s+(.+)$", line)
        if clause_match:
            current_clauses.append({
                "clause_id": clause_match.group(1),
                "text": clause_match.group(2),
            })
            continue
        if current_clauses:
            current_clauses[-1]["text"] += " " + line

    if current_section:
        sections[current_section] = list(current_clauses)

    return sections


def _summarize_clause(clause: dict) -> str:
    cid = clause["clause_id"]
    text = clause["text"]
    return f"  [{cid}] {text}"


def summarize_policy(sections: dict) -> str:
    lines = []
    lines.append("POLICY SUMMARY — HR-POL-001 (Employee Leave Policy)")
    lines.append("=" * 60)
    lines.append("")

    for section_name, clauses in sections.items():
        lines.append(section_name.upper())
        lines.append("-" * 40)
        for clause in clauses:
            lines.append(_summarize_clause(clause))
        lines.append("")

    lines.append("=" * 60)
    total_clauses = sum(len(clauses) for clauses in sections.values())
    lines.append(f"Total clauses summarized: {total_clauses}")
    lines.append("All conditions preserved verbatim from source document.")

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
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
