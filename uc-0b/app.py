"""
UC-0B app.py
Implemented using the RICE + agents.md + skills.md workflow.
"""
import argparse
import os
import sys
import yaml
import re
from pathlib import Path

try:
    from google import genai
except ImportError:
    print("Error: Missing required packages. Please run: pip install google-generativeai pyyaml", file=sys.stderr)
    sys.exit(1)

def load_agent_prompt(agents_file: str) -> str:
    """Loads and formats the RICE prompt from agents.md."""
    if not os.path.exists(agents_file):
        raise FileNotFoundError(f"Agent specification missing: {agents_file}")
        
    with open(agents_file, 'r', encoding='utf-8') as f:
        content = yaml.safe_load(f)
        
    prompt = []
    if 'role' in content: 
        prompt.append(f"ROLE:\n{content['role'].strip()}\n")
    if 'intent' in content: 
        prompt.append(f"INTENT:\n{content['intent'].strip()}\n")
    if 'context' in content: 
        prompt.append(f"CONTEXT:\n{content['context'].strip()}\n")
    if 'enforcement' in content:
        prompt.append("ENFORCEMENT RULES:")
        for idx, rule in enumerate(content['enforcement'], 1):
            prompt.append(f"{idx}. {rule}")
            
    return "\n".join(prompt)

def retrieve_policy(filepath: str) -> list:
    """Skill 1: Loads the raw .txt policy file and parses its contents into structured, numbered sections."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Policy file missing: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read().strip()
    if not content:
        raise ValueError(f"Policy file {filepath} is empty.")
    
    # Skill requirement: Parse into structured numbered sections
    # Using regex to identify clause patterns like 1.1, 2.1, etc.
    lines = content.splitlines()
    clauses = []
    current_clause = ""
    
    for line in lines:
        stripped = line.strip()
        if not stripped: continue
        
        # Match lines starting with "1.1", "2. ", "3.1.2 " etc.
        if re.match(r'^\d+(\.\d+)*\s+', stripped):
            if current_clause:
                clauses.append(current_clause.strip())
            current_clause = stripped
        else:
            if current_clause:
                current_clause += " " + stripped
                
    if current_clause:
        clauses.append(current_clause.strip())
        
    if not clauses:
        # Fallback if no numbered clauses found, treat whole text as one
        clauses = [content]
        
    return clauses

import time

def summarize_policy(clauses: list, system_instruction: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")

    text_to_summarize = "\n".join(clauses)

    # ---------- TRY API FIRST ----------
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{system_instruction}\n\n{text_to_summarize}"
            )

            return response.text

        except Exception as e:
            print(f"API failed ({e}), switching to offline mode...\n")

    # ---------- FALLBACK (NO API) ----------
    print("Using offline summarizer...")

    summary = []

    for clause in clauses:
        # take first sentence of each clause
        sentence = clause.split(".")[0].strip()
        if sentence:
            summary.append(f"- {sentence}.")

    return "\n".join(summary)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy file")
    parser.add_argument("--output", required=True, help="Path to save the generated summary")
    args = parser.parse_args()

    # Locate agents.md in the current script directory
    script_dir = Path(__file__).parent
    agents_file = script_dir / "agents.md"
    
    try:
        print("Loading RICE agent specs from agents.md...")
        system_instruction = load_agent_prompt(str(agents_file))
        
        print(f"Retrieving policy from {args.input}...")
        policy_clauses = retrieve_policy(args.input)
        print(f"Detected {len(policy_clauses)} structured clauses.")
        
        print("Generating compliant summary...")
        summary = summarize_policy(policy_clauses, system_instruction)
        
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
            
        print(f"Success! Summary written to {args.output}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

