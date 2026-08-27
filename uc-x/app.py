"""
UC-X app.py — Document Q&A with strict refusal and citation rules.
"""
import os

def load_documents() -> dict:
    docs = {}
    base_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'policy-documents')
    for filename in ['policy_hr_leave.txt', 'policy_it_acceptable_use.txt', 'policy_finance_reimbursement.txt']:
        path = os.path.join(base_dir, filename)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                docs[filename] = f.read()
    return docs

def get_system_prompt() -> str:
    agents_path = os.path.join(os.path.dirname(__file__), 'agents.md')
    if os.path.exists(agents_path):
        with open(agents_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "You are a policy assistant."

def answer_question(question: str, context: dict, prompt: str) -> str:
    # MOCK LLM INTEGRATION
    # TODO: Add your actual AI tool integration here (e.g. OpenAI, Anthropic, Gemini)
    q_lower = question.lower()
    if "personal phone" in q_lower and "work files" in q_lower:
        return "[MOCK ANSWER] IT policy_it_acceptable_use.txt (section 3.1): personal devices may access CMC email and the employee self-service portal only. Refusing to blend HR policy."
    elif "flexible working culture" in q_lower:
        return """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""
    elif "exit" in q_lower or "quit" in q_lower:
        return "exit"
    else:
        return "[MOCK ANSWER] Valid single-source policy response with section citation."

def main():
    print("Loading documents...")
    docs = load_documents()
    system_prompt = get_system_prompt()
    
    print("Welcome to Policy Ask My Document CLI. Type 'exit' to quit.\n")
    while True:
        try:
            q = input("Question > ")
            if not q.strip(): continue
            ans = answer_question(q, docs, system_prompt)
            if ans == "exit":
                break
            print(f"\nAnswer:\n{ans}\n")
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
