"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os
import sys
import re

try:
    from google import genai
    from google.genai import types
    from openai import OpenAi 
    HAS_LLM = True
except ImportError:
    HAS_LLM = False

def load_agents_config(agents_md_path: str) -> str:
    """Reads agents.md to use as the system prompt (RICE structure)."""
    try:
        with open(agents_md_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "You are a strict policy document assistant."

def retrieve_documents(filepaths: list[str]) -> dict:
    """
    Skill: retrieve_documents
    Loads all 3 policy files and indexes them by document name and section number.
    """
    indexed_docs = {}
    for filepath in filepaths:
        if not os.path.exists(filepath):
            print(f"Error: File '{filepath}' is missing.", file=sys.stderr)
            continue
            
        try:
            filename = os.path.basename(filepath)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            sections = {}
            current_section = "General"
            sections[current_section] = []
            
            for line in content.split('\n'):
                match = re.match(r'^(\d+\.?\d*)\s+(.*)', line.strip())
                if match:
                    current_section = match.group(1).strip()
                    sections[current_section] = [match.group(2).strip()]
                elif line.strip():
                    sections[current_section].append(line.strip())
                    
            structured_sections = {k: " ".join(v) for k, v in sections.items()}
            indexed_docs[filename] = structured_sections
        except Exception as e:
            print(f"Error reading {filepath}: {e}", file=sys.stderr)
            
    return indexed_docs

def answer_question(question: str, indexed_docs: dict, system_prompt: str) -> str:
    """
    Skill: answer_question
    Searches indexed documents to return a single-source answer with citation OR the refusal template.
    """
    # Format the context
    context_lines = []
    for doc_name, sections in indexed_docs.items():
        context_lines.append(f"--- Document: {doc_name} ---")
        for section_num, section_text in sections.items():
            context_lines.append(f"Section {section_num}: {section_text}")
    
    context_text = "\n".join(context_lines)
    
    if not HAS_LLM:
        return f"[MOCK ANSWER - LLM NOT CONFIGURED]\n\nQuestion: {question}\nContext length: {len(context_text)}"
        
    client = genai.Client()
    
    prompt = f"Context Documents:\n{context_text}\n\nQuestion:\n{question}\n\nPlease answer based ONLY on the provided context."
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.0,
            ),
        )
        return response.text
    except Exception as e:
        return f"LLM API Error: {str(e)}"

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    agents_path = os.path.join(base_dir, "agents.md")
    
    policy_files = [
        os.path.normpath(os.path.join(base_dir, "..", "data", "policy-documents", "policy_hr_leave.txt")),
        os.path.normpath(os.path.join(base_dir, "..", "data", "policy-documents", "policy_it_acceptable_use.txt")),
        os.path.normpath(os.path.join(base_dir, "..", "data", "policy-documents", "policy_finance_reimbursement.txt"))
    ]
    
    print("Loading AI configuration...")
    system_prompt = load_agents_config(agents_path)
    
    print("Retrieving and indexing policy documents...")
    indexed_docs = retrieve_documents(policy_files)
    
    if not indexed_docs:
        print("No documents loaded. Exiting.")
        return
        
    print("\nSystem ready. Type 'exit' or 'quit' to stop.")
    print("-" * 50)
    
    while True:
        try:
            question = input("\nYour question: ").strip()
            if question.lower() in ['exit', 'quit']:
                break
            if not question:
                continue
                
            print("\nThinking...")
            answer = answer_question(question, indexed_docs, system_prompt)
            print("-" * 50)
            print(answer)
            print("-" * 50)
            
        except KeyboardInterrupt:
            break
        except EOFError:
            break
            
if __name__ == "__main__":
    main()
