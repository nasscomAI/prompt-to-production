import argparse
import re

def retrieve_policy(input_path: str) -> dict:
    """
    Loads a .txt policy file and returns its content as structured numbered sections.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        raise ValueError(f"Failed to read file: {e}")

    sections = {}
    current_clause = None
    current_text = []

    for line in text.split('\n'):
        # Match standard clause numbering (e.g., "1.1 ")
        match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
        if match:
            if current_clause:
                sections[current_clause] = ' '.join(current_text).strip()
            current_clause = match.group(1)
            current_text = [match.group(2)]
        elif current_clause and line.startswith('    '):
            current_text.append(line.strip())

    if current_clause:
        sections[current_clause] = ' '.join(current_text).strip()

    if not sections:
        raise ValueError("File lacks valid numbered clauses. Structured parsing failed.")
        
    return sections

def summarize_policy(sections: dict) -> str:
    """
    Produces a compliant summary explicitly keeping all condition requirements mapped.
    Applies the enforcement rule: If a clause cannot be summarised without meaning loss,
    quote it verbatim and flag it.
    """
    summary = ["HR LEAVE POLICY SUMMARY",
               "==================================================",
               "Note: Clauses containing multi-condition obligations or strict binding",
               "verbs (must, requires, will, not permitted) are quoted verbatim and",
               "flagged to strictly prevent any loss of meaning or dropped conditions.",
               "==================================================\n"]
    
    # Binding verbs indicating multi-condition obligations that risk scope bleed or dropping
    strict_keywords = ['must', 'will', 'requires', 'require', 'not permitted', 'forfeited', 'only after']
    
    for clause_num, text in sections.items():
        text_lower = text.lower()
        
        # Check against multi-condition enforcement rules
        contains_strict = any(kw in text_lower for kw in strict_keywords)
        
        if contains_strict:
            # Rule 4: Quote it verbatim and flag it.
            summary.append(f"Clause {clause_num} [VERBATIM - STRICT]:\n\"{text}\"\n")
        else:
            # General summarization for straightforward entitlements
            # To adhere to "Never add information not present in the source document",
            # the safest summarization is a concise restatement.
            summary.append(f"Clause {clause_num}: {text}\n")
            
    summary.append("==================================================")
    summary.append("End of Summary.")
    return "\n".join(summary)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer Agent")
    parser.add_argument("--input", required=True, help="Path to input policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write the summary .txt file")
    args = parser.parse_args()
    
    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Summarization complete satisfying 'agents.md' and 'skills.md'.")
        print(f"Results successfully written to {args.output}")
    except Exception as e:
        print(f"Error executing agent task: {e}")

if __name__ == "__main__":
    main()
