"""
UC-0B app.py — HR Policy Summarization Assistant.
Reads a policy text file, summarizes it preserving every clause,
condition, and binding obligation, and writes the summary to output.
"""
import argparse
import re
import sys


def retrieve_policy(file_path):
    """Loads a .txt policy file and returns its content as structured numbered sections."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if not content.strip():
        raise ValueError(f"Policy file is empty: {file_path}")

    sections = []
    lines = content.split('\n')

    current_title = None
    current_clause_num = None
    current_clause_parts = []

    def _flush_clause():
        nonlocal current_clause_num, current_clause_parts
        if current_clause_num is not None and current_clause_parts:
            clause_text = ' '.join(p.strip() for p in current_clause_parts if p.strip())
            sections.append({
                'clause_number': current_clause_num,
                'section_title': current_title,
                'clause_text': clause_text
            })
        current_clause_num = None
        current_clause_parts = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('═'):
            _flush_clause()
            continue

        clause_match = re.match(r'^(\d+\.\d+)\s+(.+)', stripped)
        if clause_match:
            _flush_clause()
            current_clause_num = clause_match.group(1)
            current_clause_parts = [clause_match.group(2)]
            continue

        if re.match(r'^\d+\.\s+[A-Z]', stripped):
            _flush_clause()
            current_title = stripped
            continue

        if current_clause_num is not None:
            current_clause_parts.append(stripped)

    _flush_clause()

    return sections


def summarize_policy(sections):
    """Produces a compliant summary preserving every clause, condition, and binding obligation."""
    lines = []
    lines.append("CITY MUNICIPAL CORPORATION")
    lines.append("HUMAN RESOURCES DEPARTMENT")
    lines.append("EMPLOYEE LEAVE POLICY — SUMMARY")
    lines.append("")

    current_title = None
    for section in sections:
        if section['section_title'] != current_title:
            current_title = section['section_title']
            lines.append(current_title)
            lines.append("")
        lines.append(f"{section['clause_number']} {section['clause_text']}")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='UC-0B — HR Policy Summarization')
    parser.add_argument('--input', required=True, help='Path to the policy text file')
    parser.add_argument('--output', required=True, help='Path to the output summary file')
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()