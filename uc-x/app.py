"""
UC-X app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import os
import sys
import re
from google import genai
from google.genai import types

# ==========================================
# CONSTANTS & CONFIGURATION
# ==========================================

# Enforcement Rule 3: The exact refusal template, no variations.
REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

DEFAULT_FILES = [
    "../data/policy-documents/policy_hr_leave.txt",
    "../data/policy-documents/policy_it_acceptable_use.txt",
    "../data/policy-documents/policy_finance_reimbursement.txt"
]

# ==========================================
# SKILL 1: retrieve_documents
# ==========================================
def retrieve_documents(file_paths):
    """
    Loads all specified policy files and indexes their content strictly 
    by document name and section number.
    """
    indexed_docs = {}
    
    # Regex to capture section numbers (e.g., 2.3) and the text that follows
    pattern = re.compile(r'^(\d+\.\d+)(.*?)(?=^\d+\.\d+|\Z)', re.MULTILINE | re.DOTALL)

    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"\nError [retrieve_documents]: Required file '{file_path}' is missing.", file=sys.stderr)
            print("Halting execution to prevent incomplete context.", file=sys.stderr)
            sys.exit(1)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"\nError [retrieve_documents]: Failed to read '{file_path}'. {e}", file=sys.stderr)
            sys.exit(1)

        doc_name = os.path.basename(file_path)
        matches = pattern.findall(content)

        if not matches:
            print(f"\nError [retrieve_documents]: No explicit section numbers found in '{doc_name}'.", file=sys.stderr)
            print("Halting execution to prevent condition dropping and incomplete context.", file=sys.stderr)
            sys.exit(1)

        indexed_docs[doc_name] = {}
        for match in matches:
            section_num = match[0].strip()
            section_text = match[1].strip()
            indexed_docs[doc_name][section_num] = section_text

    return indexed_docs

# ==========================================
# SKILL 2: answer_question
# ==========================================
def answer_question(question, indexed_docs):
    """
    Searches the indexed documents to provide a definitive, single-source answer 
    with explicit citations or outputs the strict refusal template.
    """
    
    # Format the indexed context into a readable string for the LLM
    context_str = ""
    for doc_name, sections in indexed_docs.items():
        context_str += f"\n--- DOCUMENT: {doc_name} ---\n"
        for sec_num, sec_text in sections.items():
            context_str += f"Section {sec_num}: {sec_text}\n"

    system_prompt = f"""
    ROLE: You are a rigid internal policy compliance agent restricted solely to querying and citing provided HR, IT, and Finance policy documents.

    INTENT: Deliver exact, single-source answers with explicit document and section citations, or output the precise refusal template when a query cannot be definitively answered by a single document.

    CONTEXT: You have access only to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt. You must ignore all external knowledge, industry norms, or general corporate practices.

    INDEXED DOCUMENTS DATABASE:
    {context_str}

    ENFORCEMENT RULES (CRITICAL):
    1. Never combine claims from two different documents into a single answer. If an answer requires blending policies, output ONLY the refusal template.
    2. Never use hedging phrases: "while not explicitly covered", "typically", "generally understood", "it is common practice".
    3. If question is not explicitly answered in the documents — use the refusal template exactly, no variations.
    4. Cite source document name + section number for every factual claim.
    5. Multi-condition obligations must be stated in full (e.g., if two approvals are required, state both). Do not drop conditions.

    REFUSAL TEMPLATE:
    {REFUSAL_TEMPLATE}
    """

    try:
        if not os.environ.get("GEMINI_API_KEY"):
             raise ValueError("GEMINI_API_KEY environment variable is not set.")
             
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=question,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.0, # Zero temperature is required for strict rule adherence and preventing hallucinations
            )
        )
        
        # Additional safety net: If the model attempted to output the refusal template but modified it, 
        # catch it and force the exact constant string.
        if "policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt" in response.text and "Please contact" in response.text:
            return REFUSAL_TEMPLATE
            
        return response.text.strip()
        
    except Exception as e:
        # Error handling: If API fails, default to safe refusal to prevent silent failure
        print(f"\n[System Error during generation: {e}]", file=sys.stderr)
        return REFUSAL_TEMPLATE

# ==========================================
# MAIN INTERACTIVE CLI PIPELINE
# ==========================================
def main():
    print("Initializing UC-X Policy Agent...")
    print("Loading and indexing documents...")
    
    # Initialize Skill 1
    indexed_docs = retrieve_documents(DEFAULT_FILES)
    
    total_docs = len(indexed_docs)
    total_sections = sum(len(sections) for sections in indexed_docs.values())
    print(f"Successfully indexed {total_sections} sections across {total_docs} documents.\n")
    print("="*60)
    print("Interactive Policy CLI started. Type your questions below.")
    print("Type 'exit' or 'quit' to close.")
    print("="*60)

    # Interactive Loop
    while True:
        try:
            user_input = input("\nQuestion: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting...")
                break
            
            if not user_input:
                continue
                
            # Initialize Skill 2
            answer = answer_question(user_input, indexed_docs)
            print(f"\nAnswer:\n{answer}")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            break

if __name__ == "__main__":
    main()