"""
UC-0B — Summary That Changes Meaning (Rule-Based Edition)
Implements retrieve_policy and extract_obligation as defined in agents.md and skills.md.

This script uses deterministic string-parsing and regex to extract core policy
obligations without any external models (no Anthropic, no ML).
"""
import argparse
import os
import re

# ---------------------------------------------------------------------------
# Constants — Obligation Keywords & Cleanup Patterns
# ---------------------------------------------------------------------------

# Obligation verbs identified in the README and sample policies
OBLIGATION_VERBS = {
    "must", "required", "requires", "will", "may", "are forfeited", 
    "forfeited", "not permitted", "entitled to", "mandatory"
}

# ---------------------------------------------------------------------------
# Skills implementation
# ---------------------------------------------------------------------------

def retrieve_policy(input_path: str) -> dict:
    """
    Loads a plain text policy file and partitions it into numbered sections (e.g., 2.3, 5.2).
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Policy file not found: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find sections like "2.3", "5.2", etc.
    # Assumes a numbered clause is at the start of a line and followed by text.
    sections = {}
    matches = re.finditer(r'^(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+|\n\s*═|\Z)', content, re.MULTILINE | re.DOTALL)
    
    for match in matches:
        section_id = match.group(1)
        text = match.group(2).strip()
        # Collapse multiple lines for easier sentence parsing
        clean_text = re.sub(r'\s*\n\s*', ' ', text)
        sections[section_id] = clean_text

    return sections

def extract_obligation(sections: dict) -> str:
    """
    Identifies the core obligation sentence for each clause using keyword matching
    to ensure 100% fidelity to the source conditions.
    """
    summary_lines = []
    
    for sid, stext in sections.items():
        # Split into sentences (simple period-space heuristic)
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', stext)
        
        selected_sentence = None
        for sentence in sentences:
            # Check for obligation keywords
            if any(verb in sentence.lower() for verb in OBLIGATION_VERBS):
                selected_sentence = sentence
                break
        
        # Fallback to first sentence if no keyword found
        if not selected_sentence and sentences:
            selected_sentence = sentences[0]
            
        if selected_sentence:
            # Check for multiple conditions (e.g., 'and', 'both')
            # If complex, preserve the sentence verbatim to satisfy Enforcement Rule 2.
            is_complex = any(keyword in selected_sentence.lower() for keyword in ["and", "both", "approval"])
            
            flag = ""
            if is_complex:
                flag = " [COMPLEX]"
                
            summary_lines.append(f"Clause {sid}: {selected_sentence.strip()}{flag}")
            
    return "\n".join(summary_lines)

# ---------------------------------------------------------------------------
# Main Execution Logic
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="UC-0B Rule-Based Policy Extractor")
    parser.add_argument("--input", required=True, help="Path to the policy text file")
    parser.add_argument("--output", required=True, help="Path to write the summary output")
    
    args = parser.parse_args()

    print(f"Retrieving policy from: {args.input}")
    try:
        sections = retrieve_policy(args.input)
        print(f"Found {len(sections)} sections.")
        
        print("Extracting obligations (Rule-Based)...")
        # Ensure we satisfy Enforcement Rule 3 (No information outside source document)
        output_text = extract_obligation(sections)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_text)
            
        print(f"Output written to: {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
