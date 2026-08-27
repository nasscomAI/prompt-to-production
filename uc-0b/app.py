import argparse
import os
import sys

def retrieve_policy(file_path: str) -> str:
    """Skill: retrieve_policy — loads .txt policy file, returns content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        sys.exit(1)

def summarize_policy(policy_text: str) -> str:
    """Skill: summarize_policy — produces compliant summary with clause references based on agents.md."""
    
    # RICE rules defined in agents.md
    system_instruction = """
ROLE:
HR Policy Summarization Agent. You summarize human resources policy documents with strict fidelity. Your operational boundary is strictly limited to text summarization of provided policy documents, ensuring no loss of conditions, softening of obligations, or scope bleed.

INTENT:
Produce a concise, faithful summary of the provided policy document. A correct output must include every numbered clause from the original document, preserving all multi-condition obligations exactly as stated. The summary must not contain any external information, and any clause that cannot be summarized without altering its meaning must be quoted verbatim and flagged.

CONTEXT:
You are allowed to use ONLY the provided policy document text. You are explicitly forbidden from using external knowledge, assumptions about "standard practice", or typical organizational behaviors. Do not include phrases like "as is standard practice" or "typically in government organisations".

ENFORCEMENT RULES:
1. Every numbered clause must be present in the summary
2. Multi-condition obligations must preserve ALL conditions — never drop one silently
3. Never add information not present in the source document
4. If a clause cannot be summarised without meaning loss — quote it verbatim and flag it
5. Refuse to summarize if asked to include information not present in the provided source document or if the document is not a policy text.
"""
    prompt = f"Please summarize the following policy document according to your strict enforcement rules:\n\n{policy_text}"

    # Standard LLM check. We try Google Gemini first, then OpenAI.
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    openai_api_key = os.environ.get("OPENAI_API_KEY")

    if gemini_api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-pro', system_instruction=system_instruction)
            response = model.generate_content(prompt)
            return response.text
        except ImportError:
            print("To use Gemini, please run: pip install google-generativeai")
    elif openai_api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except ImportError:
            print("To use OpenAI, please run: pip install openai")
    else:
        print("ERROR: No API key found. Please set GEMINI_API_KEY or OPENAI_API_KEY in your environment.")
        # Fallback to outputting the built prompt for manual testing
        fallback = f"==== SYSTEM PROMPT ====\n{system_instruction}\n\n==== USER PROMPT ====\n{prompt}\n\n==== END ===="
        print("Falling back to generating a file with the constructed prompts.")
        return fallback

    print("ERROR: The required python package for your API key is not installed.")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="UC-0B: Summary That Changes Meaning")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to output summary .txt file")
    args = parser.parse_args()

    print(f"Reading input file: {args.input}")
    policy_doc = retrieve_policy(args.input)

    print("Generating summarization using defined constraints...")
    summary = summarize_policy(policy_doc)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"Success! Compliant summary written to: {args.output}")

if __name__ == "__main__":
    main()
