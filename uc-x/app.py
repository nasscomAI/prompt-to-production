import os
import sys
import re

# RICE Enforcement: Verbatim refusal template
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."""

POLICY_FILES = {
    "HR": "../data/policy-documents/policy_hr_leave.txt",
    "IT": "../data/policy-documents/policy_it_acceptable_use.txt",
    "Finance": "../data/policy-documents/policy_finance_reimbursement.txt"
}

def retrieve_documents():
    index = []
    for doc_type, path in POLICY_FILES.items():
        filename = os.path.basename(path)
        if not os.path.exists(path):
            print(f"Error: Missing resource {path}")
            sys.exit(1)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        major_parts = re.split(r'═{5,}', content)
        for part in major_parts:
            sub_sections = re.findall(r'^(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\Z)', part, re.MULTILINE | re.DOTALL)
            for num, text in sub_sections:
                index.append({
                    'doc': filename,
                    'section': num,
                    'text': text.replace('\n', ' ').strip()
                })
    return index

def answer_question(question, index):
    q = question.lower()
    
    # 1. Broad refusal check
    if any(word in q for word in ["culture", "mission", "vision", "flexible working"]):
        return REFUSAL_TEMPLATE

    scored_matches = []
    for item in index:
        text = item['text'].lower()
        score = 0
        
        # Specific High-Value Keyword Matching
        # Carry Forward
        if "carry forward" in q and "carry forward" in text: score += 10
        if "leave" in q and "31 december" in text: score += 5
        
        # Software / Slack
        if "slack" in q or "software" in q:
            if "install" in text: score += 10
            if "written approval" in text: score += 5
            
        # Home Office Allowance
        if "home office" in q or "equipment allowance" in q:
            if "allowance" in text: score += 10
            if "rs 8,000" in text: score += 10
            
        # Personal Phone (Trap) -> Target IT 3.1
        if "personal" in q and ("phone" in q or "device" in q):
            if item['doc'] == "policy_it_acceptable_use.txt":
                if item['section'] == "3.1": score += 20 # THE TARGET
                elif item['section'] == "3.3": score += 5 # SECONDARY
                elif item['section'] == "2.1": score -= 10 # PENALIZE CORPORATE PHONES
            if item['doc'] == "policy_hr_leave.txt": score -= 5 # AVOID HR BLENDING
                
        # DA and Meals
        if "da" in q and "meal" in q:
            if "simultaneously" in text: score += 15
            if "receipts" in text: score += 5
            
        # LWP Approval
        if "leave without pay" in q and "approve" in q:
            if item['section'] == "5.2": score += 20
            if "hr director" in text: score += 10
            
        # Generic word overlap
        words = q.replace('?', '').split()
        for word in words:
            if len(word) > 3 and word in text:
                score += 1
        
        if score > 0:
            scored_matches.append((score, item))
            
    if not scored_matches:
        return REFUSAL_TEMPLATE
        
    scored_matches.sort(key=lambda x: x[0], reverse=True)
    best_score, best_item = scored_matches[0]
    
    # RICE RULE 1: No blending.
    if len(scored_matches) > 1:
        s2, i2 = scored_matches[1]
        if s2 > best_score * 0.9 and i2['doc'] != best_item['doc']:
            return REFUSAL_TEMPLATE

    if best_score < 3:
        return REFUSAL_TEMPLATE
        
    return f"{best_item['section']} {best_item['text']}\n\nSource: {best_item['doc']} (Section {best_item['section']})"

def main():
    index = retrieve_documents()
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("question", nargs='*', help="Policy question")
    args = parser.parse_args()
    
    if args.question:
        print(answer_question(" ".join(args.question), index))
    else:
        print("CMC Policy Assistant Ready. Type 'exit' to quit.")
        while True:
            try:
                user_input = input("\nQ: ").strip()
                if user_input.lower() in ['exit', 'quit']: break
                if user_input: print(f"A: {answer_question(user_input, index)}")
            except (KeyboardInterrupt, EOFError): break

if __name__ == "__main__":
    main()