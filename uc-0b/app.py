import argparse
import re

MANDATORY_CLAUSES = ['2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2']

SCOPE_BLEED_PHRASES = [
    "standard industry standards",
    "typical government practices",
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to"
]

def retrieve_policy(file_path: str) -> dict:
    """
    Skill: retrieve_policy
    Parse the input text into a dictionary of the 10 specific mandatory clauses.
    Raises exception if any are missing.
    """
    clauses = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    current_clause = None
    buffer = []

    for line in lines:
        match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
        if match:
            if current_clause:
                clauses[current_clause] = " ".join(buffer).strip()
            current_clause = match.group(1)
            buffer = [match.group(2)]
        elif current_clause and line.strip() and not line.startswith('═'):
            if re.match(r'^\d+\.\s+[A-Z\s\(\)\-]+$', line.strip()):
                continue
            buffer.append(line.strip())
            
    if current_clause:
        clauses[current_clause] = " ".join(buffer).strip()

    extracted = {}
    missing = []
    for mandatory in MANDATORY_CLAUSES:
        if mandatory in clauses:
            extracted[mandatory] = clauses[mandatory]
        else:
            missing.append(mandatory)
            
    if missing:
        raise ValueError(f"CRITICAL OMISSION: The following mandatory clauses are missing from the parsed document: {', '.join(missing)}")

    return extracted


def enforce_rules(clause_num, clause_text):
    """
    Actively validate binding verbs, 5.2 trap, and strip scope bleed.
    Returns (summarized_text, is_verbatim, warning_msg).
    """
    text_lower = clause_text.lower()
    is_verbatim = False
    warning_msg = None
    
    # Prohibit Scope Bleed: Automatically strip out external phrases
    clean_text = clause_text
    for bleed in SCOPE_BLEED_PHRASES:
        # Case insensitive replace
        clean_text = re.sub(re.escape(bleed), "", clean_text, flags=re.IGNORECASE).strip()
        # Clean up double spaces that might result
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
    text_lower = clean_text.lower()
    
    # Binding Verbs
    binding_verbs = ['must', 'will', 'requires', 'required', 'not permitted', 'forfeited']
    has_binding = any(verb in text_lower for verb in binding_verbs)
    
    # The Trap (Clause 5.2)
    if clause_num == '5.2':
        if "department head" not in text_lower or "hr director" not in text_lower:
            is_verbatim = True
            warning_msg = "WARNING: Clause 5.2 trap triggered. Missing dual approval conditions (Department Head AND HR Director). Reverting to verbatim."
            clean_text = clause_text # Revert any summarization
    
    if has_binding or (clause_num == '5.2' and is_verbatim):
        is_verbatim = True
        
    return clean_text, is_verbatim, warning_msg


def summarize_policy(clauses: dict) -> str:
    """
    Skill: summarize_policy
    Generate a Markdown summary. Quotes verbatim and flags for human review if complexity fails.
    """
    summary_lines = ["# Document Summary (Enforced Compliance)\n"]
    
    for clause_num in MANDATORY_CLAUSES:
        clause_text = clauses[clause_num]
        
        clean_text, is_verbatim, warning_msg = enforce_rules(clause_num, clause_text)
        
        if warning_msg:
            summary_lines.append(f"> [!WARNING]\n> {warning_msg}\n")
            
        if is_verbatim:
            summary_lines.append(f"**Clause {clause_num} [VERBATIM/BINDING]**:\n> {clean_text}\n")
        else:
            summary_lines.append(f"**Clause {clause_num}**:\n{clean_text}\n")
            
    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Processor (Strict Mode)")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to output summary .txt file")
    args = parser.parse_args()

    try:
        extracted_clauses = retrieve_policy(args.input)
        summary = summarize_policy(extracted_clauses)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Compliance Summary generated successfully at {args.output}")
        
    except Exception as e:
        print(f"Error processing policy: {e}")
        exit(1)


if __name__ == "__main__":
    main()
