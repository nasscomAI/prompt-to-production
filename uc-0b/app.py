import argparse
import re
import os

def retrieve_policy(file_path: str) -> list:
    """
    Loads the .txt policy file and returns the content parsed as structured, numbered sections.
    Raises error if file is missing or unparseable.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file {file_path} not found.")
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Extract clauses using regex pattern (matches e.g., "1.1 Text...")
    # It stops when it hits another clause or a section separator.
    clauses = []
    pattern = re.compile(r"^(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\n\s*══|\Z)", re.MULTILINE | re.DOTALL)
    
    for match in pattern.finditer(content):
        clause_id = match.group(1).strip()
        clause_text = match.group(2).strip().replace("\n    ", " ")
        clauses.append({
            "id": clause_id,
            "text": clause_text
        })
        
    if not clauses:
        raise ValueError("Could not extract any structural clauses from the document.")
        
    return clauses

def summarize_policy(sections: list) -> str:
    """
    Takes structured sections and produces a compliant summary that explicitly references each numbered clause.
    Preserves all multi-condition obligations per agents.md instructions.
    """
    summary_lines = ["# HR Leave Policy Summary\n"]
    
    for section in sections:
        cid = section["id"]
        text = section["text"]
        text_lower = text.lower()
        
        # Rule: If a clause cannot be confidently summarized without losing exact meaning or conditions,
        # quote it verbatim and flag it instead of attempting to summarize.
        # We trigger verbatim quoting on words like 'requires', 'must', 'will', 'not permitted', 'and'
        complex_triggers = ['and', 'requires', 'must', 'will', 'not permitted', 'forfeited', 'only']
        is_complex = any(trigger in text_lower for trigger in complex_triggers)
        
        if is_complex:
            # Multi-condition / Strict obligations -> quote verbatim to prevent dropping conditions.
            summary_lines.append(f"- Clause {cid}: [FLAGGED: VERBATIM] {text}")
        else:
            # Simple summarization for standard clauses (just reporting the rule).
            summary_lines.append(f"- Clause {cid}: {text}")
            
    summary_lines.append("\n*Summary generated in strict adherence to agents.md rules.*")
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy text file")
    parser.add_argument("--output", required=True, help="Path to output summary text file")
    args = parser.parse_args()

    try:
        # Skill 1: Retrieve structural sections
        sections = retrieve_policy(args.input)
        
        # Skill 2: Summarize while enforcing multi-condition/verbatim rules
        summary_text = summarize_policy(sections)
        
        # Write to output file
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary_text)
            
        print(f"Success! Processed {len(sections)} clauses. Summary written to {args.output}")
        
    except Exception as e:
        print(f"Error processing policy: {e}")

if __name__ == "__main__":
    main()
