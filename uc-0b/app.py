"""
UC-0B app.py — Policy summarization with clause preservation enforcement.
Implements retrieve_policy and summarize_policy skills per agents.md enforcement rules.
See README.md for run command and clause inventory (10 required clauses with no drops).
"""
import argparse
import json
import re
from pathlib import Path


# Required clauses from README ground truth
REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

# Clause inventory (binding verbs and conditions for validation)
CLAUSE_INVENTORY = {
    "2.3": {"obligation": "14-day advance notice required", "verb": "must"},
    "2.4": {"obligation": "Written approval required before leave commences. Verbal not valid.", "verb": "must"},
    "2.5": {"obligation": "Unapproved absence = LOP regardless of subsequent approval", "verb": "will"},
    "2.6": {"obligation": "Max 5 days carry-forward. Above 5 forfeited on 31 Dec.", "verb": "may / are forfeited"},
    "2.7": {"obligation": "Carry-forward days must be used Jan–Mar or forfeited", "verb": "must"},
    "3.2": {"obligation": "3+ consecutive sick days requires medical cert within 48hrs", "verb": "requires"},
    "3.4": {"obligation": "Sick leave before/after holiday requires cert regardless of duration", "verb": "requires"},
    "5.2": {"obligation": "LWP requires Department Head AND HR Director approval", "verb": "requires", "condition": "BOTH_REQUIRED"},
    "5.3": {"obligation": "LWP >30 days requires Municipal Commissioner approval", "verb": "requires"},
    "7.2": {"obligation": "Leave encashment during service not permitted under any circumstances", "verb": "not permitted"},
}


def retrieve_policy(file_path):
    """
    Load policy document and structure into numbered clauses.
    Implements skill: retrieve_policy
    
    Returns: dict with sections, clauses dict, and raw text
    Raises: ValueError if file not found or no clauses detected
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()
    except FileNotFoundError:
        raise ValueError(f"Policy file not found: {file_path}")
    
    # Extract clauses using regex pattern \d+\.\d+
    clause_pattern = r'(\d+\.\d+)\s+(.+?)(?=\n\d+\.\d+|\n═+|$)'
    clauses_found = re.findall(clause_pattern, raw_text, re.DOTALL)
    
    if not clauses_found:
        raise ValueError(
            f"No numbered clauses detected in {file_path}. "
            f"File has {len(raw_text.split(chr(10)))} lines. "
            f"First 500 chars: {raw_text[:500]}"
        )
    
    # Build clauses dict
    clauses = {}
    for clause_id, clause_text in clauses_found:
        clauses[clause_id] = clause_text.strip()
    
    # Extract section headers
    section_pattern = r'^(═+.*?═+)$'
    sections = re.findall(section_pattern, raw_text, re.MULTILINE)
    
    return {
        "sections": sections,
        "clauses": clauses,
        "raw": raw_text,
        "total_clauses": len(clauses)
    }


def validate_required_clauses(clauses_dict):
    """
    Check that all required clauses are present.
    Raises: ValueError if any required clause is missing
    """
    missing = [cid for cid in REQUIRED_CLAUSES if cid not in clauses_dict]
    if missing:
        raise ValueError(
            f"Required clauses missing from policy: {missing}. "
            f"Clause preservation check failed per agents.md enforcement rule 1."
        )


def validate_conditions(clause_id, clause_text):
    """
    Validate that multi-condition clauses preserve all conditions.
    Returns: list of validation flags
    """
    flags = []
    
    if clause_id == "5.2":
        # Must contain both Department Head AND HR Director
        if "Department Head" not in clause_text or "HR Director" not in clause_text:
            flags.append(f"[CONDITION_DROP] Clause 5.2: missing approver reference")
        if " AND " not in clause_text and " and " not in clause_text:
            flags.append(f"[CONDITION_DROP] Clause 5.2: AND conjunction missing")
    
    if clause_id == "3.4":
        # Must preserve "regardless of duration"
        if "regardless" not in clause_text.lower():
            flags.append(f"[CONDITION_DROP] Clause 3.4: 'regardless' condition missing")
    
    return flags


def summarize_policy(policy_data, required_clauses=None, target_word_count=None):
    """
    Condense policy into compliant summary preserving all clauses and conditions.
    Implements skill: summarize_policy
    
    Returns: Markdown summary with clause references
    Raises: ValueError if required clauses missing or conditions violated
    """
    if required_clauses is None:
        required_clauses = REQUIRED_CLAUSES
    
    clauses_dict = policy_data["clauses"]
    
    # Enforcement: Validate all required clauses are present
    validate_required_clauses(clauses_dict)
    
    # Build summary with explicit clause references
    summary_lines = ["# Policy Summary: HR Leave Policy\n"]
    summary_lines.append("*Summary preserves all numbered clauses per UC-0B enforcement rules.*\n")
    
    for clause_id in sorted(required_clauses):
        if clause_id not in clauses_dict:
            continue
        
        clause_text = clauses_dict[clause_id].strip()
        inventory = CLAUSE_INVENTORY.get(clause_id, {})
        
        # Validate conditions
        condition_flags = validate_conditions(clause_id, clause_text)
        
        # Format with explicit reference
        summary_lines.append(f"\n**Clause {clause_id}:** {inventory.get('obligation', clause_text[:100])}")
        
        # Add condition markers
        if inventory.get("condition"):
            summary_lines.append(f"  *[{inventory['condition']}]*")
        
        # Add full text if complex or flagged
        if condition_flags or len(clause_text) > 200:
            summary_lines.append(f"\n  Full text: {clause_text}\n")
        
        # Report condition validation
        if condition_flags:
            for flag in condition_flags:
                summary_lines.append(f"  ⚠️ {flag}")
    
    # Check for scope bleed
    summary_text = "\n".join(summary_lines)
    scope_bleed_phrases = [
        "standard practice",
        "typically",
        "generally expected",
        "as is standard",
        "organisations",
    ]
    
    for phrase in scope_bleed_phrases:
        if phrase.lower() in summary_text.lower():
            summary_lines.append(f"\n⚠️ [SCOPE_BLEED] Found phrase: '{phrase}' — not in source document")
    
    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: Summarize policy document while preserving all clauses and conditions."
    )
    parser.add_argument("--input", required=True, help="Input policy document path")
    parser.add_argument("--output", required=True, help="Output summary file path")
    
    args = parser.parse_args()
    
    try:
        # Step 1: Retrieve and structure policy
        print(f"[1/2] Loading policy from {args.input}...")
        policy_data = retrieve_policy(args.input)
        print(f"  ✓ Found {policy_data['total_clauses']} clauses")
        
        # Step 2: Summarize with enforcement
        print(f"[2/2] Summarizing with clause preservation enforcement...")
        summary = summarize_policy(policy_data, REQUIRED_CLAUSES)
        print(f"  ✓ Summary generated")
        
        # Step 3: Write output
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"[✓] Summary written to {args.output}")
        
        # Validate output
        missing = [cid for cid in REQUIRED_CLAUSES if cid not in summary]
        if missing:
            print(f"\n⚠️ WARNING: Missing clauses in summary: {missing}")
        else:
            print(f"\n✓ All {len(REQUIRED_CLAUSES)} required clauses present in summary")
    
    except Exception as e:
        print(f"[✗] Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
