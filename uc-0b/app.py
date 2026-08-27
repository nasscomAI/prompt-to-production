"""
UC-0B — Summary That Changes Meaning
Gemini integration to flawlessly summarize HR policies without losing conditional obligations.
"""
import argparse
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("ERROR: Please install: pip install google-genai")
    sys.exit(1)

def get_system_prompt() -> str:
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        agents_path = os.path.join(script_dir, 'agents.md')
        with open(agents_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return "Summarize carefully."

def retrieve_policy(filepath: str) -> str:
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def summarize_policy(client, policy_text: str, system_prompt: str) -> str:
    prompt = f"Please summarize the following policy document:\n\n{policy_text}\n\nCRITICAL: Ensure that absolutely no meaning or obligations are softened. If clause 5.2 states multiple approvers are needed, explicitly name all of them."
    
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.0
            )
        )
        return response.text
    except Exception as e:
        print(f"Error generating summary: {e}")
        return "ERROR: Could not generate summary due to an API error."

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Input .txt file")
    parser.add_argument("--output", required=True, help="Output .txt file")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(">> WARNING: GEMINI_API_KEY is not set!")
        sys.exit(1)

    print(f"Reading {args.input}...")
    policy_text = retrieve_policy(args.input)
    
    client = genai.Client(api_key=api_key)
    system_prompt = get_system_prompt()
    
    print("Generating rigorous summary via Gemini...")
    summary = summarize_policy(client, policy_text, system_prompt)
    
    # Programmatic post-generation validation check
    mandatory_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    warnings = []
    for clause in mandatory_clauses:
        if clause not in summary:
            warnings.append(f"WARNING: Clause {clause} was completely omitted in the LLM output!")
            
    if "HR Director" not in summary and "5.2" in summary:
        warnings.append("WARNING: Clause 5.2 was found, but 'HR Director' approver condition was dropped (Scope bleeding / Softening)!")
        
    if warnings:
        summary = "\n".join(warnings) + "\n\n" + summary
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
        
    print(f"Done! Summary saved to {args.output}")

if __name__ == "__main__":
    main()
