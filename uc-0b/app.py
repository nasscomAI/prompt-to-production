"""
UC-0B app.py — Implemented using RICE + agents.md + skills.md + CRAFT workflow.
"""
import argparse
import os
import sys

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: google-genai package is not installed. Please run: pip install google-genai")
    sys.exit(1)

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    parser = argparse.ArgumentParser(description="HR Policy Summarizer (Agentic Workflow)")
    parser.add_argument("--input", required=True, help="Input policy document (.txt)")
    parser.add_argument("--output", required=True, help="Output summary file (.txt)")
    args = parser.parse_args()

    # Load agent and skills configurations
    script_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        agents_md = read_file(os.path.join(script_dir, "agents.md"))
        skills_md = read_file(os.path.join(script_dir, "skills.md"))
        input_text = read_file(args.input)
    except FileNotFoundError as e:
        print(f"Error loading required files: {e}")
        sys.exit(1)

    system_prompt = f"""You are executing a summarization task based on strict operational parameters.

# AGENT CONFIGURATION
{agents_md}

# SKILLS CONFIGURATION
{skills_md}

INSTRUCTIONS:
Using the skills defined above, process the provided document and generate a highly accurate, compliant summary. 
You MUST strictly adhere to all enforcement rules and trap avoidance constraints specified in the AGENT CONFIGURATION.
Do NOT output anything except the final summary.
"""
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        print("Please set it before running the script: set GEMINI_API_KEY=your_new_key")
        sys.exit(1)

    # Use the new Google GenAI SDK
    client = genai.Client(api_key=api_key)
    
    print(f"Processing document: {args.input}...")
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Document Content to Process:\n\n{input_text}",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1, # Low temperature for more deterministic/strict adherence
            )
        )
    except Exception as e:
        print(f"API Error during generation: {e}")
        sys.exit(1)

    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(response.text)

    print(f"Success! Compliant summary generated and saved to: {args.output}")

if __name__ == "__main__":
    main()
