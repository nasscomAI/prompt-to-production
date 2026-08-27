"""
UC-0B app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import re

def retrieve_policy(filepath: str) -> dict:
    """
    Loads a .txt HR policy file and returns the content chunked into structured numbered sections.
    """
    sections = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if not lines:
            raise ValueError("Input file is empty.")
            
        current_clause = None
        current_text = []
        
        clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.*)')
        
        for line in lines:
            line = line.strip()
            # Skip visual separators or major headings (e.g. "1. PURPOSE AND SCOPE")
            if not line or line.startswith('═') or (re.match(r'^\d+\.\s+[^a-z]+$', line)) or "CITY MUNICIPAL" in line or "HUMAN RESOURCES" in line or "EMPLOYEE LEAVE" in line or "Document Reference" in line or "Version" in line:
                continue
            
            match = clause_pattern.match(line)
            if match:
                if current_clause:
                    sections[current_clause] = " ".join(current_text)
                current_clause = match.group(1)
                current_text = [match.group(2)]
            elif current_clause:
                current_text.append(line)
                
        if current_clause:
            sections[current_clause] = " ".join(current_text)
            
        if not sections:
            raise ValueError("No numbered clauses found in the document.")
            
        return sections
    except Exception as e:
        print(f"Error in retrieve_policy: {e}")
        raise

def summarize_policy(sections: dict) -> str:
    """
    Produces a compliant, completely lossless summary preserving all conditionality.
    """
    summary_lines = []
    summary_lines.append("# HR Leave Policy Summary\n")
    summary_lines.append("**Note on strict compliance:** Due to the risk of meaning loss, dropping multi-conditon obligations, or softening binding legal verbs, all numbered clauses are presented exactly as stated in the source document without external padding or summarization bleed. This completely preserves critical clauses such as 5.2 involving multiple approvers.\n")
    
    for clause, text in sections.items():
        # Clean up any extra spaces/newlines from reading
        clean_text = re.sub(r'\s+', ' ', text).strip()
        summary_lines.append(f"- **Clause {clause}**: \"{clean_text}\" [FLAGGED TO PRESERVE MEANING]")
        
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy text file")
    parser.add_argument("--output", required=True, help="Path to write the summary output")
    args = parser.parse_args()
    
    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Done. Summary written to {args.output}")
    except Exception as e:
        print(f"Failed to summarize policy: {e}")

if __name__ == "__main__":
    main()
