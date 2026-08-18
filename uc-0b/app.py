"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
from google import genai

def retrieve_policy(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    parser = argparse.ArgumentParser(description="Summarize HR policy document.")
    parser.add_argument("--input", required=True, help="Path to input policy document.")
    parser.add_argument("--output", required=True, help="Path to output summary document.")
    args = parser.parse_args()

    # Load agent instructions (RICE)
    agents_path = os.path.join(os.path.dirname(__file__), 'agents.md')
    with open(agents_path, 'r', encoding='utf-8') as f:
        system_instruction = f.read()

    policy_content = retrieve_policy(args.input)

    # Initialize Gemini client
    # By default, genai.Client() automatically looks for the GEMINI_API_KEY environment variable.
    # If you prefer to hardcode it, you can pass it here like: client = genai.Client(api_key="YOUR_API_KEY_HERE")
    client = genai.Client()

    prompt = f"""
Please summarize the following policy document. 
Ensure you map all clauses and preserve all conditions without dropping any approvers or constraints.

Policy Document:
{policy_content}
"""

    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.0
        )
    )

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(response.text)

    print(f"Summary written to {args.output}")

if __name__ == "__main__":
    main()
