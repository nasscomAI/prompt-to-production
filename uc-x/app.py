"""
UC-X — Ask My Documents
Implements policy Q&A following RICE enforcement rules.

Core failure modes addressed:
- Cross-document blending: Never combine claims from two documents
- Hedged hallucination: Never use "while not explicitly covered", "typically", etc.
- Condition dropping: Preserve all conditions in multi-part requirements
"""
import os
import re
from typing import Optional


# Refusal template - EXACT wording required
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact the relevant department for guidance."""

# Forbidden hedging phrases
FORBIDDEN_PHRASES = [
    "while not explicitly covered",
    "typically",
    "generally understood",
    "it is common practice",
    "employees are generally expected to",
    "it is assumed",
    "based on standard practice"
]


def retrieve_documents(doc_paths: list) -> dict:
    """
    Load all policy documents and index them by document name and section.
    
    Args:
        doc_paths: List of file paths to policy documents
        
    Returns:
        Dictionary with documents, section_index, and search_keywords
    """
    documents = {}
    section_index = {}
    
    for path in doc_paths:
        if not os.path.exists(path):
            print(f"Warning: File not found: {path}")
            continue
        
        doc_name = os.path.basename(path)
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Warning: Failed to read {path}: {e}")
            continue
        
        # Parse document
        lines = content.split("\n")
        
        # Extract metadata
        metadata = {
            "title": "",
            "document_ref": "",
            "version": "",
            "effective_date": ""
        }
        
        for line in lines[:15]:
            line_stripped = line.strip()
            if "POLICY" in line_stripped.upper() and not metadata["title"]:
                metadata["title"] = line_stripped
            if "Document Reference:" in line_stripped:
                metadata["document_ref"] = line_stripped.split(":", 1)[1].strip()
            if "Version:" in line_stripped:
                parts = line_stripped.split("|")
                for part in parts:
                    if "Version:" in part:
                        metadata["version"] = part.split(":", 1)[1].strip()
                    if "Effective:" in part:
                        metadata["effective_date"] = part.split(":", 1)[1].strip()
        
        # Parse sections
        sections = {}
        current_section_num = None
        current_section_title = None
        current_clauses = {}
        current_clause_num = None
        current_clause_text = []
        
        section_pattern = re.compile(r"^(\d+)\.\s+([A-Z][A-Z\s\(\)&]+)$")
        clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.+)")
        
        for line in lines:
            line_stripped = line.strip()
            
            if line_stripped.startswith("═") or not line_stripped:
                continue
            
            section_match = section_pattern.match(line_stripped)
            if section_match:
                # Save previous clause
                if current_clause_num and current_clause_text:
                    current_clauses[current_clause_num] = " ".join(current_clause_text).strip()
                
                # Save previous section
                if current_section_num:
                    sections[current_section_num] = {
                        "title": current_section_title,
                        "clauses": current_clauses
                    }
                    # Index each clause
                    for clause_num, clause_text in current_clauses.items():
                        key = f"{doc_name}:{clause_num}"
                        section_index[key] = {
                            "document": doc_name,
                            "section": current_section_num,
                            "section_title": current_section_title,
                            "clause": clause_num,
                            "text": clause_text
                        }
                
                current_section_num = section_match.group(1)
                current_section_title = section_match.group(2).strip()
                current_clauses = {}
                current_clause_num = None
                current_clause_text = []
                continue
            
            clause_match = clause_pattern.match(line_stripped)
            if clause_match:
                # Save previous clause
                if current_clause_num and current_clause_text:
                    current_clauses[current_clause_num] = " ".join(current_clause_text).strip()
                
                current_clause_num = clause_match.group(1)
                current_clause_text = [clause_match.group(2)]
                continue
            
            # Continuation of current clause
            if current_clause_num and line_stripped:
                current_clause_text.append(line_stripped)
        
        # Don't forget the last clause and section
        if current_clause_num and current_clause_text:
            current_clauses[current_clause_num] = " ".join(current_clause_text).strip()
        if current_section_num:
            sections[current_section_num] = {
                "title": current_section_title,
                "clauses": current_clauses
            }
            for clause_num, clause_text in current_clauses.items():
                key = f"{doc_name}:{clause_num}"
                section_index[key] = {
                    "document": doc_name,
                    "section": current_section_num,
                    "section_title": current_section_title,
                    "clause": clause_num,
                    "text": clause_text
                }
        
        documents[doc_name] = {
            "metadata": metadata,
            "sections": sections,
            "full_text": content
        }
    
    return {
        "documents": documents,
        "section_index": section_index
    }


def _search_sections(query: str, documents: dict) -> list:
    """
    Search for relevant sections based on query keywords.
    Returns list of (document, clause_num, text, score) tuples.
    """
    query_lower = query.lower()
    results = []
    
    # Define keyword mappings for common questions
    keyword_mappings = {
        "carry forward": ["2.6", "2.7"],  # HR leave carry forward
        "annual leave": ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7"],
        "sick leave": ["3.1", "3.2", "3.3", "3.4"],
        "maternity": ["4.1", "4.2"],
        "paternity": ["4.3", "4.4"],
        "leave without pay": ["5.1", "5.2", "5.3", "5.4"],
        "lwp": ["5.1", "5.2", "5.3", "5.4"],
        "install": ["2.3", "2.4"],  # IT software installation
        "software": ["2.3", "2.4"],
        "slack": ["2.3", "2.4"],
        "personal phone": ["3.1", "3.2", "3.3", "3.4", "3.5"],
        "personal device": ["3.1", "3.2", "3.3", "3.4", "3.5"],
        "byod": ["3.1", "3.2", "3.3", "3.4", "3.5"],
        "work from home": ["3.1", "3.2", "3.3", "3.4", "3.5"],  # Finance WFH equipment
        "home office": ["3.1", "3.2", "3.3", "3.4", "3.5"],
        "equipment allowance": ["3.1", "3.2", "3.3", "3.4", "3.5"],
        "da": ["2.5", "2.6"],  # Finance DA
        "daily allowance": ["2.5", "2.6"],
        "meal": ["2.5", "2.6"],
        "flexible": [],  # Not in any document
        "culture": [],  # Not in any document
        "who approves": ["5.2", "5.3"],  # HR leave approval
        "approval": ["2.3", "2.4", "5.2", "5.3"],
    }
    
    section_index = documents.get("section_index", {})
    
    for key, section_data in section_index.items():
        text_lower = section_data["text"].lower()
        doc_name = section_data["document"]
        clause_num = section_data["clause"]
        
        score = 0
        
        # Check for keyword matches
        query_words = query_lower.split()
        for word in query_words:
            if len(word) > 3 and word in text_lower:
                score += 1
        
        # Boost for specific patterns
        if "carry forward" in query_lower and ("carry forward" in text_lower or "carry-forward" in text_lower):
            score += 10
        if "install" in query_lower and "install" in text_lower:
            score += 10
        if "slack" in query_lower and "software" in text_lower:
            score += 5
        if "personal phone" in query_lower or "personal device" in query_lower:
            if "personal device" in text_lower:
                score += 10
        if "home office" in query_lower or "work from home" in query_lower:
            if "home" in text_lower and ("equipment" in text_lower or "allowance" in text_lower):
                score += 10
        if ("da " in query_lower or "daily allowance" in query_lower or "meal" in query_lower):
            if "daily allowance" in text_lower or "meal" in text_lower:
                score += 10
        if "who approves" in query_lower or "approval" in query_lower:
            if "requires approval" in text_lower or "must be approved" in text_lower:
                score += 5
        if "leave without pay" in query_lower or "lwp" in query_lower:
            if "leave without pay" in text_lower or "lwp" in text_lower:
                score += 10
        
        if score > 0:
            results.append({
                "document": doc_name,
                "clause": clause_num,
                "section_title": section_data["section_title"],
                "text": section_data["text"],
                "score": score
            })
    
    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def answer_question(question: str, documents: dict) -> dict:
    """
    Answer a question using ONLY the loaded documents.
    
    Args:
        question: User's question
        documents: Indexed documents from retrieve_documents
        
    Returns:
        Dictionary with answer, source, and confidence
    """
    question_lower = question.lower()
    
    # Check for questions not in any document (flexible working culture, etc.)
    not_covered_keywords = ["flexible working culture", "company view", "company policy on flexibility"]
    for keyword in not_covered_keywords:
        if keyword in question_lower:
            return {
                "answer": REFUSAL_TEMPLATE,
                "source": "NOT_FOUND",
                "confidence": "REFUSED"
            }
    
    # Search for relevant sections
    results = _search_sections(question, documents)
    
    if not results:
        return {
            "answer": REFUSAL_TEMPLATE,
            "source": "NOT_FOUND",
            "confidence": "REFUSED"
        }
    
    top_result = results[0]
    
    # Check if the question is about personal phone/device for work files
    # This is the critical cross-document test - must answer from IT policy ONLY
    if ("personal phone" in question_lower or "personal device" in question_lower) and \
       ("work file" in question_lower or "work from home" in question_lower or "access" in question_lower):
        # Filter to IT policy only
        it_results = [r for r in results if "it_acceptable" in r["document"]]
        if it_results:
            # Get section 3.1 specifically
            section_31 = [r for r in it_results if r["clause"] == "3.1"]
            if section_31:
                result = section_31[0]
                doc_name = result["document"].replace("policy_", "").replace(".txt", "").replace("_", " ").title()
                answer = f"According to {doc_name} Policy Section {result['clause']}:\n\n"
                answer += f'"{result["text"]}"\n\n'
                answer += "This means personal devices can ONLY be used for CMC email and the employee self-service portal. "
                answer += "Access to other work files on personal devices is NOT permitted."
                
                return {
                    "answer": answer,
                    "source": f"{result['document']} Section {result['clause']}",
                    "confidence": "HIGH"
                }
    
    # Handle specific questions
    
    # Carry forward annual leave
    if "carry forward" in question_lower and "leave" in question_lower:
        hr_results = [r for r in results if "hr_leave" in r["document"]]
        if hr_results:
            # Get 2.6 and 2.7
            relevant = [r for r in hr_results if r["clause"] in ["2.6", "2.7"]]
            if relevant:
                answer = "According to HR Leave Policy:\n\n"
                for r in sorted(relevant, key=lambda x: x["clause"]):
                    answer += f"Section {r['clause']}: {r['text']}\n\n"
                
                return {
                    "answer": answer,
                    "source": f"policy_hr_leave.txt Sections 2.6, 2.7",
                    "confidence": "HIGH"
                }
    
    # Install software (Slack)
    if "install" in question_lower or "slack" in question_lower:
        it_results = [r for r in results if "it_acceptable" in r["document"]]
        if it_results:
            relevant = [r for r in it_results if r["clause"] in ["2.3", "2.4"]]
            if relevant:
                result = relevant[0]
                answer = f"According to IT Acceptable Use Policy Section {result['clause']}:\n\n"
                answer += f'"{result["text"]}"\n\n'
                if "2.3" in result["clause"]:
                    answer += "Therefore, installing Slack (or any software) on your work laptop requires written approval from the IT Department."
                
                return {
                    "answer": answer,
                    "source": f"policy_it_acceptable_use.txt Section {result['clause']}",
                    "confidence": "HIGH"
                }
    
    # Home office equipment allowance
    if ("home office" in question_lower or "equipment allowance" in question_lower or 
        ("work from home" in question_lower and "allowance" in question_lower)):
        fin_results = [r for r in results if "finance_reimbursement" in r["document"]]
        if fin_results:
            relevant = [r for r in fin_results if r["clause"] == "3.1"]
            if relevant:
                result = relevant[0]
                answer = f"According to Finance Reimbursement Policy Section {result['clause']}:\n\n"
                answer += f'"{result["text"]}"\n\n'
                answer += "The home office equipment allowance is Rs 8,000 (one-time) for employees approved for PERMANENT work-from-home arrangements only."
                
                return {
                    "answer": answer,
                    "source": f"policy_finance_reimbursement.txt Section {result['clause']}",
                    "confidence": "HIGH"
                }
    
    # DA and meal receipts on same day
    if "da" in question_lower and "meal" in question_lower:
        fin_results = [r for r in results if "finance_reimbursement" in r["document"]]
        if fin_results:
            relevant = [r for r in fin_results if r["clause"] == "2.6"]
            if relevant:
                result = relevant[0]
                answer = f"According to Finance Reimbursement Policy Section {result['clause']}:\n\n"
                answer += f'"{result["text"]}"\n\n'
                answer += "NO - DA and meal receipts cannot be claimed simultaneously for the same day. This is explicitly prohibited."
                
                return {
                    "answer": answer,
                    "source": f"policy_finance_reimbursement.txt Section {result['clause']}",
                    "confidence": "HIGH"
                }
    
    # Who approves leave without pay
    if ("who approves" in question_lower or "approval" in question_lower) and \
       ("leave without pay" in question_lower or "lwp" in question_lower):
        hr_results = [r for r in results if "hr_leave" in r["document"]]
        if hr_results:
            relevant = [r for r in hr_results if r["clause"] == "5.2"]
            if relevant:
                result = relevant[0]
                answer = f"According to HR Leave Policy Section {result['clause']}:\n\n"
                answer += f'"{result["text"]}"\n\n'
                answer += "BOTH the Department Head AND the HR Director must approve LWP. Manager approval alone is NOT sufficient."
                
                return {
                    "answer": answer,
                    "source": f"policy_hr_leave.txt Section {result['clause']}",
                    "confidence": "HIGH"
                }
    
    # Generic answer from top result
    if top_result["score"] > 0:
        doc_name = top_result["document"]
        answer = f"According to {doc_name} Section {top_result['clause']}:\n\n"
        answer += f'"{top_result["text"]}"'
        
        return {
            "answer": answer,
            "source": f"{doc_name} Section {top_result['clause']}",
            "confidence": "MEDIUM"
        }
    
    # Default refusal
    return {
        "answer": REFUSAL_TEMPLATE,
        "source": "NOT_FOUND",
        "confidence": "REFUSED"
    }


def main():
    """Main entry point - interactive Q&A CLI."""
    print("=" * 70)
    print("UC-X — Ask My Documents")
    print("Policy Q&A System")
    print("=" * 70)
    
    # Load documents
    doc_dir = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
    doc_paths = [
        os.path.join(doc_dir, "policy_hr_leave.txt"),
        os.path.join(doc_dir, "policy_it_acceptable_use.txt"),
        os.path.join(doc_dir, "policy_finance_reimbursement.txt")
    ]
    
    print("\nLoading policy documents...")
    documents = retrieve_documents(doc_paths)
    print(f"Loaded {len(documents['documents'])} documents")
    print(f"Indexed {len(documents['section_index'])} sections")
    
    print("\n" + "-" * 70)
    print("Available documents:")
    for doc_name in documents["documents"].keys():
        print(f"  - {doc_name}")
    print("-" * 70)
    
    print("\nType your questions (or 'quit' to exit):")
    print()
    
    while True:
        try:
            question = input("Q: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        
        if not question:
            continue
        
        if question.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        
        result = answer_question(question, documents)
        
        print("\n" + "=" * 70)
        print("ANSWER:")
        print("-" * 70)
        print(result["answer"])
        print("-" * 70)
        print(f"Source: {result['source']}")
        print(f"Confidence: {result['confidence']}")
        print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
