"""
UC-X app.py — Policy Question Answerer
Loads policy documents, answers employee questions with single-source citations.
See README.md for run command and expected behaviour.
"""
import os
import sys
from pathlib import Path

# Policy document paths
POLICY_DIR = Path(__file__).parent.parent / "data" / "policy-documents"
POLICIES = {
    "policy_hr_leave.txt": POLICY_DIR / "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt": POLICY_DIR / "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt": POLICY_DIR / "policy_finance_reimbursement.txt",
}

REFUSAL_TEMPLATE = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)


def retrieve_documents():
    """
    Load and index all three policy documents by document name and section number.
    Returns: Dictionary indexed by {document_name: document_text}
    """
    documents = {}
    for doc_name, doc_path in POLICIES.items():
        if not doc_path.exists():
            print(f"Error: Policy document not found at {doc_path}")
            sys.exit(1)
        with open(doc_path, "r", encoding="utf-8") as f:
            documents[doc_name] = f.read()
    return documents


def answer_question(question, documents):
    """
    Search indexed policy documents for single-source answer.
    Returns: {answer, source_document, section_number} or refusal template
    """
    question_lower = question.lower()
    
    # Simple keyword-based search (can be enhanced with semantic search)
    results = []
    
    for doc_name, doc_text in documents.items():
        lines = doc_text.split("\n")
        for i, line in enumerate(lines):
            if any(word in question_lower for word in question_lower.split()):
                # Found potential match
                results.append({
                    "document": doc_name,
                    "text": line.strip(),
                    "line_number": i + 1
                })
    
    # If multiple documents match, it's a blend scenario — refuse
    doc_matches = set(r["document"] for r in results)
    if len(doc_matches) > 1:
        return {"refusal": REFUSAL_TEMPLATE}
    
    # If single source found, return with citation
    if results:
        return {
            "answer": results[0]["text"],
            "source_document": results[0]["document"],
            "section_number": f"Line {results[0]['line_number']}"
        }
    
    # No match found — use refusal template
    return {"refusal": REFUSAL_TEMPLATE}


def format_response(result):
    """Format the answer result for display."""
    if "refusal" in result:
        return result["refusal"]
    
    response = f"\n{result['answer']}\n"
    response += f"\n📄 Source: {result['source_document']} ({result['section_number']})\n"
    return response


def main():
    """Interactive CLI for policy questions."""
    print("=" * 70)
    print("UC-X — Ask My Documents")
    print("=" * 70)
    print("Policy documents loaded: policy_hr_leave.txt, policy_it_acceptable_use.txt,")
    print("                         policy_finance_reimbursement.txt")
    print("\nType your policy question and press Enter. Type 'quit' to exit.\n")
    
    documents = retrieve_documents()
    
    while True:
        try:
            question = input("❓ Your question: ").strip()
            
            if question.lower() in ["quit", "exit", "q"]:
                print("\nThank you for using UC-X. Goodbye!")
                break
            
            if not question:
                print("Please enter a valid question.\n")
                continue
            
            result = answer_question(question, documents)
            response = format_response(result)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\nExiting UC-X. Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
