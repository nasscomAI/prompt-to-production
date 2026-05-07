"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import sys
import re
from google import genai
from google.genai import types

# ==========================================
# SKILL 1: retrieve_policy
# ==========================================
def retrieve_policy(file_path):
    """
    Loads a plain text policy file and returns its content organized into structured, numbered sections.
    """
    if not os.path.exists(file_path):
        print(f"Error [retrieve_policy]: File '{file_path}' cannot be read. Halting execution.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error [retrieve_policy]: Failed to read file. {e}", file=sys.stderr)
        sys.exit(1)

    # Regex to extract numbered clauses (e.g., "2.3", "5.2") and their text
    pattern = re.compile(r'^(\d+\.\d+)(.*?)(?=^\d+\.\d+|\Z)', re.MULTILINE | re.DOTALL)
    matches = pattern.findall(content)

    if not matches:
        print("Error [retrieve_policy]: Text cannot be reliably parsed into numbered clauses. Ensure correct format to prevent clause omission.", file=sys.stderr)
        sys.exit(1)

    structured_sections = []
    for match in matches:
        clause_num = match[0].strip()
        clause_text = match[1].strip()
        structured_sections.append({
            "clause": clause_num,
            "text": f"{clause_num} {clause_text}"
        })

    return structured_sections


# ==========================================
# SKILL 2: summarize_policy
# ==========================================
def summarize_policy(structured_sections):
    """
    Processes structured policy sections to generate a concise summary that strictly 
    retains all clause references and binding multi-condition obligations.
    """
    
    system_prompt = """
    ROLE: You are a policy summarization agent responsible for condensing HR leave policy documents without altering, softening, or omitting any core obligations or binding conditions.

    INTENT: Produce a compliant summary document where every core obligation from the source is accurately represented, verifiable against the original clause inventory without clause omission or obligation softening.

    CONTEXT: Rely strictly on the provided source document. Do not include external knowledge, standard practices, or generalized expectations not explicitly stated in the text.

    ENFORCEMENT RULES (CRITICAL):
    1. Every numbered clause provided must be present in the summary.
    2. Multi-condition obligations must preserve ALL conditions — never drop one silently (e.g., if two approvers are required, list both).
    3. Never add information not present in the source document.
    4. ERROR HANDLING / ESCALATION: If a clause cannot be summarised without meaning loss, condition dropping, or obligation softening, you must quote it verbatim and explicitly flag it by appending "[FLAG: VERBATIM QUOTE - RISK OF MEANING LOSS]".
    """

    clauses_text = "\n\n".join([f"Clause {s['clause']}:\n{s['text']}" for s in structured_sections])
    
    user_prompt = f"""
    Summarize the following HR leave policy document clause by clause. 
    Strictly adhere to your enforcement rules.
    
    SOURCE DOCUMENT CLAUSES:
    {clauses_text}
    """

    try:
        summary_result = call_llm(system_prompt, user_prompt)
        return summary_result
    except Exception as e:
        print(f"Error [summarize_policy]: Generation failed. {e}", file=sys.stderr)
        sys.exit(1)


def call_llm(system_prompt, user_prompt):
    """
    Calls the Gemini API using the google-genai SDK.
    """
    # The client automatically picks up the GEMINI_API_KEY environment variable
    if not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it before running the script.")
        
    client = genai.Client()
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.0, # Temperature 0 is critical for strict rule adherence
            )
        )
        return response.text
    except Exception as e:
         raise RuntimeError(f"API request failed: {e}")


# ==========================================
# MAIN EXECUTION PIPELINE
# ==========================================
def main():
    parser = argparse.ArgumentParser(description="UC-0B: Policy Summarization Agent")
    parser.add_argument("--input", required=True, help="Path to the input policy document (.txt)")
    parser.add_argument("--output", required=True, help="Path to the output summary document (.txt)")
    args = parser.parse_args()

    print(f"Reading and parsing policy document from: {args.input}")
    
    # Execute Skill 1
    structured_sections = retrieve_policy(args.input)
    print(f"Successfully extracted {len(structured_sections)} clauses.")

    # Execute Skill 2
    print("Generating compliant summary...")
    final_summary = summarize_policy(structured_sections)

    # Output Management
    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(final_summary)
        
    print(f"Summary successfully written to: {args.output}")

if __name__ == "__main__":
    main()