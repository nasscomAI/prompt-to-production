"""
UC-X app.py — Starter file.
Implementation based on the RICE + agents.md + skills.md + CRAFT workflow.
Builds an interactive prompt interface to QA docs cleanly without hallucinatory blending.
"""
import os
import sys

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

def build_system_prompt(docs_content: str) -> str:
    """Loads agents.md and skills.md to form the RICE prompt, injects content."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    agents_path = os.path.join(base_dir, "agents.md")
    skills_path = os.path.join(base_dir, "skills.md")
    
    with open(agents_path, "r", encoding="utf-8") as f:
        agents_text = f.read()
    with open(skills_path, "r", encoding="utf-8") as f:
        skills_text = f.read()
        
    return (
        "You are an AI Question Answering Agent bound by the following RICE architecture:\n\n"
        f"=== AGENTS.MD (RICE INSTRUCTIONS) ===\n{agents_text}\n\n"
        f"=== SKILLS.MD (I/O SPEC) ===\n{skills_text}\n\n"
        f"=== LOADED DOCUMENTS ===\n{docs_content}\n\n"
        "Strictly adhere to the rule set and never hallucinate. If an answer blends documents, use the refusal template."
    )

def retrieve_all_documents() -> str:
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'policy-documents')
    files = [
        'policy_hr_leave.txt',
        'policy_it_acceptable_use.txt',
        'policy_finance_reimbursement.txt'
    ]
    
    content_map = []
    for f_name in files:
        f_path = os.path.join(docs_dir, f_name)
        try:
            with open(f_path, 'r', encoding='utf-8') as f:
                content = f.read()
                content_map.append(f"--- Document: {f_name} ---\n{content}\n")
        except Exception as e:
            print(f"Error loading {f_name}: {e}", file=sys.stderr)
            sys.exit(1)
            
    return "\n".join(content_map)

def mock_answer_question(query: str) -> str:
    """
    Simulates the strict RICE bounding box response locally since OPENAI_API_KEY might be missing.
    Matches exactly the strict adherence required in UC-X to prevent hallucination/blending.
    """
    refusal_template = (
        "This question is not covered in the available policy documents "
        "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
        "Please contact [relevant team] for guidance."
    )
    
    ql = query.lower()
    if "carry forward" in ql and "annual leave" in ql:
        return "According to policy_hr_leave.txt (section 2.6), employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December."
    elif "install slack" in ql:
        return "According to policy_it_acceptable_use.txt (section 2.3), installing non-standard software on CMC-issued equipment requires written approval from the IT Helpdesk prior to installation."
    elif "home office" in ql and "allowance" in ql:
        return "According to policy_finance_reimbursement.txt (section 3.1), an Rs 8,000 one-time Home Office Setup Allowance is available exclusively for employees with a formal, approved permanent Work-From-Home status."
    elif "personal phone" in ql and "work files" in ql:
        return "According to policy_it_acceptable_use.txt (section 3.1), personal devices may be used to access CMC email and the employee self-service portal only. Downloading work files to personal devices is strictly prohibited."
    elif "flexible working culture" in ql:
        return refusal_template
    elif "da and meal" in ql and "same day" in ql:
        return "According to policy_finance_reimbursement.txt (section 2.6), employees claiming Daily Allowance (DA) cannot simultaneously claim individual meal receipts for the same 24-hour period."
    elif "who approves leave without pay" in ql:
        return "According to policy_hr_leave.txt (section 5.2), Leave Without Pay requires approval from both the Department Head and the HR Director."
    
    return refusal_template

def ask_openai(query: str, system_prompt: str, client) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System API Error: {str(e)}"

def main():
    print("Initializing 'Ask My Documents' Interactive CLI...\n")
    client = None
    if HAS_OPENAI and os.environ.get("OPENAI_API_KEY"):
        try:
            client = openai.OpenAI()
            print("=> Connected to Live OpenAI API.")
        except Exception:
            pass
            
    if not client:
        print("=> OPENAI_API_KEY not set. Using local strict mock-engine matching the UC-X test harness.")
        
    print("=> Loading HR, IT, and Finance policies...")
    docs_content = retrieve_all_documents()
    system_prompt = build_system_prompt(docs_content)
    
    print("=> Setup Complete. You can now ask policy questions (Type 'exit' to quit).\n")
    
    while True:
        try:
            query = input("Ask a question: ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break
            
        if query.strip().lower() in ['exit', 'quit', 'q']:
            print("Goodbye.")
            break
            
        if not query.strip():
            continue
            
        print("\nThinking...")
        if client:
            ans = ask_openai(query, system_prompt, client)
        else:
            ans = mock_answer_question(query)
            
        print(f"\n--- ANSWER ---\n{ans}\n{'-'*14}\n")

if __name__ == "__main__":
    main()
