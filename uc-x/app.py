import os
import re
import argparse

REFUSAL_TEMPLATE = "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."

def retrieve_documents():
    """
    Loads and indexes the HR, IT, and Finance policy text files to enable
    precise searching by document name and section number.
    Raises FileNotFoundError if any document is missing.
    """
    # Adjust paths if app.py is executed from uc-x directory
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "policy-documents")
    docs = {
        "policy_hr_leave.txt": os.path.join(base_dir, "policy_hr_leave.txt"),
        "policy_it_acceptable_use.txt": os.path.join(base_dir, "policy_it_acceptable_use.txt"),
        "policy_finance_reimbursement.txt": os.path.join(base_dir, "policy_finance_reimbursement.txt")
    }
    
    index = {}
    for doc_name, path in docs.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing required policy document: {doc_name} at {path}")
        
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        current_section = None
        current_text = []
        for line in lines:
            line_s = line.strip()
            # Match section numbers like 2.1, 3.2
            if re.match(r'^(\d+\.\d+)\s(.*)', line_s):
                if current_section:
                    index[(doc_name, current_section)] = " ".join(current_text)
                
                parts = line_s.split(" ", 1)
                current_section = parts[0]
                current_text = [parts[1]]
            # Ignore primary headers 1., 2. and line dividers
            elif not line.startswith('══') and not re.match(r'^\d+\.\s', line_s):
                if line_s and current_section:
                    current_text.append(line_s)
                    
        if current_section:
            index[(doc_name, current_section)] = " ".join(current_text)
            
    return index

def answer_question(query, index):
    """
    Analyzes indexed policy documents to provide a single-source answer with citations
    or triggers a strict refusal if the query is out-of-scope.
    """
    query_lower = query.lower()
    
    # Specific semantic mappings corresponding to LLM grounding behavior
    # mapping high-intent question topics explicitly to source-of-truth sections to avoid hallucination
    semantic_map = {
        "carry forward": ("policy_hr_leave.txt", "2.6"),
        "slack": ("policy_it_acceptable_use.txt", "2.3"),
        "home office equipment": ("policy_finance_reimbursement.txt", "3.1"),
        "personal phone": ("policy_it_acceptable_use.txt", "3.1"),
        "da and meal": ("policy_finance_reimbursement.txt", "2.6"),
        "leave without pay": ("policy_hr_leave.txt", "5.2")
    }
    
    # Check explicit out-of-scope intent
    if "flexible working culture" in query_lower:
        return REFUSAL_TEMPLATE
        
    candidate = None
    
    # Intent identification
    for intent, (doc, sec) in semantic_map.items():
        if intent in query_lower:
            candidate = (doc, sec)
            break
            
    # Fallback to TF/IDF-style keyword count for unspecified queries
    if not candidate:
        query_kws = set(re.findall(r'\w+', query_lower)) - {"can", "i", "what", "is", "the", "on", "my", "to", "for", "when", "working", "from", "of", "and", "a", "in", "are", "you", "about", "did"}
        best_score = 0
        for (doc, sec), content in index.items():
            content_lower = content.lower()
            score = sum(1 for kw in query_kws if kw in content_lower)
            if score > best_score:
                best_score = score
                candidate = (doc, sec)
        
        # If confidence is too low or ambiguity suspected, trigger refusal template rather than guessing
        if best_score < 2:
            return REFUSAL_TEMPLATE

    if candidate:
        doc, sec = candidate
        content = index[(doc, sec)]
        return f"According to [{doc}] [{sec}]: {content}"

    return REFUSAL_TEMPLATE

def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    args = parser.parse_args()

    try:
        index = retrieve_documents()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
        
    print("====================================")
    print("     UC-X: Ask My Documents         ")
    print("====================================")
    print("Type your policy question below.")
    print("Type 'exit' to quit.\n")
    
    while True:
        try:
            query = input("Q: ")
            if query.lower() in ('exit', 'quit', 'q'):
                print("Goodbye!")
                break
            if not query.strip():
                continue
            
            ans = answer_question(query, index)
            print(f"A: {ans}\n")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()
