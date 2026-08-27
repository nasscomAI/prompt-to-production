"""
UC-X — Ask My Documents
Interactive policy document search enforcing single-source answers with citation.
"""
import os
import re
import sys
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# Refusal template - exact wording per agents.md
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents 
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). 
Please contact the Human Resources or IT Department for guidance."""

class PolicyDocumentSearch:
    def __init__(self, docs_dir: str = "../data/policy-documents"):
        self.docs_dir = docs_dir
        self.documents = {}
        self.load_documents()
    
    def load_documents(self):
        """Load all policy documents."""
        doc_files = [
            "policy_hr_leave.txt",
            "policy_it_acceptable_use.txt",
            "policy_finance_reimbursement.txt"
        ]
        
        for doc_file in doc_files:
            doc_path = os.path.join(self.docs_dir, doc_file)
            
            if os.path.exists(doc_path):
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    self.documents[doc_file] = {
                        'full_text': content,
                        'lines': lines,
                        'line_count': len(lines)
                    }
                    print(f"✓ Loaded {doc_file}")
            else:
                print(f"⚠ Warning: Document not found: {doc_path}")
        
        if not self.documents:
            print("Error: No policy documents found.")
            sys.exit(1)
    
    def search_documents(self, query: str) -> List[Tuple[str, str, int, str]]:
        """
        Search all documents for query terms.
        Returns list of (document_name, clause, line_number, text).
        """
        results = []
        
        # Extract key terms from query (remove common words)
        query_lower = query.lower()
        stop_words = {'can', 'i', 'am', 'is', 'are', 'the', 'a', 'an', 'to', 'of', 'in', 'on', 'at', 'by'}
        query_terms = [w for w in query_lower.split() if w not in stop_words and len(w) > 2]
        
        # Search each document
        for doc_name, doc_data in self.documents.items():
            content_lower = doc_data['full_text'].lower()
            
            # Find matches in content
            for term in query_terms:
                # Look for the term or close variations
                pattern = r'\b' + re.escape(term) + r'\w*'
                matches = list(re.finditer(pattern, content_lower))
                
                if matches:
                    # Find which lines contain matches
                    for match in matches:
                        char_pos = match.start()
                        line_num = content_lower[:char_pos].count('\n') + 1
                        
                        # Get the line text and surrounding context
                        if line_num <= len(doc_data['lines']):
                            line_text = doc_data['lines'][line_num - 1].strip()
                            
                            # Find clause number if present
                            clause_match = re.search(r'(\d+\.\d+)', line_text)
                            clause = clause_match.group(1) if clause_match else f"Line {line_num}"
                            
                            if line_text:
                                results.append((doc_name, clause, line_num, line_text))
            
            # Also search for direct clause references (e.g., "3.1", "5.2")
            clause_pattern = r'(\d+\.\d+)'
            if re.search(clause_pattern, query):
                clause_ref = re.search(clause_pattern, query).group(1)
                
                for i, line in enumerate(doc_data['lines']):
                    if clause_ref in line:
                        # Found clause, get next few lines for context
                        context_lines = []
                        for j in range(i, min(i + 3, len(doc_data['lines']))):
                            context_lines.append(doc_data['lines'][j].strip())
                        
                        context = ' '.join(context_lines)
                        if context:
                            results.append((doc_name, clause_ref, i + 1, context))
        
        # Deduplicate results
        unique_results = []
        seen = set()
        for result in results:
            key = (result[0], result[1])
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        return unique_results
    
    def enforce_single_source(self, results: List[Tuple[str, str, int, str]], query: str) -> str:
        """
        Enforce single-source rule: answer must come from exactly one document.
        Returns formatted answer or refusal template.
        """
        if not results:
            return REFUSAL_TEMPLATE
        
        # Check if results span multiple documents
        doc_set = set(result[0] for result in results)
        
        if len(doc_set) > 1:
            # Multiple documents involved - use refusal template
            return REFUSAL_TEMPLATE
        
        # Single document - gather results and format answer
        doc_name = results[0][0]
        answer_lines = []
        
        for result in results:
            clause = result[1]
            line_num = result[2]
            text = result[3]
            
            answer_lines.append(f"  [{clause}] {text}")
        
        answer = f"""Answer found in {doc_name}:

{chr(10).join(answer_lines)}"""
        
        return answer
    
    def ask(self, question: str) -> str:
        """
        Answer a question using documents.
        Enforces single-source rule and returns citation.
        """
        # Search documents
        results = self.search_documents(question)
        
        # Enforce single-source and format answer
        answer = self.enforce_single_source(results, question)
        
        return answer
    
    def run_interactive(self):
        """Run interactive CLI."""
        print("\n" + "=" * 70)
        print("UC-X: ASK MY DOCUMENTS")
        print("=" * 70)
        print(f"\nLoaded {len(self.documents)} policy documents.")
        print("\nType your question and press Enter. Type 'quit' or 'exit' to end.\n")
        
        while True:
            try:
                question = input("Your question: ").strip()
                
                if not question:
                    continue
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("\nThank you for using Ask My Documents!")
                    break
                
                # Get answer
                answer = self.ask(question)
                
                print(f"\n{answer}\n")
                print("-" * 70 + "\n")
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}\n")


def main():
    """Main entry point."""
    # Try common relative paths
    possible_dirs = [
        "../data/policy-documents",
        "data/policy-documents",
        "./data/policy-documents",
        os.path.expanduser("~/Downloads/prompt-to-production/data/policy-documents"),
    ]
    
    docs_dir = None
    for possible_dir in possible_dirs:
        if os.path.exists(possible_dir):
            docs_dir = possible_dir
            break
    
    if not docs_dir:
        print(f"Error: Could not find policy documents directory.")
        print(f"Searched: {possible_dirs}")
        sys.exit(1)
    
    # Create searcher and run interactive mode
    searcher = PolicyDocumentSearch(docs_dir)
    searcher.run_interactive()


if __name__ == "__main__":
    main()
