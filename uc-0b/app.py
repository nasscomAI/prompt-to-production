import argparse
import os
import time
from dotenv import load_dotenv
from groq import Groq

# Load API key from root .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

client = Groq(max_retries=3)

def retrieve_policy(file_path: str) -> str:
    """Skill: retrieve_policy - Loads policy file content."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found at: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def summarize_policy(policy_text: str) -> str:
    """Skill: summarize_policy - Generates strict, condition-preserving summary."""
    system_prompt = """You are an expert legal and HR policy compliance auditor.

YOUR TASK: Summarize the provided HR Leave Policy while strictly adhering to these rules:
1. Every numbered clause present in the input text MUST be represented in the summary.
2. Preserve all binding conditions, timelines, and multi-condition obligations exactingly (e.g., preserve specific approval roles like Department Head AND HR Director, 14-day notice, etc.).
3. Do NOT omit any conditions or soften obligations.
4. Do NOT add external assumptions or standard industry practices (no scope bleed).
5. If a clause cannot be summarized without risking loss of exact legal meaning, quote it verbatim and flag it.

Format the output clearly by clause number."""

    user_prompt = f"Summarize the following policy document according to all enforcement rules:\n\n{policy_text}"

    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",  # Replaces deprecated llama-3.3-70b-versatile
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return f"Error generating summary: {e}"

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to save summary text file")
    args = parser.parse_args()

    print(f"Loading policy file: {args.input}")
    policy_content = retrieve_policy(args.input)

    print("Generating summary via Groq API...")
    summary_result = summarize_policy(policy_content)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary_result)

    print(f"Summary successfully written to {args.output}")

if __name__ == "__main__":
    main()