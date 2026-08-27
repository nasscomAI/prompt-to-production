"""
UC-X app.py — Implemented using RICE + agents.md + skills.md + CRAFT workflow.
"""
import os
import sys

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: google-genai package is not installed. Please run: pip install google-genai")
    sys.exit(1)

def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Could not find {filepath}")
        sys.exit(1)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load agent and skills configurations
    agents_md = read_file(os.path.join(script_dir, "agents.md"))
    skills_md = read_file(os.path.join(script_dir, "skills.md"))
    
    # Load documents
    data_dir = os.path.join(os.path.dirname(script_dir), "data", "policy-documents")
    docs = {
        "policy_hr_leave.txt": read_file(os.path.join(data_dir, "policy_hr_leave.txt")),
        "policy_it_acceptable_use.txt": read_file(os.path.join(data_dir, "policy_it_acceptable_use.txt")),
        "policy_finance_reimbursement.txt": read_file(os.path.join(data_dir, "policy_finance_reimbursement.txt"))
    }
    
    # Prepare document text
    doc_text = "\n\n".join([f"--- DOCUMENT: {name} ---\n{content}" for name, content in docs.items()])

    system_prompt = f"""You are executing an internal corporate policy Q&A task based on strict operational parameters.

# AGENT CONFIGURATION
{agents_md}

# SKILLS CONFIGURATION
{skills_md}

INSTRUCTIONS:
Using the skills defined above, answer the user's question based strictly on the provided documents.
You MUST strictly adhere to all enforcement rules and trap avoidance constraints specified in the AGENT CONFIGURATION.
Do NOT use external knowledge. 
If the question requires blending documents or the answer isn't explicitly found, output the EXACT refusal template.

# INDEXED DOCUMENTS
{doc_text}
"""
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        print("Please set it before running the script: set GEMINI_API_KEY=your_key")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    
    print("="*60)
    print("Ask My Documents - Corporate Policy Q&A")
    print("Type 'exit' or 'quit' to stop.")
    print("="*60)
    
    while True:
        try:
            question = input("\nYour Question: ").strip()
            if not question:
                continue
            if question.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
                
            print("\nSearching documents...")
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"User Question: {question}",
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.0, # 0.0 for maximum determinism and strict rule following
                )
            )
            print("-" * 60)
            print(response.text.strip())
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"API Error during generation: {e}")

if __name__ == "__main__":
    main()
