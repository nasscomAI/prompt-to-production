"""
UC-0B app.py — Policy Summarization
Built using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import re
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

def retrieve_policy(filepath: str) -> str:
    """
    Skill: retrieve_policy
    Loads a .txt policy file and returns its content as structured numbered sections.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return ""

    clauses = []
    current_clause = None
    
    for line in content.split('\n'):
        # Match lines like "1.1 Text starts here"
        match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
        if match:
            if current_clause:
                clauses.append(current_clause)
            current_clause = {"id": match.group(1), "text": match.group(2).strip()}
        # Append continuation lines (ignore empty lines, headers, or Section lines like "1. PURPOSE")
        elif current_clause and line.strip() and not line.startswith('═') and not re.match(r'^\d+\.', line):
            current_clause["text"] += " " + line.strip()
            
    if current_clause:
        clauses.append(current_clause)
        
    structured_text = ""
    for c in clauses:
        structured_text += f"Clause {c['id']}: {c['text']}\n"
        
    return structured_text

def summarize_policy(structured_text: str, agent_prompt: str) -> str:
    """
    Skill: summarize_policy
    Takes structured sections and produces a compliant summary with clause references via AI.
    """
    if not structured_text.strip():
        return "Error: No policy content provided to summarize."
        
    try:
        payload = {
            "model": MODEL_NAME,
            "system": agent_prompt,
            "prompt": f"Here is the strict policy text to summarize:\n\n{structured_text}\n\nPlease generate the compliant summary.",
            "stream": False,
            "options": {
                "temperature": 0.0
            }
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        
        data = response.json()
        return data.get("response", "No summary generated.")
        
    except requests.exceptions.RequestException as e:
        print(f"API Connection Error: Is Ollama running? ({e})")
        return f"Error: API Connection Failed - {str(e)}"
    except Exception as e:
        print(f"Error during summarization: {e}")
        return f"Error: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="UC-0B Strict Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()
    
    # Load agent prompt directly from agents.md
    agent_path = os.path.join(os.path.dirname(__file__), "agents.md")
    try:
        with open(agent_path, 'r', encoding='utf-8') as f:
            agent_prompt = f.read()
    except FileNotFoundError:
        print("Error: agents.md not found. Cannot proceed without the RICE agent prompt.")
        return
        
    print(f"Reading and structuring policy from {args.input}...")
    structured_content = retrieve_policy(args.input)
    
    if not structured_content:
        print("Failed to structure content or input file was empty.")
        return
        
    print("Generating compliant summary...")
    summary = summarize_policy(structured_content, agent_prompt)
    
    print(f"Writing summary to {args.output}...")
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print("Complete.")
    except Exception as e:
        print(f"Error writing to output file {args.output}: {e}")

if __name__ == "__main__":
    main()
