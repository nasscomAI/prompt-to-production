"""
UC-0B app.py — HR Policy Summarizer.
Uses role and rules from agents.md to ensure compliance.
"""
import argparse
import os
import google.generativeai as genai

def retrieve_policy(file_path):
    """Skill: Loads .txt policy file and returns content."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def summarize_policy(policy_text, agents_content):
    """Skill: Summarizes policy using agent rules."""
    # Note: In a real environment, you'd configure the API key here
    # genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel("gemini-pro")
    
    prompt = f"""
{agents_content}

Strictly follow the role, intent, and enforcement rules above to summarize the following HR policy document.

Policy Document:
{policy_text}

Summary:
"""
    response = model.generate_content(prompt)
    return response.text

def main():
    parser = argparse.ArgumentParser(description="HR Policy Summarizer (UC-0B)")
    parser.add_argument("--input", required=True, help="Path to input .txt policy file")
    parser.add_argument("--output", required=True, help="Path to save the summary .txt file")
    args = parser.parse_args()

    # Load agent definitions
    with open("agents.md", "r", encoding="utf-8") as f:
        agents_content = f.read()

    try:
        policy_text = retrieve_policy(args.input)
        # For the purpose of this demonstration/task, we'll simulate the call 
        # or use the provided environment if configured.
        summary = summarize_policy(policy_text, agents_content)
        
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"Summary written to {args.output}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
