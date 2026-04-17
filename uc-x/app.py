import os
import re

class PolicyAgent:
    def __init__(self, agent_md_path):
        self.refusal_template = ""
        self.documents = {}
        self.load_config(agent_md_path)

    def load_config(self, path):
        if os.path.exists(path):
            with open(path, 'r') as f:
                content = f.read()
                # Extract the refusal template (Rule 3)
                match = re.search(r"Rule 3: Use the following Refusal Template exactly if a question is not covered: '(.*?)'", content, re.DOTALL)
                if match:
                    self.refusal_template = match.group(1).replace('\n', ' ')
        
    def index_documents(self, data_dir):
        files = [
            'policy_hr_leave.txt',
            'policy_it_acceptable_use.txt',
            'policy_finance_reimbursement.txt'
        ]
        print(f"[*] Indexing {len(files)} policy documents...")
        for filename in files:
            path = os.path.join(data_dir, filename)
            if os.path.exists(path):
                with open(path, 'r') as f:
                    content = f.read()
                    # Parse by sections like 2.3, 3.1, etc.
                    sections = re.findall(r'^(\d\.\d)\s+(.*?)(?=\n\d\.\d|\n═|\Z)', content, re.MULTILINE | re.DOTALL)
                    self.documents[filename] = {s[0]: s[1].strip().replace('\n    ', ' ') for s in sections}
        print("[+] Indexing complete.")

    def answer(self, question):
        q = question.lower()
        scored_answers = []

        # Simple semantic search (keyword matching)
        for doc_name, sections in self.documents.items():
            for section_id, text in sections.items():
                # Count matching words
                keywords = q.split()
                matches = sum(1 for word in keywords if word in text.lower() or word in section_id)
                if matches > 1: # Basic threshold
                    scored_answers.append({
                        "doc": doc_name,
                        "section": section_id,
                        "text": text,
                        "score": matches
                    })
        
        if not scored_answers:
            return self.refusal_template

        # Sort by best match
        scored_answers.sort(key=lambda x: x['score'], reverse=True)
        best = scored_answers[0]

        # ENFORCEMENT Rule 1: Single source only.
        # ENFORCEMENT Rule 4: Citation required.
        return f"{best['text']}\n\n[Source: {best['doc']}, Section {best['section']}]"

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "../data/policy-documents")
    agent_md = os.path.join(base_dir, "agents.md")

    agent = PolicyAgent(agent_md)
    agent.index_documents(data_dir)

    print("\n" + "="*50)
    print(" CMC POLICY ASSISTANT - INTERACTIVE CLI")
    print("="*50)
    print("Type your question and press Enter. Type 'exit' to quit.\n")

    while True:
        user_input = input("Question: ").strip()
        if user_input.lower() in ['exit', 'quit']:
            break
        
        if not user_input:
            continue

        response = agent.answer(user_input)
        print(f"\nAnswer:\n{response}\n")
        print("-" * 50)

if __name__ == "__main__":
    main()
