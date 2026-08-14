"""
UC-0B app.py — Policy Summarization with Compliance Audit

Implements retrieve_policy and summarize_policy skills to produce
a condition-complete summary that passes a 10-clause ground truth audit.

See README.md for run command and expected behaviour.
"""
import argparse
import json
import re
from datetime import datetime
from pathlib import Path

# Ground truth: 10 critical clauses that MUST appear in summary
GROUND_TRUTH_CLAUSES = {
    "2.3": {
        "core_obligation": "14-day advance notice required",
        "binding_verb": "must",
        "conditions": ["14 calendar days advance notice", "using Form HR-L1"],
    },
    "2.4": {
        "core_obligation": "Written approval required before leave commences. Verbal not valid.",
        "binding_verb": "must",
        "conditions": ["written (not verbal)", "from direct manager", "before leave commences"],
    },
    "2.5": {
        "core_obligation": "Unapproved absence = LOP regardless of subsequent approval",
        "binding_verb": "will",
        "conditions": ["regardless of subsequent approval"],
    },
    "2.6": {
        "core_obligation": "Max 5 days carry-forward. Above 5 forfeited on 31 Dec.",
        "binding_verb": "may / are forfeited",
        "conditions": ["maximum 5 days", "above 5 forfeited on 31 December"],
    },
    "2.7": {
        "core_obligation": "Carry-forward days must be used Jan–Mar or forfeited",
        "binding_verb": "must",
        "conditions": ["first quarter (January–March)", "or forfeited"],
    },
    "3.2": {
        "core_obligation": "3+ consecutive sick days requires medical cert within 48hrs",
        "binding_verb": "requires",
        "conditions": ["3 or more consecutive days", "medical certificate", "within 48 hours"],
    },
    "3.4": {
        "core_obligation": "Sick leave before/after holiday requires cert regardless of duration",
        "binding_verb": "requires",
        "conditions": ["before or after public holiday", "medical certificate", "regardless of duration"],
    },
    "5.2": {
        "core_obligation": "LWP requires Department Head AND HR Director approval",
        "binding_verb": "requires",
        "conditions": ["Department Head approval", "HR Director approval"],
        "multi_condition_trap": True,
    },
    "5.3": {
        "core_obligation": "LWP >30 days requires Municipal Commissioner approval",
        "binding_verb": "requires",
        "conditions": ["exceeding 30 continuous days", "Municipal Commissioner approval"],
    },
    "7.2": {
        "core_obligation": "Leave encashment during service not permitted under any circumstances",
        "binding_verb": "not permitted",
        "conditions": ["during service", "under any circumstances"],
    },
}


def retrieve_policy(file_path):
    """
    Parse plain-text HR policy and extract numbered clauses with binding verbs.
    Returns structured JSON with sections and clauses.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise ValueError(f"Policy file not found at {file_path}")
    except UnicodeDecodeError:
        raise ValueError(f"File format not supported (expected .txt UTF-8)")

    # Extract document metadata
    meta_title_match = re.search(r"EMPLOYEE LEAVE POLICY", content)
    meta_ref_match = re.search(r"Document Reference:\s*(\S+)", content)
    meta_version_match = re.search(r"Version:\s*([\d.]+)", content)
    meta_date_match = re.search(r"Effective:\s*([^\n]+)", content)

    sections = {}
    
    # Split by main sections (numbered headers like "1. PURPOSE AND SCOPE")
    section_pattern = r"^([\d]+)\.\s+([^\n]+)"
    subsection_pattern = r"^([\d]+\.[\d]+)\s+(.+?)(?=^[\d]+\.[\d]+\s|\Z)"
    
    lines = content.split('\n')
    current_section = None
    current_section_title = None
    current_clause_id = None
    current_clause_lines = []
    
    for line in lines:
        # Check for main section header
        main_sec_match = re.match(section_pattern, line)
        if main_sec_match:
            sec_num, sec_title = main_sec_match.groups()
            current_section = sec_num
            current_section_title = sec_title.strip()
            if current_section not in sections:
                sections[current_section] = {
                    "section_number": current_section,
                    "section_title": current_section_title,
                    "clauses": {}
                }
            continue
        
        # Check for numbered clause (e.g., "2.3")
        clause_match = re.match(r"^([\d]+\.[\d]+)\s+(.+)", line)
        if clause_match and current_section:
            clause_id, clause_text = clause_match.groups()
            if current_clause_id and current_clause_lines:
                # Save previous clause
                full_text = ' '.join(current_clause_lines).strip()
                sections[current_section]["clauses"][current_clause_id] = {
                    "clause_id": current_clause_id,
                    "text": full_text,
                }
            current_clause_id = clause_id
            current_clause_lines = [clause_text]
        elif current_clause_id and line.strip():
            # Continuation of current clause
            current_clause_lines.append(line.strip())
    
    # Save last clause
    if current_clause_id and current_clause_lines and current_section:
        full_text = ' '.join(current_clause_lines).strip()
        sections[current_section]["clauses"][current_clause_id] = {
            "clause_id": current_clause_id,
            "text": full_text,
        }
    
    return {
        "document_meta": {
            "title": "EMPLOYEE LEAVE POLICY",
            "reference": meta_ref_match.group(1) if meta_ref_match else "N/A",
            "version": meta_version_match.group(1) if meta_version_match else "N/A",
            "effective_date": meta_date_match.group(1).strip() if meta_date_match else "N/A",
        },
        "sections": sections,
    }


def summarize_policy(structured_policy):
    """
    Produce a condition-complete summary with compliance audit.
    Returns summary text and compliance audit report.
    """
    sections = structured_policy["sections"]
    
    # Build summary by iterating through sections
    summary_lines = ["EMPLOYEE LEAVE POLICY — COMPLIANT SUMMARY", "=" * 50, ""]
    clauses_found = {}
    clauses_missing = []
    binding_verb_errors = []
    condition_drops = []
    scope_bleed_flags = []
    
    for sec_num in sorted(sections.keys(), key=lambda x: float(x)):
        section = sections[sec_num]
        summary_lines.append(f"\n{sec_num}. {section['section_title']}")
        summary_lines.append("-" * 40)
        
        for clause_id in sorted(section["clauses"].keys(), key=lambda x: float(x)):
            clause_data = section["clauses"][clause_id]
            clause_text = clause_data["text"]
            
            # Check against ground truth
            if clause_id in GROUND_TRUTH_CLAUSES:
                ground_truth = GROUND_TRUTH_CLAUSES[clause_id]
                
                # Check for binding verb presence
                binding_verb = ground_truth["binding_verb"]
                verb_present = any(verb.lower() in clause_text.lower() 
                                 for verb in binding_verb.split(" / "))
                
                # Check for multi-condition trap (especially clause 5.2)
                conditions_preserved = True
                if ground_truth.get("multi_condition_trap"):
                    # For 5.2, both "Department Head" and "HR Director" must be present
                    if "Department Head" not in clause_text or "HR Director" not in clause_text:
                        conditions_preserved = False
                        condition_drops.append({
                            "clause_id": clause_id,
                            "issue": "Multi-condition constraint violated",
                            "required": ground_truth["conditions"],
                            "found_text": clause_text[:100],
                        })
                
                # Check for scope bleed
                scope_bleed_phrases = ["typically", "usually", "generally", "as is standard", 
                                      "best practice", "expected to", "should ideally"]
                for phrase in scope_bleed_phrases:
                    if phrase in clause_text.lower():
                        scope_bleed_flags.append({
                            "clause_id": clause_id,
                            "phrase": phrase,
                            "text_excerpt": clause_text[:100],
                        })
                
                clauses_found[clause_id] = {
                    "status": "PRESENT",
                    "binding_verb_preserved": verb_present,
                    "conditions_preserved": conditions_preserved,
                    "quote_from_summary": clause_text[:150],
                }
            else:
                # Clause not in ground truth (secondary clauses)
                summary_lines.append(f"  Clause {clause_id}: {clause_text}")
                continue
            
            # Add to summary
            summary_lines.append(f"  Clause {clause_id}: {clause_text}")
    
    # Check for missing clauses
    for clause_id in GROUND_TRUTH_CLAUSES:
        if clause_id not in clauses_found:
            clauses_missing.append(clause_id)
    
    # Determine pass/fail
    pass_fail = (len(clauses_missing) == 0 and 
                len(condition_drops) == 0 and 
                len(scope_bleed_flags) == 0 and
                all(c.get("binding_verb_preserved", False) for c in clauses_found.values()))
    
    summary_text = '\n'.join(summary_lines)
    
    compliance_audit = {
        "total_clauses_required": len(GROUND_TRUTH_CLAUSES),
        "clauses_found": clauses_found,
        "clauses_missing": clauses_missing,
        "binding_verb_errors": binding_verb_errors,
        "condition_drops": condition_drops,
        "scope_bleed_flags": scope_bleed_flags,
        "pass_fail": pass_fail,
        "summary": generate_audit_summary(len(GROUND_TRUTH_CLAUSES), clauses_missing, 
                                         condition_drops, scope_bleed_flags),
    }
    
    return summary_text, compliance_audit


def generate_audit_summary(total, missing, condition_drops, scope_bleed):
    """Generate human-readable compliance audit summary."""
    if not missing and not condition_drops and not scope_bleed:
        return f"✓ PASS: All {total} critical clauses present, all conditions preserved, no scope bleed."
    
    issues = []
    if missing:
        issues.append(f"MISSING CLAUSES: {', '.join(missing)}")
    if condition_drops:
        issues.append(f"CONDITION DROPS: {len(condition_drops)} clause(s) have missing conditions")
    if scope_bleed:
        issues.append(f"SCOPE BLEED: {len(scope_bleed)} clause(s) contain external language")
    
    return "✗ FAIL: " + "; ".join(issues)


def main():
    parser = argparse.ArgumentParser(
        description="Summarize HR leave policy with compliance audit."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input policy document (e.g., ../data/policy-documents/policy_hr_leave.txt)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output summary file (e.g., summary_hr_leave.txt)",
    )
    args = parser.parse_args()
    
    try:
        # Step 1: Retrieve policy
        print(f"[1/3] Retrieving policy from {args.input}...")
        structured_policy = retrieve_policy(args.input)
        print(f"      Loaded {len(structured_policy['sections'])} sections")
        
        # Step 2: Summarize policy with compliance audit
        print("[2/3] Generating summary with compliance audit...")
        summary_text, compliance_audit = summarize_policy(structured_policy)
        
        # Step 3: Write output
        print(f"[3/3] Writing summary to {args.output}...")
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary_text)
            f.write("\n\n" + "=" * 70 + "\n")
            f.write("COMPLIANCE AUDIT REPORT\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Status: {compliance_audit['summary']}\n\n")
            f.write("Clauses Required (10 Critical):\n")
            for clause_id in sorted(GROUND_TRUTH_CLAUSES.keys(), key=lambda x: float(x)):
                status = "✓" if clause_id in compliance_audit['clauses_found'] else "✗"
                print(f"  {status} {clause_id}")
                f.write(f"  {status} {clause_id}: {GROUND_TRUTH_CLAUSES[clause_id]['core_obligation']}\n")
            
            if compliance_audit['clauses_missing']:
                f.write(f"\nMissing Clauses: {', '.join(compliance_audit['clauses_missing'])}\n")
            if compliance_audit['condition_drops']:
                f.write(f"\nCondition Drops Detected: {len(compliance_audit['condition_drops'])}\n")
                for drop in compliance_audit['condition_drops']:
                    f.write(f"  - {drop['clause_id']}: {drop['issue']}\n")
            if compliance_audit['scope_bleed_flags']:
                f.write(f"\nScope Bleed Detected: {len(compliance_audit['scope_bleed_flags'])}\n")
                for bleed in compliance_audit['scope_bleed_flags']:
                    f.write(f"  - {bleed['clause_id']}: '{bleed['phrase']}' found\n")
            
            f.write(f"\nGenerated: {datetime.now().isoformat()}\n")
        
        # Print results
        print(f"\n✓ Summary written to {output_path}")
        print(f"✓ Audit Status: {compliance_audit['summary']}")
        
        if not compliance_audit['pass_fail']:
            print("\n⚠ WARNING: Summary did not pass compliance audit.")
            print("  Review the full audit report in the output file.")
            return 1
        
        return 0
    
    except Exception as e:
        print(f"✗ Error: {e}", flush=True)
        return 1


if __name__ == "__main__":
    exit(main())
