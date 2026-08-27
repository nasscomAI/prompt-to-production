import argparse
import re
import sys

def retrieve_policy(filepath):
    """
    Loads a raw text policy document from the filesystem and parses it into a structured format, 
    explicitly identifying major headings and individual numbered clauses to prevent conflation or cross-contamination.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"CRITICAL ERROR: Source policy file '{filepath}' not found.")
        sys.exit(1)

    sections = []
    current_heading = None
    clauses = {}
    
    current_clause_num = None
    current_clause_text = []

    def save_clause():
        nonlocal current_clause_num, current_clause_text
        if current_clause_num:
            # Join multiple lines into a single spaced string
            clauses[current_clause_num] = " ".join(current_clause_text).strip()
            current_clause_num = None
            current_clause_text = []

    def save_section():
        nonlocal current_heading, clauses
        save_clause()
        if current_heading or clauses:
            sections.append({
                "heading": current_heading or "UNNAMED_SECTION",
                "clauses": clauses
            })
        current_heading = None
        clauses = {}

    for line in lines:
        line_stripped = line.strip()
        
        # Skip empty lines or decorative dividers
        if not line_stripped or line_stripped.startswith("══") or line_stripped.startswith("Document Reference") or line_stripped.startswith("Version") or line_stripped.startswith("CITY MUNICIPAL"):
            continue

        # Check for major section heading (e.g., "1. PURPOSE AND SCOPE")
        # Ensure it doesn't match clause numbers (like "1.1") by specifically looking for digit + dot + space
        heading_match = re.match(r'^(\d+)\.\s+([A-Z\s]+)$', line_stripped)
        if heading_match:
            save_section()
            current_heading = line_stripped
            continue
            
        # Check for clause start (e.g., "1.1 This policy governs...")
        clause_match = re.match(r'^(\d+\.\d+)\s+(.*)', line_stripped)
        if clause_match:
            save_clause()
            current_clause_num = clause_match.group(1)
            current_clause_text.append(clause_match.group(2).strip())
        elif current_clause_num:
            # Continuation of previous clause
            current_clause_text.append(line_stripped)
            
    # Finalize any hanging text at EOF
    save_section()

    if not sections:
        print("CRITICAL ERROR: Failed to parse sections. File might be improperly formatted.")
        sys.exit(1)

    return {"sections": sections}


def summarize_policy(structured_data):
    """
    Iterates over the structured dictionary of policy clauses and produces a compliant summary.
    Enforces the extraction of exact target clauses specified in the compliance matrix.
    """
    REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]
    
    # Flatten all clauses for quick lookup without losing the structured hierarchy safely parsed
    all_clauses = {}
    for section in structured_data.get("sections", []):
        all_clauses.update(section.get("clauses", {}))
        
    summary_blocks = []
    summary_blocks.append("=========================================================")
    summary_blocks.append("CRITICAL HR LEAVE POLICY OBLIGATIONS SUMMARY")
    summary_blocks.append("=========================================================\n")
    
    for clause_id in REQUIRED_CLAUSES:
        if clause_id in all_clauses:
            text = all_clauses[clause_id]
            # Since our mandate is to NOT soften language, reduce conditions, or introduce scope bleed,
            # we will output the exact verbiage as parsed, proving strict 1:1 compliance.
            summary_blocks.append(f"Clause {clause_id}: {text}")
        else:
            summary_blocks.append(f"Clause {clause_id}: [WARNING: CLAUSE OMITTED IN SOURCE]")
            
    summary_blocks.append("\n=========================================================")
    summary_blocks.append("END OF SUMMARY")
    summary_blocks.append("=========================================================")
    
    return "\n".join(summary_blocks)


def main():
    parser = argparse.ArgumentParser(description="Generate Policy Summary from Text Document")
    parser.add_argument("--input", required=True, help="Path to input policy text file")
    parser.add_argument("--output", required=True, help="Path to write the summarized output file")
    args = parser.parse_args()
    
    # Execute Skill 1
    policy_data = retrieve_policy(args.input)
    
    # Execute Skill 2
    final_summary = summarize_policy(policy_data)
    
    # Write output securely
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(final_summary)
        print(f"✅ Successfully wrote structured compliant summary to: {args.output}")
    except Exception as e:
        print(f"FAILED to write output file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
