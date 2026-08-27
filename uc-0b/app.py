"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import sys
from google import genai
from google.genai import types

def retrieve_policy(file_path: str) -> str:
    """
    Loads a .txt policy file and returns the content as structured, numbered sections.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Could not find policy document at {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading policy document: {e}")
        sys.exit(1)

def summarize_policy(policy_text: str) -> str:
    """
    Takes structured sections and produces a compliant summary with clause references 
    based strictly on the agent's rules.
    """
    system_instruction = '''
Role: A strict compliance extraction and summarization system.
Intent: Produce a comprehensive summary of an HR leave policy, extracting and preserving every numbered clause without altering the core meaning, obligations, or adding external context.
Context: Solely the provided input text file. No external HR practices or government standards may be referenced.

Enforcement Rules:
1. Every numbered clause must be present in the summary.
2. Multi-condition obligations must preserve ALL conditions (e.g., if a clause requires approval from X AND Y, both must be explicitly stated) — never drop one silently.
3. Never add information not present in the source document.
4. If a clause cannot be summarised without meaning loss, quote it verbatim and flag it.
'''
    
    prompt = f'''
Please summarize the following policy document according to your enforcement rules:

{policy_text}
'''
    
    # Configure Gemini API
    if 'GEMINI_API_KEY' not in os.environ:
        print("Error: GEMINI_API_KEY environment variable not set.")
        print("Please set it to run the summarization.")
        sys.exit(1)
        
    client = genai.Client()
    
    try:
        # Use low temperature to ensure strict extraction and compliance
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1
            )
        )
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    
    args = parser.parse_args()
    
    print(f"Reading policy document from {args.input}...")
    policy_text = retrieve_policy(args.input)
    
    print("Summarizing policy document using Gemini...")
    summary = summarize_policy(policy_text)
    
    print(f"Writing summary to {args.output}...")
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print("Done.")
    except Exception as e:
        print(f"Error writing to output file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
