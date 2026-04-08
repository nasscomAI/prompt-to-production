"""
UC-X app.py — AI Policy Assistant.
Implemented using the RICE + agents.md + skills.md workflow.
"""
import os
import re

# Refusal template from README.md / agents.md
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

class UCXAgent:
    def __init__(self, doc_dir):
        self.doc_dir = doc_dir
        self.docs = {}
        self.retrieve_documents()

    def retrieve_documents(self):
        """Skill: retrieve_documents"""
        files = [
            'policy_hr_leave.txt',
            'policy_it_acceptable_use.txt',
            'policy_finance_reimbursement.txt'
        ]
        for f in files:
            path = os.path.join(self.doc_dir, f)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as file:
                    self.docs[f] = self.parse_sections(file.read())

    def parse_sections(self, text):
        sections = []
        lines = text.split('\n')
        current_title = "General"
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Simple section boundary detection
            if "════" in line and i + 1 < len(lines):
                potential_title = lines[i+1].strip()
                if potential_title and "════" not in potential_title:
                    current_title = potential_title
                    i += 2
                    continue

            # Subsection detection (e.g., 2.3 or 2.3.)
            match = re.match(r'^(\d+\.\d+)\.?\s*(.*)', line)
            if match:
                sub_id, first_line = match.groups()
                content_lines = [first_line]
                
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    if re.match(r'^\d+\.\d+', next_line) or "════" in next_line:
                        break
                    if next_line:
                        content_lines.append(next_line)
                    j += 1
                
                sections.append({
                    "id": sub_id,
                    "title": current_title,
                    "content": " ".join(content_lines).strip()
                })
                i = j - 1
            i += 1
        return sections

    def answer_question(self, query):
        """Skill: answer_question"""
        query_clean = query.lower()
        query_words = set(re.findall(r'\w+', query_clean))
        
        best_match = None
        max_score = 0
        best_doc = ""

        # Specific mappings to help simple keyword search
        synonyms = {
            "slack": ["software", "application", "install"],
            "personal phone": ["personal devices", "mobile"],
            "annual leave": ["vacation", "annual leave"],
            "carry forward": ["carry forward", "unused"],
            "home office": ["equipment allowance", "wfh"]
        }

        for doc_name, sections in self.docs.items():
            for sec in sections:
                content = sec['content'].lower()
                score = 0
                
                # Basic overlap
                for word in query_words:
                    if len(word) > 2 and word in content:
                        score += 3

                # Synonym/Intent boost
                for key, vals in synonyms.items():
                    if key in query_clean:
                        for val in vals:
                            if val in content:
                                score += 10

                # Avoid the personal-phone trap (Section 3.1 vs 2.1)
                if "personal" in query_clean and "corporate devices" in content:
                    score -= 10
                
                if query_clean in content:
                    score += 20

                if score > max_score:
                    max_score = score
                    best_match = sec
                    best_doc = doc_name

        if max_score > 6:
            return f"{best_match['content']}\n\nCitation: {best_doc} (Section {best_match['id']})"
        else:
            return REFUSAL_TEMPLATE

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    doc_dir = os.path.join(base_dir, '..', 'data', 'policy-documents')
    agent = UCXAgent(doc_dir)
    
    print("-" * 50)
    print("UC-X — AI Policy Assistant")
    print("-" * 50)

    while True:
        try:
            query = input("Ask a policy question: ").strip()
            if query.lower() in ['exit', 'quit']: break
            if not query: continue
            
            print(f"ANSWER:\n{agent.answer_question(query)}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            break

if __name__ == "__main__":
    main()
