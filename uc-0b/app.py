import argparse
import os
import sys
import re

try:
    import openai
except ImportError:
    openai = None

SYSTEM_PROMPT = """role: >
  You are a policy summarization agent. Your operational boundary is strictly limited to reading the provided HR leave policy document and producing a structured text summary.
intent: >
  A compliant summary that includes all numbered clauses with their references, preserving all core obligations and multi-condition requirements without softening their meaning.
context: >
 You are allowed to use ONLY the provided source document that is input ../data/policy-documents/policy_hr_leave.txt. You must absolutely exclude outside knowledge, standard practices, or general employee expectations. Do not infer or invent information not explicitly stated in the text.
enforcement:
  - "Every numbered clause must be present in the summary"
  - "Multi-condition obligations must preserve ALL conditions — never drop one silently"
  - "Never add information not present in the source document"
  - "If a clause cannot be summarised without meaning loss — quote it verbatim and flag it"
"""

def retrieve_policy(file_path: str) -> list:
    """
    Loads a .txt policy file and returns the content as structured numbered sections.
    """
    if not os.path.exists(file_path) or not os.access(file_path, os.R_OK):
        raise ValueError(f"Parse Error: File '{file_path}' is missing or unreadable. Halting execution.")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        raise ValueError(f"Parse Error: Could not read file '{file_path}': {e}. Halting execution.")

    sections = []
    current_section = None
    current_text = []

    for line in content.split('\n'):
        match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
        if match:
            if current_section:
                sections.append({
                    "section_number": current_section,
                    "text": " ".join(current_text).strip()
                })
            current_section = match.group(1)
            current_text = [match.group(2).strip()]
        elif current_section:
            # Ignore separator lines and unnumbered section headers like '1. PURPOSE AND SCOPE'
            if not line.startswith('══') and not re.match(r'^\d+\.\s+[A-Z]', line):
                if line.strip():
                    current_text.append(line.strip())

    if current_section:
        sections.append({
            "section_number": current_section,
            "text": " ".join(current_text).strip()
        })
        
    if not sections:
        raise ValueError("Parse Error: File is not formatted with clear sections. Halting execution.")

    return sections

def summarize_policy(sections: list) -> str:
    """
    Takes structured sections and produces a compliant summary with clause references.
    """
    if not isinstance(sections, list) or not sections:
        raise ValueError("Error: Input must be a valid list of section objects. Halting execution.")
    
    use_llm = bool(os.getenv("OPENAI_API_KEY") and openai)
    
    if use_llm:
        client = openai.OpenAI()
        
        doc_content = "\n\n".join(f"Clause {s['section_number']}:\n{s['text']}" for s in sections)
        user_prompt = f"Please summarize the following policy document according to the strict system rules:\n\n{doc_content}"
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"  [!] LLM summarization failed: {e}")
            print("  [!] Falling back to strict verbatim quoting...")
            
    # Fallback to quoting verbatim to adhere to enforcement rules (no dropping conditions/obligations)
    summary_lines = []
    for s in sections:
        summary_lines.append(f"[{s['section_number']}] [VERBATIM - FLAGGED TO PREVENT MEANING LOSS]: {s['text']}")
    return "\n\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to the policy document (.txt)")
    parser.add_argument("--output", required=True, help="Path to write the summary (.txt)")
    args = parser.parse_args()

    print(f"Loading and structuring policy from '{args.input}'...")
    try:
        sections = retrieve_policy(args.input)
        print(f"Successfully retrieved {len(sections)} sections.")
    except Exception as e:
        print(e)
        sys.exit(1)
        
    print("Generating compliant summary...")
    try:
        summary = summarize_policy(sections)
    except Exception as e:
        print(e)
        sys.exit(1)
        
    print(f"Writing summary to '{args.output}'...")
    try:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print("Done.")
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
