import os
import sys
import re
import json
import subprocess
import time

try:
    from google import genai
    from google.genai import types
except ModuleNotFoundError:
    print("Installing required package 'google-genai' into the current environment...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-genai", "--quiet"])
    from google import genai
    from google.genai import types

REFUSAL_TEMPLATE = """This question is not covered in the available policy documents
(policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
Please contact [relevant team] for guidance."""

def retrieve_documents(file_paths):
    """
    Loads all 3 policy files and indexes them by document name and section number.
    Error handling: If any required policy document is missing or unreadable, halt execution rather than running with incomplete data.
    """
    indexed_data = {}
    for path in file_paths:
        if not os.path.exists(path):
            print(f"Error: Required policy document is missing: {path}")
            sys.exit(1)
            
        doc_name = os.path.basename(path)
        indexed_data[doc_name] = {}
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Error: Required policy document is unreadable: {path}. Exception: {e}")
            sys.exit(1)
            
        current_section = None
        current_text = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Match section numbering (e.g. "2.1 text...")
            match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
            if match:
                if current_section:
                    indexed_data[doc_name][current_section] = " ".join(current_text)
                current_section = match.group(1)
                current_text = [match.group(2)]
            elif current_section:
                # Ignore top level headers like "2. ANNUAL LEAVE" or decorators "==="
                if not re.match(r'^\d+\.\s+[A-Z\s]+$', line) and not line.startswith('═'):
                    current_text.append(line)
                    
        if current_section:
            indexed_data[doc_name][current_section] = " ".join(current_text)
            
    return indexed_data

def answer_question(question, indexed_data):
    """
    Searches indexed documents to return a single-source answer with an exact citation or the required refusal template.
    Error handling: If answering requires cross-document blending, drops required conditions, or invites hedged hallucination, 
    immediately output the exact refusal template with no variations.
    """
    system_instruction = f"""Role: A policy Q&A agent whose operational boundary is to answer employee questions strictly based on the provided company policy documents.
Intent: To provide accurate, verifiable answers without hallucination or cross-document blending. A correct output either answers the question from a single source document with a specific citation, or outputs the exact refusal template if the answer is missing or ambiguous.
Context: Allowed to use only policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt. Must not use outside knowledge or assumptions.

Enforcement rules:
1. Never combine claims from two different documents into a single answer.
2. Never use hedging phrases: "while not explicitly covered", "typically", "generally understood", "it is common practice".
3. If question is not in the documents — use the refusal template exactly, no variations.
4. Cite source document name + section number for every factual claim.
5. If answering requires cross-document blending, drops required conditions, or invites hedged hallucination, immediately output the exact refusal template with no variations.

Refusal Template to use when needed:
{REFUSAL_TEMPLATE}"""

    context_str = json.dumps(indexed_data, indent=2)
    prompt = f"POLICY DOCUMENTS (Indexed):\n{context_str}\n\nUSER QUESTION:\n{question}\n\nANSWER:\n"
    
    try:
        time.sleep(13)  # Free tier allows 5 req/min; pace requests
        client = genai.Client() # Requires GEMINI_API_KEY environment variable

        # Retry up to 3 times on 503/429 transient errors
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.0
                    )
                )
                answer = response.text.strip()
                break
            except Exception as api_err:
                err_str = str(api_err)
                if attempt < 2 and ("503" in err_str or "429" in err_str):
                    wait = 30 * (attempt + 1)
                    print(f"[Rate limit / server busy, retrying in {wait}s...]")
                    time.sleep(wait)
                else:
                    raise
        
        # Error handling / strict enforcement post-processing
        bad_phrases = ["while not explicitly covered", "typically", "generally understood", "it is common practice"]
        lower_answer = answer.lower()
        if any(phrase in lower_answer for phrase in bad_phrases):
            return REFUSAL_TEMPLATE
            
        return answer
    except Exception as e:
        print(f"DEBUG EXCEPTION: {e}")
        # Fallback to refusal template on API or processing errors
        return REFUSAL_TEMPLATE

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_paths = [
        os.path.join(base_dir, "../data/policy-documents/policy_hr_leave.txt"),
        os.path.join(base_dir, "../data/policy-documents/policy_it_acceptable_use.txt"),
        os.path.join(base_dir, "../data/policy-documents/policy_finance_reimbursement.txt")
    ]
    
    print("Loading documents...")
    indexed_docs = retrieve_documents(file_paths)
    print("Documents loaded successfully.")
    
    print("\nAsk My Documents CLI")
    print("Type your question below (or 'exit' to quit).\n")
    
    while True:
        try:
            q = input("> ")
            if q.lower() in ('exit', 'quit'):
                break
            if not q.strip():
                continue
                
            ans = answer_question(q, indexed_docs)
            print(f"\n{ans}\n")
        except KeyboardInterrupt:
            print()
            break
        except EOFError:
            print()
            break

if __name__ == "__main__":
    main()
