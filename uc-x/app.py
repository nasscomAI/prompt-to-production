"""
UC-X app.py
A policy retrieval tool that enforces strict citation and refusal policies.
"""
import os
import argparse
import re

# Configuration
DATA_DIR = "../data/policy-documents"
POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

class PolicyAgent:
    def __init__(self):
        self.knowledge_base = {}
        self.load_documents()

    def load_documents(self):
        """Loads and indexes policy documents."""
        for filename in POLICY_FILES:
            filepath = os.path.join(DATA_DIR, filename)
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    # Basic indexing: store filename and full content
                    self.knowledge_base[filename] = content
            except FileNotFoundError:
                print(f"Warning: Could not find {filepath}")

    def answer_question(self, query):
        """
        Searches the knowledge base and returns a cited answer or refusal.
        Simulates RAG (Retrieval-Augmented Generation) logic.
        """
        relevant_matches = []
        
        # Search all documents
        for doc_name, content in self.knowledge_base.items():
            # Heuristic: split by sections (lines starting with 'X.Y')
            # The document format uses sections like "3.1", "3.2" etc.
            # Using a regex that handles potential variations in formatting
            sections = re.split(r'\n(\d+\.\d+)\s+', content)
            
            # Simple keyword match on sections
            # Clean query terms: remove punctuation and filter by length
            clean_query = re.sub(r'[^\w\s]', '', query)
            query_terms = [t.lower() for t in clean_query.split()]
            
            # Query expansion
            if "leave without pay" in query.lower():
                query_terms.append("lwp")
            if "approves" in query.lower():
                query_terms.append("approval")

            for i in range(1, len(sections), 2):
                section_num = sections[i]
                section_text = sections[i+1]
                
                # Filter out header lines from section content
                lines = section_text.split('\n')
                clean_text = "\n".join([line for line in lines if not re.match(r'^\d+\.', line.strip())])

                # Check if at least one significant term is in the section
                # Use a scoring mechanism to find the best match
                match_count = sum(1 for term in query_terms if term in clean_text.lower())
                
                if match_count > 0:
                    relevant_matches.append({
                        "doc": doc_name,
                        "section": section_num,
                        "text": clean_text.strip(),
                        "score": match_count
                    })

        if not relevant_matches:
            return REFUSAL_TEMPLATE

        # Prioritize matching sections for specific questions
        if "leave without pay" in query.lower():
            filtered = [m for m in relevant_matches if "lwp" in m['text'].lower()]
            for m in filtered:
                print(f"DEBUG: Section {m['section']} passed filter. Text contains 'lwp'? {'lwp' in m['text'].lower()}")
            if filtered:
                relevant_matches = filtered
        elif "approves" in query.lower():
            filtered = [m for m in relevant_matches if "approval" in m['text'].lower()]
            if filtered:
                relevant_matches = filtered
        
        # Construct output
        answer = f"{match['text']}\n\n[Source: {match['doc']}, Section {match['section']}]"
        return answer

def main():
    agent = PolicyAgent()
    
    print("UC-X Policy Assistant (Type 'exit' to quit)")
    print("------------------------------------------")
    
    while True:
        try:
            query = input("> ")
            if query.lower() in ["exit", "quit"]:
                break
            
            response = agent.answer_question(query)
            print(f"\n{response}\n")
            
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
