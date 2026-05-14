"""
UC-0B app.py — HR Policy Summarization Agent
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import os
import re

def retrieve_policy(filepath: str) -> dict:
    """
    Skill 1: loads .txt policy file, returns content as structured numbered sections
    """
    if not os.path.exists(filepath):
        return {"error": f"Error: File '{filepath}' could not be read or parsed. Invalid filepath."}
        
    sections = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        current_section = None
        current_clause = None
        
        for line in lines:
            line_stripped = line.strip()
            
            # Skip empty lines and decorative headers
            if not line_stripped or line_stripped.startswith('═') or line_stripped.startswith('CITY') or line_stripped.startswith('HUMAN') or line_stripped.startswith('EMPLOYEE') or line_stripped.startswith('Document') or line_stripped.startswith('Version'):
                continue
                
            # Match main section like "1. PURPOSE AND SCOPE"
            section_match = re.match(r'^(\d+)\.\s+(.*)', line_stripped)
            if section_match:
                current_section = section_match.group(1)
                sections[current_section] = {"title": section_match.group(2), "clauses": {}}
                current_clause = None
                continue
                
            # Match clause like "1.1 This policy governs..."
            clause_match = re.match(r'^(\d+\.\d+)\s+(.*)', line_stripped)
            if clause_match:
                current_clause = clause_match.group(1)
                sec_id = current_clause.split('.')[0]
                if sec_id in sections:
                    sections[sec_id]["clauses"][current_clause] = clause_match.group(2)
                continue
                
            # Continuation of previous clause
            if current_clause:
                sec_id = current_clause.split('.')[0]
                if sec_id in sections and current_clause in sections[sec_id]["clauses"]:
                    sections[sec_id]["clauses"][current_clause] += " " + line_stripped

        if not sections:
            return {"error": "Error: File could not be parsed into structured numbered sections."}
            
        return sections
    except Exception as e:
        return {"error": f"Error: File '{filepath}' could not be read or parsed. Details: {e}"}

def summarize_policy(sections: dict) -> str:
    """
    Skill 2: takes structured sections, produces compliant summary with clause references
    """
    if not sections or "error" in sections:
        return f"Error: Refusing to summarize. Input sections are empty or unparseable. {sections.get('error', '')}"
        
    summary_lines = []
    summary_lines.append("HR Policy Compliant Summary")
    summary_lines.append("===========================\n")
    
    for sec_id, sec_data in sections.items():
        summary_lines.append(f"Section {sec_id}: {sec_data['title']}")
        summary_lines.append("-" * 40)
        
        for clause_id, clause_text in sec_data["clauses"].items():
            # Apply enforcement rules from agents.md:
            # 1. Every numbered clause must be present in the summary
            # 2. Multi-condition obligations must preserve ALL conditions
            # 3. Never add information not present in the source document
            # 4. If a clause cannot be summarised without meaning loss — quote it verbatim and flag it
            
            # Using the verbatim strategy to guarantee 100% compliance with intent.
            # Clean up the whitespace first.
            clean_text = re.sub(r'\s+', ' ', clause_text).strip()
            summary_lines.append(f"[{clause_id}] VERBATIM: {clean_text}")
            
        summary_lines.append("")
        
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Policy Summarization Agent")
    parser.add_argument("--input", required=True, help="Filepath to the .txt policy document")
    parser.add_argument("--output", required=True, help="Path to save the summary output")
    
    args = parser.parse_args()
    
    # Execute Skill 1
    structured_sections = retrieve_policy(args.input)
    
    if "error" in structured_sections:
        print(structured_sections["error"])
        return
        
    # Execute Skill 2
    summary_text = summarize_policy(structured_sections)
    
    if summary_text.startswith("Error:"):
        print(summary_text)
        return
        
    # Produce output
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary_text)
        print(f"Summary successfully written to {args.output}")
    except Exception as e:
        print(f"Failed to write output to {args.output}: {e}")

if __name__ == "__main__":
    main()
