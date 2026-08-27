import argparse
import os
from dotenv import load_dotenv
import google.genai as genai
import google.genai.types as types

load_dotenv()  # loads GEMINI_API_KEY from .env file if present

def get_agent_instructions() -> str:
    """Reads the agents.md file to get the R.I.C.E template instructions dynamically."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    agents_path = os.path.join(script_dir, "agents.md")
    
    if not os.path.exists(agents_path):
        raise FileNotFoundError(f"Missing agents.md definition at {agents_path}")
        
    with open(agents_path, 'r', encoding='utf-8') as f:
        return f.read()

def retrieve_policy(file_path: str) -> str:
    """Loads a .txt policy file and returns its content as a string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise RuntimeError(f"Failed to read policy file: {e}")

def summarize_policy(client, policy_content: str, agent_instructions: str) -> str:
    """Takes structured sections and produces a compliant summary based on agents.md."""
    
    # We use the raw text from agents.md as the System Instruction to enforce compliance
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=f"Policy Document Content:\n{policy_content}",
        config=types.GenerateContentConfig(
            system_instruction=agent_instructions,
            temperature=0.0, # temperature 0 is best for strictly adhering to rules without hallucination
        )
    )
    return response.text

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input",  default="../data/policy-documents/policy_hr_leave.txt", help="Path to policy document (.txt)")
    parser.add_argument("--output", default="summary_hr_leave.txt", help="Path to write the summary (.txt)")
    args = parser.parse_args()

    # Check for GEMINI_API_KEY
    if "GEMINI_API_KEY" not in os.environ:
        print("Error: GEMINI_API_KEY environment variable is not set.")
        print("Get your API key from Google AI Studio and set it to run this script.")
        return

    client = genai.Client()

    try:
        print(f"Loading rules from agents.md...")
        agent_instructions = get_agent_instructions()
        
        print(f"Retrieving policy from {args.input}...")
        policy_content = retrieve_policy(args.input)
        
        print("Summarizing policy (this may take a moment)...")
        summary = summarize_policy(client, policy_content, agent_instructions)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Done. Compliant summary written to {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
