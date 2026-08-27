"""
UC-0B app.py — Policy Summarization Agent
Built using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import os
import sys
import re

# Attempt to import an LLM library. 
# Using google-genai as the default example.
try:
    from google import genai
    from google.genai import types
    HAS_LLM = True
except ImportError:
    HAS_LLM = False

def load_agents_config(agents_md_path: str) -> str:
    """Reads agents.md to use as the system prompt (RICE structure)."""
    try:
        with open(agents_md_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "You are a strict, meaning-preserving summarizer."

def retrieve_policy(filepath: str) -> dict:
    """
    Skill: retrieve_policy
    Loads .txt policy file, returns content as structured numbered sections.
    """
    if not os.path.exists(filepath):
        return {"error": f"File '{filepath}' is missing."}
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        sections = {}
        current_section = "General"
        sections[current_section] = []
        
        # Simple extraction for numbered clauses like "2.3" or "1."
        for line in content.split('\n'):
            match = re.match(r'^(\d+\.?\d*)\s+(.*)', line.strip())
            if match:
                current_section = match.group(1).strip()
                sections[current_section] = [match.group(2).strip()]
            elif line.strip():
                sections[current_section].append(line.strip())
                
        structured_sections = {k: " ".join(v) for k, v in sections.items()}
        return structured_sections
    except Exception as e:
        return {"error": f"Failed to read file: {e}"}

def summarize_policy(structured_sections: dict, system_prompt: str) -> str:
    """
    Skill: summarize_policy
    Takes structured sections, produces compliant summary with clause references.
    """
    if "error" in structured_sections:
        return structured_sections["error"]
        
    # Convert structured data back to text for the LLM
    policy_text = "\n".join([f"Clause {k}: {v}" for k, v in structured_sections.items()])
    
    if not HAS_LLM:
        print("Warning: LLM SDK (google-genai) is not installed. Returning a mock summary.", file=sys.stderr)
        print("To run with AI, please install your preferred SDK and update summarize_policy().", file=sys.stderr)
        # Fallback to a mock summary when SDK is missing
        return f"[MOCK SUMMARY GENERATED - LLM NOT CONFIGURED]\n\nSystem Rules Used:\n{system_prompt}\n\nParsed Policy:\n{policy_text}"
        
    client = genai.Client()
    
    prompt = f"Please summarize the following policy according to your system instructions:\n\n{policy_text}"
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.0,
            ),
        )
        return response.text
    except Exception as e:
        return f"LLM API Error: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt")
    parser.add_argument("--output", required=True, help="Path to output summary .txt")
    args = parser.parse_args()
    
    # Path to agents.md
    base_dir = os.path.dirname(os.path.abspath(__file__))
    agents_path = os.path.join(base_dir, "agents.md")
    
    # 1. Load the RICE prompt
    system_prompt = load_agents_config(agents_path)
    
    # 2. Execute Skill: retrieve_policy
    structured_content = retrieve_policy(args.input)
    
    # 3. Execute Skill: summarize_policy
    summary = summarize_policy(structured_content, system_prompt)
    
    # 4. Write Output
    try:
        output_dir = os.path.dirname(os.path.abspath(args.output))
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"Done. Summary written to {args.output}")
    except Exception as e:
        print(f"Error writing to output file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
