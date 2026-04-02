import os
import sys
import google.generativeai as genai

def retrieve_documents():
    """
    Loads all 3 policy files and indexes them.
    Corresponds to the 'retrieve_documents' skill in skills.md.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '..', 'data', 'policy-documents')
    
    files_to_load = [
        'policy_hr_leave.txt',
        'policy_it_acceptable_use.txt',
        'policy_finance_reimbursement.txt'
    ]
    
    documents = {}
    for filename in files_to_load:
        filepath = os.path.join(data_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                documents[filename] = f.read()
        except FileNotFoundError:
            return {"error": f"Error: Cannot load {filename}. Make sure the data directory is configured correctly."}
            
    return documents

def answer_question(query: str, indexed_docs: dict, system_instruction: str) -> str:
    """
    Searches indexed documents returning a single-source answer with a citation, 
    OR the verbatim refusal template.
    Corresponds to the 'answer_question' skill in skills.md.
    """
    docs_context = ""
    for name, content in indexed_docs.items():
        docs_context += f"--- Document: {name} ---\n{content}\n\n"
        
    prompt = f"Available Documents:\n{docs_context}\n\nEmployee Question:\n{query}"
    
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_instruction
        )
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.0
            ) # Extremely important for following enforcement strictly
        )
        return response.text
    except Exception as e:
        return f"System Error executing answer_question skill: {e}"

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    agents_file = os.path.join(current_dir, 'agents.md')
    
    try:
        with open(agents_file, 'r', encoding='utf-8') as f:
            system_instruction = f.read()
    except FileNotFoundError:
        print("Error: agents.md not found. Run this in the uc-x directory.")
        sys.exit(1)
        
    docs = retrieve_documents()
    if "error" in docs:
        print(docs["error"])
        sys.exit(1)
        
    print("=== UC-X 'Ask My Documents' ===")
    print("All documents loaded and indexed successfully.")
    print("Type your questions below, or type 'exit' or 'quit' to close.\n")
    
    while True:
        try:
            user_input = input("Employee: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ('exit', 'quit'):
                print("Exiting...")
                break
                
            answer = answer_question(user_input, docs, system_instruction)
            print(f"\nAgent:\n{answer}\n")
            
            import time
            time.sleep(2) # Added basic rate limiting mitigation
            
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()
