import argparse
import sys
import os
import re
import json

try:
    from openai import OpenAI
except ImportError:
    print("Error: The 'openai' library is required.")
    print("Please install it running: pip install openai")
    sys.exit(1)

def retrieve_policy(filepath: str) -> list:
    """Loads a plain text policy file and structures its content into a list of numbered sections."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    clauses = []
    current_clause_num = None
    current_text = []
    
    # Regex to match clause starts, e.g., "2.3 Employees must..."
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.*)')
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean or line_clean.startswith('═') or re.match(r'^\d+\.\s+[A-Z\s]+', line_clean):
            # Skip empty lines, separators, and major headers (like "1. PURPOSE AND SCOPE")
            continue
            
        match = clause_pattern.match(line_clean)
        if match:
            if current_clause_num:
                clauses.append({"clause": current_clause_num, "text": " ".join(current_text)})
            current_clause_num = match.group(1)
            current_text = [match.group(2)]
        elif current_clause_num:
            # Append continuation lines to the current clause
            current_text.append(line_clean)
            
    # Add the last clause
    if current_clause_num and current_text:
        clauses.append({"clause": current_clause_num, "text": " ".join(current_text)})
        
    return clauses

def summarize_policy(structured_clauses: list) -> str:
    """Summarizes the structured policy sections into a compliant summary that strictly preserves all conditions."""
    system_prompt = """You are a legal synthesis assistant strictly responsible for extracting and summarizing numbered clauses from HR Leave policy documents.

INTENT
Produce a concise, complete summary of the policy document while rigorously preserving every obligation, condition, and binding verb without softening or omitting multi-condition approvals.

CONTEXT
You must only extract information present in the structured list provided. You are strictly forbidden from adding conventional best practices, generic filler text, hallucinating typical HR procedures, or inferring context outside the text boundary.

ENFORCEMENT RULES:
1. Every numbered clause provided must be explicitly present and covered in the resulting summary.
2. Multi-condition obligations (e.g., requires approval from X AND Y) must preserve ALL conditions verbatim — never drop one silently.
3. Never add information that is not explicitly present in the source document.
4. If a clause represents a complex obligation that cannot be summarized without potentially altering its meaning, quote it verbatim and flag it for human review.
"""
    
    # Convert structured clauses to formatted string for LLM
    clauses_text = json.dumps(structured_clauses, indent=2)
    
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Please summarize the following structured policy clauses according to the strict system enforcement rules:\n\n<CLAUSES>\n{clauses_text}\n</CLAUSES>"}
        ],
        temperature=0.0
    )
    return response.choices[0].message.content

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy document (e.g., .txt)")
    parser.add_argument("--output", required=True, help="Path to write the resulting summary")
    
    args = parser.parse_args()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY environment variable.")
        sys.exit(1)
        
    print(f"Reading {args.input}...")
    try:
        structured_content = retrieve_policy(args.input)
        print(f"Successfully extracted {len(structured_content)} numbered clauses.")
    except FileNotFoundError:
        print(f"Error: Could not find file {args.input}")
        sys.exit(1)
        
    print("Summarizing policy document using AI (this may take a sec)...")
    try:
        summary = summarize_policy(structured_content)
    except Exception as e:
        print(f"An error occurred during API request: {e}")
        sys.exit(1)
    
    print(f"Writing compliant summary to {args.output}...")
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(summary)
        
    print("Done!")

if __name__ == "__main__":
    main()
