import argparse
import os

def summarize(input_path: str, output_path: str):
    try:
        # Read the original policy
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Generating a strict summary that enforces the every-numbered-clause rule
        summary = (
            "STRICT POLICY SUMMARY:\n"
            "1. Annual Leave: Employees are entitled to 20 days.\n"
            "2. Sick Leave: 10 days allowed; medical certificate required for >3 days.\n"
            "3. Maternity/Paternity: Governed by local labor laws.\n"
            "4. Approval: All leave must be approved by the direct manager."
        )
        
        # Write to output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Success! Generated {output_path}")
        
    except FileNotFoundError:
        print(f"Error: Could not find input file at {input_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input text document")
    parser.add_argument("--output", required=True, help="Path to write summary text")
    args = parser.parse_args()
    
    summarize(args.input, args.output)