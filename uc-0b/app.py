import os
import re
import sys
import json
import argparse

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: The 'google-genai' package is required. Install it using `pip install google-genai`.")
    sys.exit(1)
    
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv is optional but recommended

def retrieve_policy(filepath: str) -> dict:
    """
    Skill 1: Loads a .txt policy file and returns the content as structured numbered sections.
    """
    if not os.path.exists(filepath):
        print(f"Error: Policy document not found at {filepath}")
        sys.exit(1)
        
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
        
    clauses = {}
    # Regex to find numbered clauses like "1.1", "2.3" and capture their text until the next clause or end of file
    pattern = re.compile(r'^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+|\Z)', re.MULTILINE | re.DOTALL)
    
    matches = pattern.findall(text)
    for clause_id, content in matches:
        # Clean up whitespace and newlines for a structured output
        cleaned_content = ' '.join(content.split())
        clauses[clause_id] = cleaned_content
        
    if not clauses:
        print("Error: No structured sections found in the document. Ensure it follows the expected numbered format.")
        sys.exit(1)
        
    return clauses

def summarize_policy(structured_sections: dict, agents_text: str, skills_text: str) -> str:
    """
    Skill 2: Takes structured sections and produces a compliant summary with clause references.
    """
    if not structured_sections:
        print("Error: Provided sections to summarize are empty.")
        sys.exit(1)
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: Please set the GEMINI_API_KEY environment variable (or add it to a .env file) to use the Gemini model.")
        sys.exit(1)
        
    client = genai.Client(api_key=api_key)
    
    system_instruction = f"AGENT INSTRUCTIONS:\n{agents_text}\n\nSKILLS OVERVIEW:\n{skills_text}"
    
    prompt = f"Please summarize the following policy document clauses according to your strict enforcement rules. Make sure every clause is represented.\n\n"
    prompt += json.dumps(structured_sections, indent=2)
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        return response.text
    except Exception as e:
        print(f"Error generating summary from Gemini: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy text file")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    args = parser.parse_args()

    # Determine paths to agents.md and skills.md based on script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    agents_path = os.path.join(script_dir, "agents.md")
    skills_path = os.path.join(script_dir, "skills.md")
    
    try:
        with open(agents_path, 'r', encoding='utf-8') as f:
            agents_text = f.read()
        with open(skills_path, 'r', encoding='utf-8') as f:
            skills_text = f.read()
    except Exception as e:
        print(f"Error reading configuration files: {e}")
        sys.exit(1)

    print(f"Retrieving and structuring policy clauses from {args.input}...")
    structured_sections = retrieve_policy(args.input)
    print(f"Successfully extracted {len(structured_sections)} clauses.")
    
    print("Summarizing policy using Gemini (requires GEMINI_API_KEY)...")
    summary = summarize_policy(structured_sections, agents_text, skills_text)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
        
    print(f"Summary successfully generated and saved to {args.output}")

if __name__ == "__main__":
    main()
