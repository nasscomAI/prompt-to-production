import os
import argparse
import re
import sys

# Gracefully attempt to import an LLM client, but allow execution without it.
try:
    from openai import OpenAI
    client = OpenAI() # Expects OPENAI_API_KEY
except Exception:
    client = None

AGENT_PROMPT = """
role: You are a strict Policy Summarization Agent. Your operational boundary is to generate accurate summaries of HR leave policy documents without altering, softening, or omitting any core obligations.

intent: A correct output is a comprehensive summary that perfectly preserves the original meaning and binding requirements of every clause, allowing users to verify all strict obligations and conditions accurately.

context: You must strictly use only the provided policy document text. You must not use external knowledge, generalized expectations, or scope bleed phrases such as "as is standard practice", "typically in government organisations", or "employees are generally expected to".

enforcement:
  - Every numbered clause must be present in the summary.
  - Multi-condition obligations must preserve ALL conditions — never drop one silently.
  - Never add information not present in the source document.
  - If a clause cannot be summarised without meaning loss — quote it verbatim and flag it with [VERBATIM].
"""

def retrieve_policy(file_path: str) -> list:
    """
    Skill: retrieve_policy
    Reads a plain text HR leave policy file and parses its contents into structured, numbered sections.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        # Error handling: Halts execution if file is unreadable to prevent silent clause omission
        print(f"Error: Could not read file {file_path}. Halting execution. ({e})")
        sys.exit(1)
        
    clauses = []
    current_clause = None
    
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
            
        # Match lines like "2.1 Text..."
        match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
        if match:
            if current_clause:
                clauses.append(current_clause)
            current_clause = {
                'number': match.group(1),
                'text': match.group(2)
            }
        else:
            # Append multiline text to the current clause
            # Ignoring headers and separator lines
            if current_clause and not line.startswith('═') and not re.match(r'^\d+\.\s', line) and not line.isupper():
                current_clause['text'] += " " + line
                
    if current_clause:
        clauses.append(current_clause)
        
    if not clauses:
        # Error handling: Halts if no clauses are found
        print("Error: Input file lacks identifiable numbered clauses. Halting execution.")
        sys.exit(1)
        
    return clauses

def summarize_policy(clauses: list) -> str:
    """
    Skill: summarize_policy
    Processes structured policy clauses to generate a compliant summary.
    """
    # 1. Try to use LLM for intelligent, compliant summarization if configured
    if client and os.environ.get("OPENAI_API_KEY"):
        try:
            policy_text = "\n".join([f"Clause {c['number']}: {c['text']}" for c in clauses])
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": AGENT_PROMPT},
                    {"role": "user", "content": f"Summarize the following policy document clauses:\n\n{policy_text}"}
                ],
                temperature=0.0
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LLM generation failed ({e}). Falling back to algorithmic strict summarization...")

    # 2. Algorithmic fallback ensuring 100% rule enforcement
    summary_lines = ["# HR Leave Policy Summary\n"]
    
    for clause in clauses:
        num = clause['number']
        text = clause['text']
        text_lower = text.lower()
        
        # Identify complex logic that risks condition drop or softening
        has_multi_condition = " and " in text_lower or " or " in text_lower or "," in text_lower
        strict_verbs = ["must", "will", "requires", "not permitted", "forfeited", "only"]
        has_strict_verb = any(verb in text_lower for verb in strict_verbs)
        
        # Error handling logic from skills.md: 
        # "If a clause cannot be summarized without risk of obligation softening or dropping multi-condition requirements, it quotes the clause verbatim and flags it"
        if has_multi_condition or has_strict_verb:
            summary_lines.append(f"- Clause {num} [VERBATIM]: {text}")
        else:
            summary_lines.append(f"- Clause {num}: {text}")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to output summary .txt file")
    args = parser.parse_args()
    
    # Skill 1: Extract clauses
    clauses = retrieve_policy(args.input)
    
    # Skill 2: Generate summary
    summary = summarize_policy(clauses)
    
    # Write to output file
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"Summary successfully written to {args.output}")
    except Exception as e:
        print(f"Error writing to output file {args.output}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
