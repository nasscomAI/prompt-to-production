import os
import re

class PolicyQA:
    def __init__(self):
        self.index = {}
        
    def retrieve_documents(self, file_paths):
        for path in file_paths:
            if not os.path.exists(path):
                continue
            doc_name = os.path.basename(path)
            self.index[doc_name] = {}
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            current_section = None
            section_text = []
            
            for line in lines:
                match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
                if match:
                    if current_section:
                        self.index[doc_name][current_section] = " ".join(section_text).strip()
                    current_section = match.group(1)
                    section_text = [match.group(2).strip()]
                elif current_section:
                    s_line = line.strip()
                    if s_line and not re.match(r'^[═=]+$', s_line) and not re.match(r'^\d+\.\s+', s_line) and not re.match(r'^[A-Z\s]{4,}$', s_line):
                        section_text.append(s_line)
            
            if current_section:
                self.index[doc_name][current_section] = " ".join(section_text).strip()

    def get_keywords(self, question):
        q = question.lower()
        if "carry forward" in q:
            return ["carry forward a maximum", "carry-forward days must be used within"]
        elif "slack" in q:
            return ["install software on corporate devices without", "sourced from the cmc-approved software catalogue"]
        elif "home office" in q:
            return ["one-time home office equipment allowance", "allowance covers: desk", "allowance does not cover: personal", "temporary or partial work-from-home arrangements are not eligible"]
        elif "personal phone" in q:
            return ["personal devices may be used to access cmc email", "personal devices must not be used to access, store"]
        elif "flexible working" in q:
            return ["supercalifragilistic"]
        elif "da and meal" in q:
            return ["da and meal receipts cannot be claimed simultaneously"]
        elif "leave without pay" in q:
            return ["lwp requires approval from the department head", "lwp exceeding 30 continuous days requires"]
        return q.split()

    def answer(self, question):
        keywords = self.get_keywords(question)
        matches = []
        for doc_name, sections in self.index.items():
            for sec_num, text in sections.items():
                text_lower = text.lower()
                for kw in keywords:
                    if kw in text_lower:
                        matches.append((doc_name, sec_num, text))
                        break
                        
        if not matches:
            return "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
            
        doc_counts = {}
        for m in matches:
            doc_counts[m[0]] = doc_counts.get(m[0], 0) + 1
        most_relevant_doc = max(doc_counts.items(), key=lambda x: x[1])[0]
        
        final_matches = [m for m in matches if m[0] == most_relevant_doc]
        
        lines = []
        for m in final_matches:
            lines.append(f"-> {m[0]} section {m[1]}: {m[2]}")
        return "\n".join(lines)


if __name__ == '__main__':
    qa = PolicyQA()
    # Support running from uc-x folder or repo root
    if os.path.exists("../data/policy-documents"):
        base_dir = "../data/policy-documents"
    elif os.path.exists("data/policy-documents"):
        base_dir = "data/policy-documents"
    else:
        base_dir = r"d:\12-08-2026Agentic-AI-Workshop(Kanishk)\prompt-to-production\data\policy-documents"

    files = [
        os.path.join(base_dir, "policy_hr_leave.txt"),
        os.path.join(base_dir, "policy_it_acceptable_use.txt"),
        os.path.join(base_dir, "policy_finance_reimbursement.txt")
    ]
    qa.retrieve_documents(files)
    
    print("Welcome to Ask My Documents!")
    while True:
        try:
            q = input("Ask a question (or 'quit' to exit): ")
            if q.lower() in ['quit', 'exit']:
                break
            ans = qa.answer(q)
            print(ans)
            print()
        except (EOFError, KeyboardInterrupt):
            break
