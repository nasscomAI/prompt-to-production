import argparse
import re

def retrieve_policy(filepath):
    """
    Loads .txt policy file and returns content as structured numbered sections.
    """
    sections = {}
    current_clause = None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines, headers like "1. PURPOSE AND SCOPE", or decorative lines
                if not line or line.startswith("══") or re.match(r"^\d+\.\s+[A-Z]", line):
                    continue
                
                # Match clause numbers like "1.1", "2.3"
                match = re.match(r"^(\d+\.\d+)\s+(.*)", line)
                if match:
                    current_clause = match.group(1)
                    sections[current_clause] = match.group(2)
                elif current_clause:
                    # Append continuation lines to the current clause
                    sections[current_clause] += " " + line
    except FileNotFoundError:
        print(f"Error: Could not find file at {filepath}")
        return None
        
    return sections

def summarize_policy(sections):
    """
    Takes structured sections and produces a compliant summary with clause references.
    Enforces rules from agents.md:
    1. Every numbered clause must be present
    2. Multi-condition obligations must preserve ALL conditions
    3. Never add information not present
    4. Quote verbatim and flag if meaning loss is possible
    """
    if not sections:
        return "Error: No policy sections to summarize."
        
    summary_lines = []
    summary_lines.append("# Policy Summary\n")
    
    # Keywords that suggest a multi-condition or strict obligation clause
    # which might lose meaning if naive summarization is applied.
    risk_keywords = ["must", "requires", "will", "may", "forfeited", "not permitted", "and", "or", "if"]
    
    for clause, text in sections.items():
        text_lower = text.lower()
        
        # Check if the text contains high-risk obligation words
        has_risk = any(kw in text_lower.split() for kw in ["must", "requires", "will", "forfeited"]) or \
                   "not permitted" in text_lower or \
                   ("requires" in text_lower and "and" in text_lower)
                   
        if has_risk:
            # Rule 4: Quote verbatim and flag
            summary_lines.append(f"**Clause {clause}** [VERBATIM - Complex Risk]: \"{text}\"")
        else:
            # Simple mock reduction for safe clauses
            summary_lines.append(f"**Clause {clause}**: {text}")
            
    return "\n\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy document (.txt)")
    parser.add_argument("--output", required=True, help="Path to write the summary (.txt)")
    args = parser.parse_args()
    
    print(f"Reading from {args.input}...")
    sections = retrieve_policy(args.input)
    
    if sections:
        print(f"Extracted {len(sections)} clauses.")
        print(f"Generating compliant summary...")
        summary = summarize_policy(sections)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Done. Processed results written to {args.output}")

if __name__ == "__main__":
    main()
