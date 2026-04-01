"""
UC-X app.py — Document Search and Retrieval CLI.
Built with RICE (Role, Intent, Context, Enforcement) principles.
"""
import os
import re
import sys

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

DOC_PATHS = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt"
]

class PolicySearchEngine:
    def __init__(self):
        self.sections = [] # List of {'doc':, 'id':, 'text':}

    def retrieve_documents(self):
        for path in DOC_PATHS:
            abs_path = os.path.join(os.path.dirname(__file__), path)
            if not os.path.exists(abs_path):
                continue
            
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = "\n" + f.read() # Add newline to catch first section
            
            doc_name = os.path.basename(path)
            # Match subsections like 2.6
            sub_pattern = re.compile(r'\n(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\n\d+\.|\n═|$)', re.DOTALL)
            for section_id, text in sub_pattern.findall(content):
                self.sections.append({
                    'doc': doc_name,
                    'id': section_id,
                    'text': text.strip()
                })
            
            # Match main sections like 2. ANNUAL LEAVE
            main_pattern = re.compile(r'\n(\d+)\.\s+([A-Z\s]+)\n(.*?)(?=\n\d+\.\d+|\n\d+\.|\n═|$)', re.DOTALL)
            for section_id, title, text in main_pattern.findall(content):
                # Only add if it doesn't overlap with subsections or if we want the full section summary
                # For this task, subsections are better.
                self.sections.append({
                    'doc': doc_name,
                    'id': section_id,
                    'text': f"{title}\n{text.strip()}"
                })

    def answer_question(self, query):
        query = query.lower()
        # Filter out common stop words
        stop_words = {'can', 'i', 'the', 'a', 'is', 'for', 'on', 'my', 'what', 'who', 'how', 'to', 'in', 'of', 'with'}
        query_words = [w for w in re.findall(r'\w+', query) if w not in stop_words and len(w) > 2]
        
        if not query_words:
            return REFUSAL_TEMPLATE

        best_match = None
        max_score = 0

        for section in self.sections:
            text_lower = section['text'].lower()
            score = sum(3 if w in section['id'].lower() else 1 for w in query_words if w in text_lower)
            
            if score > max_score:
                max_score = score
                best_match = section
        
        # Threshold: must match at least some significant part of the query
        if max_score < 3:
            return REFUSAL_TEMPLATE

        return f"According to {best_match['doc']} section {best_match['id']}:\n\n{best_match['text']}"

def main():
    engine = PolicySearchEngine()
    engine.retrieve_documents()

    print("UC-X — INTERNAL COMPANY POLICY ASSISTANT")
    print("Ready to answer HR, IT, and Finance policy questions.")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            line = sys.stdin.readline()
            if not line or line.strip().lower() in ('exit', 'quit'):
                break
            
            query = line.strip()
            if not query:
                continue

            answer = engine.answer_question(query)
            print("-" * 40)
            print(answer)
            print("-" * 40 + "\n")
            
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
