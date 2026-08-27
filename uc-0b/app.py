"""
UC-0B app.py
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import time

try:
    import google.generativeai as genai
except ImportError:
    print("Warning: google-generativeai is not installed. Run `pip install google-generativeai`")
    genai = None

def get_model():
    if not genai:
        raise RuntimeError("google-generativeai is required.")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY environment variable not set.")
        
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-pro')

def summarize_policy(input_path: str, output_path: str):
    """
    Read policy text, prompt Gemini with agents/skills constraints, and output summary.
    """
    print(f"Reading policy from {input_path}...")
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            policy_text = f.read()
    except Exception as e:
        print(f"Failed to read file: {e}")
        return

    try:
        model = get_model()
    except Exception as e:
        print(f"Failed to initialize model: {e}")
        return

    # Incorporating constraints from agents.md and skills.md
    prompt = f"""
ROLE:
Policy Summarization Agent. The agent's operational boundary is strictly to read the provided HR leave policy document and output a comprehensive summary of its clauses without altering their meaning, softening obligations, or bleeding scope.

INTENT:
The output is a verified summary where every numbered clause from the source text is present. Multi-condition obligations must preserve all conditions exactly as stated (e.g., requiring both Department Head AND HR Director approval), without any omissions.

CONTEXT:
The agent is entirely restricted to the information present in the source document. It is explicitly excluded from using outside knowledge, adding external context, interpolating "standard practices", or making assumptions typically found in other organizations.

ENFORCEMENT RULES:
1. Every numbered clause must be present in the summary.
2. Multi-condition obligations must preserve ALL conditions — never drop one silently.
3. Never add information not present in the source document.
4. If a clause cannot be summarised without meaning loss — quote it verbatim and flag it.

SKILLS TO APPLY:
- retrieve_policy: Load the text and structure it into numbered sections.
- summarize_policy: Produce a compliant summary with accurate clause references intact. If a clause is ambiguous or cannot be summarized without meaning loss, quote it verbatim and flag it in the output.

POLICY TEXT TO SUMMARIZE:
\"\"\"
{policy_text}
\"\"\"
"""

    print("Generating summary...")
    retries = 3
    summary_text = ""
    
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            summary_text = response.text
            break
        except Exception as e:
            if attempt == retries - 1:
                print(f"Error generating summary: {e}")
                return
            time.sleep(2)

    # Write output to file
    print(f"Writing summary to {output_path}...")
    try:
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary_text)
    except Exception as e:
        print(f"Failed to write output: {e}")

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy text file")
    parser.add_argument("--output", required=True, help="Path to write output summary")
    args = parser.parse_args()
    
    summarize_policy(args.input, args.output)
    print("Done.")

if __name__ == "__main__":
    main()
