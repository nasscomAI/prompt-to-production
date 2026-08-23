"""
UC-0B — Summary That Changes Meaning
Implementation utilizing google-genai SDK to summarize employee leave policies.
"""
import os
import argparse
from dotenv import load_dotenv

# Lazy load client helper to prevent immediate crash on import if API key is missing
_client = None

def get_client():
    """
    Initialize and return the GenAI client.
    """
    global _client
    if _client is None:
        load_dotenv()
        from google import genai
        if not os.environ.get("GEMINI_API_KEY"):
            # Try loading from the root folder directory if not loaded
            load_dotenv(dotenv_path="../.env")
        if not os.environ.get("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it in your .env file.")
        _client = genai.Client()
    return _client


def retrieve_policy(input_path: str) -> str:
    """
    Skill: Loads policy text file and parses it into structured sections.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input policy file not found at: {input_path}")
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    if not content:
        raise ValueError("Input policy file is empty.")
    return content


def summarize_policy(policy_content: str) -> str:
    """
    Skill: Uses Gemini model to generate a strict summary of the policy document.
    """
    # Prompt guided by RICE enforcement rules in agents.md
    prompt = f"""
    You are an HR Policy Summarizer agent. 
    Analyze the following employee leave policy and generate a comprehensive summary.
    
    CRITICAL ENFORCEMENT RULES:
    1. Every one of the following 10 clauses must be explicitly present in the summary:
       - Clause 2.3: 14-day advance notice required
       - Clause 2.4: Written approval required before leave commences. Verbal not valid.
       - Clause 2.5: Unapproved absence = LOP regardless of subsequent approval.
       - Clause 2.6: Max 5 days carry-forward. Above 5 forfeited on 31 Dec.
       - Clause 2.7: Carry-forward days must be used Jan–Mar or forfeited.
       - Clause 3.2: 3+ consecutive sick days requires medical cert within 48hrs.
       - Clause 3.4: Sick leave before/after holiday requires cert regardless of duration.
       - Clause 5.2: LWP requires approval from BOTH Department Head AND HR Director.
       - Clause 5.3: LWP >30 days requires Municipal Commissioner approval.
       - Clause 7.2: Leave encashment during service not permitted under any circumstances.
    
    2. Multi-condition obligations must preserve ALL conditions. Never drop conditions (e.g., Clause 5.2 requires approval from both Department Head and HR Director).
    3. Never add any information not present in the source document (no scope bleed or industry generalizations).
    4. If a clause cannot be summarized without losing meaning, quote it verbatim and add a [VERBATIM] flag next to it.
    
    Policy Document:
    \"\"\"
    {policy_content}
    \"\"\"
    """
    
    try:
        client = get_client()
        from google.genai import types
        
        # Using gemini-3.1-flash-lite as standard
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0
            )
        )
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        # Return fallback summary with flagged clauses as per error handling spec
        return (
            "ERROR: API call failed during summary generation. Fallback summary active.\n"
            "Critical Clauses demanding manual review:\n"
            "- Clause 2.3 (Notice)\n- Clause 2.4 (Approval)\n- Clause 2.5 (LOP)\n"
            "- Clause 2.6 (Carry-forward)\n- Clause 2.7 (Use by Q1)\n"
            "- Clause 3.2 (Sick leave cert)\n- Clause 3.4 (Sick leave adj)\n"
            "- Clause 5.2 (LWP approval: Dept Head + HR Director)\n"
            "- Clause 5.3 (LWP >30 days: Commissioner)\n"
            "- Clause 7.2 (No in-service encashment)\n"
        )


def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy text file")
    parser.add_argument("--output", required=True, help="Path to write summary text file")
    args = parser.parse_args()
    
    print(f"Retrieving policy from: {args.input}")
    try:
        policy_content = retrieve_policy(args.input)
    except Exception as e:
        print(f"Error retrieving policy: {e}")
        return
        
    print("Summarizing policy...")
    summary = summarize_policy(policy_content)
    
    print(f"Writing summary to: {args.output}")
    # Ensure parent directories exist
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
    print("Completed successfully!")


if __name__ == "__main__":
    main()
