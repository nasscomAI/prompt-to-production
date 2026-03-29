import os
import re
from google import genai

# Path to the documents
DOC_PATH = os.path.join("..", "data", "policy-documents")
DOC_FILES = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt"
]

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents():
    """
    Loads all 3 policy files and indexes them by document name and section number.
    Returns a list of dictionaries with source, section, and content.
    """
    documents = []
    for filename in DOC_FILES:
        filepath = os.path.join(DOC_PATH, filename)
        if not os.path.exists(filepath):
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Policy sections are identified by lines like "2. ANNUAL LEAVE" 
            # surrounded by "═════════" lines.
            # We split by these separators and capture the section titles.
            
            # Split by the double-line box (7 or more ═ characters)
            sections_raw = re.split(r'═{7,}', content)
            
            # The structure appears to be:
            # Metadata/Header
            # ═════════
            # 1. SECTION TITLE
            # ═════════
            # Section Content
            
            # We iterate through the raw sections. 
            # If a section contains a title at the start (e.g. "2. ANNUAL LEAVE"), 
            # the *next* raw section contains the content.
            
            for i in range(len(sections_raw)):
                chunk = sections_raw[i].strip()
                # Check if this chunk is a section title (e.g., "3. SICK LEAVE")
                title_match = re.match(r'^(\d+\.[ A-Z ]+)$', chunk)
                if title_match and i + 1 < len(sections_raw):
                    title = title_match.group(1)
                    actual_content = sections_raw[i+1].strip()
                    # Further split the content into numbered points (e.g., 3.1, 3.2)
                    # to make retrieval more granular if needed, or keep sections.
                    # README.md says "index by document name and section number".
                    documents.append({
                        "source": filename,
                        "section": title,
                        "content": actual_content
                    })
                
    return documents

def answer_question(client, documents, query):
    """
    Searches indexed documents and returns a single-source answer + citation or refusal template.
    Strictly follows enforcement rules from agents.md.
    """
    # Create the context from documents
    context_str = ""
    for doc in documents:
        context_str += f"\n--- SOURCE: {doc['source']} | SECTION: {doc['section']} ---\n{doc['content']}\n"

    # System prompt based on agents.md rules
    system_prompt = f"""
ROLE: UC-X Policy Summarisation Agent. Boundary: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt.

INTENT: Provide accurate, single-source answers with exact citations (document name + section number). No blended info. No hedging. No hallucinations.

RULES:
1. Never combine claims from two different documents into a single answer. 
2. Choose only ONE document that best answers the query. If multiple documents are relevant but tell different things, REFUSE using the template.
3. Never use hedging phrases like 'typically', 'generally understood', 'while not explicitly covered', 'it is common practice'.
4. Cite source document name + section number for EVERY factual claim.
5. If the question is not in the documents, OR if answering requires combining/blending multiple documents, you MUST use this EXACT refusal template verbatim:
{REFUSAL_TEMPLATE}

CONTEXT: Here are the policy documents:
{context_str}

USER QUESTION: {query}
"""

    try:
        # Use gemini-2.0-flash as a working model
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[system_prompt],
            config={
                "temperature": 0.0,
            }
        )
        return response.text.strip()
    except Exception as e:
        return f"Error connecting to AI service: {str(e)}"

def main():
    print("Welcome to UC-X — Policy Document Query System")
    print("Type 'exit' or 'quit' to quit.\n")
    
    # Check for API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable not found.")
        return
        
    client = genai.Client(api_key=api_key)
    documents = retrieve_documents()
    
    if not documents:
        print("ERROR: No policy documents found. Please check document paths.")
        return

    while True:
        try:
            user_input = input("UC-X> ").strip()
            if user_input.lower() in ("exit", "quit"):
                break
            if not user_input:
                continue
                
            answer = answer_question(client, documents, user_input)
            print(f"\n{answer}\n")
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
