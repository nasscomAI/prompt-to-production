"""
UC-0B app.py
Implemented using the RICE + agents.md + skills.md workflow.
"""
import argparse
import os
import sys
import yaml
from pathlib import Path

try:
    import google.generativeai as genai
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

def retrieve_policy(filepath: str) -> str:
    """Skill 1: Loads the raw .txt policy file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Policy file missing: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read().strip()
    if not content:
        raise ValueError(f"Policy file {filepath} is empty.")
    return content

def summarize_policy(text: str, system_instruction: str) -> str:
    """Skill 2: Produces a compliant summary using AI."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it to proceed.")
        
    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=system_instruction
    )
    
    # Prompting the model to summarize according to its loaded system instructions
    prompt = f"Please summarize the following policy document according to your strict enforcement rules:\n\n{text}"
    response = model.generate_content(prompt)
    return response.text

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
        policy_text = retrieve_policy(args.input)
        
        print("Generating compliant summary...")
        summary = summarize_policy(policy_text, system_instruction)
        
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
            
        print(f"Success! Summary written to {args.output}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
