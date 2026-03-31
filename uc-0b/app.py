import argparse

def retrieve_policy(file_path):
    """
    Loads the HR policy text file and returns structured numbered clauses.
    Handles encoding issues on Windows.
    """
    try:
        # Fix: specify utf-8 and ignore undecodable characters
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        if not content.strip():
            raise ValueError("Policy document is empty")
        # Split by lines to simulate structured clauses
        clauses = [line.strip() for line in content.split('\n') if line.strip()]
        return clauses
    except FileNotFoundError:
        raise FileNotFoundError("Input file not found")


def summarize_policy(clauses):
    """
    Generates a summary preserving all required clauses.
    Raises error if any required clause is missing.
    """
    summary = []
    
    # List of required clauses (from UC-0B README)
    required_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7",
                        "3.2", "3.4", "5.2", "5.3", "7.2"]
    
    for rc in required_clauses:
        found = False
        for clause in clauses:
            if rc in clause:
                summary.append(clause)
                found = True
                break
        if not found:
            raise ValueError(f"Clause omission detected: {rc}")
    
    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser(description="HR Policy Summary Generator")
    parser.add_argument("--input", required=True, help="Path to input policy file")
    parser.add_argument("--output", required=True, help="Path to output summary file")
    
    args = parser.parse_args()
    
    try:
        # Retrieve structured clauses
        clauses = retrieve_policy(args.input)
        
        # Generate compliant summary
        summary = summarize_policy(clauses)
        
        # Write summary to output file
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print("Summary generated successfully!")
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()