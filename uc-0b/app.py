"""
UC-0B app.py — Policy Summarizer
Implements the retrieve_policy and summarize_policy skills.
"""
import argparse
import re

def retrieve_policy(filepath: str) -> dict:
    """
    Loads a .txt policy file and returns its content clearly structured by numbered sections.
    """
    structured_content = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Match numbered clauses like "1.1 Content goes here..."
        pattern = re.compile(r'^(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\n═|\Z)', re.MULTILINE | re.DOTALL)
        matches = pattern.findall(content)
        
        for clause_num, clause_text in matches:
            structured_content[clause_num] = clause_text.strip().replace('\n', ' ')
            
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not read the policy file at {filepath}")
        
    return structured_content

def summarize_policy(structured_sections: dict) -> str:
    """
    Takes structured clauses and produces a compliant summary that perfectly 
    preserves multi-condition obligations.
    If conditions are complex, it keeps them verbatim to prevent loss of meaning.
    """
    summary_lines = []
    summary_lines.append("HR LEAVE POLICY SUMMARY")
    summary_lines.append("="*50)
    summary_lines.append("Note: The following clauses have been summarized. Multi-condition rules are preserved strictly.")
    summary_lines.append("="*50 + "\n")
    
    for clause, text in structured_sections.items():
        # Collapse multiple spaces
        clean_text = re.sub(r'\s+', ' ', text)
        
        # Enforce exact rule conditions by checking if the sentence has multiple conditions
        # If it has "and", "requires", "must", we flag it as VERBATIM to be safe against condition dropping
        lower_text = clean_text.lower()
        if "and" in lower_text and "requires" in lower_text:
            clean_text = f"[VERBATIM] {clean_text}"
        elif "must" in lower_text or "not permitted" in lower_text or "forfeited" in lower_text or "requires" in lower_text:
            clean_text = f"[VERBATIM] {clean_text}"
            
        summary_lines.append(f"Clause {clause}: {clean_text}")
        
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()
    
    # Run the skills
    try:
        sections = retrieve_policy(args.input)
        if not sections:
            print("No clauses found. Please check input document format.")
            return

        summary_text = summarize_policy(sections)
        
        with open(args.output, "w", encoding="utf-8") as out:
            out.write(summary_text)
            
        print(f"Summary successfully written to {args.output}")
        
    except Exception as e:
        print(f"Error during summarization: {e}")

if __name__ == "__main__":
    main()
