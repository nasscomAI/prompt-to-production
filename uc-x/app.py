"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os
import sys

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    try:
        from google import genai
    except ImportError:
        print("Error: google-genai library is not installed.", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    # Load documents
    docs = []
    base_dir = os.path.dirname(__file__)
    for filename in ["policy_hr_leave.txt", "policy_it_acceptable_use.txt", "policy_finance_reimbursement.txt"]:
        path = os.path.join(base_dir, "..", "data", "policy-documents", filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                docs.append(f"--- Document: {filename} ---\n{f.read()}")

    all_docs_text = "\n\n".join(docs)

    agents_md_path = os.path.join(base_dir, "agents.md")
    with open(agents_md_path, "r", encoding="utf-8") as f:
        agents_content = f.read()

    system_instruction = f"""
Please act as the agent defined by the following instructions and rules:
{agents_content}

Here are the policy documents:
{all_docs_text}
"""

    print("Policy QA Assistant (Type 'exit' to quit)")
    print("-" * 40)

    while True:
        try:
            question = input("Q: ")
            if question.strip().lower() in ["exit", "quit"]:
                break
        except (KeyboardInterrupt, EOFError):
            break

        prompt = f"{system_instruction}\n\nQuestion: {question}"

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        print(f"A: {response.text.strip()}\n")

if __name__ == "__main__":
    main()
