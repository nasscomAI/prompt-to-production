import os
import re
import sys

# Ensure UTF-8 output even on Windows terminals
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# UC-X Configuration
DATA_DIR = os.path.join("..", "data", "policy-documents")
POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

class UCXAgent:
    def __init__(self):
        self.documents = {}
        self.load_documents()

    def load_documents(self):
        """Skill: retrieve_documents"""
        for filename in POLICY_FILES:
            path = os.path.join(DATA_DIR, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.documents[filename] = self.parse_sections(content)
            except FileNotFoundError:
                print(f"Error: Missing mandatory file {filename}")
                self.documents[filename] = {}

    def parse_sections(self, content):
        """Parses document into a dictionary of sections including sub-sections"""
        sections = {}
        # Match major headers (e.g., 2. ANNUAL LEAVE) or sub-sections (e.g., 2.1 Content)
        # We look for numbers at the start of lines followed by text
        matches = list(re.finditer(r'^([0-9]+(?:\.[0-9]+)?)\.?\s+(.*)', content, re.MULTILINE))
        
        for i, match in enumerate(matches):
            section_id = match.group(1)
            start = match.start()
            # The section ends where the next numbered section starts
            end = matches[i+1].start() if i+1 < len(matches) else len(content)
            section_content = content[start:end].strip()
            # Clean up formatting characters
            section_content = re.sub(r'[═─]{3,}', '', section_content).strip()
            sections[section_id] = section_content
            
        return sections

    def answer_question(self, question):
        """Skill: answer_question"""
        q_clean = question.lower()
        
        # Simple stemming/normalization (e.g., handles 'approves', 'approval' -> 'approv')
        def normalize(word):
            word = word.strip()
            if len(word) > 4:
                if word.endswith('s'): word = word[:-1]
                if word.endswith('ing'): word = word[:-3]
                if word.endswith('ed'): word = word[:-2]
                if word.endswith('al'): word = word[:-2]
            return word

        # Handle acronyms and common terms
        if 'lwp' in q_clean or 'leave without pay' in q_clean:
            q_clean += " lwp leave without pay"
        if 'wfh' in q_clean or 'work from home' in q_clean:
            q_clean += " wfh work from home"
        if 'byod' in q_clean or 'personal device' in q_clean:
            q_clean += " byod personal phone device"
            
        stop_words = {'the', 'a', 'can', 'i', 'to', 'for', 'is', 'in', 'on', 'of', 'and', 'with', 'at', 'by', 'from', 'my', 'your', 'any', 'who', 'what', 'which', 'do'}
        raw_keywords = [kw for kw in re.findall(r'\w+', q_clean) if kw not in stop_words]
        norm_keywords = [normalize(kw) for kw in raw_keywords]
        
        if not norm_keywords:
            return REFUSAL_TEMPLATE

        matches = []
        for doc_name, sections in self.documents.items():
            for section_id, content in sections.items():
                content_lower = content.lower()
                content_words = [normalize(w) for w in re.findall(r'\w+', content_lower)]
                
                score = 0
                unique_matches = 0
                for kw in norm_keywords:
                    if kw in content_words:
                        unique_matches += 1
                        score += 5
                        # Bonus for whole word match of original keyword
                        if any(rk in content_lower for rk in raw_keywords if normalize(rk) == kw):
                            score += 5
                
                # Critical TRAP: Personal phone/device context
                # Section 3.1 in IT policy is about personal devices.
                # Section 2.1 in IT policy is about corporate devices.
                # If question is about 'personal', strictly penalize 'corporate' sections and vice versa.
                has_personal_q = any(x in q_clean for x in ['personal', 'own', 'byod'])
                has_corporate_q = any(x in q_clean for x in ['company', 'work', 'corporate', 'issued'])
                
                if has_personal_q and 'corporate device' in content_lower:
                    score = score // 4
                if has_personal_q and 'issued by cmc' in content_lower:
                    score = score // 4
                if has_corporate_q and 'personal device' in content_lower:
                    score = score // 4

                if score > 0:
                    matches.append({
                        "doc": doc_name,
                        "id": section_id,
                        "content": content,
                        "score": score,
                        "unique": unique_matches
                    })

        # Sort by unique matches primarily, then score
        matches.sort(key=lambda x: (x['unique'], x['score']), reverse=True)

        if not matches or matches[0]['unique'] < 2: # Must match at least 2 unique normalized keywords
            return REFUSAL_TEMPLATE

        best = matches[0]
        
        # Blending Detection: If top matches from different docs have very similar keyword overlap
        competing_sources = {m['doc'] for m in matches if m['unique'] >= best['unique'] and m['score'] >= best['score'] * 0.7}
        if len(competing_sources) > 1:
            # Check if this is the personal device trap (IT has specific answer, HR mentions work tools)
            # If IT has a strong match, we should probably prefer it over generic HR mentions
            # unless it's genuinely ambiguous.
            if len(competing_sources) == 2 and 'policy_it_acceptable_use.txt' in competing_sources:
                # Prioritize IT for device questions
                it_matches = [m for m in matches if m['doc'] == 'policy_it_acceptable_use.txt']
                if it_matches and it_matches[0]['unique'] >= best['unique']:
                    best = it_matches[0]
                else:
                    return REFUSAL_TEMPLATE
            else:
                return REFUSAL_TEMPLATE

        return f"{best['content']}\n\nSource: {best['doc']} (Section {best['id']})"

def main():
    agent = UCXAgent()
    print("UC-X Policy Information Retrieval Agent")
    print("---------------------------------------")
    print(f"Loaded {len(POLICY_FILES)} policy documents.")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            # Use sys.stdin.readline for more reliable input on some consoles
            sys.stdout.write("Question: ")
            sys.stdout.flush()
            query = sys.stdin.readline().strip()
            
            if query.lower() in ['exit', 'quit']:
                break
            if not query:
                continue
            
            response = agent.answer_question(query)
            sys.stdout.write(f"\nAnswer:\n{response}\n\n")
            sys.stdout.write("-" * 40 + "\n")
            sys.stdout.flush()
        except EOFError:
            break
        except Exception as e:
            sys.stdout.write(f"Error: {e}\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
