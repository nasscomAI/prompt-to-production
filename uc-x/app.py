"""
UC-X app.py — Strict Policy Q&A Assistant.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import os
import sys
import argparse
import google.generativeai as genai

def load_file(filepath):
    """Utility to load a file safely."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"[Error: {filepath} not found]"

def load_context():
    """Loads agents.md, skills.md, and policy documents."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    agents_md = load_file(os.path.join(base_dir, 'agents.md'))
    skills_md = load_file(os.path.join(base_dir, 'skills.md'))
    
    # Load policy docs
    docs_dir = os.path.join(base_dir, '..', 'data', 'policy-documents')
    hr_doc = load_file(os.path.join(docs_dir, 'policy_hr_leave.txt'))
    it_doc = load_file(os.path.join(docs_dir, 'policy_it_acceptable_use.txt'))
    finance_doc = load_file(os.path.join(docs_dir, 'policy_finance_reimbursement.txt'))
    
    policies = f"""
    --- POLICY 1: policy_hr_leave.txt ---
    {hr_doc}
    --- POLICY 2: policy_it_acceptable_use.txt ---
    {it_doc}
    --- POLICY 3: policy_finance_reimbursement.txt ---
    {finance_doc}
    """
    
    return agents_md, skills_md, policies

def build_system_prompt(agents_md, skills_md):
    """Constructs the RICE / CRAFT system prompt."""
    return f"""You are a specialized enterprise AI agent. You must strictly adhere to the following configuration:

### AGENT PROFILE (agents.md)
{agents_md}

### CAPABILITIES & ERROR HANDLING (skills.md)
{skills_md}

Remember the rigorous RICE enforcement and the Refusal conditions!
"""

def main():
    parser = argparse.ArgumentParser(description="Strict Policy Q&A Assistant")
    parser.add_argument("--query", "-q", type=str, help="Directly provide a question to answer")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
         # Optionally set it here for local testing, otherwise ask the user to export it
         print("Warning: GEMINI_API_KEY environment variable is not set.")
         print("Please set it before running this script: `export GEMINI_API_KEY=your_key`")
         print("Alternatively, define it dynamically in your environment.")
         # We'll allow the app to initialize but it will fail on query.
    
    try:
        genai.configure(api_key=api_key)
        # Using gemini-2.5-flash or flash depending on preference. Defaulting to pro for strict instruction following.
        model = genai.GenerativeModel('gemini-2.5-flash')
    except Exception as e:
        print(f"Failed to initialize Gemini: {e}")
        sys.exit(1)

    print("Loading policies and agent rules...")
    agents_md, skills_md, policies = load_context()
    
    system_prompt = build_system_prompt(agents_md, skills_md)
    
    # We prepend the system prompt and policies to the conversation, 
    # but the recommended approach with generative ai is using the `system_instruction` param
    try:
        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt)
    except TypeError:
         # Fallback for older google-generativeai SDKs where system_instruction wasn't directly passed to constructor
         pass

    print("Agent initialized. You can explore the policies.")
    
    def ask_question(question):
        # Build prompt: context + question
        prompt = f"""
Here are the policy documents you must use to answer the question:
{policies}

USER QUESTION:
{question}
"""
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error querying LLM: {e}"

    if args.query:
        print(f"\nQUERY: {args.query}\n")
        print("ANSWER:")
        print(ask_question(args.query))
    else:
        while True:
            try:
                question = input("\nAsk a policy question (or type 'quit' to exit): ")
                if question.strip().lower() in ['quit', 'exit']:
                    break
                if not question.strip():
                    continue
                print("\nThinking...")
                print(ask_question(question))
            except KeyboardInterrupt:
                break
            except EOFError:
                break

if __name__ == "__main__":
    main()
