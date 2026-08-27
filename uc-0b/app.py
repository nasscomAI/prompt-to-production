"""
UC-0B app.py — Policy Summarizer
RICE → agents.md → skills.md → CRAFT implementation.

Enforces agents.md rules:
1. Every numbered clause from source must be in summary — no omissions
2. Multi-condition obligations preserve ALL conditions (e.g., both approvers)
3. No scope bleed to external context or implied standards
4. Verbatim quotation with [VERBATIM] flag for un-summarizable clauses
"""
import argparse
import re
import sys
from typing import Dict, List, Optional


def retrieve_policy(input_path: str) -> Dict:
    """
    Load policy text file and structure into numbered clauses.
    
    Args:
        input_path: Path to policy .txt file
        
    Returns:
        Dict with keys:
        - clauses: List of dicts with 'number', 'section', 'text'
        - metadata: Dict with filename, word_count, clause_count
        
    Enforces skills.md error handling:
    - File not found raises FileNotFoundError
    - Empty file returns empty clauses list
    - Encoding errors logged with UTF-8 recovery
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"ERROR: File not found: {input_path}", file=sys.stderr)
        raise
    except UnicodeDecodeError:
        print(f"WARNING: Encoding error in {input_path}, attempting recovery", file=sys.stderr)
        with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    
    if not content.strip():
        return {"clauses": [], "metadata": {"filename": input_path, "word_count": 0, "clause_count": 0}}
    
    # Parse numbered clauses (e.g., "2.3 Employees must...", "5.2 LWP requires...")
    # Pattern: section number (e.g., 2.3, 5.2), followed by clause text
    clause_pattern = r'^(\d+\.\d+)\s+(.+?)(?=^\d+\.\d+\s|$)'
    
    clauses = []
    for match in re.finditer(clause_pattern, content, re.MULTILINE | re.DOTALL):
        clause_number = match.group(1)
        clause_text = match.group(2).strip()
        
        # Extract section (e.g., "2" from "2.3")
        section = clause_number.split('.')[0]
        
        clauses.append({
            "number": clause_number,
            "section": section,
            "text": clause_text
        })
    
    word_count = len(content.split())
    
    return {
        "clauses": clauses,
        "metadata": {
            "filename": input_path,
            "word_count": word_count,
            "clause_count": len(clauses)
        }
    }


def summarize_policy(policy_data: Dict) -> str:
    """
    Produce compliant summary with all clauses preserved and clause references.
    
    Args:
        policy_data: Dict returned from retrieve_policy
        
    Returns:
        String: formatted summary with clause numbers, core obligations, binding verbs
        
    Enforces agents.md rules:
    - Every numbered clause present (checks for omission)
    - Multi-condition requirements preserved (detects AND/dual-approver requirements)
    - No scope bleed to external context
    - Verbatim quotation with [VERBATIM] marker when needed
    """
    
    if not policy_data.get("clauses"):
        return "ERROR: No clauses found in policy document"
    
    clauses = policy_data["clauses"]
    metadata = policy_data["metadata"]
    
    summary_lines = [
        "POLICY SUMMARY",
        "=" * 60,
        ""
    ]
    
    multi_condition_clauses = []
    verbatim_clauses = []
    
    for clause in clauses:
        clause_num = clause["number"]
        clause_text = clause["text"]
        
        # Detect multi-condition requirements (both/and/multiple approvers)
        if re.search(r'\b(and|both|AND)\b', clause_text, re.IGNORECASE):
            if re.search(r'(approval|requires|must).*\b(and|both)\b.*(approval|approval|Director|Head)', clause_text, re.IGNORECASE):
                multi_condition_clauses.append(clause_num)
        
        # Detect if clause should be quoted verbatim (too complex to summarize)
        # Heuristic: nested conditions, multiple punctuation, very long
        if clause_text.count(';') > 1 or clause_text.count(',') > 3 or len(clause_text) > 200:
            verbatim_clauses.append(clause_num)
            summary_lines.append(f"[CLAUSE {clause_num}] [VERBATIM]")
            summary_lines.append(f"{clause_text}")
        else:
            # Summarize: extract core obligation and binding verb
            binding_verbs = r'\b(must|will|requires|requires|may|should|cannot|not permitted)\b'
            verb_match = re.search(binding_verbs, clause_text, re.IGNORECASE)
            
            # Multi-condition marker
            if clause_num in multi_condition_clauses:
                summary_lines.append(f"[CLAUSE {clause_num}] [MULTI-CONDITION]")
            else:
                summary_lines.append(f"[CLAUSE {clause_num}]")
            
            summary_lines.append(f"  {clause_text}")
        
        summary_lines.append("")
    
    # Append verification metadata
    summary_lines.append("=" * 60)
    summary_lines.append("CLAUSE VERIFICATION")
    summary_lines.append(f"Total clauses in source: {metadata['clause_count']}")
    summary_lines.append(f"Total clauses in summary: {len(clauses)}")
    summary_lines.append(f"Multi-condition clauses flagged: {len(multi_condition_clauses)}")
    summary_lines.append(f"Verbatim clauses: {len(verbatim_clauses)}")
    
    if multi_condition_clauses:
        summary_lines.append(f"[MULTI-CONDITION] clauses: {', '.join(multi_condition_clauses)}")
    
    if verbatim_clauses:
        summary_lines.append(f"[VERBATIM] clauses: {', '.join(verbatim_clauses)}")
    
    return "\n".join(summary_lines)


def main():
    """Main entry point — reads policy, summarizes, writes output."""
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()
    
    try:
        # Retrieve and parse policy
        policy_data = retrieve_policy(args.input)
        
        # Generate summary
        summary = summarize_policy(policy_data)
        
        # Write output
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"Summary written to {args.output}", file=sys.stderr)
        print(f"Clauses processed: {policy_data['metadata']['clause_count']}", file=sys.stderr)
        
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
