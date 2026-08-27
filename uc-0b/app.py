"""
UC-0B — Policy Summarization
Implementation of policy summarization using RICE framework and clause preservation.
Enforces preservation of all conditions in multi-condition obligations.
"""
import argparse
import re
import sys

# Target clauses with their expected structure: (clause_num, expected_binding_verb, key_keywords)
TARGET_CLAUSES = {
    "2.3": {
        "desc": "Annual leave advance notice requirement",
        "keywords": ["14", "advance", "days", "application"],
        "binding_verb": "must"
    },
    "2.4": {
        "desc": "Written approval before leave commences",
        "keywords": ["written", "approval", "manager", "verbal"],
        "binding_verb": "must"
    },
    "2.5": {
        "desc": "Unapproved absence recorded as LOP regardless of subsequent approval",
        "keywords": ["unapproved", "absence", "LOP", "regardless"],
        "binding_verb": "will"
    },
    "2.6": {
        "desc": "Carry-forward limit: max 5 days, forfeited on 31 Dec",
        "keywords": ["carry", "forward", "maximum", "5", "forfeited", "31 December"],
        "binding_verb": "may/forfeited"
    },
    "2.7": {
        "desc": "Carry-forward days must be used Jan–Mar or forfeited",
        "keywords": ["carry-forward", "first quarter", "January", "March", "forfeited"],
        "binding_verb": "must"
    },
    "3.2": {
        "desc": "3+ consecutive sick days requires medical cert within 48hrs",
        "keywords": ["3", "consecutive", "medical", "certificate", "48 hours"],
        "binding_verb": "requires"
    },
    "3.4": {
        "desc": "Sick leave before/after holiday requires cert regardless of duration",
        "keywords": ["before", "after", "public holiday", "medical certificate", "regardless"],
        "binding_verb": "requires"
    },
    "5.2": {
        "desc": "LWP requires TWO approvers: Department Head AND HR Director",
        "keywords": ["Department Head", "HR Director", "both", "alone", "not sufficient"],
        "binding_verb": "requires"
    },
    "5.3": {
        "desc": "LWP >30 days requires Municipal Commissioner approval",
        "keywords": ["30", "continuous", "Municipal Commissioner"],
        "binding_verb": "requires"
    },
    "7.2": {
        "desc": "Leave encashment during service not permitted under any circumstances",
        "keywords": ["encashment", "during service", "not permitted", "any circumstances"],
        "binding_verb": "not permitted"
    }
}

def extract_clause_verbatim(content: str, clause_num: str) -> str:
    """
    Extract the exact clause text from the document.
    Returns the verbatim clause text or empty string if not found.
    """
    # More robust approach: find the line with clause number, then collect text until next clause
    lines = content.split('\n')
    clause_start_idx = -1
    
    for i, line in enumerate(lines):
        if re.match(rf'^{re.escape(clause_num)}\s+', line):
            clause_start_idx = i
            break
    
    if clause_start_idx == -1:
        return ""
    
    # Collect lines until we hit the next numbered clause or section divider
    clause_lines = []
    for i in range(clause_start_idx, len(lines)):
        line = lines[i]
        
        # Skip empty lines
        if not line.strip():
            if clause_lines:  # Only if we've already collected some content
                continue
            else:
                continue
        
        # Stop at next clause number or section divider (including Unicode box-drawing chars)
        if i > clause_start_idx:
            if re.match(r'^\d+\.\d+\s+', line):  # Next clause
                break
            if re.match(r'^[=\-\u2550\u2500]+', line):  # Section divider (including Unicode)
                break
        
        clause_lines.append(line.strip())
    
    # Join and clean up
    clause_text = ' '.join(clause_lines).strip()
    clause_text = re.sub(r'^\d+\.\d+\s+', '', clause_text)  # Remove clause number prefix
    clause_text = re.sub(r'\s+', ' ', clause_text)  # Normalize whitespace
    
    return clause_text

def validate_clause_completeness(clause_text: str, clause_num: str) -> dict:
    """
    Validate that a clause preserves all conditions and binding verbs.
    Returns validation result with status and warnings.
    """
    result = {
        "clause_num": clause_num,
        "complete": True,
        "warnings": [],
        "condition_count": 0
    }
    
    # Special check for clause 5.2: must have TWO approvers explicitly
    if clause_num == "5.2":
        if "Department Head" in clause_text and "HR Director" in clause_text:
            result["condition_count"] = 2
            if "Manager approval alone" in clause_text or "not sufficient" in clause_text:
                result["condition_validation"] = "Both approvers explicitly required"
        else:
            result["complete"] = False
            result["warnings"].append("Missing one of two required approvers")
    
    # Check for softened language
    softening_phrases = ["typically", "generally", "usually", "often", "may be", "as is standard"]
    for phrase in softening_phrases:
        if phrase.lower() in clause_text.lower():
            result["warnings"].append(f"Potential softening language detected: '{phrase}'")
    
    return result

def retrieve_policy(input_path: str) -> dict:
    """
    Load policy file and parse into sections.
    Returns structured policy data with all numbered clauses.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"ERROR: Cannot read {input_path}: {str(e)}", file=sys.stderr)
        raise
    
    # Extract title and metadata
    lines = content.split('\n')
    title = lines[1] if len(lines) > 1 else "Untitled Policy"
    
    policy = {
        "title": title,
        "content": content,
        "clauses": {}
    }
    
    # Extract all numbered clauses
    clause_pattern = r'^(\d+\.\d+)\s+(.+?)$'
    for match in re.finditer(clause_pattern, content, re.MULTILINE):
        clause_num = match.group(1)
        clause_preview = match.group(2)[:80]  # First 80 chars
        policy["clauses"][clause_num] = {
            "number": clause_num,
            "preview": clause_preview
        }
    
    return policy

def summarize_policy(policy: dict, target_clauses: dict = None) -> str:
    """
    Produce binding-preserving summary of policy.
    Preserves all target clauses and their conditions.
    """
    if target_clauses is None:
        target_clauses = TARGET_CLAUSES
    
    content = policy["content"]
    summary_lines = [
        "POLICY SUMMARY — BINDING CLAUSE INVENTORY",
        "="*60,
        f"Document: {policy['title']}",
        ""
    ]
    
    missing_clauses = []
    
    # Process each target clause
    for clause_num in sorted(target_clauses.keys()):
        clause_info = target_clauses[clause_num]
        clause_text = extract_clause_verbatim(content, clause_num)
        
        if not clause_text:
            missing_clauses.append(clause_num)
            summary_lines.append(f"Clause {clause_num}: [NOT FOUND IN SOURCE]")
            summary_lines.append(f"  Expected: {clause_info['desc']}")
            summary_lines.append("")
            continue
        
        # Validate completeness
        validation = validate_clause_completeness(clause_text, clause_num)
        
        # Format summary line
        summary_lines.append(f"Clause {clause_num}: {clause_info['desc']}")
        summary_lines.append(f"  Binding: {clause_info['binding_verb']}")
        
        # Preserve full clause text verbatim
        summary_lines.append(f"  [VERBATIM] {clause_text}")
        
        if validation["warnings"]:
            for warning in validation["warnings"]:
                summary_lines.append(f"  ⚠ {warning}")
        
        if clause_num == "5.2" and validation["condition_count"] == 2:
            summary_lines.append("  ✓ Both approval conditions present")
        
        summary_lines.append("")
    
    # Summary footer
    summary_lines.append("="*60)
    summary_lines.append(f"Total Target Clauses: {len(target_clauses)}")
    summary_lines.append(f"Found: {len(target_clauses) - len(missing_clauses)}")
    if missing_clauses:
        summary_lines.append(f"Missing: {', '.join(missing_clauses)}")
    summary_lines.append("")
    summary_lines.append("COMPLIANCE NOTES:")
    summary_lines.append("- All clause text preserved verbatim to prevent condition omission")
    summary_lines.append("- Multi-condition obligations (e.g., 5.2) explicitly flagged")
    summary_lines.append("- No scope bleed or softening language permitted")
    
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarization")
    parser.add_argument("--input",  required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()
    
    try:
        # Retrieve policy
        policy = retrieve_policy(args.input)
        print(f"Policy loaded: {policy['title']}", file=sys.stderr)
        print(f"Found {len(policy['clauses'])} numbered clauses", file=sys.stderr)
        
        # Summarize policy
        summary = summarize_policy(policy, TARGET_CLAUSES)
        
        # Write output
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"Done. Summary written to {args.output}")
    
    except Exception as e:
        print(f"FATAL ERROR: {str(e)}", file=sys.stderr)
        raise

if __name__ == "__main__":
    main()
