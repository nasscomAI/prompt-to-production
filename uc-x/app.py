"""
UC-X app.py — Policy Document Q&A System
Interactive CLI for HR, IT, and Finance policy questions.
Built with RICE-enforced single-source answering and refusal template.
"""
import os
import re
import sys
from pathlib import Path

class PolicyQASystem:
    def __init__(self, policy_dir="../data/policy-documents"):
        self.policy_dir = policy_dir
        self.documents = {}
        self.indexed_docs = {}
        self.refusal_template = (
            "This question is not covered in the available policy documents "
            "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
            "Please contact the relevant department for guidance."
        )
        self.load_documents()
    
    def load_documents(self):
        """Load and index all policy documents."""
        policy_files = [
            ("policy_hr_leave.txt", "HR", "HR-POL-001"),
            ("policy_it_acceptable_use.txt", "IT", "IT-POL-003"),
            ("policy_finance_reimbursement.txt", "Finance", "FIN-POL-007"),
        ]
        
        for filename, dept, ref_id in policy_files:
            filepath = os.path.join(self.policy_dir, filename)
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Policy file not found: {filepath}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.documents[filename] = {
                'dept': dept,
                'ref_id': ref_id,
                'content': content
            }
            
            # Index by section numbers
            self.indexed_docs[filename] = self._parse_sections(content)
        
        print(f"✓ Loaded {len(self.documents)} policy documents")
        print(f"  - HR Leave Policy (policy_hr_leave.txt)")
        print(f"  - IT Acceptable Use (policy_it_acceptable_use.txt)")
        print(f"  - Finance Reimbursement (policy_finance_reimbursement.txt)")
        print()
    
    def _parse_sections(self, content):
        """Parse document into indexed sections."""
        sections = {}
        lines = content.split('\n')
        current_section = None
        current_text = []
        
        for line in lines:
            # Match section headers like "2. ANNUAL LEAVE" or "3.1 This policy..."
            match = re.match(r'^(\d+(?:\.\d+)?)\s+', line)
            if match:
                if current_section:
                    sections[current_section] = '\n'.join(current_text).strip()
                current_section = match.group(1)
                current_text = [line]
            elif current_section:
                current_text.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_text).strip()
        
        return sections
    
    def search_sections(self, query_keywords):
        """Search indexed sections for relevant content."""
        matches = {}  # {filename: [(section_num, relevance_score), ...]}
        
        keywords = query_keywords.lower().split()
        
        for filename, sections in self.indexed_docs.items():
            file_matches = []
            for section_num, section_text in sections.items():
                text_lower = section_text.lower()
                match_count = sum(1 for kw in keywords if kw in text_lower)
                if match_count > 0:
                    file_matches.append((section_num, match_count))
            
            if file_matches:
                matches[filename] = sorted(file_matches, key=lambda x: x[1], reverse=True)
        
        return matches
    
    def extract_answer(self, filename, section_num):
        """Extract answer from a specific section with citation."""
        if filename not in self.indexed_docs:
            return None
        
        section_text = self.indexed_docs[filename].get(section_num)
        if not section_text:
            return None
        
        dept = self.documents[filename]['dept']
        ref_id = self.documents[filename]['ref_id']
        
        return {
            'source': f"{dept} Policy ({filename}) — {ref_id}",
            'section': section_num,
            'text': section_text,
            'citation': f"Source: {dept} Policy, Section {section_num}"
        }
    
    def answer_question(self, question):
        """Answer a user question with single-source enforcement."""
        keywords = question.lower().replace('?', '').replace('.', '')
        matches = self.search_sections(keywords)
        
        if not matches:
            print(f"\n{self.refusal_template}\n")
            return
        
        # Check if answer spans multiple documents (cross-document blending risk)
        if len(matches) > 1:
            # Try to find a single-source answer
            print("\n⚠️  Your question could relate to multiple policies.\n")
            
            # Give precedence based on specificity
            best_source = None
            for filename in matches:
                top_sections = matches[filename][:3]
                # Check if these sections have high relevance
                if top_sections[0][1] >= 2:  # At least 2 keyword matches
                    if best_source is None:
                        best_source = filename
            
            if best_source:
                # Use best source
                top_section = matches[best_source][0][0]
                answer = self.extract_answer(best_source, top_section)
                if answer:
                    print(f"{answer['citation']}")
                    print(f"\n{answer['text']}\n")
                return
            else:
                # Genuinely ambiguous
                print(f"{self.refusal_template}\n")
                return
        
        # Single-source answer
        filename = list(matches.keys())[0]
        top_section = matches[filename][0][0]
        
        answer = self.extract_answer(filename, top_section)
        if answer:
            print(f"\n{answer['citation']}")
            print(f"\n{answer['text']}\n")
        else:
            print(f"\n{self.refusal_template}\n")
    
    def run_interactive(self):
        """Run the interactive CLI."""
        print("=" * 70)
        print("CMC POLICY QUESTION ANSWERING SYSTEM")
        print("=" * 70)
        print("\nYou can ask questions about:")
        print("  • Employee leave policies (HR)")
        print("  • IT device and data use (IT)")
        print("  • Expense reimbursement (Finance)")
        print("\nType 'exit' or 'quit' to end.\n")
        print("-" * 70)
        
        while True:
            try:
                question = input("\n📋 Your question: ").strip()
                
                if question.lower() in ['exit', 'quit']:
                    print("\nThank you for using the Policy Q&A System. Goodbye!")
                    break
                
                if not question:
                    print("Please enter a question.")
                    continue
                
                print()
                self.answer_question(question)
                
            except KeyboardInterrupt:
                print("\n\nExiting. Goodbye!")
                break
            except Exception as e:
                print(f"ERROR: {e}", file=sys.stderr)

def main():
    try:
        # Resolve policy directory path relative to script location
        script_dir = Path(__file__).parent.parent
        policy_dir = script_dir / "data" / "policy-documents"
        
        if not policy_dir.exists():
            raise FileNotFoundError(f"Policy directory not found: {policy_dir}")
        
        qa_system = PolicyQASystem(policy_dir=str(policy_dir))
        qa_system.run_interactive()
        
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"FATAL ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

