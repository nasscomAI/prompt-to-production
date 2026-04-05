"""
UC-X app.py — Q&A System using RICE + agents.md + skills.md
"""
import os
import sys
import google.generativeai as genai

def load_documents():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "policy-documents")
    docs = {}
    filenames = [
        "policy_hr_leave.txt", 
        "policy_it_acceptable_use.txt", 
        "policy_finance_reimbursement.txt"
    ]
    for filename in filenames:
        filepath = os.path.normpath(os.path.join(data_dir, filename))
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                docs[filename] = f.read()
        else:
            print(f"Warning: Could not find {filename} at {filepath}")
    return docs

def main():
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("API Key not found in environment.")
        api_key = input("Please paste your Gemini API Key (input will be hidden): ").strip()
        if not api_key:
            print("Error: API Key is required to run this script.")
            sys.exit(1)
            
    genai.configure(api_key=api_key)    
    agents_md_path = os.path.join(os.path.dirname(__file__), "agents.md")
    if not os.path.exists(agents_md_path):
        print(f"Error: Could not find agents.md at {agents_md_path}")
        sys.exit(1)
        
    with open(agents_md_path, "r", encoding="utf-8") as f:
        system_instruction = f.read()
        
    docs = load_documents()
    if not docs:
        print("Error: No documents loaded.")
        sys.exit(1)
        
    docs_context = "\n\n--- DOCUMENT CONTEXT ---\n\n"
    for filename, text in docs.items():
        docs_context += f"=== BEGIN DOCUMENT: {filename} ===\n"
        docs_context += text + "\n"
        docs_context += f"=== END DOCUMENT: {filename} ===\n\n"
        
    system_instruction += docs_context
    
    # Auto-discover model since API versions change
    valid_models = []
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name.lower():
                valid_models.append(m.name)
    except Exception as e:
        print(f"Error listing models: {e}")
        sys.exit(1)
        
    if not valid_models:
        print("Error: No compatible gemini models found for your API key.")
        sys.exit(1)
        
    model_name = valid_models[-1] # Usually later lists are newer
    for m in valid_models:
        if "flash" in m.lower():
            model_name = m
            break
            
    # print(f"Auto-selected model: {model_name}")
            
    # Use 0.0 temp for factual Q&A
    generation_config = genai.types.GenerationConfig(
        temperature=0.0
    )
    
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_instruction,
        generation_config=generation_config
    )


    
    print("UC-X Ask My Documents")
    print("Type 'exit' to quit.")
    print("-" * 30)
    
    while True:
        try:
            query = input("\nQuestion: ").strip()
            if not query:
                continue
            if query.lower() in ['exit', 'quit']:
                break
                
            response = model.generate_content(query)
            print(f"\nAnswer:\n{response.text}")
            
        except EOFError:
            break
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError generating response: {e}")

if __name__ == "__main__":
    main()
