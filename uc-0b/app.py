import sys
import re
import os

def summarize_policy(input_path, output_path):
    print(f"Reading policy document from: {input_path}...")
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()

        # Split text into lines/sentences for processing
        lines = text.split('\n')
        
        summary_lines = [
            "# HR Leave Policy - Executive Summary\n",
            "*(Agent execution: Strict numerical & clause constraint retention)*\n\n",
            "### Core Rules & Constraints:\n"
        ]
        
        # Agent Logic: Retain any line containing numbers, bullets, or clause markers
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Regex to find numbers or specific clause markers
            has_number = re.search(r'\d+', line)
            is_bullet_or_clause = line.startswith('-') or line.startswith('*') or "Clause" in line
            
            if has_number or is_bullet_or_clause:
                # Clean up formatting and append as a bullet point
                clean_line = line.lstrip('- *')
                summary_lines.append(f"- {clean_line}\n")

        # Write out the summary
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(summary_lines)
            
        print(f"Successfully generated rule-compliant summary at: {output_path}")

    except FileNotFoundError:
        print(f"Error: Could not find the input file at {input_path}")
        print("Make sure you are running the script from inside the uc-0b folder!")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Define paths relative to the uc-0b directory
    input_file = os.path.join("..", "data", "policy-documents", "policy_hr_leave.txt")
    output_file = "summary_hr_leave.txt"
    
    summarize_policy(input_file, output_file)