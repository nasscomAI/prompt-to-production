"""
UC-0B app.py — Summary That Changes Meaning
"""
import argparse
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def retrieve_policy(filepath: str) -> str:
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def get_system_prompt() -> str:
    prompt = "You are a legal summarization agent.\n\n"
    agents_path = os.path.join(os.path.dirname(__file__), "agents.md")
    if os.path.exists(agents_path):
        with open(agents_path, "r", encoding="utf-8") as f:
            prompt += f.read()
    return prompt

def summarize_policy(policy_text: str) -> str:
    system_prompt = get_system_prompt()
    user_prompt = f"Please summarize the following policy strictly adhering to your enforcement rules:\n\n{policy_text}"
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0
    )
    return response.choices[0].message.content

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy text file")
    parser.add_argument("--output", required=True, help="Path to output summary text file")
    args = parser.parse_args()

    print(f"Reading policy from {args.input}...")
    policy_text = retrieve_policy(args.input)
    
    print("Summarizing policy...")
    summary = summarize_policy(policy_text)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"Summary written to {args.output}")

if __name__ == "__main__":
    main()
