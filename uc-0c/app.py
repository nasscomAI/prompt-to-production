"""
UC-0C app.py — Implemented using RICE + agents.md + skills.md + CRAFT workflow.
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
    parser = argparse.ArgumentParser(description="Municipal Budget Growth Analyzer (Agentic Workflow)")
    parser.add_argument("--input", required=True, help="Input budget document (.csv)")
    parser.add_argument("--ward", required=False, help="Ward name")
    parser.add_argument("--category", required=False, help="Budget category")
    parser.add_argument("--growth-type", required=False, help="Type of growth (e.g., MoM, YoY)")
    parser.add_argument("--output", required=True, help="Output summary file (.csv)")
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

    system_prompt = f"""You are executing a financial data analysis task based on strict operational parameters.

# AGENT CONFIGURATION
{agents_md}

# SKILLS CONFIGURATION
{skills_md}

INSTRUCTIONS:
Using the skills defined above, process the provided dataset and generate a highly accurate table of computed growth. 
You MUST strictly adhere to all enforcement rules and trap avoidance constraints specified in the AGENT CONFIGURATION.
Do NOT output anything except the final CSV table or your refusal message if rules are broken.

USER REQUESTED PARAMETERS:
- Ward: {args.ward if args.ward else 'NOT SPECIFIED'}
- Category: {args.category if args.category else 'NOT SPECIFIED'}
- Growth Type: {args.growth_type if args.growth_type else 'NOT SPECIFIED'}
"""
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        print("Please set it before running the script: set GEMINI_API_KEY=your_key")
        sys.exit(1)

    # Use the new Google GenAI SDK
    client = genai.Client(api_key=api_key)
    
    print(f"Processing document: {args.input}...")
    try:
        # Use gemini-2.5-flash which is widely supported and handles tabular data well
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Dataset to Process (CSV format):\n\n{input_text}",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1, # Low temperature for more deterministic/strict adherence to constraints
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

    print(f"Success! Output generated and saved to: {args.output}")

if __name__ == "__main__":
    main()
