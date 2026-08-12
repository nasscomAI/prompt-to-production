"""
UC-X app.py — Ask My Documents
"""
import argparse
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

DOCS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]

def load_documents():
    content = ""
    base_dir = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
    for doc in DOCS:
        path = os.path.join(base_dir, doc)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content += f"--- {doc} ---\n"
                content += f.read()
                content += "\n\n"
    return content

def get_system_prompt() -> str:
    prompt = "You are a Policy Q&A Agent.\n\n"
    agents_path = os.path.join(os.path.dirname(__file__), "agents.md")
    if os.path.exists(agents_path):
        with open(agents_path, "r", encoding="utf-8") as f:
            prompt += f.read()
    return prompt

def answer_question(question: str, docs_content: str) -> str:
    system_prompt = get_system_prompt()
    user_prompt = f"Available Documents:\n{docs_content}\n\nQuestion: {question}"
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0
    )
    return response.choices[0].message.content

def run_tests(docs_content: str):
    tests = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone for work files from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?"
    ]
    for i, t in enumerate(tests, 1):
        print(f"\nQ{i}: {t}")
        ans = answer_question(t, docs_content)
        print(f"A: {ans}")

def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--test", action="store_true", help="Run 7 test questions automatically")
    args = parser.parse_args()

    print("Loading documents...")
    docs_content = load_documents()

    if args.test:
        run_tests(docs_content)
        return

    print("\nAsk My Documents (type 'exit' to quit)")
    while True:
        try:
            q = input("\nQ: ")
            if q.strip().lower() in ["exit", "quit"]:
                break
            if not q.strip():
                continue
            
            ans = answer_question(q, docs_content)
            print(f"A: {ans}")
        except KeyboardInterrupt:
            break
        except EOFError:
            break

if __name__ == "__main__":
    main()
