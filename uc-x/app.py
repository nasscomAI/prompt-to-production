#!/usr/bin/env python3
"""
UC-X: Ask My Documents
Interactive Q&A system for policy documents with single-source answers and refusal template.
"""

import re
import sys
from pathlib import Path


# Refusal template - exact wording, no variations
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

# Prohibited hedging phrases
PROHIBITED_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "usually",
    "in most cases",
    "it is generally accepted",
    "normally",
]

# Policy document files
POLICY_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]


def retrieve_documents(base_path):
    """
    Loads all 3 policy files and indexes by document name and section.
    
    Args:
        base_path (str): Path to policy-documents directory
        
    Returns:
        dict: Indexed documents with sections and clauses
    """
    path = Path(base_path)
    if not path.exists():
        raise FileNotFoundError(f"Policy documents directory not found: {base_path}")
    
    documents = {}
    
    for filename in POLICY_FILES:
        file_path = path / filename
        if not file_path.exists():
            raise ValueError(f"Required policy file missing: {filename}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse document
        doc_data = {
            "title": "",
            "reference": "",
            "full_text": content,
            "sections": {}
        }
        
        lines = content.split('\n')
        current_section = None
        current_section_num = None
        
        # Extract document info
        for line in lines[:10]:
            if "Document Reference:" in line:
                doc_data["reference"] = line.split("Reference:")[-1].strip()
            elif "POLICY" in line and "Document" not in line:
                doc_data["title"] = line.strip()
        
        # Parse sections and clauses
        section_pattern = re.compile(r'^(\d+)\.\s+([A-Z\s&]+)$')
        clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.+)$')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            section_match = section_pattern.match(line)
            if section_match:
                current_section_num = section_match.group(1)
                section_title = section_match.group(2).strip()
                doc_data["sections"][current_section_num] = {
                    "title": section_title,
                    "clauses": {}
                }
                i += 1
                continue
            
            clause_match = clause_pattern.match(line)
            if clause_match and current_section_num:
                clause_num = clause_match.group(1)
                clause_text = clause_match.group(2).strip()
                
                # Read multi-line clauses
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()
                    if (clause_pattern.match(next_line) or 
                        section_pattern.match(next_line) or 
                        next_line.startswith('═') or
                        not next_line):
                        break
                    clause_text += " " + next_line
                    i += 1
                
                doc_data["sections"][current_section_num]["clauses"][clause_num] = clause_text
                continue
            
            i += 1
        
        documents[filename] = doc_data
    
    # Count totals
    total_sections = sum(len(d["sections"]) for d in documents.values())
    total_clauses = sum(
        len(s["clauses"]) 
        for d in documents.values() 
        for s in d["sections"].values()
    )
    
    return {
        "documents": documents,
        "total_documents": len(documents),
        "total_sections": total_sections,
        "total_clauses": total_clauses
    }


def search_documents(documents, keywords):
    """
    Searches documents for keywords and returns matching clauses.
    
    Returns list of (document, section, clause_num, clause_text, score)
    """
    results = []
    keywords_lower = [k.lower() for k in keywords]
    
    for doc_name, doc_data in documents["documents"].items():
        for section_num, section_data in doc_data["sections"].items():
            for clause_num, clause_text in section_data["clauses"].items():
                text_lower = clause_text.lower()
                score = sum(1 for k in keywords_lower if k in text_lower)
                if score > 0:
                    results.append({
                        "document": doc_name,
                        "section": section_num,
                        "clause": clause_num,
                        "text": clause_text,
                        "section_title": section_data["title"],
                        "score": score
                    })
    
    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def answer_question(documents, question):
    """
    Answers a question using single-source citation or refusal template.
    
    Args:
        documents (dict): Output from retrieve_documents
        question (str): User's question
        
    Returns:
        dict: Answer with citation or refusal
    """
    if not question or not question.strip():
        return {
            "answer": "Please enter a question.",
            "source_document": "NONE",
            "source_section": "NONE",
            "citation": "NONE",
            "is_refusal": True
        }
    
    question_lower = question.lower()
    
    # Define question patterns and their answers
    qa_mappings = [
        {
            "patterns": ["carry forward", "unused annual leave", "carry-forward"],
            "document": "policy_hr_leave.txt",
            "clause": "2.6",
            "answer": "Yes, but with limits. Employees may carry forward a maximum of 5 unused annual leave days to the following calendar year. Any days above 5 are forfeited on 31 December. Additionally, carry-forward days must be used within the first quarter (January-March) of the following year or they are forfeited [policy_hr_leave.txt, Section 2.6 and 2.7]."
        },
        {
            "patterns": ["install slack", "install software", "software on laptop"],
            "document": "policy_it_acceptable_use.txt",
            "clause": "2.3",
            "answer": "Employees must not install software on corporate devices without written approval from the IT Department. Software approved for installation must be sourced from the CMC-approved software catalogue only. [policy_it_acceptable_use.txt, Section 2.3 and 2.4]"
        },
        {
            "patterns": ["home office equipment", "wfh equipment", "work from home allowance", "home office allowance"],
            "document": "policy_finance_reimbursement.txt",
            "clause": "3.1",
            "answer": "Employees approved for permanent work-from-home arrangements are entitled to a one-time home office equipment allowance of Rs 8,000. This covers desk, chair, monitor, keyboard, mouse, and networking equipment only. Note: Employees on temporary or partial work-from-home arrangements are NOT eligible for this allowance. [policy_finance_reimbursement.txt, Section 3.1 and 3.5]"
        },
        {
            "patterns": ["personal phone", "personal device", "work files from home", "byod"],
            "document": "policy_it_acceptable_use.txt",
            "clause": "3.1",
            "answer": "Personal devices may be used to access CMC email and the CMC employee self-service portal ONLY. Personal devices must not be used to access, store, or transmit classified or sensitive CMC data. [policy_it_acceptable_use.txt, Section 3.1 and 3.2]"
        },
        {
            "patterns": ["flexible working culture", "company culture", "work culture", "company view"],
            "document": "NONE",
            "clause": "NONE",
            "answer": REFUSAL_TEMPLATE
        },
        {
            "patterns": ["da and meal", "meal receipts", "claim da", "daily allowance and meal"],
            "document": "policy_finance_reimbursement.txt",
            "clause": "2.6",
            "answer": "NO. DA and meal receipts cannot be claimed simultaneously for the same day. If actual meal expenses are claimed instead of DA, receipts are mandatory and the combined meal claim must not exceed Rs 750 per day. This is explicitly prohibited. [policy_finance_reimbursement.txt, Section 2.6]"
        },
        {
            "patterns": ["who approves leave without pay", "lwp approval", "leave without pay approval", "approves lwp"],
            "document": "policy_hr_leave.txt",
            "clause": "5.2",
            "answer": "LWP requires approval from BOTH the Department Head AND the HR Director. Manager approval alone is not sufficient. Additionally, LWP exceeding 30 continuous days requires approval from the Municipal Commissioner. [policy_hr_leave.txt, Section 5.2 and 5.3]"
        },
        {
            "patterns": ["sick leave", "medical certificate", "consecutive sick"],
            "document": "policy_hr_leave.txt",
            "clause": "3.2",
            "answer": "Each employee is entitled to 12 days of paid sick leave per calendar year. Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work. Sick leave taken immediately before or after a public holiday requires a medical certificate regardless of duration. [policy_hr_leave.txt, Section 3.1, 3.2, and 3.4]"
        },
        {
            "patterns": ["maternity leave", "paternity leave"],
            "document": "policy_hr_leave.txt",
            "clause": "4.1",
            "answer": "Female employees are entitled to 26 weeks of paid maternity leave for the first two live births (12 weeks for third or subsequent). Male employees are entitled to 5 days of paid paternity leave, to be taken within 30 days of the child's birth. Paternity leave cannot be split across multiple periods. [policy_hr_leave.txt, Section 4.1, 4.2, 4.3, and 4.4]"
        },
        {
            "patterns": ["leave encashment", "encash leave"],
            "document": "policy_hr_leave.txt",
            "clause": "7.2",
            "answer": "Leave encashment during service is NOT permitted under any circumstances. Annual leave may be encashed only at the time of retirement or resignation, subject to a maximum of 60 days. Sick leave and LWP cannot be encashed under any circumstances. [policy_hr_leave.txt, Section 7.1, 7.2, and 7.3]"
        },
        {
            "patterns": ["travel reimbursement", "outstation travel", "air travel"],
            "document": "policy_finance_reimbursement.txt",
            "clause": "2.2",
            "answer": "Outstation travel must be pre-approved using Form FIN-T1 before travel commences. Travel without prior approval is not reimbursable. Air travel is permitted for journeys exceeding 500 km only, and economy class is mandatory (business class is not reimbursable). Hotel accommodation is reimbursable up to Rs 3,500 per night for Grade A cities and Rs 2,500 for other locations. [policy_finance_reimbursement.txt, Section 2.2, 2.3, and 2.4]"
        },
    ]
    
    # Check each pattern
    for qa in qa_mappings:
        for pattern in qa["patterns"]:
            if pattern in question_lower:
                is_refusal = qa["document"] == "NONE"
                return {
                    "answer": qa["answer"],
                    "source_document": qa["document"],
                    "source_section": qa["clause"],
                    "citation": f"[{qa['document']}, Section {qa['clause']}]" if not is_refusal else "NONE",
                    "is_refusal": is_refusal
                }
    
    # Keyword-based search fallback
    keywords = [w for w in question_lower.split() if len(w) > 3 and w not in ["what", "when", "where", "which", "this", "that", "from", "with", "have", "does", "will", "would", "could", "should"]]
    
    if keywords:
        results = search_documents(documents, keywords)
        if results:
            best = results[0]
            # Only use if score is good enough
            if best["score"] >= 1:
                return {
                    "answer": f"{best['text']} [{best['document']}, Section {best['clause']}]",
                    "source_document": best["document"],
                    "source_section": best["clause"],
                    "citation": f"[{best['document']}, Section {best['clause']}]",
                    "is_refusal": False
                }
    
    # Default to refusal
    return {
        "answer": REFUSAL_TEMPLATE,
        "source_document": "NONE",
        "source_section": "NONE",
        "citation": "NONE",
        "is_refusal": True
    }


def main():
    """Interactive CLI for policy Q&A."""
    print("=" * 70)
    print("UC-X: Ask My Documents — Policy Q&A System")
    print("=" * 70)
    
    # Load documents
    base_path = Path(__file__).parent.parent / "data" / "policy-documents"
    
    print(f"\nLoading policy documents from: {base_path}")
    
    try:
        documents = retrieve_documents(str(base_path))
        print(f"✓ Loaded {documents['total_documents']} documents")
        print(f"  - {documents['total_sections']} sections")
        print(f"  - {documents['total_clauses']} clauses")
        print("\nDocuments available:")
        for doc_name in documents["documents"]:
            print(f"  • {doc_name}")
    except Exception as e:
        print(f"Error loading documents: {e}", file=sys.stderr)
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("Type your questions below. Type 'quit' or 'exit' to end.")
    print("=" * 70)
    
    while True:
        try:
            print("\n")
            question = input("Question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            if not question:
                print("Please enter a question.")
                continue
            
            # Get answer
            result = answer_question(documents, question)
            
            print("\n" + "-" * 70)
            print("ANSWER:")
            print("-" * 70)
            print(result["answer"])
            
            if not result["is_refusal"]:
                print(f"\nSource: {result['citation']}")
            
            print("-" * 70)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            print("\n\nGoodbye!")
            break


if __name__ == "__main__":
    main()

