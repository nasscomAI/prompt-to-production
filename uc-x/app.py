import os
import re

# Refusal template — must be used EXACTLY when question is not covered
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)

# Hedging phrases that must NEVER appear
HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "as is standard",
    "usually",
    "in most cases",
    "commonly",
]

# Stop words to ignore
STOP_WORDS = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
              "have", "has", "had", "do", "does", "did", "will", "would", "could",
              "should", "may", "might", "must", "shall", "can", "need",
              "to", "of", "in", "for", "on", "with", "at", "by",
              "from", "as", "into", "through", "during", "before", "after", "above",
              "below", "between", "under", "and", "but", "or", "yet", "so", "if",
              "because", "although", "though", "while", "where", "when", "that",
              "which", "who", "whom", "whose", "what", "this", "these", "those",
              "i", "me", "my", "we", "our", "you", "your", "he", "him",
              "his", "she", "her", "it", "its", "they", "them", "their",
              "company", "cmc", "employee", "employees", "policy", "work", "working"}

# Document paths
POLICY_FILES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt",
]


def is_separator_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if re.match(r'^[\s\•\—\=\-\*\.▬║│├└┐┌┤┴┬┼═╬╦╩╠╣╗╝╚╔█▀▄▌▐░▒\•]{3,}$', stripped):
        return True
    return False


def is_section_header(line: str) -> bool:
    stripped = line.strip()
    return bool(re.match(r'^\d+\.\s+[A-Z]', stripped))


def parse_policy_file(file_path: str):
    doc_name = os.path.basename(file_path)
    
    if not os.path.exists(file_path):
        print(f"Warning: {file_path} not found.")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    sections = []
    current_clause_num = None
    current_clause_lines = []
    
    for raw_line in lines:
        line = raw_line.rstrip('\n').rstrip('\r')
        
        if is_separator_line(line):
            continue
        
        if is_section_header(line):
            if current_clause_num and current_clause_lines:
                clause_text = " ".join(current_clause_lines).strip()
                clause_text = re.sub(r'\s+', ' ', clause_text)
                sections.append({
                    "section_number": current_clause_num,
                    "section_text": clause_text,
                    "doc_name": doc_name
                })
            
            match = re.match(r'^(\d+)\.\s+(.*)$', line.strip())
            if match:
                current_clause_num = match.group(1)
                current_clause_lines = [match.group(2)]
            continue
        
        if current_clause_num:
            stripped = line.strip()
            if stripped:
                current_clause_lines.append(stripped)
    
    if current_clause_num and current_clause_lines:
        clause_text = " ".join(current_clause_lines).strip()
        clause_text = re.sub(r'\s+', ' ', clause_text)
        sections.append({
            "section_number": current_clause_num,
            "section_text": clause_text,
            "doc_name": doc_name
        })
    
    return sections


def retrieve_documents(file_paths: list) -> dict:
    index = {}
    for fp in file_paths:
        sections = parse_policy_file(fp)
        for sec in sections:
            key = (sec["doc_name"], sec["section_number"])
            index[key] = sec["section_text"]
    return index


def extract_content_words(text: str) -> set:
    """Extract meaningful words from text, excluding stop words."""
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    return {w for w in words if w not in STOP_WORDS}


def score_relevance(question: str, section_text: str) -> int:
    """
    Score how relevant a section is to the question.
    Higher score = more relevant.
    """
    q_lower = question.lower()
    text_lower = section_text.lower()
    
    # Extract content words
    q_words = extract_content_words(question)
    text_words = extract_content_words(section_text)
    
    # Direct content word overlap
    overlap = len(q_words & text_words)
    
    # Specific key term matching (higher weight)
    key_terms = {
        "leave": 2, "annual": 2, "sick": 2, "maternity": 2, "paternity": 2,
        "carry forward": 3, "forfeit": 3, "medical": 2, "certificate": 2,
        "LWP": 3, "loss of pay": 3, "public holiday": 2, "compensatory": 2,
        "grievance": 2, "encashment": 3, "retirement": 2,
        "install": 3, "software": 3, "laptop": 2, "device": 2,
        "corporate device": 3, "personal device": 4, "portal": 3, "email": 2,
        "endpoint": 2, "security": 2, "bandwidth": 2, "catalogue": 2,
        "reimbursement": 3, "travel": 2, "outstation": 2, "DA": 3,
        "daily allowance": 3, "meal": 3, "receipt": 3, "receipts": 3,
        "home office": 3, "allowance": 2, "equipment": 2,
        "claim": 2, "approve": 2, "approval": 2,
    }
    
    bonus = 0
    for term, weight in key_terms.items():
        if term in q_lower and term in text_lower:
            bonus += weight
    
    return overlap + bonus


def answer_question(question: str, index: dict) -> str:
    if not question.strip():
        return REFUSAL_TEMPLATE
    
    q_content = extract_content_words(question)
    
    # Score all sections
    scored = []
    for (doc_name, sec_num), text in index.items():
        score = score_relevance(question, text)
        if score > 0:
            scored.append({
                "doc_name": doc_name,
                "sec_num": sec_num,
                "text": text,
                "score": score
            })
    
    if not scored:
        return REFUSAL_TEMPLATE
    
    scored.sort(key=lambda x: x["score"], reverse=True)
    top = scored[0]
    
    # STRICT: Must have score >= 5 to be considered a match
    if top["score"] < 5:
        return REFUSAL_TEMPLATE
    
    # STRICT: At least 2 content words from question must appear in the answer text
    text_content = extract_content_words(top["text"])
    shared = q_content & text_content
    if len(shared) < 2:
        return REFUSAL_TEMPLATE
    
    # Check for hedging
    answer = f"According to {top['doc_name']} (Section {top['sec_num']}):\n\n{top['text']}"
    for hedge in HEDGING_PHRASES:
        if hedge.lower() in answer.lower():
            return REFUSAL_TEMPLATE
    
    return answer


def main():
    print("=" * 60)
    print("UC-X — Ask My Documents")
    print("=" * 60)
    print("Loading policy documents...")
    
    index = retrieve_documents(POLICY_FILES)
    print(f"Loaded {len(index)} sections from {len(POLICY_FILES)} documents.")
    print("\nType your question below. Type 'exit' to quit.\n")
    
    while True:
        try:
            question = input("Q> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
        
        if question.lower() in ["exit", "quit", "q"]:
            print("Goodbye.")
            break
        
        if not question:
            continue
        
        answer = answer_question(question, index)
        print(f"\nA> {answer}\n")
        print("-" * 60)


if __name__ == "__main__":
    main()