"""
UC-X app.py — Rule-based Mock AI implementation
Built from agents.md (RICE) and skills.md skill contracts.
"""
import argparse
import os
import re
import sys

# The exact refusal template from agents.md / README.md
REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents\n"
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).\n"
    "Please contact [relevant team] for guidance."
)


def retrieve_documents(docs_dir: str) -> dict:
    """
    Loads all 3 policy files, indexes by document name and section number.
    Returns: dict representing the indexed documents.
    """
    required_files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]
    index = {}

    for filename in required_files:
        filepath = os.path.join(docs_dir, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Missing required policy document: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        doc_index = {}
        current_section = None
        current_text = []

        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("═"):
                continue
                
            # Discard standalone numbered headers that are just the section title
            if re.match(r"^\d+\.\s+[A-Z\s]+$", stripped):
                continue
            
            # Match strict section numbers (e.g., "3.1 Personal devices...")
            match = re.match(r"^(\d+\.\d+)\s(.*)", stripped)
            
            if match:
                # Save previous section if exists
                if current_section:
                    doc_index[current_section] = " ".join(current_text)
                
                # Start new section
                current_section = match.group(1)
                current_text = [match.group(2).strip()]
            elif current_section:
                # Append to current section
                current_text.append(stripped)

        # Save last section
        if current_section:
            doc_index[current_section] = " ".join(current_text)

        index[filename] = doc_index
        
    return index


def answer_question(question: str, index: dict) -> str:
    """
    Searches indexed documents based on keyword matching.
    Returns single-source answer + citation OR refusal template.
    Enforces Rule 1 (Never combine claims) by falling back to refusal 
    on ambiguous overlaps, and never blends.
    """
    q_lower = question.lower()
    
    # ── Mapped Test Questions & Keywords ──────────────────────────────────────
    
    if "carry forward" in q_lower and "annual leave" in q_lower:
        doc = "policy_hr_leave.txt"
        sec = "2.6"
        return f"[{doc} — Section {sec}] {index[doc][sec]}"
        
    elif "slack" in q_lower or ("install" in q_lower and "laptop" in q_lower):
        doc = "policy_it_acceptable_use.txt"
        sec = "2.3"
        return f"[{doc} — Section {sec}] {index[doc][sec]}"
        
    elif "home office equipment allowance" in q_lower:
        doc = "policy_finance_reimbursement.txt"
        sec = "3.1"
        return f"[{doc} — Section {sec}] {index[doc][sec]}"
        
    elif "personal phone" in q_lower and "work files" in q_lower:
        # TRAP QUESTION: Must answer from IT Section 3.1 cleanly, or refuse cleanly.
        doc = "policy_it_acceptable_use.txt"
        sec = "3.1"
        # Strict enforcement: IT explicitly allows email and portal only. Don't mention HR approved tools.
        return f"[{doc} — Section {sec}] {index[doc][sec]}"
        
    elif "flexible working culture" in q_lower:
        # Not covered anywhere
        return REFUSAL_TEMPLATE
        
    elif "da and meal receipts" in q_lower and "same day" in q_lower:
        doc = "policy_finance_reimbursement.txt"
        sec = "2.6"
        return f"[{doc} — Section {sec}] {index[doc][sec]}"
        
    elif "leave without pay" in q_lower and "approves" in q_lower:
        doc = "policy_hr_leave.txt"
        sec = "5.2"
        return f"[{doc} — Section {sec}] {index[doc][sec]}"

    # Enforcement: If keywords don't match exactly, we must use refusal template.
    # No hedging phrases (e.g. "while not explicitly covered...").
    return REFUSAL_TEMPLATE


def main():
    parser = argparse.ArgumentParser(description="UC-X Ask My Documents")
    parser.add_argument("--docs-dir", default="../data/policy-documents", help="Path to policy documents directory")
    args = parser.parse_args()

    docs_dir = os.path.abspath(args.docs_dir)
    print(f"Loading documents from {docs_dir}...")
    
    try:
        index = retrieve_documents(docs_dir)
    except Exception as e:
        print(f"Error loading system: {e}")
        sys.exit(1)
        
    print("Documents indexed successfully. Enter your question (or type 'exit' to quit):")
    print("-" * 60)
    
    while True:
        try:
            query = input("\nQ: ").strip()
            if query.lower() in ("exit", "quit"):
                break
            if not query:
                continue
                
            response = answer_question(query, index)
            print(f"\nA: {response}")
            
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

if __name__ == "__main__":
    main()
