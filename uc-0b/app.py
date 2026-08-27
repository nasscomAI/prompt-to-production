import argparse
import os
try:
    from openai import OpenAI
except ImportError:
    print("Please install openai: pip install openai")
    import sys
    sys.exit(1)

# Initialize the OpenAI client (ensure OPENAI_API_KEY is set in your environment)
client = OpenAI()

import json
import re

def retrieve_policy(input_path: str) -> dict:
    """
    Loads a .txt policy file and returns content as structured numbered sections.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Error: Input file '{input_path}' not found.")
    
    with open(input_path, mode='r', encoding='utf-8') as f:
        content = f.read()
        
    sections = {}
    current_section = "Header"
    sections[current_section] = []
    
    for line in content.split('\n'):
        clean_line = line.strip()
        if not clean_line or '════' in clean_line:
            continue
        if re.match(r'^\d+\.\s+[A-Z\s/]+$', clean_line):
            current_section = clean_line
            sections[current_section] = []
        else:
            sections[current_section].append(clean_line)
            
    # Join lines back for readibility
    for k in sections:
        sections[k] = '\n'.join(sections[k])
        
    return sections

def summarize_policy(policy_content: dict) -> str:
    """
    Takes structured policy text, produces compliant summary with clause references.
    """
    system_prompt = """
# role
HR Policy Summarizer Agent responsible for reading the human resources leave policy document and extracting a completely factual and exhaustive summary without altering, softening, or omitting any conditions or obligations.

# intent
Produce a comprehensive summary of the HR leave policy where every numbered clause is present, all multi-condition obligations preserve all conditions (e.g., requiring both Department Head AND HR Director approval), and no external or standard practice information is added.

# context
You are allowed to use ONLY the provided source document. You MUST strictly exclude any external knowledge, standard corporate practices, or assumed government organization norms.

# enforcement
- "Every numbered clause must be present in the summary"
- "Multi-condition obligations must preserve ALL conditions — never drop one silently"
- "Never add information not present in the source document"
- "If a clause cannot be summarised without meaning loss — quote it verbatim and flag it"
- "If asked to summarize without a provided source document, refuse rather than guessing"
"""

    user_prompt = f"Policy Document JSON:\n{json.dumps(policy_content, indent=2)}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error summarizing policy: {e}")
        return f"System Error: {str(e)}"

def process_document(input_path: str, output_path: str):
    print(f"Reading policy from {input_path}...")
    try:
        policy_content = retrieve_policy(input_path)
    except Exception as e:
        print(str(e))
        return

    print("Generating summary...")
    summary = summarize_policy(policy_content)

    print(f"Writing summary to {output_path}...")
    with open(output_path, mode='w', encoding='utf-8') as f:
        f.write(summary)
    print("Done.")

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    args = parser.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable is not set. Execution may fail.")
        
    process_document(args.input, args.output)

if __name__ == "__main__":
    main()
