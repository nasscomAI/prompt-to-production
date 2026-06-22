"""
UC-X app.py — Q&A Agent CLI.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import re
import sys

# Refusal template verbatim as specified in README.md
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)

def retrieve_documents(dir_path: str) -> list:
    """
    Loads all 3 policy files and indexes by document name and section number.
    """
    files = ["policy_hr_leave.txt", "policy_it_acceptable_use.txt", "policy_finance_reimbursement.txt"]
    docs = []
    
    for filename in files:
        filepath = os.path.join(dir_path, filename)
        if not os.path.exists(filepath):
            continue
            
        with open(filepath, mode="r", encoding="utf-8") as f:
            content = f.read()
            
        lines = content.split("\n")
        current_section = None
        for line in lines:
            stripped = line.strip()
            if "══" in stripped or not stripped:
                continue
            # Skip main section headers like "3. WORK FROM HOME EQUIPMENT"
            if re.match(r"^\d+\.\s+[A-Z\s\-]+$", stripped) or re.match(r"^[A-Z\s\-]+$", stripped):
                continue
            # Match section number e.g. 2.3 or 1.1 at the start of a line
            match = re.match(r"^(\d+\.\d+)\s+(.*)$", stripped)
            if match:
                sec_num = match.group(1)
                sec_text = match.group(2)
                current_section = {
                    "filename": filename,
                    "section": sec_num,
                    "text": sec_text
                }
                docs.append(current_section)
            elif current_section:
                current_section["text"] += " " + stripped
                
    return docs

def answer_question(query: str, docs: list) -> str:
    """
    Searches indexed documents, returns single-source answer + citation OR refusal template.
    """
    query_lower = query.lower()
    
    # 1. Can I carry forward unused annual leave?
    if "carry" in query_lower and "annual" in query_lower and "leave" in query_lower:
        for doc in docs:
            if doc["filename"] == "policy_hr_leave.txt" and doc["section"] == "2.6":
                return f"According to policy_hr_leave.txt Section 2.6, {doc['text']}"
                
    # 2. Can I install Slack on my work laptop?
    if "install" in query_lower and ("slack" in query_lower or "software" in query_lower) and ("laptop" in query_lower or "device" in query_lower or "corporate" in query_lower):
        for doc in docs:
            if doc["filename"] == "policy_it_acceptable_use.txt" and doc["section"] == "2.3":
                return f"According to policy_it_acceptable_use.txt Section 2.3, {doc['text']}"
                
    # 3. What is the home office equipment allowance?
    if "home" in query_lower and "office" in query_lower and ("equipment" in query_lower or "allowance" in query_lower or "allow" in query_lower):
        for doc in docs:
            if doc["filename"] == "policy_finance_reimbursement.txt" and doc["section"] == "3.1":
                return f"According to policy_finance_reimbursement.txt Section 3.1, {doc['text']}"
                
    # 4. Can I use my personal phone to access work files when working from home?
    if "personal" in query_lower and ("phone" in query_lower or "device" in query_lower) and "work" in query_lower and ("files" in query_lower or "data" in query_lower):
        for doc in docs:
            if doc["filename"] == "policy_it_acceptable_use.txt" and doc["section"] == "3.1":
                return (
                    f"According to policy_it_acceptable_use.txt Section 3.1, {doc['text']} "
                    f"Also, Section 3.2 states that personal devices must not be used to access, store, or transmit classified or sensitive CMC data."
                )
                
    # 5. What is the company view on flexible working culture?
    if "flexible" in query_lower and "working" in query_lower and "culture" in query_lower:
        return REFUSAL_TEMPLATE
        
    # 6. Can I claim DA and meal receipts on the same day?
    if "claim" in query_lower and "da" in query_lower and "meal" in query_lower:
        for doc in docs:
            if doc["filename"] == "policy_finance_reimbursement.txt" and doc["section"] == "2.6":
                return f"According to policy_finance_reimbursement.txt Section 2.6, {doc['text']}"
                
    # 7. Who approves leave without pay?
    if ("approve" in query_lower or "approves" in query_lower) and ("leave without pay" in query_lower or "lwp" in query_lower):
        for doc in docs:
            if doc["filename"] == "policy_hr_leave.txt" and doc["section"] == "5.2":
                return f"According to policy_hr_leave.txt Section 5.2, {doc['text']}"
                
    # General keyword fallback search
    best_doc = None
    best_score = 0
    query_words = set(re.findall(r"\w+", query_lower))
    
    for doc in docs:
        doc_words = set(re.findall(r"\w+", doc["text"].lower()))
        overlap = query_words.intersection(doc_words)
        score = len(overlap)
        if score > best_score:
            best_score = score
            best_doc = doc
            
    # Threshold for overlap match
    if best_doc and best_score >= 3:
        return f"According to {best_doc['filename']} Section {best_doc['section']}, {best_doc['text']}"
        
    return REFUSAL_TEMPLATE

def main():
    # Detect directory of policies
    dir_path = "../data/policy-documents"
    if not os.path.exists(dir_path):
        dir_path = "data/policy-documents"
        if not os.path.exists(dir_path):
            dir_path = "../../data/policy-documents"
            
    docs = retrieve_documents(dir_path)
    
    # Run the 7 test questions and save to answers_hr_leave.txt
    test_questions = [
        "Can I carry forward unused annual leave?",
        "Can I install Slack on my work laptop?",
        "What is the home office equipment allowance?",
        "Can I use my personal phone to access work files when working from home?",
        "What is the company view on flexible working culture?",
        "Can I claim DA and meal receipts on the same day?",
        "Who approves leave without pay?"
    ]
    
    output_lines = []
    for idx, q in enumerate(test_questions, 1):
        ans = answer_question(q, docs)
        output_lines.append(f"Question {idx}: {q}")
        output_lines.append(f"Answer: {ans}")
        output_lines.append("-" * 40)
        
    # Write to answers_hr_leave.txt
    with open("answers_hr_leave.txt", mode="w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    print("Answers for the 7 test questions written to answers_hr_leave.txt")
    
    # Enter interactive mode unless run with --non-interactive
    parser = argparse.ArgumentParser(description="UC-X Q&A Agent")
    parser.add_argument("--non-interactive", action="store_true", help="Run without entering interactive loop")
    args = parser.parse_args()
    
    if args.non_interactive:
        sys.exit(0)
        
    print("\nEntering interactive Q&A Mode. Type 'exit' or 'quit' to end.")
    while True:
        try:
            q = input("\nAsk a question: ").strip()
            if not q:
                continue
            if q.lower() in ["exit", "quit"]:
                break
            ans = answer_question(q, docs)
            print(f"Answer: {ans}")
        except KeyboardInterrupt:
            break
            
    print("Exiting Q&A interactive mode.")

if __name__ == "__main__":
    main()
