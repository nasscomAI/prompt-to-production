"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary_hr_leave.txt")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("Error: google-genai library is not installed. Please install it using 'pip install google-genai'.", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    with open(args.input, "r", encoding="utf-8") as f:
        policy_text = f.read()

    # Load agents.md to form the system instructions
    agents_md_path = os.path.join(os.path.dirname(__file__), "agents.md")
    with open(agents_md_path, "r", encoding="utf-8") as f:
        agents_content = f.read()

    prompt = f"""
Please act as the agent defined by the following instructions and rules:
{agents_content}

Here is the policy document to summarize:
{policy_text}
"""

    print("Generating summary...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(response.text)

    print(f"Done. Summary written to {args.output}")

if __name__ == "__main__":
    main()
