"""
UC-0B app.py
"""
import argparse
import re

def retrieve_policy(file_path: str) -> dict:
    """loads .txt policy file, returns content as structured numbered sections"""
    sections = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex to capture numbered clauses
    clause_pattern = re.compile(r'^(\d+\.\d+)\s+(.*?)(?=^\d+\.\d+|\n═|\Z)', re.MULTILINE | re.DOTALL)
    
    matches = clause_pattern.findall(content)
    for num, text in matches:
        sections[num] = text.strip().replace('\n', ' ')
        sections[num] = re.sub(r'\s+', ' ', sections[num])
        
    return sections

def summarize_policy(sections: dict) -> str:
    """takes structured sections, produces compliant summary with clause references"""
    critical_clauses = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    
    summary_lines = [
        "HR Leave Policy Summary",
        "=======================",
        "This summary contains the exact obligations extracted directly from the source policy document to ensure zero policy drift.",
        ""
    ]
    
    for clause in critical_clauses:
        if clause in sections:
            summary_lines.append(f"Clause {clause}: {sections[clause]}")
        else:
            summary_lines.append(f"Clause {clause}: [MISSING FROM SOURCE]")
            
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy document (.txt)")
    parser.add_argument("--output", required=True, help="Path to write the summary")
    args = parser.parse_args()
    
    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Successfully processed {args.input} and generated summary at {args.output}")
    except Exception as e:
        print(f"Error processing policy: {e}")

if __name__ == "__main__":
    main()
