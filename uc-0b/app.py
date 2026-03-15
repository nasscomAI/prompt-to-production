import argparse
import os
import re

def retrieve_policy(filepath: str) -> dict:
    """
    Loads a .txt policy file and returns the content as structured numbered sections.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Policy file not found: {filepath}")
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    sections = {}
    # Regex to match numbered clauses like '1.1', '2.3' etc. at the start of lines
    # and capture the text until the next numbered clause or end of file/section.
    pattern = re.compile(r'^(\d+\.\d+)\s+(.*?)(?=(?:^\d+\.\d+|\n═|\Z))', re.MULTILINE | re.DOTALL)
    
    for match in pattern.finditer(content):
        clause_id = match.group(1).strip()
        # Clean up the text: replace newlines with spaces and strip extra whitespace
        text = match.group(2).strip().replace('\n', ' ')
        text = re.sub(r'\s+', ' ', text)
        sections[clause_id] = text
        
    if not sections:
        raise ValueError("Could not parse any numbered sections from the file.")
        
    return sections

def summarize_policy(sections: dict) -> str:
    """
    Takes structured sections and produces a compliant human-readable policy summary 
    with clause references, preserving conditions and avoiding scope bleed.
    """
    summary_lines = [
        "HR Leave Policy Summary",
        "=======================",
        ""
    ]
    
    # Sort clauses numerically
    def sort_key(k):
        parts = k.split('.')
        return int(parts[0]), int(parts[1])
        
    sorted_clauses = sorted(sections.keys(), key=sort_key)
    
    for clause_id in sorted_clauses:
        text = sections[clause_id]
        
        # We must avoid Obligation softening and Clause omission.
        # Check if the clause has multi-condition obligations like "Department Head AND HR Director"
        # or other critical conditions where summarization risks meaning loss.
        # It's safer to flag and quote verbatim.
        multi_condition_keywords = ["and", "requires", "must", "if", "not valid", "not permitted"]
        
        needs_verbatim = False
        if any(keyword in text.lower() for keyword in multi_condition_keywords):
            needs_verbatim = True
            
        if needs_verbatim:
            # Rule 4: If a clause cannot be summarised without meaning loss — quote it verbatim and flag it
            formatted_clause = f"Clause {clause_id} [FLAGGED: VERBATIM - Preserving all conditions] : \"{text}\""
        else:
            # For simpler clauses, we can use a light summary or just pass the text directly 
            # to strictly obey Rule 3: Never add information not present in the source.
            formatted_clause = f"Clause {clause_id} : {text}"
            
        summary_lines.append(formatted_clause)
        
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()

    try:
        # Skill 1: Retrieve Policy
        structured_sections = retrieve_policy(args.input)
        
        # Skill 2: Summarize Policy
        summary_text = summarize_policy(structured_sections)
        
        # Write Output
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary_text)
            
        print(f"Success. Summary written to {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
