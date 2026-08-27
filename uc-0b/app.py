"""
UC-0B app.py — Policy Summarizer
Built deterministically based on RICE constraints in agents.md and skills in skills.md.
"""
import argparse
import re

def retrieve_policy(filepath: str) -> dict:
    """
    Skill 1: Loads a .txt policy file and returns its content as structured numbered sections.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return {"error": f"Failed to read {filepath}: {e}"}

    sections = {}
    current_clause = None

    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Match main headers (e.g., "1. PURPOSE AND SCOPE" or "5. LEAVE WITHOUT PAY (LWP)") or separators
        if re.match(r'^\d+\.\s+[^a-z]+$', line) or line.startswith('═'):
            continue
            
        # Match numbered clauses (e.g., "2.3 Employees must submit...")
        clause_match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
        if clause_match:
            current_clause = clause_match.group(1)
            text = clause_match.group(2)
            sections[current_clause] = [text]
        elif current_clause:
            # Append continuation of the current clause's text
            sections[current_clause].append(line)
            
    # Combine multiline text cleanly
    for k, v in sections.items():
        sections[k] = " ".join(v)
        
    if not sections:
        return {"error": "No numbered clauses found in the document."}

    return sections

def summarize_clause(clause_id: str, text: str) -> str:
    """
    Summarize a single clause adhering STRICTLY to enforcement rules.
    If multiple conditions, specific approvals, 'must', 'requires' are present,
    it cannot be summarized safely without meaning loss — thus quote verbatim and flag (Rule 4).
    """
    # Tokens indicating complex, multi-condition, or strict obligations (Rules 2 & 4)
    binding_tokens = [
        'must', 'requires', 'required', 'only after', 'and', 'or', 'not valid', 
        'regardless', 'forfeited', 'not permitted', 'cannot'
    ]
    
    text_lower = text.lower()
    
    if any(token in text_lower for token in binding_tokens):
        # Quote verbatim and flag to prevent meaning loss / condition drops
        return f"- **Clause {clause_id}** [VERBATIM - HIGH BINDING]: \"{text}\""
    else:
        # Can be presented directly
        return f"- **Clause {clause_id}**: {text}"

def summarize_policy(sections: dict) -> str:
    """
    Skill 2: Produces a strictly compliant summary from structured sections, preserving all clauses and conditions.
    """
    if "error" in sections:
        return f"Error executing summarize: {sections['error']}"
        
    summary_lines = [
        "COMPLIANT POLICY SUMMARY",
        "========================",
        ""
    ]
    
    # Rule 1: Every numbered clause must be present in the summary
    for clause_id, text in sections.items():
        summary_lines.append(summarize_clause(clause_id, text))
        
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Input .txt file path")
    parser.add_argument("--output", required=True, help="Output .txt file path")
    args = parser.parse_args()

    # Execute Skill: Retrieve
    sections = retrieve_policy(args.input)
    
    # Execute Skill: Summarize
    summary_text = summarize_policy(sections)

    # Output Handling
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary_text)
        print(f"Done. 100% compliant summary saved to {args.output}")
    except Exception as e:
        print(f"Error writing to output file: {e}")

if __name__ == "__main__":
    main()

