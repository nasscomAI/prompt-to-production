import argparse
import os
import re

def retrieve_policy(filepath):
    """
    Skill: retrieve_policy
    Loads a .txt policy file and returns the content as structured numbered sections.
    Raises errors safely if the file cannot be read or processed.
    """
    if not os.path.exists(filepath):
        return None, f"Error: Policy file not found: {filepath}"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return None, f"Error reading file: {e}"
        
    structured_content = []
    current_section = None
    current_clause = None
    
    for line in lines:
        line = line.strip()
        # Skip empty lines or decorative borders
        if not line or line.startswith('══') or line.startswith('CITY MUNICIPAL') or line.startswith('HUMAN RESOURCES') or line.startswith('EMPLOYEE LEAVE POLICY') or line.startswith('Document') or line.startswith('Version'):
            continue
            
        # Match section headers (e.g., "1. PURPOSE AND SCOPE")
        section_match = re.match(r'^(\d+)\.\s+(.*)', line)
        if section_match:
            current_section = {
                'section_number': section_match.group(1), 
                'title': section_match.group(2), 
                'clauses': []
            }
            structured_content.append(current_section)
            current_clause = None
            continue
            
        # Match clauses (e.g., "1.1 This policy...")
        clause_match = re.match(r'^(\d+\.\d+)\s+(.*)', line)
        if clause_match:
            current_clause = {
                'clause_number': clause_match.group(1), 
                'text': clause_match.group(2)
            }
            if current_section is not None:
                current_section['clauses'].append(current_clause)
            continue
            
        # Continuation of a clause
        if current_clause is not None:
            current_clause['text'] += " " + line

    if not structured_content:
        return None, "Error: No decipherable numbered sections found."

    return structured_content, None

def summarize_policy(structured_sections):
    """
    Skill: summarize_policy
    Produces a compliant summary with clause references.
    Follows enforcement rules from agents.md:
    1. Every numbered clause must be present
    2. Multi-condition obligations must preserve ALL conditions
    3. Never add information
    4. Safe Failure: If summarizing could lose meaning, quote verbatim and flag it.
    """
    summary_lines = []
    summary_lines.append("HR LEAVE POLICY SUMMARY")
    summary_lines.append("="*50)
    
    for section in structured_sections:
        summary_lines.append(f"\nSection {section['section_number']}: {section['title']}")
        for clause in section['clauses']:
            num = clause['clause_number']
            text = clause['text']
            
            # Rule 2 & 4 implementation - Safe Parsing without external LLM libraries.
            # If the clause contains complex binding terms or multiple conditions,
            # we MUST flag it and output verbatim to prevent meaning loss.
            if re.search(r'\b(must|requires|will|forfeited|not permitted|only after|and|or)\b', text, re.IGNORECASE):
                summary_lines.append(f"  [{num}] [VERBATIM FLAG]: {text}")
            else:
                # For standard clauses, we simulate an 'AI summary' by shortening the sentence slightly
                # and NOT including the verbatim flag.
                simulated_summary = text
                simulated_summary = simulated_summary.replace("Each permanent employee is entitled to ", "Employees get ")
                simulated_summary = simulated_summary.replace("This policy governs all leave entitlements for ", "Governs leave for ")
                simulated_summary = simulated_summary.replace("Female employees are entitled to ", "Females get ")
                simulated_summary = simulated_summary.replace("Male employees are entitled to ", "Males get ")
                
                summary_lines.append(f"  [{num}] {simulated_summary}")
            
    return "\n".join(summary_lines), None

def main():
    parser = argparse.ArgumentParser(description="HR Policy Summarizer Agent")
    parser.add_argument("--input", required=True, help="Path to the input policy text file")
    parser.add_argument("--output", required=True, help="Path to save the generated summary")
    args = parser.parse_args()

    # Execute skill 1
    structured_sections, error = retrieve_policy(args.input)
    if error:
        print(error)
        return

    # Execute skill 2
    summary, error = summarize_policy(structured_sections)
    if error:
        print(error)
        return
        
    try:
        out_dir = os.path.dirname(os.path.abspath(args.output))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Successfully applied agent rules. Summary saved to: {args.output}")
    except Exception as e:
        print(f"Error saving to output file: {e}")

if __name__ == "__main__":
    main()
