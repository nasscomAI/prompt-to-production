"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import json

def generate_summary(text):
    """
    Uses the CRAFT framework to ensure the LLM preserves nuance.
    """
    # C: Context - Customer Support Audit
    # R: Role - Senior Quality Auditor
    # A: Action - Summarize without losing meaning
    # F: Format - JSON
    # T: Target - The input text
    
    prompt = f"""
    Context: You are auditing customer support transcripts for accuracy.
    Role: Senior Quality Auditor.
    Task: Summarize the following transcript. 
    Constraint 1: Do not downplay the user's frustration or technical issues.
    Constraint 2: Do not invent facts not present in the text.
    Format: Return ONLY a JSON object with: "summary", "sentiment", and "preserved_entities".
    
    Transcript: "{text}"
    """
    
    # In a production environment, you would call your LLM here:
    # response = client.chat.completions.create(model="gpt-4", messages=[{"role": "user", "content": prompt}])
    
    # For the workshop/CLI demonstration:
    print(f"\n--- AI PROMPT GENERATED ---")
    print(prompt)
    
    # Mock output to demonstrate the expected JSON structure
    mock_response = {
        "summary": "User is unable to access the billing portal and expressed high frustration with the support delay.",
        "sentiment": "Negative",
        "preserved_entities": ["billing portal", "support delay"]
    }
    return json.dumps(mock_response, indent=2)

def main():
    parser = argparse.ArgumentParser(description="uc-0b: Meaning-Preserving Summarizer")
    parser.add_argument("--text", type=str, help="The transcript text to summarize", required=True)
    
    args = parser.parse_args()
    
    try:
        result = generate_summary(args.text)
        print("\n--- FINAL OUTPUT ---")
        print(result)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()