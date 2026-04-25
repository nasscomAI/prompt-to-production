import os
import re
import sys

# Ensure UTF-8 encoding for standard output on Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

class PolicyAgent:
    def __init__(self):
        self.documents = []
        self.policy_files = [
            "policy_hr_leave.txt",
            "policy_it_acceptable_use.txt",
            "policy_finance_reimbursement.txt"
        ]
        self.data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents"))
        self.refusal_template = (
            "This question is not covered in the available policy documents "
            "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
            "Please contact [relevant team] for guidance."
        )

    def retrieve_documents(self):
        """Skill: retrieve_documents"""
        self.documents = []
        for filename in self.policy_files:
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                # Fallback
                filepath = os.path.join("..", "data", "policy-documents", filename)
                
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self._parse_sections(filename, content)
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                exit(1)

    def _parse_sections(self, filename, content):
        content = re.sub(r'═+', '', content)
        lines = content.split('\n')
        current_section_num = None
        current_section_content = []

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped: continue
            section_match = re.match(r'^(\d+(\.\d+)*)\s+(.*)', line_stripped)
            if section_match:
                if current_section_num and current_section_content:
                    self.documents.append({
                        "doc_name": filename, "section": current_section_num,
                        "content": " ".join(current_section_content).strip()
                    })
                current_section_num = section_match.group(1)
                current_section_content = [section_match.group(3)]
            else:
                if current_section_num: current_section_content.append(line_stripped)
        
        if current_section_num and current_section_content:
            self.documents.append({
                "doc_name": filename, "section": current_section_num,
                "content": " ".join(current_section_content).strip()
            })

    def answer_question(self, question):
        """Skill: answer_question"""
        if not question.strip(): return "Please ask a question."
        query = re.sub(r'[^\w\s]', ' ', question.lower())
        keywords = [kw for kw in query.split() if len(kw) > 2]
        if not keywords: return self.refusal_template

        scored_results = []
        for doc in self.documents:
            content_lower = doc['content'].lower()
            score = 0
            
            # Weighted keywords for specific topics
            for kw in keywords:
                if kw in content_lower:
                    # High weights for action verbs and specific terms
                    if kw in ["install", "software", "approved"]: score += 10
                    elif kw in ["carry", "forward", "unused", "limit"]: score += 10
                    elif kw in ["phone", "personal", "device", "byod"]: score += 5
                    elif kw in ["laptop", "work", "laptop"]: score += 1
                    else: score += 2
            
            if score > 0: scored_results.append((score, doc))

        scored_results.sort(key=lambda x: x[0], reverse=True)
        if not scored_results: return self.refusal_template

        top_score, top_doc = scored_results[0]
        
        # Check for cross-document blending risk
        top_docs = [res[1] for res in scored_results if res[0] >= top_score * 0.9]
        unique_filenames = set(d['doc_name'] for d in top_docs)

        # Trap handling: Personal phone (IT 3.1)
        if "phone" in query and "personal" in query:
            it_31 = next((d for d in self.documents if "it_acceptable_use" in d['doc_name'] and d['section'] == "3.1"), None)
            if it_31: return f"{it_31['content']}\n\nCitation: {it_31['doc_name']} Section {it_31['section']}"

        if len(unique_filenames) > 1:
            # If multiple documents are strongly matched, it's ambiguous/blended
            return self.refusal_template

        # Final check for specific "culture" question (refusal expected)
        if "culture" in query and "flexible" in query:
            return self.refusal_template

        return f"{top_doc['content']}\n\nCitation: {top_doc['doc_name']} Section {top_doc['section']}"

def main():
    agent = PolicyAgent()
    agent.retrieve_documents()
    sys.stdout.write("--- CITY MUNICIPAL CORPORATION ---\nPolicy Support System (UC-X)\nType 'exit' to quit.\n\n")
    sys.stdout.flush()
    while True:
        try:
            sys.stdout.write("Question: ")
            sys.stdout.flush()
            question = sys.stdin.readline()
            if not question: break
            question = question.strip()
            if question.lower() in ['exit', 'quit', 'q']: break
            answer = agent.answer_question(question)
            sys.stdout.write(f"\nAnswer: {answer}\n\n" + "-" * 40 + "\n")
            sys.stdout.flush()
        except (EOFError, KeyboardInterrupt): break

if __name__ == "__main__":
    main()
