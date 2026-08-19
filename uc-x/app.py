import os
import sys
import re

# Refusal Template as defined in agents.md and README
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

# Hedging phrases to ban in enforcement (Rule 2)
HEDGING_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice"
]

# STOP WORDS to remove from query before scoring/coverage check
STOP_WORDS = {
    "what", "is", "the", "company", "view", "on", "can", "for", "and", "how", "much", 
    "when", "who", "why", "are", "you", "your", "should", "please", "about", "that", 
    "this", "available", "under", "with", "from", "any", "must", "all", "its", "each",
    "being", "been", "was", "were", "has", "had", "will", "would", "could", "their"
}

# Section header regex (e.g., 2.3 or Section 2.3)
RE_SECTION = re.compile(r'^\s*(?:Section\s+)?(\d+(?:\.\d+)?)\s*[:.-]?\s*(.*)$', re.IGNORECASE)

def retrieve_documents(file_paths):
    """
    Skill 1: loads all 3 policy files, indexes by document name and section number.
    Segments files into individual numbered sections for granular citation.
    """
    index = {}
    
    for path in file_paths:
        abs_path = os.path.abspath(path)
        base_name = os.path.basename(path)
        
        if not os.path.exists(abs_path):
            print(f"Error: Mandatory policy file {base_name} missing at {abs_path}")
            sys.exit(1)
            
        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            sections = []
            current_section = None
            
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue
                
                # Ignore decorative dividers
                if all(c in ('═', '─', ' ', '\t') for c in stripped):
                    continue
                    
                match = RE_SECTION.match(stripped)
                if match:
                    if current_section:
                        current_section["content"] = current_section["content"].strip()
                        sections.append(current_section)
                    
                    current_section = {
                        "number": match.group(1),
                        "title": match.group(2).strip(),
                        "content": stripped + "\n"
                    }
                elif current_section:
                    current_section["content"] += line
            
            if current_section:
                current_section["content"] = current_section["content"].strip()
                sections.append(current_section)
                
            if not sections:
                index[base_name] = [{"number": "1", "title": "Full Document", "content": "".join(lines).strip()}]
            else:
                index[base_name] = sections
                
        except Exception as e:
            print(f"Error reading {base_name}: {e}")
            sys.exit(1)
    
    return index

def answer_question(question, index):
    """
    Skill 2: searches indexed data for a single-source match.
    Enforces R.I.C.E rules including accurate retrieval and refusal for gaps.
    """
    question_lower = question.lower()
    
    # Technical Keywords Weights
    token_weights = {
        "install": 20, "software": 20, "slack": 25, "phone": 15, "mobile": 15,
        "files": 20, "confidential": 20, "reimburse": 20, "allowance": 20,
        "leave": 15, "annual": 15, "sick": 15, "grievance": 15, "carry": 20,
        "encash": 20, "da": 25, "approved": 10, "written": 10, "it": 10
    }
    
    # Tokenize and filter stop words
    all_tokens = re.findall(r'[a-z0-9]{2,}', question_lower)
    core_tokens = [t for t in all_tokens if t not in STOP_WORDS]
    unique_core_tokens = set(core_tokens)
    
    if not unique_core_tokens:
        return REFUSAL_TEMPLATE

    matches = []

    for doc_name, sections in index.items():
        for sec in sections:
            content_lower = sec["content"].lower()
            title_lower = sec["title"].lower()
            
            # Coverage Check
            matched_tokens = {t for t in unique_core_tokens if t in content_lower}
            coverage_ratio = len(matched_tokens) / len(unique_core_tokens)
            
            score = 0
            for token in matched_tokens:
                weight = token_weights.get(token, 2)
                # Matches in title are extremely important
                if token in title_lower:
                    score += weight * 30
                # Matches in content
                score += weight * content_lower.count(token)
            
            if score > 0:
                # Specificity bonus
                final_score = score / (1 + (len(sec["content"]) / 1200))
                
                matches.append({
                    "doc": doc_name,
                    "section": sec["number"],
                    "content": sec["content"],
                    "score": final_score,
                    "coverage": coverage_ratio,
                    "matched_count": len(matched_tokens)
                })
    
    matches.sort(key=lambda x: x["score"], reverse=True)
    if not matches:
        return REFUSAL_TEMPLATE
        
    best = matches[0]
    
    # STRICT REFUSAL LOGIC (Rule 3)
    # 1. Coverage check: If the query has multiple core words, we need at least 50% coverage.
    if len(unique_core_tokens) >= 2 and best["coverage"] < 0.5:
        return REFUSAL_TEMPLATE
    
    # 2. Score threshold: Ensure the match is actually meaningful
    if best["score"] < 15.0:
        return REFUSAL_TEMPLATE
    
    # Rule 1 Enforcement: Blending Trap (scores too close across docs)
    if len(matches) > 1:
        second = matches[1]
        if second["doc"] != best["doc"] and (best["score"] - second["score"]) / best["score"] < 0.30:
            return REFUSAL_TEMPLATE

    # Rule 2 Enforcement: No hedging.
    best_content_clean = best["content"].lower()
    for phrase in HEDGING_PHRASES:
        if phrase in best_content_clean:
            return REFUSAL_TEMPLATE
            
    # Success Citation Format
    doc_display = best["doc"].replace("policy_", "").replace(".txt", "").replace("_", " ").upper()
    return f"{best['content']}\n\nCitation: {doc_display} Section {best['section']}"

def main():
    if hasattr(sys.stdin, 'reconfigure'):
        sys.stdin.reconfigure(encoding='utf-8')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_paths = [
        os.path.join(script_dir, "../data/policy-documents/policy_hr_leave.txt"),
        os.path.join(script_dir, "../data/policy-documents/policy_it_acceptable_use.txt"),
        os.path.join(script_dir, "../data/policy-documents/policy_finance_reimbursement.txt")
    ]
    
    index = retrieve_documents(input_paths)
    print("UC-X Policy Document Assistant - Ready")
    
    while True:
        try:
            query = input("\nQ: ").strip()
            if query.lower() in ('exit', 'quit'):
                break
            if not query:
                continue
                
            ans = answer_question(query, index)
            print(f"\nA: {ans}")
            
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
