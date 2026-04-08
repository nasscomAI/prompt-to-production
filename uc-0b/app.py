import argparse
import os
import sys

def retrieve_policy(file_path):
    """Skill 1: Loads the .txt policy file with UTF-8 encoding."""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.") [cite: 135]
        sys.exit(1)
    
    # ADD encoding='utf-8' HERE
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read() 
    
    return content

def summarize_policy(content):
    """
    Skill 2: Produces a compliant summary[cite: 235].
    In a real AI agent, this would call an LLM API. 
    For this assignment, ensure it reflects the 'Enforcement' rules 
    found in your agents.md[cite: 202].
    """
    # This is a placeholder for the AI's summarization logic.
    # It must preserve every numbered clause verbatim if 
    # meaning loss is detected[cite: 182, 216].
    summary = "--- HR LEAVE POLICY SUMMARY (UC-0B) ---\n\n"
    summary += "Note: All binding obligations and approvers preserved per enforcement rules.\n\n"
    summary += content # In your live lab, the AI will rewrite this.
    return summary

def main():
    # Setup Argument Parser based on UC-0B requirements [cite: 156, 271]
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt")
    parser.add_argument("--output", required=True, help="Path to output summary .txt")
    
    args = parser.parse_args()

    # Step 1: Retrieve [cite: 125]
    policy_text = retrieve_policy(args.input)
    
    # Step 2: Summarize [cite: 125]
    final_summary = summarize_policy(policy_text)
    
    # Step 3: Write Output
    # Add encoding='utf-8' here to prevent the EncodeError
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(final_summary)    
    
    print(f"✅ Summary successfully generated: {args.output} ")

if __name__ == "__main__":
    main()