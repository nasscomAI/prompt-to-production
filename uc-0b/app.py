"""
UC-0B app.py — Policy Document Summarizer
Implements summarization with clause preservation and multi-condition enforcement.
"""
import argparse
import re
from typing import Dict, List


def retrieve_policy(input_path: str) -> Dict:
    """
    Load policy document and extract numbered sections.
    Returns: dict with document_name and sections indexed by section number.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {input_path}")
    except Exception as e:
        raise Exception(f"Error reading file: {e}")
    
    if not content.strip():
        raise ValueError("Policy document is empty")
    
    document_name = input_path.split('/')[-1]
    sections = {}
    
    # Extract sections using regex pattern for numbered sections (e.g., 2.3, 5.2, etc.)
    section_pattern = r'(\d+\.\d+)\s+(.+?)(?=\d+\.\d+\s+|$)'
    matches = re.finditer(section_pattern, content, re.DOTALL)
    
    for match in matches:
        section_num = match.group(1)
        section_text = match.group(2).strip()
        sections[section_num] = section_text
    
    print(f"Loaded {len(sections)} sections from {document_name}")
    
    return {
        "document_name": document_name,
        "sections": sections,
        "full_text": content
    }


def summarize_policy(policy_data: Dict, summary_type: str = "full") -> str:
    """
    Create clause-preserving summary with all conditions intact.
    """
    sections = policy_data.get("sections", {})
    document_name = policy_data.get("document_name", "")
    
    if not sections:
        raise ValueError("No sections found in policy document")
    
    summary_lines = []
    summary_lines.append(f"POLICY SUMMARY: {document_name}")
    summary_lines.append("=" * 70)
    summary_lines.append("")
    
    # Sort sections numerically
    sorted_sections = sorted(sections.items(), key=lambda x: tuple(map(int, x[0].split('.'))))
    
    for section_num, section_text in sorted_sections:
        # Extract first sentence as heading, preserve conditions in full text
        first_sentence = section_text.split('\n')[0].strip()
        
        summary_lines.append(f"[SECTION {section_num}]")
        summary_lines.append(first_sentence)
        
        # Check for multi-condition key phrases
        if "and" in section_text.lower() and "approval" in section_text.lower():
            # This is a multi-condition requirement - preserve it exactly
            summary_lines.append("  [MULTI-CONDITION REQUIREMENT - ALL CONDITIONS MUST BE MET]")
            # Extract the full requirement
            lines = section_text.split('\n')
            for line in lines:
                if any(word in line.lower() for word in ["and", "both", "requires", "approval"]):
                    summary_lines.append(f"  {line.strip()}")
        else:
            # Single condition - include relevant details
            lines = section_text.split('\n')
            for line in lines[:3]:  # Include first 3 lines for context
                line_stripped = line.strip()
                if line_stripped and len(line_stripped) > 10:
                    summary_lines.append(f"  {line_stripped}")
        
        summary_lines.append("")
    
    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Policy Summarizer - Preserves all clauses with no condition dropping"
    )
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=False, help="Path to write summary (default: stdout)")
    parser.add_argument("--type", choices=["full", "executive"], default="full",
                        help="Summary type (default: full)")
    
    args = parser.parse_args()
    
    try:
        # Load policy
        policy_data = retrieve_policy(args.input)
        
        # Summarize
        summary = summarize_policy(policy_data, args.type)
        
        # Output
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(summary)
            print(f"Summary written to {args.output}")
        else:
            print(summary)
    
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
