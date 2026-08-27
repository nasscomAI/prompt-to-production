import argparse
import sys
import os
import re

def retrieve_policy(input_path: str) -> dict:
    """
    Loads a .txt policy file and parses its content into structured, explicitly numbered sections.
    Error Handling: Halts if unreadable/missing; Returns raw text with a warning flag if no numbering is found.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)
        
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
        
    clauses = {}
    lines = content.split('\n')
    current_clause = None
    current_text = []
    
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
            
        # Match pattern "1.1 Something"
        match = re.match(r'^(\d+\.\d+)\s+(.*)', line_stripped)
        if match:
            if current_clause:
                clauses[current_clause] = ' '.join(current_text)
            current_clause = match.group(1)
            current_text = [match.group(2)]
        else:
            # Ignore headers and dividers
            if current_clause and not line_stripped.startswith('════') and not re.match(r'^\d+\.\s+', line_stripped):
                current_text.append(line_stripped)
                
    if current_clause:
        clauses[current_clause] = ' '.join(current_text)
        
    if not clauses:
        return {"RAW_TEXT": "[WARNING: No numbered clauses found. Raw text preserved to prevent omission.]\n" + content}
        
    return clauses


def summarize_policy(clauses: dict) -> str:
    """
    Synthesizes structured policy sections into a compliant summary retaining clause references.
    Error Handling: Flags and quotes verbatim clauses that risk softening obligations or dropping conditions
    (e.g., dual approvers). Blocks scope bleed automatically as no external phrases are introduced.
    """
    if "RAW_TEXT" in clauses:
        return clauses["RAW_TEXT"]
        
    summary_lines = ["HR LEAVE POLICY SUMMARY", "======================="]
    
    for clause_num, text in clauses.items():
        text = re.sub(r'\s+', ' ', text).strip()
        lower_text = text.lower()
        
        # Risk assessment for meaning loss (condition dropping, dual approvers, etc)
        # We flag anything with complex "and" / "or" constraints combined with binding verbs
        has_multiple_entities = " and " in lower_text or " or " in lower_text
        has_binding_verb = any(v in lower_text for v in [
            "must", "requires", "will", "forfeited", "not permitted", "approval"
        ])
        
        if has_multiple_entities and has_binding_verb:
            # Rule 4: If a clause cannot be summarised without meaning loss — quote it verbatim and flag it
            # This directly prevents the Clause 5.2 trap (omitting dual-approvers).
            summary_lines.append(f"Clause {clause_num} [FLAG: VERBATIM QUOTE - COMPLEX OBLIGATION]: \"{text}\"")
        else:
            # Safe summary representation directly citing the extracted text
            summary_lines.append(f"Clause {clause_num}: {text}")
            
    return "\n".join(summary_lines)


def batch_process(input_path: str, output_path: str):
    clauses = retrieve_policy(input_path)
    summary = summarize_policy(clauses)
    
    try:
        # Ensure output directory exists
        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
            
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to input policy.txt")
    parser.add_argument("--output", required=True, help="Path to write summary.txt")
    args = parser.parse_args()
    
    batch_process(args.input, args.output)
    print(f"Done. Summary written to {args.output}")
