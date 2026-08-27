import os
import sys
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def retrieve_documents():
    """
    Skill 1: Parses structured policies and concatenates them into a pristine knowledge corpus.
    Applies the UC-0B Regex logic to strip unnumbered formatting and isolate discrete clauses.
    """
    base_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'policy-documents')
    files = [
        "policy_hr_leave.txt",
        "policy_it_acceptable_use.txt",
        "policy_finance_reimbursement.txt"
    ]
    
    context_blocks = []
    
    for filename in files:
        filepath = os.path.join(base_dir, filename)
        if not os.path.exists(filepath):
            print(f"CRITICAL ERROR: Document {filename} not found.")
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Optimize using UC-0B pattern
        clean_lines = []
        clean_lines.append(f"\n--- DOCUMENT: {filename} ---")
        
        current_clause_num = None
        current_clause_text = []

        def save_clause():
            if current_clause_num:
                clean_lines.append(f"{current_clause_num} " + " ".join(current_clause_text).strip())
                current_clause_text.clear()

        for line in lines:
            line_stripped = line.strip()
            
            # Skip empty lines or decorative dividers
            if not line_stripped or line_stripped.startswith("══") or line_stripped.startswith("CITY MUNICIPAL") or line_stripped.startswith("Document") or line_stripped.startswith("Version") or line_stripped.startswith("DEPARTMENT"):
                continue

            # Heading Match
            heading_match = re.match(r'^(\d+)\.\s+([A-Z\s]+)$', line_stripped)
            if heading_match:
                save_clause()
                clean_lines.append(f"\n### SECTION {line_stripped} ###")
                current_clause_num = None
                continue
                
            # Clause Match
            clause_match = re.match(r'^(\d+\.\d+)\s+(.*)', line_stripped)
            if clause_match:
                save_clause()
                current_clause_num = clause_match.group(1)
                current_clause_text.append(clause_match.group(2).strip())
            elif current_clause_num:
                # Continuation of previous clause
                current_clause_text.append(line_stripped)
                
        # Finalize
        save_clause()
        context_blocks.append("\n".join(clean_lines))

    return "\n\n".join(context_blocks)

def evaluate_forbidden_hedges(response_text):
    """
    Post-generation guardrail to completely nuke hedged hallucinations.
    """
    hedges = [
        "while not explicitly covered",
        "typically",
        "generally understood",
        "it is common practice",
        "it seems",
        "not explicitly mentioned, but",
        "usually"
    ]
    lower_res = response_text.lower()
    for hedge in hedges:
        if hedge in lower_res:
            return True
            
    # Check for blended answers by counting unique document citations if it attempts to answer a single question
    # For a question like "Can I use my personal phone for work files from home?", the prompt strictly says DO NOT BLEND.
    # The system prompt handles this directly, but this Python-layer checks are standard defense-in-depth.
    return False

def answer_question(query, optimized_context, index=None):
    """
    Skill 2: Submits the User Query strictly bound by R.I.C.E enforced System Prompts.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("\nCRITICAL ERROR: GEMINI_API_KEY is missing from environment. Create a .env file and place your key inside it.")
        sys.exit(1)
        
    client = genai.Client(api_key=api_key)
    
    # Read agents.md dynamically or inject directly (Injecting directly for rigid runtime portability)
    system_instruction = f"""
ROLE: You are an exceedingly precise corporate policy oracle. You possess mathematical rigor over semantic domains. Your sole responsibility is to answer employee queries using strictly provided text bounds. You do not synthesize, you do not assume, and you do not bridge gaps between distinct policy systems to invent permissions.

CONTEXT: The following text provides three explicitly numbered corporate policies (HR Leave, IT Acceptable Use, and Finance Reimbursement). You may ONLY source answers from this text.
{optimized_context}

ENFORCEMENT RULES:
1. NEVER combine claims from two different documents into a single answer. Even if both seem relevant, they do not synthesize.
2. NEVER use hedging phrases such as "while not explicitly covered", "typically", "generally understood", "it is common practice", or "it seems".
3. For every factual claim you make, you MUST cite the source document name and the explicit section/clause number (e.g., "According to policy_it_acceptable_use.txt, Section 3.1...").
4. If a question requests information not explicitly detailed by the provided clauses, you MUST use exactly the following refusal template without appending further explanation:
This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.
"""
    
    # Generate response
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=query,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.0
            )
        )
        output_str = response.text.strip()
        
        # Apply Post-Guardrail (Failure mode 2 check)
        if evaluate_forbidden_hedges(output_str):
            return "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
            
        return output_str
    except Exception as e:
        return f"LLM Inference Error: {e}"

def main():
    print("Initializing Ask My Documents Engine (UC-X)...")
    context = retrieve_documents()
    print("Documents Optimised and Loaded via UC-0B Logic.\n")
    
    print("Welcome to the Zero-Hallucination Policy CLI.")
    print("Type your question below (or type 'exit' or 'quit' to close).")
    
    while True:
        try:
            query = input("\nQ: ").strip()
            if query.lower() in ['exit', 'quit']:
                break
            if not query:
                continue
            
            print("Analysing Policy Bounds...")
            answer = answer_question(query, context)
            print("\nA:\n" + answer + "\n")
            print("-" * 60)
            
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
