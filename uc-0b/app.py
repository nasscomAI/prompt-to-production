"""
UC-0B app.py — Policy Summarizer
Enforces clause completeness, binding verb preservation, and multi-condition retention.
Implements skills: extract_numbered_clauses, preserve_multi_condition_obligations, 
check_binding_verb_strength, verify_no_clause_omission, generate_summary_output
"""
import argparse
import re
from typing import Dict, List, Tuple, Set

# Define all required clauses from policy_hr_leave.txt
REQUIRED_CLAUSES = {
    "2.3", "2.4", "2.5", "2.6", "2.7",  # Annual Leave
    "3.2", "3.4",                        # Sick Leave  
    "5.2", "5.3",                        # LWP
    "7.2"                                # Leave Encashment
}

# Binding verbs that must not be softened
BINDING_VERBS = {"must", "will", "requires", "not permitted", "may", "are forfeited"}

# Multi-condition clauses that require ALL conditions preserved
MULTI_CONDITION_CLAUSES = {
    "5.2": ["Department Head", "HR Director"],  # Both approvers required
}

def extract_numbered_clauses(policy_text: str) -> Dict[str, Dict]:
    """
    Parse policy document and extract all numbered clause sections.
    Returns: Dict mapping clause_id → {section, binding_verb, text, line_range}
    """
    clauses = {}
    lines = policy_text.split('\n')
    
    # Regex to match numbered clauses (e.g., "2.3", "5.2")
    clause_pattern = r'^(\d+\.\d+)\s+(.+)$'
    
    for i, line in enumerate(lines):
        match = re.match(clause_pattern, line.strip())
        if match:
            clause_id = match.group(1)
            clause_text = match.group(2)
            
            # Collect full clause text (may span multiple lines)
            full_text = clause_text
            j = i + 1
            while j < len(lines) and not re.match(clause_pattern, lines[j].strip()):
                next_line = lines[j].strip()
                if next_line and not next_line.startswith('═'):
                    full_text += " " + next_line
                j += 1
            
            # Extract binding verb
            binding_verb = extract_binding_verb(full_text)
            
            clauses[clause_id] = {
                "section": clause_id.split('.')[0],
                "binding_verb": binding_verb,
                "text": full_text.strip(),
                "line_range": (i + 1, j)
            }
    
    return clauses


def extract_binding_verb(clause_text: str) -> str:
    """
    Identify the binding verb in clause text.
    """
    clause_lower = clause_text.lower()
    
    if "must" in clause_lower:
        return "must"
    elif "requires" in clause_lower or "require" in clause_lower:
        return "requires"
    elif "not permitted" in clause_lower:
        return "not permitted"
    elif "will" in clause_lower:
        return "will"
    elif "are forfeited" in clause_lower:
        return "are forfeited"
    elif "may" in clause_lower:
        return "may"
    else:
        return "unspecified"


def preserve_multi_condition_obligations(clauses: Dict[str, Dict]) -> List[Tuple[str, bool, str]]:
    """
    Detect and verify multi-condition clauses.
    Returns: List of (clause_id, all_conditions_present, message)
    """
    results = []
    
    for clause_id, required_conditions in MULTI_CONDITION_CLAUSES.items():
        if clause_id in clauses:
            clause_text = clauses[clause_id]["text"].lower()
            all_present = all(cond.lower() in clause_text for cond in required_conditions)
            
            if all_present:
                results.append((clause_id, True, f"✓ All {len(required_conditions)} conditions preserved"))
            else:
                missing = [c for c in required_conditions if c.lower() not in clause_text]
                results.append((clause_id, False, f"✗ MISSING CONDITIONS: {missing}"))
    
    return results


def check_binding_verb_strength(clause_id: str, clause_data: Dict) -> Tuple[bool, str]:
    """
    Verify binding verb is preserved (not softened).
    """
    verb = clause_data["binding_verb"]
    
    if verb in BINDING_VERBS:
        return True, f"✓ Binding verb '{verb}' preserved"
    else:
        return False, f"✗ Unrecognized binding verb: {verb}"


def verify_no_clause_omission(extracted_clauses: Dict[str, Dict]) -> Tuple[bool, Set[str], int]:
    """
    Confirm all required clauses present.
    Returns: (all_present, missing_clauses, count_present)
    """
    found_clauses = set(extracted_clauses.keys())
    missing = REQUIRED_CLAUSES - found_clauses
    
    return len(missing) == 0, missing, len(found_clauses & REQUIRED_CLAUSES)


def generate_summary_output(clauses: Dict[str, Dict], validation_results: Dict) -> str:
    """
    Format verified clauses into readable summary text.
    """
    output = []
    output.append("=" * 70)
    output.append("CITY MUNICIPAL CORPORATION — HR LEAVE POLICY SUMMARY")
    output.append("Extracted Clauses with Binding Obligations")
    output.append("=" * 70)
    output.append("")
    
    # Report any validation issues
    if validation_results.get("missing_clauses"):
        output.append("[VALIDATION ERROR] Missing clauses:")
        for clause_id in sorted(validation_results["missing_clauses"]):
            output.append(f"  - {clause_id}")
        output.append("")
    
    # Report multi-condition checks
    if validation_results.get("multi_condition_results"):
        output.append("MULTI-CONDITION VERIFICATION:")
        for clause_id, all_present, message in validation_results["multi_condition_results"]:
            output.append(f"  Clause {clause_id}: {message}")
        output.append("")
    
    # Output all extracted clauses
    output.append("EXTRACTED CLAUSES:")
    output.append("-" * 70)
    
    for clause_id in sorted(clauses.keys(), key=lambda x: tuple(map(int, x.split('.')))):
        clause_data = clauses[clause_id]
        verb = clause_data["binding_verb"]
        text = clause_data["text"]
        
        output.append(f"\n[{clause_id}] (Binding: {verb})")
        output.append(f"    {text}")
    
    output.append("\n" + "=" * 70)
    output.append(f"SUMMARY: {len(clauses)} clauses extracted and preserved")
    output.append("=" * 70)
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy document")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()
    
    # Read input policy
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            policy_text = f.read()
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {args.input}")
        return
    except Exception as e:
        print(f"ERROR reading input file: {e}")
        return
    
    # Extract all numbered clauses
    clauses = extract_numbered_clauses(policy_text)
    
    # Validate completeness
    all_present, missing, count_found = verify_no_clause_omission(clauses)
    
    # Check multi-condition obligations
    multi_condition_results = preserve_multi_condition_obligations(clauses)
    
    # Validate binding verbs
    binding_verb_results = []
    for clause_id, clause_data in clauses.items():
        is_valid, message = check_binding_verb_strength(clause_id, clause_data)
        binding_verb_results.append((clause_id, is_valid, message))
    
    # Prepare validation results
    validation_results = {
        "all_clauses_present": all_present,
        "missing_clauses": missing,
        "clauses_found": count_found,
        "required_clauses_count": len(REQUIRED_CLAUSES),
        "multi_condition_results": multi_condition_results,
        "binding_verb_results": binding_verb_results
    }
    
    # Generate summary
    summary = generate_summary_output(clauses, validation_results)
    
    # Write output
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"✓ Summary written to {args.output}")
        print(f"✓ Clauses extracted: {count_found}/{len(REQUIRED_CLAUSES)} required")
        
        if missing:
            print(f"✗ MISSING CLAUSES: {missing}")
        else:
            print("✓ All required clauses present")
            
        for clause_id, all_present, message in multi_condition_results:
            print(f"  {message}")
    
    except Exception as e:
        print(f"ERROR writing output file: {e}")


if __name__ == "__main__":
    main()
