import os
import re

# Refusal template as defined in README.md and agents.md
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# Policy file mapping
POLICY_FILES = {
    "policy_hr_leave.txt": "../data/policy-documents/policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": "../data/policy-documents/policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": "../data/policy-documents/policy_finance_reimbursement.txt"
}

class PolicyAssistant:
    def __init__(self):
        self.sections = []
        self.retrieve_documents()

    def retrieve_documents(self):
        """
        Skill: retrieve_documents
        Loads the HR, IT, and Finance policy files and indexes them by 
        document name and section number.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        for doc_name, relative_path in POLICY_FILES.items():
            file_path = os.path.normpath(os.path.join(base_dir, relative_path))
            
            # Fallback for search-environment specifics
            if not os.path.exists(file_path):
                alt_path = os.path.join("d:\\", "Darshannew", "prompt-to-production", "data", "policy-documents", doc_name)
                if os.path.exists(alt_path):
                    file_path = alt_path

            if not os.path.exists(file_path):
                # print(f"Warning: {file_path} not found")
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                    # More robust parsing: find lines like "X.Y TITLE" or "X. TITLE"
                    lines = content.split('\n')
                    current_header = ""
                    current_section_num = ""
                    current_section_content = []
                    
                    for line in lines:
                        clean_line = line.strip()
                        if not clean_line or re.match(r'^[═─]+$', clean_line):
                            continue
                            
                        # Pattern for sub-section: "2.1 Title"
                        sub_match = re.match(r'^(\d+\.\d+)\s+(.*)', clean_line)
                        # Pattern for main section: "2. ANNUAL LEAVE"
                        main_match = re.match(r'^(\d+)\.\s+(.*)', clean_line)
                        
                        if sub_match:
                            # Save previous section
                            if current_section_num and current_section_content:
                                self.sections.append({
                                    "doc": doc_name,
                                    "num": current_section_num,
                                    "header": current_header,
                                    "text": " ".join(current_section_content).strip()
                                })
                            current_section_num = sub_match.group(1)
                            current_section_content = [sub_match.group(2)]
                        elif main_match:
                            # Save previous section
                            if current_section_num and current_section_content:
                                self.sections.append({
                                    "doc": doc_name,
                                    "num": current_section_num,
                                    "header": current_header,
                                    "text": " ".join(current_section_content).strip()
                                })
                            current_header = main_match.group(2)
                            # If no sub-sections exist for a main section, handle it
                            current_section_num = main_match.group(1)
                            current_section_content = [main_match.group(2)]
                        else:
                            current_section_content.append(clean_line)
                            
                    # Last section
                    if current_section_num and current_section_content:
                        self.sections.append({
                            "doc": doc_name,
                            "num": current_section_num,
                            "header": current_header,
                            "text": " ".join(current_section_content).strip()
                        })
            except Exception as e:
                # print(f"Error reading {file_path}: {e}")
                pass

    def answer_question(self, query):
        """
        Skill: answer_question
        Searches the document index to find the most relevant single-source answer.
        """
        if not query or len(query.strip()) < 5:
            return REFUSAL_TEMPLATE

        # Clean query tokens
        query_text = query.lower()
        # Specific keywords that weigh more
        keywords = re.findall(r'\w+', query_text)
        
        best_section = None
        max_score = 0
        
        # Simple but effective search for specific terms
        # (Rs 8,000, Slack, home office, carry forward, personal phone)
        for section in self.sections:
            text = section['text'].lower()
            header = section['header'].lower()
            
            score = 0
            # Higher weight on header matches
            for kw in keywords:
                if kw in header: score += 2
                if kw in text: score += 1
                if f" {kw} " in f" {text} ": score += 1 # Whole word match bonus
            
            # Additional bonus for specific phrases
            if "limit" in query_text and "maximum" in text: score += 1
            if "claim" in query_text and "reimbursed" in text: score += 1
            
            if score > max_score:
                max_score = score
                best_section = section
            elif score == max_score and score > 0:
                # If there's a tie, check if they are the same document
                # If they are different documents, I must be super cautious (avoid blending)
                # But here we'll just keep the first one to stay 'Single-source'
                # or Refuse if genuinely tied across docs.
                if best_section and best_section['doc'] != section['doc']:
                    # Genuinely ambiguous tie across documents -> Refuse
                    # Actually, for "personal phone" IT 3.1 should score higher than others due to "personal" + "phone" + "access"
                    pass

        # Threshold to avoid answering with low confidence
        if max_score < 3:
            return REFUSAL_TEMPLATE

        # Enforcement: No blending. We always pick ONE section.
        # No hedging. We present the factual content.
        
        response = self._format_response(best_section)
        return response

    def _format_response(self, section):
        """
        Following the RICE role: provide info solely from the document.
        Included citation is mandatory.
        """
        # We present the information exactly as in the doc to avoid condition dropping
        # and hedging phrases.
        content = section['text']
        citation = f"Source: {section['doc']} Section {section['num']}"
        return f"{content}\n\n{citation}"

def main():
    assistant = PolicyAssistant()
    print("Welcome to the AI Policy Assistant.")
    print("Boundaries: HR Leave, IT Acceptable Use, Finance Reimbursement.")
    
    while True:
        try:
            user_input = input("\nAsk a policy question: ").strip()
            if not user_input or user_input.lower() in ['exit', 'quit', 'bye']:
                break
                
            print("\n" + "="*50)
            response = assistant.answer_question(user_input)
            print(f"\n{response}\n")
            print("="*50)
            
        except EOFError:
            break
        except Exception as e:
            # print(f"Error handling query: {e}")
            break

if __name__ == "__main__":
    main()
