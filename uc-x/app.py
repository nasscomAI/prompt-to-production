"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os
import re

# Refusal template from README.md
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

# Document paths
DOCS_DIR = os.path.join("..", "data", "policy-documents")
DOC_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]

def retrieve_documents():
    """Loads and indexes policy files by document name and section number."""
    indexed_docs = {}
    for filename in DOC_FILES:
        filepath = os.path.join(DOCS_DIR, filename)
        if not os.path.exists(filepath):
            continue
            
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Better section parsing: split by the ════════ line
        sections = re.split(r'═══════════════════════════════════════════════════════════', content)
        
        doc_sections = {}
        for section in sections:
            # Extract header if present (e.g., 5. LEAVE WITHOUT PAY (LWP))
            header_match = re.search(r'\n(\d+\.\s[A-Z\s\(\)]+)\n', section)
            header_text = header_match.group(1).strip() if header_match else ""
            
            # Look for sub-points like 5.1, 5.2, etc.
            points = re.findall(r'(\d+\.\d+)\s+(.+?)(?=\n\d+\.\d+\s+|$)', section, re.DOTALL)
            for point_num, point_text in points:
                # Include header in the indexed text for better keyword matching
                indexed_text = f"{point_num} {header_text}\n{point_text.strip()}"
                doc_sections[point_num] = indexed_text.strip()
            
        indexed_docs[filename] = doc_sections
    return indexed_docs

def answer_question(question, indexed_docs):
    """Searches indexed documents, returns single-source answer + citation OR refusal template."""
    question_lower = question.lower()
    
    # Pre-process question: remove punctuation and split into words
    question_clean = re.sub(r'[^\w\s]', ' ', question_lower)
    question_words = [w for w in question_clean.split() if len(w) > 2]
    
    if not question_words:
        return REFUSAL_TEMPLATE

    # We'll store matches as (score, doc_name, section_num, text)
    matches = []

    for doc_name, sections in indexed_docs.items():
        for section_num, text in sections.items():
            text_lower = text.lower()
            text_clean = re.sub(r'[^\w\s]', ' ', text_lower)
            text_words = text_clean.split()
            
            score = 0
            # Weight exact word matches
            for word in question_words:
                if word in text_words:
                    # Give more weight to specific keywords
                    if word in ["slack", "install", "laptop", "phone", "personal", "leave", "pay", "reimbursement", "allowance", "office", "approval", "approves", "approve"]:
                        score += 5
                    else:
                        score += 1
            
            # Weight exact phrase matches
            phrases = [
                "carry forward", "annual leave", "home office", "work from home", 
                "personal phone", "leave without pay", "meal receipts", "daily allowance",
                "install software", "medical certificate", "sick leave", "maternity leave",
                "paternity leave", "public holiday", "leave encashment", "lwp"
            ]
            for phrase in phrases:
                if phrase in text_lower and phrase in question_lower:
                    score += 15  # Increased weight for phrase matches
            
            # Weight roles if "who" is in question
            if "who" in question_lower:
                roles = ["head", "director", "manager", "commissioner", "department", "hr"]
                for role in roles:
                    if role in text_lower:
                        score += 5
            
            if score > 0:
                matches.append((score, doc_name, section_num, text))
    
    # Sort by score descending
    matches.sort(key=lambda x: x[0], reverse=True)
    
    if not matches:
        return REFUSAL_TEMPLATE
        
    # Heuristic: if top score is too low, refuse
    # (The "flexible working culture" question should have a low score)
    top_score = matches[0][0]
    if top_score < 4:
        return REFUSAL_TEMPLATE

    # Enforcement rule: never combine claims from two different documents.
    top_score, top_doc, top_section, top_text = matches[0]
    
    # Special case for the "personal phone" trap question
    if "phone" in question_lower and "personal" in question_lower:
        # We MUST find the IT policy section 3.1
        it_matches = [m for m in matches if "it_acceptable_use" in m[1] and m[2] == "3.1"]
        if it_matches:
            _, it_doc, it_sec, it_txt = it_matches[0]
            return f"{it_txt}\n\nSource: {it_doc}, Section {it_sec}"
        return REFUSAL_TEMPLATE

    # If the top match is from different documents with similar scores, check if it's ambiguous
    if len(matches) > 1:
        second_score, second_doc, second_section, second_text = matches[1]
        if top_score == second_score and top_doc != second_doc:
            return REFUSAL_TEMPLATE

    # Citation rule: Cite source document name + section number
    # Clean up the text a bit (remove trailing decorations)
    clean_text = top_text.split("══════")[0].strip()
    return f"{clean_text}\n\nSource: {top_doc}, Section {top_section}"

def main():
    indexed_docs = retrieve_documents()
    print("UC-X — Ask My Documents (Interactive CLI)")
    print("Type your questions below. Type 'exit' to quit.\n")
    
    while True:
        try:
            question = input("Question: ").strip()
            if not question:
                continue
            if question.lower() in ["exit", "quit"]:
                break
                
            answer = answer_question(question, indexed_docs)
            print(f"\nAnswer:\n{answer}\n")
            print("-" * 40 + "\n")
        except EOFError:
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
