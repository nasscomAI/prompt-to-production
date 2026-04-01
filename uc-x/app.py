"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os

def ask_my_documents(query):
    policy_dir = "../data/policy-documents/"
    files = [f for f in os.listdir(policy_dir) if f.endswith('.txt')]
    
    found_info = []
    
    # Simple Keyword Search Logic
    for filename in files:
        with open(os.path.join(policy_dir, filename), 'r', encoding='utf-8') as f:
            content = f.read()
            if query.lower() in content.lower():
                # Extract a small snippet around the keyword
                start = max(0, content.lower().find(query.lower()) - 50)
                snippet = content[start:start+200].replace('\n', ' ')
                found_info.append(f"Source: {filename}\nExcerpt: ...{snippet}...")

    if not found_info:
        return "I'm sorry, I couldn't find any information regarding that in our current policies."
    
    return "\n\n".join(found_info)

if __name__ == "__main__":
    # Test Question
    user_query = "leave" 
    print(f"Question: How do I apply for {user_query}?")
    print("-" * 30)
    print(ask_my_documents(user_query))