"""
UC-0B app.py
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse

CRITICAL_CLAUSES = ['2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2']

def retrieve_policy(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        # read lines, but we should join multi-line clauses. For simplicity, just reading lines.
        # Wait, some clauses are split into multiple lines.
        text = f.read()
        return text

def summarize_policy(text):
    summary = ["# HR Leave Policy Summary\\n"]
    
    # Split text into sentences or lines, but since clauses start with a number, let's extract them using regex.
    import re
    # Match clause number at start of line, followed by the rest of the clause until the next double newline or clause number
    for clause_id in CRITICAL_CLAUSES:
        # Match "2.3 text text\n text"
        pattern = rf"^({clause_id}\s+(?:.*?))(?=^\d\.\d|\Z)"
        match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
        if match:
            # clean up newlines for a single summary clause
            clause_text = match.group(1).replace('\n', ' ').strip()
            summary.append(f"[VERBATIM] {clause_text}")

    return "\n".join(summary)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    text = retrieve_policy(args.input)
    summary_text = summarize_policy(text)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary_text)
    
    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
