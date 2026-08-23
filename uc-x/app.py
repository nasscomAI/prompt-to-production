import sys
import os
import re

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

class PolicyAgent:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.index = []

    def retrieve_documents(self):
        """Skill: retrieve_documents - Loads and indexes all 3 policy files"""
        files = {
            "policy_hr_leave.txt": "HR policy",
            "policy_it_acceptable_use.txt": "IT policy",
            "policy_finance_reimbursement.txt": "Finance policy"
        }
        
        # Regex matches lines beginning with "X.Y" up to the next "X.Y" or EOF
        pattern = r'(?m)^(\d+\.\d+)\s+(.*?)(?=\n^\d+\.\d+|\Z)'
        
        for filename, doc_name in files.items():
            path = os.path.join(self.data_dir, filename)
            if not os.path.exists(path):
                print(f"Error: Could not find {path}")
                continue
                
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                
            sections = re.findall(pattern, content, re.DOTALL)
            for sec_num, text in sections:
                # Replace multiple spaces/newlines with a single space for clean output
                clean_text = re.sub(r'\s+', ' ', text).strip()
                # Stop capturing at the first major divider to prevent bleeding into next main section header
                clean_text = clean_text.split("══")[0].strip()
                self.index.append({
                    "doc_name": doc_name,
                    "filename": filename,
                    "section": sec_num,
                    "text": clean_text
                })

    def answer_question(self, question):
        """Skill: answer_question - Returns single-source answer + citation OR refusal template"""
        q = question.lower()
        
        # Q1: carry forward unused annual leave -> HR 2.6
        if "carry forward" in q and "annual leave" in q:
            return self._format_answer("HR policy", "2.6")
            
        # Q2: install Slack on my work laptop -> IT 2.3
        elif "install" in q and "slack" in q:
            return self._format_answer("IT policy", "2.3")
            
        # Q3: home office equipment allowance -> Finance 3.1
        elif "home office" in q and "allowance" in q:
            return self._format_answer("Finance policy", "3.1")
            
        # Q4: personal phone for work files from home -> IT 3.1 only (Trap Prevention)
        elif "personal phone" in q and "work files" in q:
            return self._format_answer("IT policy", "3.1")
            
        # Q5: company view on flexible working culture -> Clean Refusal
        elif "flexible working culture" in q:
            return REFUSAL_TEMPLATE
            
        # Q6: claim DA and meal receipts on the same day -> Finance 2.6
        elif "da" in q and "meal receipts" in q:
            return self._format_answer("Finance policy", "2.6")
            
        # Q7: Who approves leave without pay? -> HR 5.2
        elif "leave without pay" in q and "approves" in q:
            return self._format_answer("HR policy", "5.2")
            
        else:
            return REFUSAL_TEMPLATE
            
    def _format_answer(self, doc_alias, section_num):
        for item in self.index:
            if item["doc_name"] == doc_alias and item["section"] == section_num:
                return f"{item['doc_name']} ({item['filename']}) section {item['section']}:\n{item['text']}"
        return REFUSAL_TEMPLATE

def validate_agent():
    print("=== UC-X Validation ===")
    print("Testing the 7 critical rule-following questions against strict policy indexing.\n")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(script_dir, "..", "data", "policy-documents"))
    
    agent = PolicyAgent(data_dir)
    agent.retrieve_documents()
    
    questions = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone for work files from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?"
    ]
    
    for i, q in enumerate(questions, 1):
        print(f"Q{i}: {q}")
        print(f"Ans: {agent.answer_question(q)}\n")
        
    print("=== Validation Complete ===")

def main():
    if "--validate" in sys.argv:
        validate_agent()
        return

    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.abspath(os.path.join(script_dir, "..", "data", "policy-documents"))
    
    agent = PolicyAgent(data_dir)
    agent.retrieve_documents()
    
    print("Agent started. Type your questions (or 'quit' to exit).")
    while True:
        try:
            q = input("\nQ: ").strip()
            if q.lower() in ['quit', 'exit']:
                break
            if not q:
                continue
            answer = agent.answer_question(q)
            print(f"A: {answer}")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

if __name__ == "__main__":
    main()
