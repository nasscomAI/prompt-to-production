"""
UC-0B app.py — LLM implementation for HR policy summarization.
"""
import argparse
import os
import sys

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Please install google-genai package: pip install google-genai")
    sys.exit(1)

def retrieve_policy(filepath: str) -> str:
    """Skill 1: Retrieve policy document."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def summarize_policy(policy_text: str) -> str:
    """Skill 2: Summarize using AI based on RICE enforcement."""
    # Ensure API key is set
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        api_key = input("GEMINI_API_KEY not found. Please enter your API key: ").strip()
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set. Please set it before running.")
        
    client = genai.Client(api_key=api_key)
    
    # RICE Context from agents.md
    system_instruction = '''
role: >
  You are an HR Policy Summarization Agent. Your operational boundary is strict document summarization; you are not permitted to interpret, soften, or omit any binding obligations.

intent: >
  A correct output must contain all required clauses present in the original document, preserving all conditions and multi-approver requirements accurately, formatted as a clear and verifiable summary with clause references.

context: >
  You may only use the provided policy document. You are explicitly excluded from using outside knowledge, standard practices, or general government expectations not found in the source text.

enforcement:
  - "Every numbered clause must be present in the summary."
  - "Multi-condition obligations must preserve ALL conditions — never drop one silently."
  - "Never add information not present in the source document."
  - "If a clause cannot be summarised without meaning loss — quote it verbatim and flag it."
'''
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f"Summarize the following policy document according to your strict instructions:\n\n{policy_text}",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
        )
    )
    return response.text

def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write the summary txt")
    args = parser.parse_args()
    
    try:
        policy_content = retrieve_policy(args.input)
        print("Policy retrieved successfully. Summarizing using AI...")
        summary = summarize_policy(policy_content)
        
        # Ensure output directory exists just in case
        output_dir = os.path.dirname(os.path.abspath(args.output))
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Done. Summary written to {args.output}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
