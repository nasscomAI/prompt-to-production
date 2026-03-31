import argparse
import os
import re

# Refusal template defined in README.md and agents.md
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

class PolicyExpert:
    def __init__(self):
        self.documents = {}
        self.docs_dir = os.path.join("..", "data", "policy-documents")
        self.doc_filenames = [
            "policy_hr_leave.txt",
            "policy_it_acceptable_use.txt",
            "policy_finance_reimbursement.txt"
        ]

    def retrieve_documents(self):
        """
        Skill: retrieve_documents
        Loads and indexes 3 policy files by name and section number.
        """
        for filename in self.doc_filenames:
            path = os.path.join(self.docs_dir, filename)
            if not os.path.exists(path):
                continue
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split by section headers (e.g. "2. ANNUAL LEAVE" or "1. PURPOSE AND SCOPE")
            # and then by section numbering (e.g. "1.1", "2.3")
            doc_data = {}
            
            # Match section numbers and their content
            sections = re.findall(r'(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\n═|\Z)', content, re.DOTALL | re.MULTILINE)
            for sec_num, sec_content in sections:
                clean_content = re.sub(r'\s+', ' ', sec_content).strip()
                doc_data[sec_num] = clean_content
            
            self.documents[filename] = doc_data

    def answer_question(self, question):
        """
        Skill: answer_question
        Searches indexed documents for a single-source answer.
        Enforces RICE rules.
        """
        q_lower = question.lower()
        # Remove common stop words for better keyword matching
        stop_words = {'the', 'is', 'at', 'which', 'on', 'can', 'i', 'to', 'for', 'my', 'what', 'when'}
        q_keywords = [w for w in re.findall(r'\w+', q_lower) if w not in stop_words]
        
        potential_answers = []

        for doc_name, sections in self.documents.items():
            for sec_num, content in sections.items():
                content_lower = content.lower()
                # Count exact keyword matches
                matches = sum(1 for kw in q_keywords if kw in content_lower)
                
                # We need a significant portion of the semantic keywords to match
                # to consider it "covered".
                if len(q_keywords) > 0 and (matches / len(q_keywords)) >= 0.4:
                    potential_answers.append({
                        "doc": doc_name,
                        "sec": sec_num,
                        "text": content,
                        "confidence": matches / len(q_keywords)
                    })

        if not potential_answers:
            return REFUSAL_TEMPLATE

        # Rule 1: Never combine claims from two different documents.
        # Select best single source
        best = max(potential_answers, key=lambda x: x["confidence"])
        
        # If confidence is low, refuse
        if best["confidence"] < 0.5:
            return REFUSAL_TEMPLATE

        # Format answer strictly with citation
        return f"{best['text']}\n\n[Source: {best['doc']} Section {best['sec']}]"

def main():
    agent = PolicyExpert()
    agent.retrieve_documents()
    
    print("\nCMC Policy Assistant - UC-X")
    print("Type 'exit' or 'quit' to stop.")
    print("-" * 30)

    while True:
        try:
            question = input("\nQuestion: ").strip()
            if question.lower() in ['exit', 'quit']:
                break
            if not question:
                continue
                
            answer = agent.answer_question(question)
            print(f"\nAnswer: {answer}")
            
        except EOFError:
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()
