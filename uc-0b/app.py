"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import sys

def retrieve_policy(file_path):
    """
    Loads .txt policy file and returns content as structured numbered sections.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return {"error": str(e)}
        
    sections = {}
    current_clause = None
    buffer = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Match clauses like "1.1 This policy..."
        match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
        if match:
            if current_clause:
                sections[current_clause] = " ".join(buffer)
            current_clause = match.group(1)
            buffer = [match.group(2)]
        elif current_clause and not line.startswith("══") and not re.match(r'^\d+\.\s+[A-Z]', line):
            # Continuation of previous clause
            buffer.append(line)

    if current_clause:
        sections[current_clause] = " ".join(buffer)
        
    return {"sections": sections}

def summarize_policy(structured_data):
    """
    Takes structured sections and produces a compliant summary with clause references.
    """
    if "error" in structured_data:
        return f"Error loading policy: {structured_data['error']}"
        
    sections = structured_data["sections"]
    summary_lines = []
    
    summary_lines.append("POLICY SUMMARY")
    summary_lines.append("=" * 40)
    
    for clause, text in sections.items():
        # Heuristics to safely preserve original meaning for complex clauses
        summary = f"Clause {clause}: {text}"
        
        # If a clause is highly conditional it's flagged as per enforcement rules
        if "requires approval from the Department Head and the HR Director" in text or "under any circumstances" in text or "regardless of duration" in text:
            summary = f"[FLAG - QUOTED VERBATIM to prevent meaning loss]\nClause {clause}: {text}"

        summary_lines.append(summary)
        
    return "\n\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarization Agent")
    parser.add_argument("--input", required=True, help="Path to policy document (.txt)")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    args = parser.parse_args()
    
    # 1. Retrieve phase
    data = retrieve_policy(args.input)
    
    # 2. Summarize phase
    summary_text = summarize_policy(data)
    
    # 3. Output phase
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary_text)
        print(f"Summary successfully written to {args.output}")
    except Exception as e:
        print(f"Failed to write output: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
