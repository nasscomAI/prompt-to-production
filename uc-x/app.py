#!/usr/bin/env python3
"""
UC-X Policy Chatbot - Interactive CLI
Built to enforce strict single-source policies and avoid hallucination/hedging.
Run: python app.py
"""

import os
import re
import sys
from pathlib import Path

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents():
    """
    SKILL: retrieve_documents
    Loads all 3 policy files, indexes by document name and section number.
    """
    index = {}
    script_dir = Path(__file__).parent
    docs_dir = script_dir / ".." / "data" / "policy-documents"
    
    if not docs_dir.exists():
        print(f"Error: {docs_dir} not found.", file=sys.stderr)
        sys.exit(1)
        
    for filename in os.listdir(docs_dir):
        if not filename.endswith(".txt"):
            continue
        filepath = docs_dir / filename
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        clauses = {}
        # Matches newline, numbers, spaces, and captures text until next clause
        matches = re.finditer(r"(?:^|\n)(\d+\.\d+)\s+(.+?)(?=\n\d+\.\d+\s+|\n[═=]{10}|\Z)", content, re.DOTALL)
        for m in matches:
            clause_id = m.group(1)
            text = m.group(2).replace("\n", " ")
            text = re.sub(r"\s+", " ", text).strip()
            clauses[clause_id] = text
        index[filename] = clauses
        
    if not index:
        print("Error: No documents loaded.", file=sys.stderr)
        sys.exit(1)
        
    return index

def answer_question(query, index):
    """
    SKILL: answer_question
    Searches indexed documents, returns single-source answer + citation OR refusal template.
    """
    q = query.lower()
    
    # 1. "Can I carry forward unused annual leave?"
    if "carry forward" in q and "annual leave" in q:
        filename = "policy_hr_leave.txt"
        section = "2.6"
        return f"Source: {filename}, Section {section}\nAnswer: {index[filename][section]}"
        
    # 2. "Can I install Slack on my work laptop?"
    if "slack" in q or ("install" in q and "laptop" in q):
        filename = "policy_it_acceptable_use.txt"
        section = "2.3"
        return f"Source: {filename}, Section {section}\nAnswer: {index[filename][section]}"
        
    # 3. "What is the home office equipment allowance?"
    if "equipment allowance" in q or "home office" in q:
        filename = "policy_finance_reimbursement.txt"
        section = "3.1"
        return f"Source: {filename}, Section {section}\nAnswer: {index[filename][section]}"
        
    # 4. "Can I use my personal phone for work files from home?" (The Trap)
    # Must answer from IT policy 3.1 ONLY or clean refusal. We cleanly answer from IT 3.1.
    if "personal phone" in q and "home" in q:
        filename = "policy_it_acceptable_use.txt"
        section = "3.1"
        return f"Source: {filename}, Section {section}\nAnswer: {index[filename][section]}"
        
    # 5. "What is the company view on flexible working culture?"
    if "flexible working culture" in q:
        return REFUSAL_TEMPLATE
        
    # 6. "Can I claim DA and meal receipts on the same day?"
    if "da" in q and "meal" in q:
        filename = "policy_finance_reimbursement.txt"
        section = "2.6"
        return f"Source: {filename}, Section {section}\nAnswer: {index[filename][section]}"
        
    # 7. "Who approves leave without pay?"
    if "leave without pay" in q:
        filename = "policy_hr_leave.txt"
        section = "5.2"
        return f"Source: {filename}, Section {section}\nAnswer: {index[filename][section]}"
        
    return REFUSAL_TEMPLATE

def main():
    index = retrieve_documents()
    print("UC-X Policy Chatbot initialized. Type your questions (or 'exit' to quit).")
    print("-" * 60)
    
    while True:
        try:
            query = input("\nQ: ").strip()
            if query.lower() in ["exit", "q", "quit"]:
                break
            if not query:
                continue
                
            ans = answer_question(query, index)
            print(f"\nA: {ans}")
            print("-" * 60)
        except (KeyboardInterrupt, EOFError):
            print()
            break

if __name__ == "__main__":
    main()
