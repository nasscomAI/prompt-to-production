import argparse
import os
import re

# Skill 1: retrieve_policy
def retrieve_policy(input_file):
    if not os.path.exists(input_file):
        return f"Error: File '{input_file}' not found."

    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()

    # Use regular expressions to detect clauses with numbers like 2.3, 2.4, etc.
    clauses = []
    lines = content.split('\n')
    current_clause = {}

    for line in lines:
        # Check if line starts with a clause number pattern like '2.3', '2.4', etc.
        match = re.match(r'(\d+\.\d+)', line.strip())
        if match:
            if current_clause and 'clause' in current_clause and 'obligation' in current_clause:
                clauses.append(current_clause)
            # Reset the current clause, now it should have the 'clause' key with the number.
            current_clause = {'clause': match.group(0)}  # Capture the clause number like '2.3'
            print(f"Detected new clause: {current_clause['clause']}")  # Debugging print
        elif line.strip():  # Only process non-empty lines
            current_clause['obligation'] = line.strip()  # Capture the obligation for the clause
            print(f"Added obligation: {current_clause['obligation']}")  # Debugging print

    # Add the last clause if it's complete
    if current_clause and 'clause' in current_clause and 'obligation' in current_clause:
        clauses.append(current_clause)
        print(f"Final clause added: {current_clause}")  # Debugging print

    return clauses


# Skill 2: summarize_policy
def summarize_policy(clauses):
    summary = []
    for clause in clauses:
        if "obligation" not in clause:
            return f"Error: Clause {clause['clause']} is missing obligation."
        
        clause_text = f"{clause['clause']}: {clause['obligation']}"
        summary.append(clause_text)
    
    # Ensure all 10 clauses are included, check for any omissions or softening
    required_clauses = [
        "2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"
    ]
    for required in required_clauses:
        if not any(clause['clause'].startswith(required) for clause in clauses):
            return f"Error: Missing required clause {required}."
    
    return "\n".join(summary)


# Main app function
def main():
    # Setup argument parser for input and output files
    parser = argparse.ArgumentParser(description="Summarize HR leave policy document")
    parser.add_argument('--input', type=str, required=True, help="Input policy file")
    parser.add_argument('--output', type=str, required=True, help="Output summary file")
    
    args = parser.parse_args()
    
    # Retrieve policy
    policy_content = retrieve_policy(args.input)
    if isinstance(policy_content, str) and policy_content.startswith("Error"):
        print(policy_content)
        return
    
    # Summarize policy
    summary = summarize_policy(policy_content)
    if isinstance(summary, str) and summary.startswith("Error"):
        print(summary)
        return
    
    # Write the summary to the output file
    with open(args.output, 'w', encoding='utf-8') as file:
        file.write(summary)
    
    print(f"Summary successfully written to {args.output}")


if __name__ == "__main__":
    main()