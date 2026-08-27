"""
UC-0B app.py — Policy Summarisation Agent
Implemented based on the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import sys
import json
import re

def retrieve_policy(file_path):
    """
    Skill: retrieve_policy
    Loads a .txt policy file and returns its content as structured numbered sections.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: Policy file not found at {file_path}")
    
    structured_data = []
    current_section = {"section": "Header", "content": []}
    
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line_strip = line.strip()
            if not line_strip or line_strip.startswith("════"):
                continue
            
            # Match main sections (e.g., "1. PURPOSE AND SCOPE") or sub-clauses (e.g., "1.1 ...")
            if re.match(r"^\d+(\.\d+)?\.?\s", line_strip):
                if current_section["content"]:
                    current_section["content"] = " ".join(current_section["content"])
                    structured_data.append(current_section)
                
                parts = line_strip.split(" ", 1)
                sec_id = parts[0]
                text = parts[1] if len(parts) > 1 else ""
                current_section = {"section": sec_id, "content": [text]}
            else:
                current_section["content"].append(line_strip)
                
    if current_section["content"]:
         current_section["content"] = " ".join(current_section["content"])
         structured_data.append(current_section)
         
    if not structured_data:
        raise ValueError("Error: File is unreadable or not formatted with clear numbered clauses.")
         
    return json.dumps(structured_data, indent=2)

def summarize_policy(structured_policy, agents_md_path):
    """
    Skill: summarize_policy
    Takes structured clauses and produces a compliant summary that strictly preserves all meaning.
    """
    if not os.path.exists(agents_md_path):
        raise FileNotFoundError(f"Error: Agent config not found at {agents_md_path}")
        
    with open(agents_md_path, "r", encoding="utf-8") as f:
        system_prompt = f.read()

    # Try Google GenAI first (the new package)
    try:
        from google import genai
        from google.genai import types
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable is missing. Please set it using: $env:GEMINI_API_KEY='your-key'")
            
        client = genai.Client(api_key=api_key)
        
        print("Generating compliant summary using Gemini...")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Please summarize the following structured policy document:\n\n{structured_policy}",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.0,
            )
        )
        return response.text

    except ImportError:
        # Fallback to OpenAI if google.genai is not installed
        try:
            from openai import OpenAI
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is missing. Please set it using: $env:OPENAI_API_KEY='your-key'")
                
            client = OpenAI(api_key=api_key)
            print("Generating compliant summary using OpenAI...")
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.0,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Please summarize the following structured policy document:\n\n{structured_policy}"}
                ]
            )
            return response.choices[0].message.content
            
        except ImportError:
            print("Error: An LLM library is required to run the agent.")
            print("Please run: pip install google-genai (or openai)")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    agents_md_path = os.path.join(script_dir, "agents.md")

    try:
        print(f"Retrieving policy from {args.input}...")
        structured_policy = retrieve_policy(args.input)
        
        summary = summarize_policy(structured_policy, agents_md_path)
        
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
            
        print(f"Success! Summary written to {args.output}")
        
    except Exception as e:
        print(f"Application Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
