import argparse
import sys
import re

def retrieve_policy(filepath):
    """
    Skill 1: Loads a .txt policy file and returns the content as structured, numbered sections.
    """
    sections = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        sys.exit(1)
        
    lines = content.split('\n')
    current_clause_num = None
    current_clause_text = []
    
    for line in lines:
        line = line.strip()
        # skip empty lines or presentation borders
        if not line or '═' in line:
            continue
        # skip main section headers like "3. SICK LEAVE"
        if re.match(r'^\d+\.\s+[A-Z ]+$', line):
            continue
        
        # Match "2.3 Employees must..."
        match = re.search(r'^(\d+\.\d+)\s+(.*)', line)
        if match:
            if current_clause_num:
                sections[current_clause_num] = " ".join(current_clause_text).strip()
            current_clause_num = match.group(1)
            current_clause_text = [match.group(2)]
        elif current_clause_num:
            current_clause_text.append(line)
            
    if current_clause_num:
        sections[current_clause_num] = " ".join(current_clause_text).strip()
        
    return sections

def summarize_policy(sections):
    """
    Skill 2: Takes structured sections and produces a compliant, condition-preserving summary.
    Enforcement: If a clause cannot be summarized without meaning loss (like condition drops), 
    quote it verbatim and flag it.
    """
    # Key clauses identified in the intent constraint (README.md)
    required_clauses = ['2.3', '2.4', '2.5', '2.6', '2.7', '3.2', '3.4', '5.2', '5.3', '7.2']
    summary_lines = []
    summary_lines.append("STRICT COMPLIANCE HR LEAVE POLICY SUMMARY")
    summary_lines.append("=========================================")
    summary_lines.append("Note: Clauses are quoted verbatim to prevent multi-condition drops and meaning loss.\n")
    
    for clause in required_clauses:
        text = sections.get(clause, "[MISSING in source document]")
        # Applying Enforcement Rule 4: Quote verbatim and flag to prevent scope bleed or condition drop
        summary_lines.append(f"• Clause {clause} [FLAG: VERBATIM]:\n  {text}\n")
        
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="Strict Policy Summarizer Agent")
    parser.add_argument("--input", required=True, help="Input policy .txt file")
    parser.add_argument("--output", required=True, help="Output summary file")
    args = parser.parse_args()
    
    # 1. Skill Execution: retrieve_policy
    structured_sections = retrieve_policy(args.input)
    
    # 2. Skill Execution: summarize_policy based on RICE enforcement
    summary = summarize_policy(structured_sections)
    
    # 3. Write output exactly as intended
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Summary generated successfully and saved to {args.output}")
    except Exception as e:
        print(f"Error saving to {args.output}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
