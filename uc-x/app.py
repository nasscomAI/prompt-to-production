import os
import re
import sys

# Constants and Refusal Template as per README.md and agents.md
POLICY_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents"))
FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

STOP_WORDS = {'a', 'an', 'the', 'and', 'or', 'to', 'for', 'in', 'on', 'at', 'with', 'by', 'of', 'i', 'my', 'is', 'it', 'what', 'when', 'where', 'who'}

def clean_word(word):
    """Clean and normalize words for matching."""
    word = word.lower().strip()
    # Handle common suffixes
    if len(word) > 4:
        if word.endswith('s'): word = word[:-1]
        elif word.endswith('ing'): word = word[:-3]
        elif word.endswith('ed'): word = word[:-2]
        elif word.endswith('al'): word = word[:-2]
    # Normalize variants
    if word == 'approv': return 'approv'
    if word == 'approve': return 'approv'
    if word == 'approval': return 'approv'
    return word

class DocStore:
    """Skill: retrieve_documents"""
    def __init__(self):
        self.documents = {}
        self.load_documents()

    def load_documents(self):
        """Loads all 3 policy files and indexes them by document name and section number."""
        for filename in FILES:
            path = os.path.join(POLICY_DIR, filename)
            if not os.path.exists(path):
                continue
            
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                self.documents[filename] = self.parse_sections(content)

    def parse_sections(self, content):
        """Robust section parser for CMC policy documents with hierarchical inheritance."""
        sections = []
        lines = content.split('\n')
        current_section = None
        current_major_header = ""
        
        for line in lines:
            line = line.strip()
            # Skip empty lines or separator lines (Unicode or ASCII)
            if not line or any(c in '═=-' for c in line[:3]):
                continue
                
            # Detect major section header (e.g., 2. ANNUAL LEAVE)
            major_match = re.match(r'^(\d+)\.\s+([A-Z\s\(\)]+)$', line)
            # Detect subsection (e.g., 2.6 Employees may...)
            sub_match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
            
            if major_match:
                current_major_header = line
                current_section = {
                    'id': major_match.group(1),
                    'text': line,
                    'context': "",
                    'type': 'major'
                }
                sections.append(current_section)
            elif sub_match:
                current_section = {
                    'id': sub_match.group(1),
                    'text': line,
                    'context': current_major_header,
                    'type': 'sub'
                }
                sections.append(current_section)
            elif current_section is not None and not line.startswith('CITY') and not line.startswith('Document'):
                current_section['text'] += " " + line
                    
        return sections

class PolicyAssistant:
    """Skill: answer_question"""
    def __init__(self, store):
        self.store = store
        self.synonyms = {
            'lwp': ['leave', 'without', 'pay'],
            'da': ['daily', 'allowance'],
            'laptop': ['device', 'computer', 'corporate', 'laptop'],
            'phone': ['device', 'mobile', 'personal', 'phone'],
            'slack': ['software', 'application', 'install', 'slack'],
            'software': ['install', 'software'],
            'equipment': ['allowance', 'office'],
            'approv': ['approv', 'approval', 'approve'],
            'allowance': ['reimbursement', 'claim']
        }
        # Document boosters with higher weights for critical keywords
        self.boosters = {
            'policy_hr_leave.txt': ['leave', 'sick', 'maternity', 'paternity', 'annual', 'retirement', 'resignation', 'grievance'],
            'policy_it_acceptable_use.txt': ['device', 'laptop', 'software', 'install', 'password', 'data', 'email', 'network', 'phone', 'access', 'file', 'personal', 'slack'],
            'policy_finance_reimbursement.txt': ['claim', 'reimbursement', 'allowance', 'travel', 'hotel', 'receipt', 'expense', 'bill', 'rs', 'meal', 'da']
        }

    def get_words(self, text):
        """Extract and clean words from text, including synonym expansion."""
        text = text.lower()
        raw_words = re.findall(r'\w+', text)
        words = {clean_word(w) for w in raw_words if w not in STOP_WORDS}
        
        # Add synonyms to the word set
        extra = set()
        for key, syns in self.synonyms.items():
            if key in text:
                for s in syns:
                    extra.add(clean_word(s))
        return words.union(extra)

    def answer(self, query):
        """Searches indexed documents to return a single-source answer + citation OR refusal."""
        query_words = self.get_words(query)
        if not query_words:
            return REFUSAL_TEMPLATE

        results = []
        for filename, sections in self.store.documents.items():
            # Calculate document boost based on raw query content
            doc_boost = 0
            for keyword in self.boosters.get(filename, []):
                if keyword in query.lower():
                    doc_boost += 1.0 # Stronger boost

            for section in sections:
                # Combine section text with its parent context
                search_text = section['text'] + " " + section['context']
                section_words = self.get_words(search_text)
                
                overlap_count = len(query_words.intersection(section_words))
                if overlap_count > 0:
                    # Give extra weight to section text matches over context matches
                    text_only_words = self.get_words(section['text'])
                    text_overlap = len(query_words.intersection(text_only_words))
                    
                    score = overlap_count + text_overlap + doc_boost
                    if section['type'] == 'sub':
                        score += 0.5
                    
                    results.append({
                        'score': score,
                        'filename': filename,
                        'section': section['id'],
                        'text': section['text']
                    })

        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)

        # Enforcement: Threshold check
        if not results or results[0]['score'] < 3.0: 
            return REFUSAL_TEMPLATE

        # Enforcement: Single-source check
        best = results[0]
        if len(results) > 1:
            second = results[1]
            # Use a slightly wider margin for ambiguity
            if abs(best['score'] - second['score']) < 0.3 and best['filename'] != second['filename']:
                return REFUSAL_TEMPLATE

        # Format citation: [filename, Section ID]
        citation = f"[{best['filename']}, Section {best['section']}]"
        
        # Clean header from result text
        output_text = re.sub(r'^\d+(\.\d+)?\.?\s*', '', best['text'])
        
        return f"{output_text.strip()} {citation}"



def main():
    try:
        store = DocStore()
    except Exception as e:
        print(f"Error loading documents: {e}")
        return

    assistant = PolicyAssistant(store)

    print("--- CITY MUNICIPAL CORPORATION POLICY ASSISTANT ---")
    print("Type your question or 'exit' to quit.")
    
    while True:
        try:
            query = input("\nQuery: ").strip()
            if query.lower() in ['exit', 'quit']:
                break
            if not query:
                continue
                
            response = assistant.answer(query)
            print(f"Answer: {response}")
            
        except (EOFError, KeyboardInterrupt):
            break

if __name__ == "__main__":
    main()


