import argparse
import json
import os
import re
import sys

try:
    import google.generativeai as genai
except ImportError:
    print("Please install google-generativeai: pip install google-generativeai")
    sys.exit(1)

def get_model(system_prompt: str):
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is missing.")
        sys.exit(1)

    try:
        genai.configure(api_key=api_key)
        
        # Use a model that supports strict instruction following
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=system_prompt
        )
        return model
    except Exception as e:
        print(f"Failed to initialize Gemini client: {e}")
        sys.exit(1)

def retrieve_policy(filepath: str) -> dict:
    """
    Loads a .txt policy file and returns its content as structured, numbered sections.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        sys.exit(1)
        
    clauses = {}
    current_clause = None
    current_text = []
    
    # Simple parser for numbered clauses starting with e.g. "1.1", "2.3"
    for line in text.split('\n'):
        match = re.match(r'^(\d+\.\d+)\s+(.+)', line)
        if match:
            if current_clause:
                clauses[current_clause] = " ".join(current_text).strip()
            current_clause = match.group(1)
            current_text = [match.group(2).strip()]
        elif current_clause and line.startswith('    '):
            current_text.append(line.strip())
        elif current_clause and line.startswith('══'):
            clauses[current_clause] = " ".join(current_text).strip()
            current_clause = None
            current_text = []
            
    if current_clause:
        clauses[current_clause] = " ".join(current_text).strip()
        
    if not clauses:
        print("Error: Could not parse any numbered sections from the file.")
        sys.exit(1)
        
    return clauses

def summarize_policy(clauses: dict) -> str:
    """
    Takes structured numbered sections and produces a compliant summary with explicit clause references.
    """
    # Dynamically load the agent and skill definitions
    try:
        with open("agents.md", "r", encoding="utf-8") as f:
            agents_md = f.read()
        with open("skills.md", "r", encoding="utf-8") as f:
            skills_md = f.read()
    except Exception as e:
        print(f"Error reading configuration files: {e}")
        sys.exit(1)

    system_prompt = f"""You are operating as defined by the following agent profile:

{agents_md}

You have the following skills available to understand your expected behavior:

{skills_md}

Strictly adhere to the enforcement rules and intent listed above.
"""
    
    model = get_model(system_prompt)
    
    user_prompt = f"Policy Clauses (JSON):\n{json.dumps(clauses, indent=2)}\n\nPlease summarize the above document according to your strict enforcement rules."
    
    try:
        response = model.generate_content(
            user_prompt,
            generation_config={"temperature": 0.0}
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error during summarization: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()

    print(f"Loading and structuring policy from {args.input}...")
    clauses = retrieve_policy(args.input)
    
    print(f"Parsed {len(clauses)} clauses. Generating strict summary...")
    summary = summarize_policy(clauses)
    
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Done. Summary written to {args.output}")
    except Exception as e:
        print(f"Error writing to output file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
