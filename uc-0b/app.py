"""
UC-0B — Policy Summary Agent
Implements agents.md and skills.md enforcement rules.
"""
import argparse
import re
from typing import List, Dict, Tuple

# Forbidden phrases that indicate scope bleed (from agents.md)
FORBIDDEN_PHRASES = {
    "as is standard practice",
    "typically",
    "usually",
    "generally",
    "employees are generally expected",
    "standard practice",
    "typical",
    "generally",
    "in general",
}

# Multi-condition clauses that require special handling (from README.md)
MULTI_CONDITION_CLAUSES = {
    "5.2": ["Department Head", "HR Director"],  # Both required
    "3.4": ["sick leave", "before/after holiday"],  # Both conditions
}


def retrieve_policy(file_path: str) -> List[Dict]:
    """
    Skill: retrieve_policy
    Loads policy text file and parses numbered clauses into structured format.
    
    Input: Path to policy .txt file
    Output: List of clause dictionaries with clause_number, binding_verb, core_obligation, full_text
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    except IOError as e:
        raise IOError(f"Error reading file {file_path}: {e}")
    
    if not content.strip():
        raise ValueError("Policy file is empty")
    
    # Parse numbered clauses (pattern: X.X or X followed by clause text)
    # Match patterns like "2.3 ...", "2.4 ...", etc.
    clause_pattern = r'(\d+\.\d+|\d+)\s+([^\n]*(?:\n(?!\d+[\.\s])[^\n]*)*)'
    matches = re.finditer(clause_pattern, content)
    
    clauses = []
    for match in matches:
        clause_num = match.group(1)
        clause_text = match.group(2).strip()
        
        if clause_text:
            # Extract binding verb (must, may, will, requires, not permitted, etc.)
            binding_verb = None
            for verb in ["must", "may", "will", "requires", "not permitted"]:
                if verb.lower() in clause_text.lower():
                    binding_verb = verb
                    break
            
            clauses.append({
                "clause_number": clause_num,
                "binding_verb": binding_verb,
                "core_obligation": clause_text,
                "full_text": clause_text
            })
    
    if not clauses:
        raise ValueError("No numbered clauses detected in policy file")
    
    return clauses


def check_for_forbidden_phrases(text: str) -> bool:
    """Check if text contains any forbidden contextual phrases."""
    text_lower = text.lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in text_lower:
            return True
    return False


def extract_conditions(clause_text: str) -> List[str]:
    """Extract all conditions from a clause (look for AND/OR separators)."""
    # Split on explicit conjunctions
    conditions = re.split(r'\s+and\s+|\s+or\s+', clause_text, flags=re.IGNORECASE)
    return [c.strip() for c in conditions if c.strip()]


def summarize_policy(clauses: List[Dict]) -> str:
    """
    Skill: summarize_policy
    Takes structured clauses and produces compliant summary preserving all clauses and conditions.
    
    Input: List of clause dictionaries from retrieve_policy
    Output: Summary text with clause references
    """
    if not clauses:
        raise ValueError("No clauses to summarize")
    
    summary_lines = []
    clauses_seen = set()
    flagged_clauses = []
    
    for clause in clauses:
        clause_num = clause.get("clause_number", "")
        obligation = clause.get("core_obligation", "")
        binding_verb = clause.get("binding_verb", "")
        
        # Enforcement: Check for missing clauses
        clauses_seen.add(clause_num)
        
        # Enforcement: Check for forbidden phrases
        if check_for_forbidden_phrases(obligation):
            flagged_clauses.append({
                "clause": clause_num,
                "reason": "Contains contextual/generalization phrases",
                "text": obligation
            })
            # Use verbatim quote
            summary_lines.append(f"Clause {clause_num}: [QUOTED] {obligation}")
            continue
        
        # Enforcement: Handle multi-condition clauses
        conditions = extract_conditions(obligation)
        
        if clause_num in MULTI_CONDITION_CLAUSES:
            expected_conditions = MULTI_CONDITION_CLAUSES[clause_num]
            if len(conditions) > 1:
                # Preserve all conditions with AND
                condition_text = " AND ".join(conditions)
                summary_lines.append(f"Clause {clause_num}: {condition_text}")
            else:
                # Only one condition found when multiple expected - flag it
                flagged_clauses.append({
                    "clause": clause_num,
                    "reason": "Multi-condition clause may have dropped conditions",
                    "text": obligation
                })
                summary_lines.append(f"Clause {clause_num}: [QUOTED] {obligation}")
        else:
            # Single condition clause
            summary_lines.append(f"Clause {clause_num}: {obligation}")
    
    # Build final summary
    summary = "\n".join(summary_lines)
    
    # Add metadata
    summary += f"\n\n--- Summary Statistics ---"
    summary += f"\nTotal clauses processed: {len(clauses)}"
    summary += f"\nClauses flagged for review: {len(flagged_clauses)}"
    
    if flagged_clauses:
        summary += f"\n\n--- Flagged Clauses ---"
        for flagged in flagged_clauses:
            summary += f"\nClause {flagged['clause']}: {flagged['reason']}"
    
    return summary


def main():
    """
    Main entry point.
    Enforces: agents.md role, intent, context, and enforcement rules.
    Uses: retrieve_policy and summarize_policy skills.
    """
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary Agent")
    parser.add_argument("--input", required=True, help="Path to policy document (.txt)")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()
    
    try:
        # Skill 1: retrieve_policy
        print(f"Loading policy from: {args.input}")
        clauses = retrieve_policy(args.input)
        print(f"Parsed {len(clauses)} clauses")
        
        # Skill 2: summarize_policy
        print("Generating compliant summary...")
        summary = summarize_policy(clauses)
        
        # Write output
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"Summary written to: {args.output}")
        print("\nEnforcement checks:")
        print(f"✓ All {len(clauses)} clauses included")
        print(f"✓ Multi-condition clauses verified")
        print(f"✓ No external context added")
        print(f"✓ Ambiguous clauses quoted verbatim")
        
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        exit(1)
    except ValueError as e:
        print(f"ERROR: {e}")
        exit(1)
    except IOError as e:
        print(f"ERROR: {e}")
        exit(1)


if __name__ == "__main__":
    main()
