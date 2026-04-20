"""
UC-0B app.py — Policy Summarizer
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os


def retrieve_policy(file_path: str) -> dict:
    """
    Loads a policy document (.txt file) and returns its content structured as numbered sections.
    
    Returns:
        Dictionary with: 'content' (full text), 'clauses' (list of clause tuples with (number, text))
        
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file is empty or cannot be read
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy document not found: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        raise ValueError(f"Failed to read policy file: {str(e)}")
    
    if not content.strip():
        raise ValueError("Policy document is empty")
    
    # Structure the document by finding numbered sections (e.g., 2.3, 2.4, 3.2, etc.)
    clauses = []
    lines = content.split('\n')
    current_clause = None
    current_text = []
    
    for line in lines:
        # Check if line starts with a clause number (e.g., "2.3", "5.2")
        stripped = line.strip()
        if stripped and stripped[0].isdigit() and '.' in stripped.split()[0]:
            # Save previous clause if exists
            if current_clause:
                clauses.append((current_clause, '\n'.join(current_text).strip()))
            
            # Extract clause number
            clause_num = stripped.split()[0]
            if clause_num.count('.') == 1:  # Simple check for X.Y format
                current_clause = clause_num
                current_text = [line]
            else:
                if current_clause:
                    current_text.append(line)
        else:
            if current_clause:
                current_text.append(line)
    
    # Add last clause
    if current_clause:
        clauses.append((current_clause, '\n'.join(current_text).strip()))
    
    return {
        'content': content,
        'clauses': clauses,
        'file_path': file_path
    }


def summarize_policy(policy_data: dict) -> str:
    """
    Extracts all numbered clauses and produces a legally compliant summary with all conditions preserved.
    
    Enforcement:
    - All 10 core clauses must be present: 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2
    - Multi-condition obligations preserved (e.g., clause 5.2 requires BOTH approvers)
    - No scope bleed or external knowledge added
    - High-stakes obligations quoted verbatim if necessary
    
    Args:
        policy_data: Dictionary from retrieve_policy containing 'content' and 'clauses'
        
    Returns:
        String summary of all clauses with their obligations and binding verbs
        
    Raises:
        ValueError: If any core clauses are missing
    """
    CORE_CLAUSES = {'2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2'}
    
    clauses = policy_data.get('clauses', [])
    clause_dict = {clause_num: text for clause_num, text in clauses}
    
    # Check for missing clauses
    found_clauses = set(clause_dict.keys())
    missing = CORE_CLAUSES - found_clauses
    
    if missing:
        raise ValueError(f"Missing core clauses: {sorted(missing)}. Found: {sorted(found_clauses)}")
    
    # Build summary with all clauses in order
    summary_lines = [
        "# POLICY SUMMARY — HR LEAVE POLICY",
        "",
        "## All Clauses with Complete Obligations:",
        ""
    ]
    
    for clause_num in sorted(CORE_CLAUSES, key=lambda x: tuple(map(int, x.split('.')))):
        clause_text = clause_dict.get(clause_num, "")
        
        # Extract binding verb and full obligation
        # For now, preserve the full clause text to avoid meaning loss
        if clause_text:
            summary_lines.append(f"**Clause {clause_num}:**")
            summary_lines.append(clause_text)
            summary_lines.append("")
    
    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy document (e.g., policy_hr_leave.txt)")
    parser.add_argument("--output", required=True, help="Path to write summary output")
    args = parser.parse_args()
    
    try:
        # Step 1: Retrieve and structure the policy
        print(f"Loading policy document: {args.input}")
        policy_data = retrieve_policy(args.input)
        print(f"Found {len(policy_data['clauses'])} clauses in document")
        
        # Step 2: Summarize with enforcement rules
        print("Summarizing policy with clause preservation enforcement...")
        summary = summarize_policy(policy_data)
        
        # Step 3: Write output
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"✓ Summary written to {args.output}")
        
    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
        exit(1)
    except ValueError as e:
        print(f"Validation Error: {str(e)}")
        exit(1)
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
