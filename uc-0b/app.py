import os
import argparse
import json
from openai import OpenAI

def parse_args():
    parser = argparse.ArgumentParser(description="UC-0B: Policy Compliance Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to output summary_hr_leave.txt")
    return parser.parse_args()

def retrieve_policy(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input policy document not found at: {file_path}")
    with open(file_path, mode='r', encoding='utf-8') as f:
        content = f.read()
    return content

def summarize_policy(client, policy_content):
    system_prompt = """You are a high-stakes Corporate Governance & Compliance Auditor. 
Your task is to summarize the provided HR Leave Policy document.

You must strictly prevent these three failure modes:
1. Clause Omission: Every numbered obligation clause (specifically 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) must be accounted for.
2. Scope Bleed: Never add external text or context like "as is standard practice" or "typically in government organisations". Only use facts explicitly written.
3. Obligation Softening: Retain absolute binding metrics. Do not change "must", "will", or "requires" into "should" or "is expected to".

CRITICAL ACCURACY TRAP TO AVOID:
- Clause 5.2 requires approval from BOTH the Department Head AND the HR Director. You must include BOTH individual entities.

Format your response as a clean, markdown list where each item starts directly with the clause number (e.g., "- Clause X.X: [Summary]"). If any clause cannot be summarized without dropping a condition or softening its restriction, you MUST quote it verbatim instead."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Policy Document Content:\\n\\n{policy_content}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error executing compliance summarization LLM generation: {str(e)}"

def main():
    args = parse_args()
    client = OpenAI()

    print(f"Reading policy document from: {args.input}")
    policy_text = retrieve_policy(args.input)

    print("Generating compliance summary...")
    summary_result = summarize_policy(client, policy_text)

    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(args.output, mode='w', encoding='utf-8') as f:
        f.write(summary_result)

    print(f"Successfully wrote compliance-mapped summary to: {args.output}")

if __name__ == "__main__":
    main()
