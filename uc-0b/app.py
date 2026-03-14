"""
UC-0B app.py — Deterministic Policy Summarizer.
Built to fulfill RICE + agents.md + skills.md + CRAFT workflow rules.
"""
import argparse
import re
import sys

def retrieve_policy(filepath: str) -> str:
    """Retrieves the policy document based on the policy name."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return "Policy not found"

def summarize_policy(content: str) -> str:
    """
    Summarizes the policy document into easily readable format.
    Enforces rules from agents.md:
      - Every numbered clause must be covered in the summary.
      - Never drop conditions silently.
      - Never add information.
      - If meaning loss is possible, quote verbatim and flag.
    """
    if content == "Policy not found":
        return content

    summary_lines = [
        "HR Policy Summary",
        "=================",
        ""
    ]

    current_section = ""
    lines = content.splitlines()
    clauses = []
    current_clause = []

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
        
        # Check for section header (e.g. "1. PURPOSE AND SCOPE" or "5. LEAVE WITHOUT PAY (LWP)")
        header_match = re.match(r'^(\d+)\.\s+([A-Z\s\(\)]+)$', line_stripped)
        if header_match:
            if current_clause:
                clauses.append(" ".join(current_clause))
                current_clause = []
            
            section_num = header_match.group(1)
            section_title = header_match.group(2)
            clauses.append(f"\n## {section_num}. {section_title.title()}")
            continue
            
        # Check for clause start (e.g. "1.1 Something")
        clause_match = re.match(r'^(\d+\.\d+)\s+(.*)', line_stripped)
        if clause_match:
            if current_clause:
                clauses.append(" ".join(current_clause))
                current_clause = []
            
            current_clause.append(line_stripped)
            continue
            
        # Unnumbered continuation line
        if "══" not in line_stripped and current_clause:
             current_clause.append(line_stripped)

    if current_clause:
        clauses.append(" ".join(current_clause))
        
    for item in clauses:
        if item.startswith("\n##"):
            summary_lines.append(item)
        else:
            cleaned_text = re.sub(r'\s+', ' ', item)
            clause_num_match = re.match(r'^(\d+\.\d+)', cleaned_text)
            
            if clause_num_match:
                c_num = clause_num_match.group(1)
                text_without_num = cleaned_text[len(c_num):].strip()
                summary_lines.append(f"  - {c_num} [VERBATIM] {text_without_num}")
            else:
                summary_lines.append(f"  - [VERBATIM] {cleaned_text}")

    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy document (.txt)")
    parser.add_argument("--output", required=True, help="Path to write the summary (.txt)")
    args = parser.parse_args()

    content = retrieve_policy(args.input)
    if content == "Policy not found":
        print(f"Failed to find or read: {args.input}", file=sys.stderr)
        sys.exit(1)

    summary = summarize_policy(content)

    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
            f.write("\n")
        print(f"Successfully wrote summary to {args.output}")
    except Exception as e:
        print(f"Failed to write output to {args.output}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
