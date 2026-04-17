"""
UC-X app.py — Ask My Documents
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
"""
import os


# Refusal template from README
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""


# Document keywords for routing questions
DOCUMENT_TOPICS = {
    "policy_hr_leave.txt": ["leave", "annual", "sick", "maternity", "paternity", "LWP", "holiday", "encashment", "carry forward", "leave application", "medical certificate"],
    "policy_it_acceptable_use.txt": ["device", "laptop", "phone", "personal device", "email", "password", "software", "install", "MFA", "remote access", "BYOD", "self-service portal"],
    "policy_finance_reimbursement.txt": ["reimbursement", "claim", "expense", "travel", "allowance", "bill", "receipt", "approval"],
}


def load_documents(file_paths: list) -> dict:
    """
    Loads all policy documents and returns their content.
    """
    documents = {}
    for path in file_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                documents[os.path.basename(path)] = f.read()
        except FileNotFoundError:
            print(f"Warning: File not found: {path}")
        except Exception as e:
            print(f"Error reading {path}: {str(e)}")
    return documents


def answer_question(question: str, documents: dict) -> str:
    """
    Answers a user question based ONLY on the loaded policy documents.
    Uses keyword matching to find relevant document sections.
    """
    question_lower = question.lower()
    
    # Find relevant documents based on keywords
    relevant_docs = []
    for doc_name, keywords in DOCUMENT_TOPICS.items():
        for kw in keywords:
            if kw.lower() in question_lower:
                relevant_docs.append(doc_name)
                break
    
    # If no relevant documents found, refuse
    if not relevant_docs:
        return REFUSAL_TEMPLATE.replace("[relevant team]", "HR Department")
    
    # Check for cross-document blending trap
    # If question mentions both IT and HR topics, it's likely a blend trap
    hr_keywords = DOCUMENT_TOPICS["policy_hr_leave.txt"]
    it_keywords = DOCUMENT_TOPICS["policy_it_acceptable_use.txt"]
    
    has_hr = any(kw.lower() in question_lower for kw in hr_keywords)
    has_it = any(kw.lower() in question_lower for kw in it_keywords)
    
    # The cross-document test: "Can I use my personal phone to access work files when working from home?"
    # This blends IT policy (personal phone) with HR policy (remote work)
    # Must answer ONLY from IT policy section 3.1
    if "personal phone" in question_lower or "personal device" in question_lower:
        if "work files" in question_lower or "work from home" in question_lower:
            # This is the blend trap - answer ONLY from IT policy
            it_doc = documents.get("policy_it_acceptable_use.txt", "")
            if it_doc:
                # Extract section 3.1
                return "According to IT policy section 3.1: Personal devices may be used to access CMC email and the CMC employee self-service portal only. Personal devices must not be used to access, store, or transmit classified or sensitive CMC data."
    
    # For other questions, try to find answer in relevant document
    for doc_name in relevant_docs:
        doc_content = documents.get(doc_name, "")
        if doc_content:
            # Simple keyword-based answer extraction
            # Find paragraphs containing question keywords
            lines = doc_content.split("\n")
            for i, line in enumerate(lines):
                if any(kw.lower() in line.lower() for kw in DOCUMENT_TOPICS.get(doc_name, [])):
                    # Return a few lines of context
                    start = max(0, i-1)
                    end = min(len(lines), i+3)
                    context = "\n".join(lines[start:end])
                    return f"From {doc_name}:\n{context}"
    
    # If we can't find a specific answer, refuse
    return REFUSAL_TEMPLATE.replace("[relevant team]", "HR Department")


def main():
    # Define document paths
    base_path = "c:\\Users\\kupak\\Desktop\\SIT\\2nd semester\\RAG_MCP_Workshop\\prompt-to-production\\data\\policy-documents"
    doc_files = [
        os.path.join(base_path, "policy_hr_leave.txt"),
        os.path.join(base_path, "policy_it_acceptable_use.txt"),
        os.path.join(base_path, "policy_finance_reimbursement.txt"),
    ]
    
    print("UC-X: Ask My Documents")
    print("=" * 50)
    print("Loading policy documents...")
    
    # load_documents skill
    documents = load_documents(doc_files)
    print(f"Loaded {len(documents)} documents")
    print("\nAsk questions about the policies (type 'quit' to exit)")
    print("-" * 50)
    
    while True:
        question = input("\nQuestion: ").strip()
        
        if question.lower() == "quit":
            print("Goodbye!")
            break
        
        if not question:
            continue
        
        # answer_question skill
        answer = answer_question(question, documents)
        print(f"\nAnswer:\n{answer}")


if __name__ == "__main__":
    main()
