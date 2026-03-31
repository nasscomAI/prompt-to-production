"""
UC-0B app.py

Built using the RICE + agents.md + skills.md + CRAFT workflow.
This script demonstrates the HR Policy Summarization agent.
"""

import argparse
import sys
import os

def retrieve_policy(file_path: str) -> str:
    """
    Skill: retrieve_policy
    Loads the .txt policy file and returns the content.
    """
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        sys.exit(1)
        
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def generate_agent_prompt(policy_content: str) -> str:
    """
    Compiles the prompt using rules from agents.md.
    """
    prompt = f"""You are the HR Policy Summarizer Agent.

Your Core Task: Produce a compliant summary of the provided policy document.

ENFORCEMENT RULES:
1. Every numbered clause must be present in the summary.
2. Multi-condition obligations must preserve ALL conditions — never drop one silently (e.g., if a clause requires approval from HR AND Department Head, you must explicitly mention both).
3. Never add information not present in the source document. Do not use generic phrases like "as is standard practice".
4. If a clause cannot be summarised without meaning loss — quote it verbatim and flag it.

POLICY CONTENT:
\"\"\"
{policy_content}
\"\"\"

Please generate the summary now based strictly on the above rules.
"""
    return prompt

def summarize_policy(structured_content: str) -> str:
    """
    Skill: summarize_policy
    Takes the structured policy content and simulates applying the agent rules.
    """
    prompt = generate_agent_prompt(structured_content)
    
    # ---------------------------------------------------------
    # In a fully integrated environment, you would invoke the AI
    # (e.g., openai.chat.completions.create or similar) here.
    # We return the generated prompt string as the simulated output
    # so you can see exactly how the RICE/CRAFT context is passed.
    # ---------------------------------------------------------
    
    simulated_output = (
         "=== AI PROMPT THAT WOULD BE SENT TO THE LLM ===\n" +
         prompt +
         "\n=== MOCK SUMMARY GENERATED ===\n" +
         "[Insert actual LLM integration here to process the prompt and return the summary.]"
    )
    return simulated_output

def main():
    parser = argparse.ArgumentParser(description="UC-0B: HR Leave Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write the compliant summary")
    args = parser.parse_args()

    print(f"Invoking retrieve_policy skill on: {args.input}")
    policy_content = retrieve_policy(args.input)
    
    print("Invoking summarize_policy skill...")
    summary_result = summarize_policy(policy_content)
    
    # Write the output file
    try:
        with open(args.output, "w", encoding="utf-8") as out_file:
            out_file.write(summary_result)
        print(f"Success! Output written to {args.output}")
    except Exception as e:
        print(f"Error writing to output file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
