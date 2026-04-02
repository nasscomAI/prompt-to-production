"""
UC-0B app.py — Policy Summary Generator
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse

def summarize_policy(input_path: str, output_path: str):
    """
    Read the policy document, generate a summary preserving all clauses without changing meaning.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract numbered clauses (simple approach)
        lines = content.split('\n')
        clauses = []
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or (len(line) > 1 and line[0].isdigit() and line[1] in '.)')):
                clauses.append(line)
        
        # Create summary
        summary = "Policy Summary:\n\n" + '\n\n'.join(clauses)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"Summary written to {output_path}")
    except FileNotFoundError:
        print(f"Input file {input_path} not found.")
    except Exception as e:
        print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary Generator")
    parser.add_argument("--input", required=True, help="Path to policy document")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()
    summarize_policy(args.input, args.output)

if __name__ == "__main__":
    main()
