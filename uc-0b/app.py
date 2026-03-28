"""
UC-0B app.py — Built using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import sys

# Attempt to import the new google genai SDK
try:
    from google import genai
except ImportError:
    print("Error: The 'google-genai' package is not installed.")
    print("Please install it running: pip install google-genai")
    sys.exit(1)

def retrieve_policy(input_path: str) -> str:
    """Skill 1: Read the policy file and return the content."""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {input_path}: {e}")
        sys.exit(1)

def build_prompt(policy_text: str) -> str:
    """Constructs the prompt utilizing the RICE principles defined in agents.md."""
    # RICE definitions loaded from agents.md
    role = "You are an expert HR Policy Summarizer. Your goal is to distill policy documents into clear summaries while strictly preserving their legal and operational integrity."
    
    intent = "Produce a concise, faithful summary of the provided text that explicitly includes all relevant clauses. The output must maintain every condition without summarizing away structural requirements (e.g., dual-approval workflows)."
    
    context = "You must rely strictly and solely on the provided text file content. You must NOT include assumptions, generalized statements, or phrases not present in the text."
    
    enforcement = """
1. Every numbered clause must be present in the summary.
2. Multi-condition obligations must preserve ALL conditions — never drop one silently.
3. Never add information not present in the source document.
4. If a clause cannot be concisely summarized without meaning loss — quote it verbatim and flag it.
"""

    prompt = f"""
{role}

INTENT: 
{intent}

CONTEXT:
{context}

ENFORCEMENT RULES (CRITICAL):
{enforcement}

--- POLICY DOCUMENT BELOW ---
{policy_text}
--- END POLICY DOCUMENT ---

Now, generate the compliant summary according to the strict guidelines above:
"""
    return prompt

def summarize_policy(prompt: str) -> str:
    """Skill 2: Calls the AI to summarize the policy based on the strict enforcement rules."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is missing.")
        print("Please set it in your terminal. Example (Windows PowerShell):")
        print("$env:GEMINI_API_KEY='your-api-key'")
        sys.exit(1)
        
    client = genai.Client(api_key=api_key)
    
    # Using the standard model for reasoning tasks
    print("Sending strict RICE prompt to Gemini API... (this may take a moment)")
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    
    if response.text:
        return response.text
    else:
        print("Error: Empty response from AI.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write the summary output")
    args = parser.parse_args()

    # Step 1: Retrieve policy document
    print(f"Reading from {args.input}...")
    policy_text = retrieve_policy(args.input)
    
    # Step 2: Build strongly typed prompt based on RICE framework
    prompt = build_prompt(policy_text)
    
    # Step 3: Send to AI and acquire summary
    summary = summarize_policy(prompt)
    
    # Step 4: Write compliant summary
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Successfully generated compliant summary and saved to {args.output}")
    except Exception as e:
        print(f"Error writing out file to {args.output}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
