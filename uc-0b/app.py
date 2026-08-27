import argparse
import re
import sys

def retrieve_policy(filepath: str) -> dict:
    """
    Loads a .txt policy file and returns the content as structured numbered sections.
    Returns a dict mapping clause numbers (e.g., '1.1') to their full text.
    """
    clauses = {}
    current_clause = None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # Match clause numbers like "1.1", "2.3", etc. at the start of the line
                match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
                if match:
                    current_clause = match.group(1)
                    clauses[current_clause] = match.group(2)
                elif current_clause and not re.match(r'^═|^#|^\d+\.', line):
                    # Continuation of previous clause
                    clauses[current_clause] += " " + line
    except FileNotFoundError:
        print(f"Error: Policy file not found at {filepath}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading policy file: {e}")
        sys.exit(1)
        
    if not clauses:
        print("Warning: No clear numbered sections found in the document.")
        
    return clauses

def summarize_policy(clauses: dict) -> str:
    """
    Takes structured sections and produces a compliant summary with clause references.
    Adheres to enforcement rules:
    - Every numbered clause must be present
    - Multi-condition obligations must preserve ALL conditions
    - Never add information not present
    - Quote verbatim and flag [VERBATIM] if meaning loss is possible
    """
    summary_lines = []
    summary_lines.append("HR LEAVE POLICY SUMMARY")
    summary_lines.append("=======================\n")
    
    # We will iterate through all clauses to ensure none are omitted.
    # To prevent meaning loss or dropping conditions, we will flag clauses 
    # with complex conditions or binding verbs as [VERBATIM] and quote them.
    
    binding_keywords = ["must", "requires", "will", "forfeit", "not permitted"]
    multi_condition_keywords = [" and ", "both", "multiple"]
    
    for clause_num, text in clauses.items():
        lower_text = text.lower()
        
        needs_verbatim = False
        
        # Check for binding verbs
        if any(keyword in lower_text for keyword in binding_keywords):
            needs_verbatim = True
            
        # Check for multi-condition
        if any(keyword in lower_text for keyword in multi_condition_keywords):
            needs_verbatim = True
            
        if needs_verbatim:
            summary_lines.append(f"- Clause {clause_num} [VERBATIM]: \"{text}\"")
        else:
            summary_lines.append(f"- Clause {clause_num}: {text}")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer Agent")
    parser.add_argument("--input", required=True, help="Path to input policy text file")
    parser.add_argument("--output", required=True, help="Path to write the summary output")
    args = parser.parse_args()
    
    # 1. Retrieve the policy
    print(f"Retrieving policy from {args.input}...")
    structured_policy = retrieve_policy(args.input)
    
    # 2. Summarize the policy
    print("Summarizing policy...")
    summary = summarize_policy(structured_policy)
    
    # 3. Write to output
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Summary successfully written to {args.output}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
