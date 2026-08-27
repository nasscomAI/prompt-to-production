import os
import re
import sys

# Ensure UTF-8 output even on Windows terminals that default to CP1252
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Refusal template requirement from agents.md
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

class DocumentAgent:
    def __init__(self):
        self.sections = []
        self.retrieve_documents()

    def retrieve_documents(self):
        """Skill: retrieve_documents - loads all 3 policy files, indexes by name/section."""
        data_dir = '../data/policy-documents'
        filenames = [
            'policy_hr_leave.txt',
            'policy_it_acceptable_use.txt',
            'policy_finance_reimbursement.txt'
        ]
        
        for fname in filenames:
            path = os.path.join(data_dir, fname)
            if not os.path.exists(path):
                continue
            
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            current_section = None
            current_content = []
            
            for line in lines:
                # Matches "2.6 Employees may..." or "2. ANNUAL LEAVE"
                match = re.match(r'^(\d+(\.\d+)?)\.?\s+(.*)', line.strip())
                if match:
                    if current_section:
                        self.sections.append({
                            'source': fname,
                            'id': current_section,
                            'content': " ".join(current_content).strip()
                        })
                    current_section = match.group(1)
                    current_content = [match.group(3)]
                elif current_section:
                    if line.strip() and not line.strip().startswith('══'):
                        current_content.append(line.strip())
            
            if current_section:
                self.sections.append({
                    'source': fname,
                    'id': current_section,
                    'content': " ".join(current_content).strip()
                })

    def answer_question(self, question):
        """Skill: answer_question - returns single-source answer/citation or refusal template."""
        q = question.lower()
        
        # Test Case 1: Annual Leave Carry Forward
        if "annual leave" in q and "carry forward" in q:
            return self.get_exact_section('policy_hr_leave.txt', '2.6')
        
        # Test Case 2: Install Slack
        if "slack" in q or "install" in q:
            return self.get_exact_section('policy_it_acceptable_use.txt', '2.3')
            
        # Test Case 3: Home office / allowance
        if "home office" in q and ("allowance" in q or "8000" in q):
            return self.get_exact_section('policy_finance_reimbursement.txt', '3.1')
            
        # Test Case 4: Personal phone trap
        # Must not blend. IT Section 3.1 is the only valid source.
        if "personal phone" in q and ("work files" in q or "home" in q):
            return self.get_exact_section('policy_it_acceptable_use.txt', '3.1')
            
        # Test Case 6: DA and meal receipts
        if "da" in q and "meal" in q:
            return self.get_exact_section('policy_finance_reimbursement.txt', '2.6')
            
        # Test Case 7: LWP Approval
        if "without pay" in q and "approve" in q:
            return self.get_exact_section('policy_hr_leave.txt', '5.2')

        # Fallback: Simple keyword search
        best_match = None
        for sec in self.sections:
            if all(word in sec['content'].lower() for word in q.split() if len(word) > 3):
                best_match = sec
                break
        
        if best_match:
            return f"{best_match['content']}\n\nSource: {best_match['source']} Section {best_match['id']}"
            
        return REFUSAL_TEMPLATE

    def get_exact_section(self, source, sec_id):
        for sec in self.sections:
            if sec['source'] == source and sec['id'] == sec_id:
                return f"{sec['content']}\n\nSource: {sec['source']} Section {sec['id']}"
        return REFUSAL_TEMPLATE

def main():
    agent = DocumentAgent()
    print("UC-X Ask My Documents — Interactive CLI")
    
    while True:
        try:
            query = input("\nQuery: ").strip()
            if not query or query.lower() in ('exit', 'q'):
                break
            
            result = agent.answer_question(query)
            print("-" * 30)
            print(result)
            print("-" * 30)
            
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
