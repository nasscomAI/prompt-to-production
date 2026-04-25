"""
UC-0B app.py — Policy Summarization Agent
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import re
import os
import yaml # Using yaml to parse agents.md if it's formatted as such, or just regex.
from openai import OpenAI

def retrieve_policy(file_path):
    """
    Skill: retrieve_policy
    Loads a .txt policy file and extracts content as structured, numbered sections.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex to find clauses like 2.3, 5.2 at the start of a line
    pattern = r'^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+|\Z)'
    matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
    
    sections = []
    for match in matches:
        sections.append({
            "clause_id": match.group(1).strip(),
            "content": match.group(2).replace('\n', ' ').strip()
        })
    
    if not sections:
        raise ValueError("No numbered clauses found in the policy document. Ensure clauses start with 'X.Y' at the beginning of a line.")
        
    return sections

def summarize_policy(sections, agent_config):
    """
    Skill: summarize_policy
    Produces a high-fidelity summary using the agent persona and enforcement rules.
    """
    client = OpenAI() # Expects OPENAI_API_KEY in environment
    
    # Prepare input text for the LLM
    input_text = "\n".join([f"Clause {s['clause_id']}: {s['content']}" for s in sections])
    
    enforcement_str = "\n".join([f"- {r}" for r in agent_config['enforcement']])
    
    prompt = f"""
You are a specialized AI agent with the following profile:

ROLE:
{agent_config['role']}

INTENT:
{agent_config['intent']}

CONTEXT:
{agent_config['context']}

ENFORCEMENT RULES:
{enforcement_str}

INPUT POLICY CLAUSES:
{input_text}

TASK:
Produce the summary following all enforcement rules strictly.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a precise Policy Summarization Agent."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    
    return response.choices[0].message.content

def load_agent_config(agent_file):
    """Reads agents.md and extracts role, intent, context, and enforcement."""
    with open(agent_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    config = {}
    # Extract using simple regex as agents.md is YAML-like but in a markdown file
    config['role'] = re.search(r'role:\s*>\s*(.*?)(?=\n\w+:|$)', content, re.DOTALL).group(1).strip()
    config['intent'] = re.search(r'intent:\s*>\s*(.*?)(?=\n\w+:|$)', content, re.DOTALL).group(1).strip()
    config['context'] = re.search(r'context:\s*>\s*(.*?)(?=\n\w+:|$)', content, re.DOTALL).group(1).strip()
    
    # Enforcement rules are a list
    enforcement_block = re.search(r'enforcement:\s*(.*?)(?=\n\w+:|$)', content, re.DOTALL).group(1)
    config['enforcement'] = [r.strip(' - "') for r in enforcement_block.strip().split('\n')]
    
    return config

def main():
    parser = argparse.ArgumentParser(description="Policy Summarization Tool (UC-0B)")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to save the summary output")
    args = parser.parse_args()

    try:
        # 1. Load Agent Config
        agent_config = load_agent_config("agents.md")
        
        # 2. Retrieve Policy (Skill)
        print(f"Retrieving policy from {args.input}...")
        sections = retrieve_policy(args.input)
        print(f"Found {len(sections)} clauses.")
        
        # 3. Summarize Policy (Skill)
        print("Generating compliant summary...")
        summary = summarize_policy(sections, agent_config)
        
        # 4. Save Output
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"Summary successfully saved to {args.output}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
