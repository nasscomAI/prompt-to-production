"""
UC-0B app.py — Policy Summarizer
Reads a policy document and produces a clause-traceable summary.
Usage: python app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
"""
import argparse
import re
import os

def parse_sections(text: str) -> list:
    """Split document into (heading, content) tuples by numbered section headings."""
    sections = []
    current_heading = "PREAMBLE"
    current_lines = []
    for line in text.splitlines():
        m = re.match(r'^(\d+(?:\.\d+)?)\s+[A-Z]', line.strip())
        if m:
            if current_lines:
                sections.append((current_heading, '\n'.join(current_lines)))
            current_heading = line.strip()
            current_lines = [line]
        else:
            current_lines.append(line)
    if current_lines:
        sections.append((current_heading, '\n'.join(current_lines)))
    return sections

def summarize_section(heading: str, content: str) -> str:
    """
    Extract all sub-clauses from a section.
    Preserves all numbers, conditions, and constraints.
    """
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    # Skip heading line (first), keep all clause lines
    clause_lines = []
    for line in lines[1:]:
        # Remove section numbers like "2.1", "2.2" at start
        clean = re.sub(r'^\d+\.\d+\s+', '', line)
        clean = re.sub(r'^\s+', '', clean)
        if clean and not clean.startswith('═'):
            clause_lines.append(f"- {clean}")
    if not clause_lines:
        return ""
    # Use the section heading (strip number prefix for readability)
    section_title = re.sub(r'^\d+\.\s*', '', heading)
    return f"{section_title}\n" + '\n'.join(clause_lines)

def summarize_document(text: str, doc_ref: str = "") -> str:
    """Produce a full clause-traceable summary of the document."""
    # Extract header metadata
    lines = text.splitlines()
    meta_lines = [l.strip() for l in lines[:6] if l.strip() and not l.startswith('═')]
    header = ' | '.join(meta_lines[:4]) if meta_lines else ""

    sections = parse_sections(text)
    summary_parts = [f"SUMMARY: {header}\n"]
    section_num = 1
    for heading, content in sections:
        if heading == "PREAMBLE":
            continue
        summarized = summarize_section(heading, content)
        if summarized:
            summary_parts.append(f"{section_num}. {summarized}\n")
            section_num += 1
    return '\n'.join(summary_parts)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input",  required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        text = f.read()

    summary = summarize_document(text, doc_ref=os.path.basename(args.input))

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
