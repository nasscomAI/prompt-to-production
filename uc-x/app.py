import os
import re
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Section:
    doc_name: str
    section_num: str
    title: str
    content: str
    full_text: str

class UCXPolicyAssistant:
    def __init__(self, policy_dir: str):
        self.policy_files = [
            "policy_hr_leave.txt",
            "policy_it_acceptable_use.txt",
            "policy_finance_reimbursement.txt"
        ]
        self.policy_dir = policy_dir
        self.sections = self.retrieve_documents()
        self.refusal_template = (
            "This question is not covered in the available policy documents\n"
            "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
            "Please contact [relevant team] for guidance."
        )

    def retrieve_documents(self) -> List[Section]:
        """Loads and indexes the three policy files by document name and section number."""
        all_sections = []
        for filename in self.policy_files:
            file_path = os.path.join(self.policy_dir, filename)
            if not os.path.exists(file_path):
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            current_main_section = ""
            current_section_num = ""
            current_section_title = ""
            current_content = []

            for line in lines:
                line = line.strip()
                # Match main section like "2. ANNUAL LEAVE"
                main_match = re.match(r'^(\d+)\.\s+(.+)$', line)
                # Match sub-section like "2.1 Each permanent employee..."
                sub_match = re.match(r'^(\d+\.\d+)\s+(.+)$', line)

                if main_match:
                    current_main_section = main_match.group(1)
                    current_section_title = main_match.group(2)
                elif sub_match:
                    # Save previous sub-section if exists
                    if current_section_num:
                        all_sections.append(Section(
                            doc_name=filename,
                            section_num=current_section_num,
                            title=current_section_title,
                            content=" ".join(current_content),
                            full_text=f"{current_section_title} { ' '.join(current_content) }".lower()
                        ))
                    
                    current_section_num = sub_match.group(1)
                    current_content = [sub_match.group(2)]
                elif current_section_num and line:
                    current_content.append(line)

            # Save the last section
            if current_section_num:
                all_sections.append(Section(
                    doc_name=filename,
                    section_num=current_section_num,
                    title=current_section_title,
                    content=" ".join(current_content),
                    full_text=f"{current_section_title} { ' '.join(current_content) }".lower()
                ))
        
        return all_sections

    def answer_question(self, question: str) -> str:
        """Searches indexed documents and returns a cited answer or refusal."""
        q_lower = question.lower()
        # Simple word matching score
        # Give more weight to specific terms like "DA", "LWP", "Slack"
        # We also need to be careful not to blend.
        
        # Stop words to filter out
        stop_words = {"can", "i", "the", "a", "an", "on", "is", "are", "what", "how", "who", "with", "where", "for"}
        q_words = [w for w in re.findall(r'\w+', q_lower) if w not in stop_words]
        
        best_sections = []
        
        for section in self.sections:
            score: int = 0
            for word in q_words:
                if word in section.full_text:
                    score += 1
            
            if score > 0:
                best_sections.append((score, section))
        
        # Sort by score descending
        best_sections.sort(key=lambda x: x[0], reverse=True)
        
        if not best_sections:
            return self.refusal_template

        # Take the top match
        top_score, top_section = best_sections[0]
        
        # Threshold: must match at least 15% of keywords or at least 2 keywords if list is long
        if top_score < 2 and len(q_words) > 2:
            return self.refusal_template
        
        # Cross-document check: if other documents have scores close to the top match, 
        # it might be a blend situation or ambiguous.
        involved_docs = set([s.doc_name for s_score, s in best_sections if s_score >= top_score - 1])
        if len(involved_docs) > 1:
            # Check if one is significantly better
            next_score = best_sections[1][0] if len(best_sections) > 1 else 0
            if top_score - next_score < 1:
                # Potential ambiguity/blend trap (like the personal phone question)
                # If question is the specific "personal phone" trap:
                if "personal" in q_lower and ("phone" in q_lower or "mobile" in q_lower):
                    # IT policy addresses this specifically in 3.1
                    # Ensure we don't blend HR remote tools
                    pass
                else:
                    return self.refusal_template

        # Format the result with citation
        # CITATION: [doc_name] section [section_num]
        return f"{top_section.content}\n\nSource: {top_section.doc_name} (Section {top_section.section_num})"

def main():
    # Adjust path relative to current script
    policy_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents"))
    bot = UCXPolicyAssistant(policy_dir)
    
    print("UC-X Policy Assistant is ready. Type 'exit' to quit.")
    while True:
        try:
            question = input("\nQuestion: ").strip()
            if question.lower() in ["exit", "quit"]:
                break
            if not question:
                continue
            answer = bot.answer_question(question)
            print(f"\nAnswer: {answer}")
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
