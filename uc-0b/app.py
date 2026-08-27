"""
UC-0B app.py — Policy Summarizer App.
Built using the RICE + agents.md + skills.md workflow.
"""
import argparse
import os
import re
import json

def retrieve_policy(filepath: str) -> list:
    """
    Skill: Loads a .txt policy file and returns the content as structured numbered sections.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find clauses starting with numbers like "2.3"
    pattern = r'(?m)^(\d+\.\d+)\s+([^\n]+(?:\n(?!\d+\.\d+\s+|════)[^\n]+)*)'
    matches = re.findall(pattern, content)
    
    if not matches:
        raise ValueError(f"Could not parse file into structured sections. Clause format not recognized in: {filepath}")

    structured_sections = []
    for num, text in matches:
        # Clean up whitespace and newlines for cleaner structured data
        clean_text = ' '.join(text.split())
        structured_sections.append({
            "clause": num,
            "text": clean_text
        })
        
    return structured_sections

def summarize_policy(sections: list) -> str:
    """
    Skill: Takes structured sections and produces a compliant summary with clause references 
    using an LLM, strictly bound by the agent enforcement rules.
    """
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        raise ImportError("Please install the 'google-genai' package (`pip install google-genai`) to run the AI skill.")

    # Initialize client (requires GEMINI_API_KEY environment variable)
    client = genai.Client()
    
    # Load the agent constraint profile
    agent_path = os.path.join(os.path.dirname(__file__), 'agents.md')
    agent_config = ""
    if os.path.exists(agent_path):
        with open(agent_path, 'r', encoding='utf-8') as f:
             agent_config = f.read()
             
    prompt = f"""
    AGENT CONFIGURATION:
    ```
    {agent_config}
    ```
    
    TASK: 
    Perform the `summarize_policy` skill. Read the following structured policy clauses and generate a high-quality summary.
    Ensure that every multi-condition obligation is preserved natively, no unauthorized info is added, and every exact clause is reflected.
    If any clause cannot be summarized without losing strict conditional meaning, quote the clause verbatim and flag it explicitly.
    Include explicit clause reference tags (e.g. [Clause 2.3]) in your summary.
    
    STRUCTURED POLICY DATA:
    ```json
    {json.dumps(sections, indent=2)}
    ```
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1 # Low temp for deterministic adherence to policies
        )
    )
    return response.text

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy document (.txt)")
    parser.add_argument("--output", required=True, help="Path to output summary document (.txt)")
    args = parser.parse_args()

    print(f"Retrieving and structuring policy from: {args.input}")
    try:
        sections = retrieve_policy(args.input)
        print(f"Successfully extracted {len(sections)} binding clauses.")
    except Exception as e:
        print(f"Error in retrieve_policy skill: {e}")
        return

    print("Executing summarize_policy AI skill...")
    try:
        summary = summarize_policy(sections)
    except Exception as e:
        print(f"Error in summarize_policy skill: {e}")
        print("Tip: Ensure 'google-genai' is installed and 'GEMINI_API_KEY' is fully loaded in your terminal.")
        return

    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Success! Summary written to: {args.output}")
    except Exception as e:
        print(f"Error writing to output file: {e}")

if __name__ == "__main__":
    main()
