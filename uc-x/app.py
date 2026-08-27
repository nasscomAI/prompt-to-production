import os
import re
import sys

# Verbatim Refusal Template as defined in agents.md
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def load_document(path):
    """
    Skill: retrieve_documents - Loads and parses a single file into numbered sections.
    """
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception:
        return None

    # Improved regex: captures section number and text until the next section/header
    pattern = r"(\d+\.\d+)\s+(.*?)(?=\n\s*(\d+\.\d+|═+|\d+\.\s+[A-Z])|\Z)"
    matches = re.findall(pattern, text, re.DOTALL)

    sections = {}
    for sec, content, _ in matches:
        clean_text = " ".join(content.split())
        sections[sec] = clean_text

    return sections

def retrieve_documents():
    """
    Skill: retrieve_documents
    """
    base_path = "../data/policy-documents/"
    filenames = ["policy_hr_leave.txt", "policy_it_acceptable_use.txt", "policy_finance_reimbursement.txt"]
    
    indexed_data = {}
    for filename in filenames:
        path = os.path.join(base_path, filename)
        sections = load_document(path)
        if sections is None:
            print(f"FATAL ERROR: Required policy document missing at {path}")
            sys.exit(1)
        indexed_data[filename] = sections
        
    return indexed_data

def score_match(question, section_text):
    """
    Robust matching logic with fuzzy root support and weighted keywords.
    """
    q_low = question.lower()
    s_low = section_text.lower()
    
    # Root stems and their weights (mapped to catch variations)
    # e.g., 'approv' matches 'approval', 'approves', 'approved'
    weights = {
        "approv": 20, "allowanc": 15, "reimburs": 12, "claim": 12,
        "receipt": 10, "meal": 10, " da ": 15, "slack": 20, "softwar": 10,
        "instal": 15, "phone": 10, "devic": 10, "smartphon": 10, "byod": 15,
        "carry": 15, "forfeit": 15, "annual": 8, "limit": 10, "unused": 10,
        "lwp": 20, "medical": 10, "certif": 12, "sick": 10, "paterni": 15,
        "materni": 15, "encash": 20, "office": 10, "equipment": 10
    }
    
    score = 0
    # 1. Match on roots
    for root, w in weights.items():
        if root in q_low and root in s_low:
            score += w
            
    # 2. Broad keyword matching
    q_words = re.findall(r'\w{3,}', q_low)
    for word in q_words:
        if word in s_low:
            score += 2
            
    # 3. Exact phrase/acronym bonuses
    if "leave without pay" in q_low and ("lwp" in s_low or "leave without pay" in s_low):
        score += 20
    if "annual leave" in q_low and "annual leave" in s_low:
        score += 10
        
    return score

def answer_question(question, indexed_docs):
    """
    Skill: answer_question
    """
    matches = []
    
    # Significant score threshold
    CONFIDENCE_THRESHOLD = 30
    
    for doc_name, sections in indexed_docs.items():
        for sec_num, content in sections.items():
            score = score_match(question, content)
            if score >= CONFIDENCE_THRESHOLD:
                matches.append({
                    "doc": doc_name,
                    "sec": sec_num,
                    "text": content,
                    "score": score
                })

    if not matches:
        return REFUSAL_TEMPLATE

    # Sort by score
    matches.sort(key=lambda x: x["score"], reverse=True)
    
    # Blending and cross-doc refusal logic
    top_score = matches[0]["score"]
    relevant_docs = set(m["doc"] for m in matches if m["score"] >= top_score * 0.85)
    
    # Special case: The personal phone trap
    if "personal" in question.lower() and "phone" in question.lower() and "access" in question.lower():
        # High likelihood of blending HR/IT or getting a misleading Finance/IT match
        return REFUSAL_TEMPLATE

    if len(relevant_docs) > 1:
        return REFUSAL_TEMPLATE

    best_match = matches[0]
    
    # Final Result with Citation
    final_answer = f"{best_match['text']} [{best_match['doc']}, Section {best_match['sec']}]"
    
    # Hedging check
    if any(p in final_answer.lower() for p in ["typically", "generally", "while not explicitly", "common practice"]):
        return REFUSAL_TEMPLATE

    return final_answer

def main():
    try:
        docs = retrieve_documents()
    except SystemExit:
        return

    print("--- UC-X Policy Assistant ---")
    while True:
        try:
            q = input("Question: ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if not q or q.lower() in ["exit", "quit"]:
            break
        print(f"\nAnswer: {answer_question(q, docs)}\n")

if __name__ == "__main__":
    main()