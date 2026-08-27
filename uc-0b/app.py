"""
UC-0B app.py — Policy Summarizer with Compliance Enforcement.
Implements retrieve_policy and summarize_policy skills from agents.md + skills.md.
Preserves all clauses, multi-conditions, binding verbs, and detects scope bleed.
"""
import argparse
import re
import json

# Define the 10 mandatory clauses from the policy
REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

# Binding verbs that must be preserved
BINDING_VERBS = {"must", "will", "may", "requires", "not permitted"}

# Scope bleed indicators (forbidden phrases)
SCOPE_BLEED_PHRASES = {
    "as is standard practice": "scope_bleed",
    "typically in government": "scope_bleed",
    "employees are generally expected to": "scope_bleed",
    "it is common that": "scope_bleed",
    "generally": "scope_bleed",
    "typically": "scope_bleed",
    "standard practice": "scope_bleed",
}

# Multi-condition clause dependencies (clause_id -> list of required conditions)
MULTI_CONDITION_CLAUSES = {
    "5.2": ["Department Head", "HR Director"],  # Both required
}


def retrieve_policy(file_path: str) -> dict:
    """
    Load HR leave policy .txt file and structure it by clause ID.
    Returns: dict with raw_text, sections (clause_id -> clause_text), clause_list
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    
    if not raw_text or not raw_text.strip():
        return {
            "raw_text": raw_text,
            "sections": {},
            "clause_list": []
        }
    
    # Extract clauses by pattern: "2.3", "2.4", etc.
    sections = {}
    clause_pattern = r"(\d+\.\d+)\s*[:.)]?\s*(.+?)(?=\n\d+\.\d+|$)"
    
    matches = re.finditer(clause_pattern, raw_text, re.DOTALL)
    for match in matches:
        clause_id = match.group(1)
        clause_text = match.group(2).strip()
        if clause_id in REQUIRED_CLAUSES:
            sections[clause_id] = clause_text
    
    return {
        "raw_text": raw_text,
        "sections": sections,
        "clause_list": REQUIRED_CLAUSES
    }


def detect_scope_bleed(text: str) -> list:
    """Detect scope bleed phrases in text."""
    violations = []
    text_lower = text.lower()
    for phrase in SCOPE_BLEED_PHRASES:
        if phrase in text_lower:
            violations.append(f"SCOPE_BLEED: Found forbidden phrase '{phrase}'")
    return violations


def detect_binding_verb_softening(original: str, summary: str, clause_id: str) -> list:
    """Detect if binding verbs have been softened."""
    violations = []
    
    # Extract binding verbs from original
    original_verbs = set()
    for verb in BINDING_VERBS:
        if re.search(r"\b" + re.escape(verb) + r"\b", original, re.IGNORECASE):
            original_verbs.add(verb.lower())
    
    # Check if softening occurred (e.g., "must" changed to "can")
    softening_map = {"must": "can", "will": "may", "requires": "suggest"}
    for hard_verb, soft_verb in softening_map.items():
        if hard_verb in original_verbs:
            # Ensure hard_verb is still in summary
            if not re.search(r"\b" + re.escape(hard_verb) + r"\b", summary, re.IGNORECASE):
                if re.search(r"\b" + re.escape(soft_verb) + r"\b", summary, re.IGNORECASE):
                    violations.append(f"BINDING_VERB_SOFTENING ({clause_id}): '{hard_verb}' changed to '{soft_verb}'")
    
    return violations


def detect_condition_drop(clause_id: str, original: str, summary: str) -> list:
    """Detect if multi-conditions have been dropped."""
    violations = []
    
    if clause_id in MULTI_CONDITION_CLAUSES:
        required_conditions = MULTI_CONDITION_CLAUSES[clause_id]
        found_conditions = 0
        
        for condition in required_conditions:
            if re.search(re.escape(condition), summary, re.IGNORECASE):
                found_conditions += 1
        
        if found_conditions < len(required_conditions):
            missing = [c for c in required_conditions 
                      if not re.search(re.escape(c), summary, re.IGNORECASE)]
            violations.append(f"CONDITION_DROP ({clause_id}): Missing condition(s): {', '.join(missing)}")
    
    return violations


def summarize_policy(policy_data: dict) -> dict:
    """
    Produce compliance-preserving summary with all 10 clauses preserved.
    Returns: dict with summary, clause_coverage, preserved_verbatim, compliance_flags
    """
    sections = policy_data["sections"]
    clause_list = policy_data["clause_list"]
    
    summary_lines = []
    clause_coverage = []
    preserved_verbatim = []
    compliance_flags = []
    
    # Check for missing clauses
    missing_clauses = [c for c in clause_list if c not in sections]
    if missing_clauses:
        for clause_id in missing_clauses:
            compliance_flags.append(f"CLAUSE_OMISSION: Clause {clause_id} missing from source document")
    
    # Process each required clause
    for clause_id in clause_list:
        if clause_id not in sections:
            continue
        
        original_text = sections[clause_id]
        clause_coverage.append(clause_id)
        
        # For now, use clause text as-is in summary
        # In production, LLM would summarize while respecting constraints
        summary_line = f"Clause {clause_id}: {original_text}"
        
        # Check for violations in this clause
        scope_bleed_violations = detect_scope_bleed(original_text)
        binding_verb_violations = detect_binding_verb_softening(original_text, summary_line, clause_id)
        condition_drop_violations = detect_condition_drop(clause_id, original_text, summary_line)
        
        compliance_flags.extend(scope_bleed_violations)
        compliance_flags.extend(binding_verb_violations)
        compliance_flags.extend(condition_drop_violations)
        
        # Check if clause needs verbatim preservation (complex multi-condition)
        if clause_id in MULTI_CONDITION_CLAUSES:
            preserved_verbatim.append({
                "clause_id": clause_id,
                "text": original_text,
                "reason": f"Multi-condition clause requires all conditions: {', '.join(MULTI_CONDITION_CLAUSES[clause_id])}"
            })
            summary_line = f"[PRESERVE_VERBATIM {clause_id}] {original_text}"
        
        summary_lines.append(summary_line)
    
    # Check for missing clauses in coverage
    for clause_id in clause_list:
        if clause_id not in clause_coverage and clause_id in sections:
            compliance_flags.append(f"CLAUSE_OMISSION: Clause {clause_id} not included in summary")
    
    return {
        "summary": "\n\n".join(summary_lines),
        "clause_coverage": clause_coverage,
        "preserved_verbatim": preserved_verbatim,
        "compliance_flags": compliance_flags
    }


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", required=True, help="Path to write summary output")
    args = parser.parse_args()
    
    try:
        # Retrieve policy
        policy_data = retrieve_policy(args.input)
        
        # Summarize with compliance checking
        result = summarize_policy(policy_data)
        
        # Write output
        with open(args.output, "w", encoding="utf-8") as f:
            f.write("# UC-0B Policy Summary\n\n")
            f.write(result["summary"])
            f.write("\n\n---\n\n")
            f.write("## Compliance Report\n\n")
            f.write(f"**Clauses Covered:** {', '.join(result['clause_coverage'])}\n\n")
            
            if result["preserved_verbatim"]:
                f.write("**Preserved Verbatim Clauses:**\n")
                for pv in result["preserved_verbatim"]:
                    f.write(f"- Clause {pv['clause_id']}: {pv['reason']}\n")
                f.write("\n")
            
            if result["compliance_flags"]:
                f.write("**Compliance Flags (Violations):**\n")
                for flag in result["compliance_flags"]:
                    f.write(f"- {flag}\n")
            else:
                f.write("**Compliance Flags:** None - summary is compliant.\n")
        
        print(f"Summary written to: {args.output}")
        print(f"Clauses covered: {len(result['clause_coverage'])}/{len(REQUIRED_CLAUSES)}")
        print(f"Compliance violations: {len(result['compliance_flags'])}")
        
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
    except Exception as e:
        print(f"ERROR: Failed to process policy: {e}")

if __name__ == "__main__":
    main()
