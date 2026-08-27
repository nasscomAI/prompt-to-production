import os
import re
import sys

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Warning: google-genai library not found. Please install it.")
    genai = None
    types = None

def retrieve_documents(file_paths):
    """
    Loads the three company policy text files and indexes their content 
    by document name and section number.
    """
    indexed_docs = {}
    for path in file_paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Error: Missing file {path}. Do not attempt to retrieve unapproved files.")
            
        doc_name = os.path.basename(path)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise IOError(f"Error reading {path}: {e}")
            
        sections = {}
        current_section = None
        current_text = []
        
        # Parse based on numbered sections (e.g., "2.6 ...")
        for line in content.split('\n'):
            match = re.match(r'^(\d+\.\d+)\s(.*)', line)
            if match:
                if current_section:
                    sections[current_section] = "\n".join(current_text).strip()
                current_section = match.group(1)
                current_text = [line]
            else:
                if current_section:
                    current_text.append(line)
                    
        if current_section:
             sections[current_section] = "\n".join(current_text).strip()
             
        indexed_docs[doc_name] = sections
    return indexed_docs

def answer_question(question, indexed_docs):
    """
    Searches the indexed documents for a user question and returns a 
    single-source answer with an exact citation or a refusal.
    """
    context_parts = []
    for doc_name, sections in indexed_docs.items():
        for sec_num, text in sections.items():
            context_parts.append(f"Document: {doc_name} | Section: {sec_num}\n{text}")
    
    context_str = "\n\n".join(context_parts)
    
    system_instruction = """You are an internal company policy assistant. Your operational boundary is strictly limited to answering user questions based solely on the provided policy documents.

intent:
A correct output provides a direct, factual answer drawn from a single source document. Every factual claim must include a citation specifying the source document name and section number. If the question cannot be answered from a single document, the output is exactly the refusal template.

context:
You are allowed to use information exclusively from the provided files (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). You must not use outside knowledge, assume common practices, or infer information not explicitly stated.

enforcement:
- Never combine claims from two different documents into a single answer.
- Never use hedging phrases: 'while not explicitly covered', 'typically', 'generally understood', 'it is common practice'.
- If the question is not in the documents, requires combining claims from two different documents, or creates genuine ambiguity — use the refusal template exactly, no variations:
This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance.
- Cite source document name + section number for every factual claim.
"""

    prompt = f"Context:\n{context_str}\n\nUser Question:\n{question}"
    
    if not genai:
        return "Error: genai SDK not installed."

    try:
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.0
            )
        )
        return response.text.strip()
    except Exception as e:
        return f"Error generating answer: {e}"

def main():
    file_paths = [
        '../data/policy-documents/policy_hr_leave.txt',
        '../data/policy-documents/policy_it_acceptable_use.txt',
        '../data/policy-documents/policy_finance_reimbursement.txt'
    ]
    
    # Initialize skills
    try:
        print("Loading documents...")
        indexed_docs = retrieve_documents(file_paths)
        print("Documents loaded successfully.\n")
    except Exception as e:
        print(e)
        sys.exit(1)
        
    print("Welcome to Ask My Documents (Interactive CLI)")
    print("Type 'exit' or 'quit' to terminate.")
    print("-" * 50)
    
    while True:
        try:
            question = input("\nEnter your question: ").strip()
            if question.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            if not question:
                continue
                
            print("\nSearching...")
            answer = answer_question(question, indexed_docs)
            print("-" * 50)
            print(answer)
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
