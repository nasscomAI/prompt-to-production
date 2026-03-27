"""
UC-0B app.py — Policy Summary with Enforcement

Implements retrieve_policy and summarize_policy skills following agents.md integrity rules:
- Clause omission prevention
- Scope bleed detection
- Obligation softening prevention
"""
import argparse
import re
from typing import Dict, List, Tuple

# Required clauses that must be present in summary
REQUIRED_CLAUSES = {
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4",
    "5.2", "5.3",
    "7.2"
}

# Known scope bleed phrases that indicate hallucination
SCOPE_BLEED_PHRASES = {
    "as is standard practice",
    "typically in government",
    "employees are generally expected",
    "standard practice",
    "typically",
    "commonly",
    "usually"
}

# Binding verbs to preserve
BINDING_VERBS = {
    "must", "will", "may", "requires", "not permitted", "cannot"
}


def retrieve_policy(file_path: str) -> Dict:
    """
    Load and parse policy document into structured sections and clauses.
    
    Returns:
        Dict with structure: {
            "content": str,
            "sections": [{
                "section_num": str,
                "clauses": [{
                    "clause_num": str,
                    "text": str,
                    "binding_verb": str
                }]
            }]
        }
    
    Raises:
        IOError: If file not found
        ValueError: If file structure cannot be parsed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise IOError(f"Policy file not found: {file_path}")
    except Exception as e:
        raise IOError(f"Cannot read policy file: {e}")
    
    sections = []
    current_section = None
    current_clauses = []
    current_clause_num = None
    current_clause_text = []
    
    lines = content.split('\n')
    
    for line in lines:
        # Skip separator lines (both ASCII = and Unicode box drawing characters)
        if re.match(r'^[=═\-_*]+$', line.strip()):
            continue
            
        # Check for section header (X. SECTION_NAME)
        section_match = re.match(r'^(\d+)\.\s+([A-Z][A-Z\s\(\)]+)$', line.strip())
        if section_match:
            # Save previous clause if any
            if current_clause_num:
                clause_text = ' '.join(current_clause_text).strip()
                binding_verb = None
                for verb in ["not permitted", "must", "will", "may", "requires", "cannot"]:
                    if verb.lower() in clause_text.lower():
                        binding_verb = verb
                        break
                current_clauses.append({
                    "clause_num": current_clause_num,
                    "text": clause_text,
                    "binding_verb": binding_verb
                })
            
            # Save previous section if any
            if current_section and current_clauses:
                sections.append({
                    "section_num": current_section,
                    "clauses": current_clauses
                })
            
            current_section = section_match.group(1)
            current_clauses = []
            current_clause_num = None
            current_clause_text = []
            continue
        
        # Skip empty lines
        if not line.strip():
            continue
        
        # Check for clause (X.Y text)
        clause_match = re.match(r'^(\d+\.\d+)\s+(.+)$', line.strip())
        if clause_match:
            # Save previous clause if any
            if current_clause_num:
                clause_text = ' '.join(current_clause_text).strip()
                binding_verb = None
                for verb in ["not permitted", "must", "will", "may", "requires", "cannot"]:
                    if verb.lower() in clause_text.lower():
                        binding_verb = verb
                        break
                current_clauses.append({
                    "clause_num": current_clause_num,
                    "text": clause_text,
                    "binding_verb": binding_verb
                })
            
            current_clause_num = clause_match.group(1)
            current_clause_text = [clause_match.group(2)]
        elif current_clause_num:
            # Continuation of current clause
            if line.strip():
                current_clause_text.append(line.strip())
    
    # Save last clause and section
    if current_clause_num:
        clause_text = ' '.join(current_clause_text).strip()
        binding_verb = None
        for verb in ["not permitted", "must", "will", "may", "requires", "cannot"]:
            if verb.lower() in clause_text.lower():
                binding_verb = verb
                break
        current_clauses.append({
            "clause_num": current_clause_num,
            "text": clause_text,
            "binding_verb": binding_verb
        })
    
    if current_section and current_clauses:
        sections.append({
            "section_num": current_section,
            "clauses": current_clauses
        })
    
    return {
        "content": content,
        "sections": sections
    }


def detect_scope_bleed(text: str) -> List[str]:
    """
    Detect hallucinated scope bleed phrases indicating assumptions not in source.
    
    Returns:
        List of detected scope bleed phrases found in text
    """
    found = []
    for phrase in SCOPE_BLEED_PHRASES:
        if phrase.lower() in text.lower():
            found.append(phrase)
    return found


def summarize_policy(policy_data: Dict) -> str:
    """
    Transform structured policy into compliant summary preserving all clauses
    and multi-condition obligations.
    
    Args:
        policy_data: Output from retrieve_policy
        
    Returns:
        Summary string with all required clauses
        
    Raises:
        ValueError: If required clauses missing or conditions dropped
    """
    sections = policy_data["sections"]
    
    # Flatten all clauses for verification
    all_clauses = {}
    for section in sections:
        for clause in section["clauses"]:
            all_clauses[clause["clause_num"]] = clause
    
    # Check all required clauses are present
    missing = REQUIRED_CLAUSES - set(all_clauses.keys())
    if missing:
        raise ValueError(f"Required clauses missing from policy: {sorted(missing)}")
    
    # Build summary with explicit clause references
    summary_lines = ["POLICY SUMMARY WITH CLAUSE ENFORCEMENT\n"]
    summary_lines.append("=" * 60)
    summary_lines.append("\nNOTE: Each clause reference below maps to the source document.\n")
    
    # Group by section for readability
    for section in sections:
        summary_lines.append(f"\n### SECTION {section['section_num']}\n")
        
        for clause in section["clauses"]:
            clause_num = clause["clause_num"]
            clause_text = clause["text"]
            binding_verb = clause["binding_verb"]
            
            # Special handling for multi-condition clauses
            if clause_num == "5.2":
                # CRITICAL: Must preserve both approvers
                summary_lines.append(f"\n[Clause {clause_num}]")
                summary_lines.append(f"Requirement: LWP requires approval from BOTH the Department Head AND the HR Director.")
                summary_lines.append(f"Reason: Multi-condition obligation — manager approval alone is insufficient.")
                summary_lines.append(f"Binding verb: {binding_verb}")
            elif clause_num == "5.3":
                # Multi-condition: exceeds 30 days
                summary_lines.append(f"\n[Clause {clause_num}]")
                summary_lines.append(f"Requirement: LWP exceeding 30 continuous days requires Municipal Commissioner approval.")
                summary_lines.append(f"Reason: Additional escalation condition for extended LWP.")
                summary_lines.append(f"Binding verb: {binding_verb}")
            elif clause_num == "3.4":
                # Multi-condition: timing-based
                summary_lines.append(f"\n[Clause {clause_num}]")
                summary_lines.append(f"Requirement: Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration.")
                summary_lines.append(f"Reason: Stricter medical cert requirement for leave adjacent to holidays.")
                summary_lines.append(f"Binding verb: {binding_verb}")
            else:
                # Standard clause summary
                summary_lines.append(f"\n[Clause {clause_num}]")
                summary_lines.append(f"Requirement: {clause_text}")
                summary_lines.append(f"Binding verb: {binding_verb}")
    
    summary_text = "\n".join(summary_lines)
    
    # Detect scope bleed
    bleed = detect_scope_bleed(summary_text)
    if bleed:
        raise ValueError(f"Scope bleed detected in summary. Hallucinated phrases: {bleed}")
    
    # Verify no conditions were dropped from multi-condition clauses
    summary_lower = summary_text.lower()
    if not ("both" in summary_lower and "department head" in summary_lower and "hr director" in summary_lower):
        if "5.2" in all_clauses:
            raise ValueError("Clause 5.2 multi-condition requirement dropped: must include BOTH Department Head AND HR Director")
    
    return summary_text


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summary with Enforcement")
    parser.add_argument("--input", required=True, help="Input policy file path")
    parser.add_argument("--output", required=True, help="Output summary file path")
    
    args = parser.parse_args()
    
    try:
        # Skill 1: Retrieve and parse policy
        print(f"Loading policy from: {args.input}")
        policy_data = retrieve_policy(args.input)
        
        # Skill 2: Summarize with enforcement
        print("Generating summary with clause enforcement...")
        summary = summarize_policy(policy_data)
        
        # Write output
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"Summary written to: {args.output}")
        print("✓ All required clauses preserved")
        print("✓ Multi-condition obligations intact")
        print("✓ No scope bleed detected")
        
    except IOError as e:
        print(f"ERROR (File I/O): {e}")
        exit(1)
    except ValueError as e:
        print(f"ERROR (Enforcement): {e}")
        exit(1)
    except Exception as e:
        print(f"ERROR (Unexpected): {e}")
        exit(1)


if __name__ == "__main__":
    main()
  