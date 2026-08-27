"""
UC-0B app.py — Summarize HR policies.
"""
import argparse
import os
import pandas as pd

def read_policy(input_path: str) -> str:
    """Reads the policy document, using pandas if it's a CSV."""
    if input_path.lower().endswith('.csv'):
        df = pd.read_csv(input_path)
        # Convert the dataframe to a text representation for the LLM
        return df.to_string(index=False)
    else:
        with open(input_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
            return f.read()

def get_system_prompt() -> str:
    """Loads rules from agents.md to form the system instructions."""
    agents_path = os.path.join(os.path.dirname(__file__), 'agents.md')
    if os.path.exists(agents_path):
        with open(agents_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "You are a helpful HR policy summarizer."

def summarize_policy(policy_text: str, system_prompt: str) -> str:
    """
    Summarize the policy using an LLM.
    """
    # TODO: Integrate your specific AI tool / SDK here. 
    # Example using OpenAI:
    # from openai import OpenAI
    # client = OpenAI()
    # response = client.chat.completions.create(
    #     model="gpt-4o",
    #     messages=[
    #         {"role": "system", "content": system_prompt},
    #         {"role": "user", "content": f"Summarize the following policy document:\n\n{policy_text}"}
    #     ]
    # )
    # return response.choices[0].message.content
    
    print("\n[WARNING] LLM integration is not fully configured. Returning mock summary.\n")
    return f"MOCK SUMMARY:\n\nApplied Rules:\n{system_prompt}\n\nDRAFT SUMMARY GENERATED HERE."

def main():
    parser = argparse.ArgumentParser(description="Summarize HR policies using AI.")
    parser.add_argument("--input", required=True, help="Path to the input policy document (.txt or .csv)")
    parser.add_argument("--output", required=True, help="Path to save the summary")
    
    args = parser.parse_args()
    
    print(f"Reading input from {args.input}...")
    policy_text = read_policy(args.input)
    
    system_prompt = get_system_prompt()
    
    print("Generating summary...")
    summary = summarize_policy(policy_text, system_prompt)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
        
    print(f"Success! Summary saved to {args.output}")

if __name__ == "__main__":
    main()
