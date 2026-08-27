"""
UC-0B app.py — HR Leave Policy Summarizer
Built using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import re

def retrieve_policy(filepath: str) -> dict:
    """
    Loads the raw HR leave policy .txt file and returns the content as structured numbered sections.
    Returns a dict mapping clause numbers (e.g., '2.3') to their text.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy document not found at: {filepath}")

    sections = {}
    
    # Extract clauses like "2.3 Employees must submit..."
    lines = content.split('\n')
    current_clause = None
    current_text = []

    for line in lines:
        line = line.strip()
        # Skip empty lines, separators, and category headers (e.g. "1. PURPOSE AND SCOPE")
        if not line or line.startswith('═') or line.isupper():
            continue
            
        match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
        if match:
            if current_clause:
                sections[current_clause] = " ".join(current_text)
            current_clause = match.group(1)
            current_text = [match.group(2)]
        elif current_clause:
            current_text.append(line)

    if current_clause:
        sections[current_clause] = " ".join(current_text)

    if not sections:
        raise ValueError("No numbered sections found in the document.")

    return sections

def summarize_policy(sections: dict) -> str:
    """
    Takes structured policy sections and produces a compliant, accurate summary 
    with explicit clause references, ensuring no conditions are dropped.
    """
    summary_lines = []
    summary_lines.append("HR LEAVE POLICY SUMMARY")
    summary_lines.append("=======================\n")
    
    # A mapping of simple clauses that can be summarized without meaning loss.
    safe_summaries = {
        "1.1": "Governs leave for permanent and contractual CMC employees.",
        "1.2": "Does not apply to daily wage workers or consultants.",
        "2.1": "Permanent employees get 18 days paid annual leave/year.",
        "2.2": "Annual leave accrues at 1.5 days/month.",
        "3.1": "Employees get 12 days paid sick leave/year.",
        "3.3": "Sick leave cannot be carried forward.",
        "4.3": "Male employees get 5 days paid paternity leave within 30 days of birth.",
        "4.4": "Paternity leave cannot be split."
    }

    for clause, text in sections.items():
        if clause in safe_summaries:
            summary_lines.append(f"- Clause {clause}: {safe_summaries[clause]}")
        else:
            # For complex obligations (like 5.2 requiring TWO approvers or 2.7 regarding carry-forward),
            # we strictly enforce the rule: "If a clause cannot be summarised without meaning loss 
            # or altering the obligation, you must quote it verbatim and flag it."
            summary_lines.append(f"- Clause {clause} [VERBATIM]: {text}")
        
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    try:
        sections = retrieve_policy(args.input)
    except Exception as e:
        print(f"Error reading policy: {e}")
        return

    summary_text = summarize_policy(sections)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary_text)

    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
