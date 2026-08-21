import argparse
import re
import sys

def retrieve_policy(file_path):
    """
    Loads a technical HR policy document and parses it into a structured dictionary 
    of numbered sections to ensure precise referencing.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Policy file not found at {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Use regex to find clauses starting with X.Y
    # Pattern looks for digit.digit at the start of a line or after a newline
    policy_dict = {}
    
    # First, let's normalize line endings and extra spaces
    content = content.replace('\r\n', '\n')
    
    # Split by clause markers (e.g., 2.3, 5.2)
    # We look for \d+\.\d+ that is either at the start of the file or preceded by a newline
    sections = re.split(r'(?m)^(\d+\.\d+)\s+', content)
    
    # sections is [header_text, "1.1", "text...", "1.2", "text...", ...]
    if len(sections) > 1:
        for i in range(1, len(sections), 2):
            clause_num = sections[i]
            clause_text = sections[i+1].strip()
            
            # Remove decorative headers like ════ or section titles
            # We can use regex to find sequences of ═ or capitalized section headers
            clause_text = re.sub(r'═+', '', clause_text)
            # Remove title blocks like "3. SICK LEAVE" if they appear at the end
            clause_text = re.sub(r'\d+\.\s+[A-Z\s]+$', '', clause_text).strip()
            
            # Clean up whitespace
            clause_text = " ".join(clause_text.split())
            policy_dict[clause_num] = clause_text
            
    return policy_dict

def summarize_policy(policy_data):
    """
    Generates a verifiable summary of structured policy sections while preserving 
    all binding obligations and multi-condition requirements.
    """
    # The 10 critical clauses from README.md
    CLAUSE_INVENTORY = [
        "2.3", "2.4", "2.5", "2.6", "2.7", 
        "3.2", "3.4", 
        "5.2", "5.3", 
        "7.2"
    ]
    
    summary_entries = []
    
    for clause in CLAUSE_INVENTORY:
        if clause in policy_data:
            text = policy_data[clause]
            
            # High-precision summary rules:
            # 1. Preserve binding verbs (must, will, requires, not permitted).
            # 2. Preserve ALL conditions (e.g., dual approval in 5.2).
            # 3. No scope bleed (no "typically", "as is standard").
            
            # For this implementation, we quote the exact clause sentences to 
            # ensure zero meaning loss, as per agents.md enforcement Rule 4.
            summary_entries.append(f"Clause {clause}: {text}")
        else:
            # Error handling: Refuse if content is missing
            summary_entries.append(f"Clause {clause}: [MISSING OBLIGATION - CRITICAL FAILURE]")
            
    return "\n".join(summary_entries)

def main():
    parser = argparse.ArgumentParser(description="UC-0B: High-Precision HR Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to save the summary .txt file")
    
    args = parser.parse_args()
    
    # Step 1: Retrieve Policy
    policy_data = retrieve_policy(args.input)
    
    # Step 2: Summarize Policy
    summary = summarize_policy(policy_data)
    
    # Step 3: Write Output
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Summary successfully written to {args.output}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
