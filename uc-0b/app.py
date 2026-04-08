"""
UC-0B app.py
Implemented using local python text parsing to extract binding obligations exactly as they appear, preserving all conditional traps (e.g., Clause 5.2).
"""
import argparse
import re

BINDING_VERBS = [
    r'\bmust\b', 
    r'\bwill\b', 
    r'\brequires\b', 
    r'\bnot permitted\b', 
    r'\bforfeited\b'
]

def retrieve_policy(filepath: str) -> dict:
    """
    Loads the .txt policy file and returns the content mapped as structured numbered sections.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        raise RuntimeError(f"Critical Error: Failed to read policy file. {e}")
        
    sections = {}
    
    # Matches patterns like "2.3 Employees must..."
    # We use a regex that looks for numbers like X.Y followed by text until the next X.Y or line of '═'
    pattern = re.compile(r'(?P<clause>\d+\.\d+)\s+(?P<text>.*?)(?=(?:\n\d+\.\d+)|(?:\n═)|$)', re.DOTALL)
    
    for match in pattern.finditer(content):
        clause = match.group('clause')
        text = match.group('text').replace('\n', ' ').strip()
        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text)
        sections[clause] = text
        
    return sections

def summarize_policy(sections: dict) -> str:
    """
    Takes structured policy sections and produces a compliant summary preserving all dependencies.
    Fallback local heuristic: Extracts clauses with binding verbs verbatim to prevent condition dropping.
    """
    summary_lines = []
    summary_lines.append("HR LEAVE POLICY - BINDING OBLIGATIONS SUMMARY\n")
    summary_lines.append("Note: Clauses with complex conditions are quoted verbatim to prevent meaning loss.\n")
    
    verb_pattern = re.compile('|'.join(BINDING_VERBS), re.IGNORECASE)
    
    for clause, text in sections.items():
        if verb_pattern.search(text):
            summary_lines.append(f"- Clause {clause}: \"{text}\"")
            
    if not summary_lines:
        return "No binding obligations found in the policy."
        
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary.txt")
    args = parser.parse_args()
    
    print("Retrieving policy sections...")
    sections = retrieve_policy(args.input)
    
    print("Summarizing policy...")
    summary_text = summarize_policy(sections)
    
    with open(args.output, 'w', encoding='utf-8') as out:
        out.write(summary_text)
        
    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
