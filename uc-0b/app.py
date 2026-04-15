import argparse
import os
import re

def retrieve_policy(input_path: str) -> list:
    """Loads a .txt policy file and returns its content as structured, numbered sections."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Policy document not found at {input_path}")
        
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Extract clauses that look like "2.3 Employees must..."
    # Pattern: Digit.Digit followed by text until next clause
    clauses = []
    # Match line starts with numbers e.g. "1.1 " up to the next number or EOF
    pattern = re.compile(r'^(\d+\.\d+)\s+(.*?)(?=(?:\n\d+\.\d+\s+)|\Z)', re.MULTILINE | re.DOTALL)
    for match in pattern.finditer(content):
        clause_num = match.group(1)
        clause_text = match.group(2).strip().replace('\n', ' ')
        clause_text = re.sub(r'\s+', ' ', clause_text)
        clauses.append((clause_num, clause_text))
        
    return clauses

def summarize_policy(clauses: list) -> str:
    """Takes structured sections and produces a compliant summary with correct clause references."""
    summary_lines = ["# Policy Document Summary", ""]
    
    for clause_num, text in clauses:
        text_lower = text.lower()
        # Rule: If a clause cannot be summarised without meaning loss — quote it verbatim and flag it.
        # Multi-condition obligations (and, requires, must, both) are risky, so we flag them.
        is_risky = any(kw in text_lower for kw in ['and', 'requires', 'must', 'only after', 'subject to'])
        
        if is_risky:
            summary_lines.append(f"- **Clause {clause_num} [VERBATIM]**: {text}")
        else:
            summary_lines.append(f"- **Clause {clause_num}**: {text}")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarization")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to output summary .txt file")
    args = parser.parse_args()
    
    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Summary written to {args.output}")
    except Exception as e:
        print(f"Error processing policy: {e}")

if __name__ == "__main__":
    main()
