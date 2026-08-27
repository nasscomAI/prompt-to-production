import os
import argparse
from google import genai
from google.genai import types

# 1. Initialize the modern GenAI Client
# It will automatically look for the GEMINI_API_KEY environment variable.
client = genai.Client()

def generate_compliance_summary(policy_text, system_instruction):
    """
    Generates a strict compliance summary using Google Gemini 2.5 Flash,
    adhering strictly to system rules at zero temperature.
    """
    try:
        # 2. Package configuration and system instructions
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.0  # Zero temperature for absolute audit accuracy
        )
        
        # 3. Request generation from Gemini
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=policy_text,
            config=config
        )
        
        return response.text
        
    except Exception as e:
        print(f"Error executing compliance summarization Gemini generation: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Compliance Summarizer via Gemini")
    parser.add_argument("--input", required=True, help="Path to input policy document txt file")
    parser.add_argument("--output", required=True, help="Path to save output summary markdown/txt file")
    args = parser.parse_args()

    # Read the policy document
    print(f"Reading policy document from: {args.input}")
    with open(args.input, "r", encoding="utf-8") as f:
        policy_text = f.read()

    # Read your strict system guardrails (skills.md context)
    system_instruction = (
        "You are an absolute compliance auditor. Summarize the policy text into exactly 10 points. "
        "Rule 1: NEVER omit complex conditional logic or multi-condition approvers (e.g., maintain 'AND/OR' constraints). "
        "Rule 2: NEVER soften mandatory actions; verbatim retain terms like 'shall', 'must', and 'required'. "
        "Rule 3: Avoid scope bleed; do NOT invent or assume industry standard practices outside the text."
    )

    print("Generating compliance summary via Gemini...")
    summary_output = generate_compliance_summary(policy_text, system_instruction)

    if summary_output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary_output)
        print(f"Successfully wrote compliance-mapped summary to: {args.output}")
    else:
        print("Failed to generate summary.")

if __name__ == "__main__":
    main()