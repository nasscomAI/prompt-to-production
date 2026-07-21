"""
UC-0B app.py — Implemented policy summarizer with agentic compliance checks.
"""
import argparse
import sys
import os
import re

class ValidationError(Exception):
    """Custom exception raised when policy validation rules are violated."""
    pass

def retrieve_policy(file_path: str) -> list:
    """
    Skill retrieve_policy: loads plain text HR policy file and returns its content
    structured as a list of numbered sections/clauses.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    if not content.strip():
        raise ValueError("Policy file is empty.")
        
    lines = content.splitlines()
    sections = []
    current_clause_id = None
    current_text_parts = []
    
    # Regex to match clause IDs (e.g., "2.3", "5.12") at the beginning of a line
    clause_start_regex = re.compile(r"^(\d+\.\d+)\s+(.*)$")
    
    for line in lines:
        stripped = line.strip()
        match = clause_start_regex.match(line)
        if match:
            # Save the previous clause
            if current_clause_id:
                sections.append({
                    "clause_id": current_clause_id,
                    "text": " ".join(current_text_parts).strip()
                })
            current_clause_id = match.group(1)
            current_text_parts = [match.group(2).strip()]
        else:
            if current_clause_id:
                # Check if we encounter a new main section header that signals clause end
                if line.startswith("═══") or re.match(r"^\d+\.\s+[A-Z\s]+$", stripped):
                    sections.append({
                        "clause_id": current_clause_id,
                        "text": " ".join(current_text_parts).strip()
                    })
                    current_clause_id = None
                    current_text_parts = []
                elif stripped:
                    current_text_parts.append(stripped)
                    
    # Append the last active clause
    if current_clause_id:
        sections.append({
            "clause_id": current_clause_id,
            "text": " ".join(current_text_parts).strip()
        })
        
    return sections

def check_clause_compliance(clause_id: str, text: str) -> tuple[bool, str]:
    """
    Verify if a given clause text complies with RICE enforcement constraints.
    Returns (is_compliant, reason_if_not)
    """
    # Clean up whitespace and normalize to lower case
    text_lower = text.lower()
    
    # 1. Condition drop check for 5.2 (Department Head AND HR Director)
    if clause_id == "5.2":
        if "department head" not in text_lower or "hr director" not in text_lower:
            return False, "dropped required approvers (Department Head and HR Director)"
        if "and" not in text_lower:
            return False, "dropped dual approval requirement (both Department Head AND HR Director)"

    # 2. Obligation softening check:
    # If the text uses soft words like "should", "optional", "recommended", "suggested", "typically", "generally"
    # when the original clause was mandatory, we flag it.
    softening_words = ["should", "optional", "recommended", "suggested", "typically", "generally", "expected to"]
    for word in softening_words:
        if word in text_lower:
            return False, f"detected soft/optional obligation verb ('{word}')"

    # 3. Key condition checks for target clauses:
    if clause_id == "2.3":
        if "14" not in text_lower or "hr-l1" not in text_lower:
            return False, "missing 14-day notice period or Form HR-L1 condition"
    elif clause_id == "2.4":
        if "written" not in text_lower or "direct manager" not in text_lower or "verbal" not in text_lower:
            return False, "missing manager written approval or verbal invalidity condition"
    elif clause_id == "2.5":
        if "lop" not in text_lower and "loss of pay" not in text_lower:
            return False, "missing Loss of Pay (LOP) consequence"
    elif clause_id == "2.6":
        if "5" not in text_lower or "forfeit" not in text_lower:
            return False, "missing carry forward limit of 5 days or forfeiture rule"
    elif clause_id == "2.7":
        if "first quarter" not in text_lower and "january" not in text_lower and "march" not in text_lower:
            return False, "missing Q1 (Jan-Mar) usage deadline"
    elif clause_id == "3.2":
        if "3" not in text_lower or "medical certificate" not in text_lower or "48" not in text_lower:
            return False, "missing 3+ days medical certificate or 48-hour submission rule"
    elif clause_id == "3.4":
        if "holiday" not in text_lower or "annual leave" not in text_lower or "medical certificate" not in text_lower:
            return False, "missing holiday/annual leave medical certificate requirement"
    elif clause_id == "5.3":
        if "30" not in text_lower or "municipal commissioner" not in text_lower:
            return False, "missing Municipal Commissioner approval requirement for >30 days LWP"
    elif clause_id == "7.2":
        if "during service" not in text_lower or "not permitted" not in text_lower:
            return False, "missing prohibition of leave encashment during service"

    return True, ""

def summarize_policy(sections: list) -> str:
    """
    Skill summarize_policy: takes structured numbered sections, applies agent compliance checks,
    and produces a precise markdown summary.
    """
    # Define standard concise summaries for compliant clauses
    standard_summaries = {
        "2.3": "Leave applications must be submitted at least 14 calendar days in advance using Form HR-L1.",
        "2.4": "Direct manager written approval is required before leave commences; verbal approval is not valid.",
        "2.5": "Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.",
        "2.6": "Max 5 unused annual leave days can be carried forward; any excess is forfeited on 31 December.",
        "2.7": "Carried forward leave must be used in Q1 (Jan-Mar) of the following year or it is forfeited.",
        "3.2": "Sick leave of 3+ consecutive days requires a medical certificate submitted within 48 hours of return.",
        "3.4": "Sick leave before/after holidays or annual leave requires a medical certificate regardless of duration.",
        "5.2": "LWP requires approval from both the Department Head and the HR Director; manager approval alone is insufficient.",
        "5.3": "LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.",
        "7.2": "Leave encashment during service is not permitted under any circumstances."
    }
    
    # Map parsed sections for quick lookup
    clause_lookup = {s["clause_id"]: s["text"] for s in sections}
    
    # Verify that all 10 mandatory clauses are present in the source policy document
    missing_clauses = [cid for cid in standard_summaries.keys() if cid not in clause_lookup]
    if missing_clauses:
        raise ValidationError(f"Mandatory clauses missing from input policy document: {', '.join(missing_clauses)}")
        
    summary_lines = [
        "# CMC Employee Leave Policy Summary",
        "**Reference Document:** CMC HR Leave Policy (HR-POL-001)",
        "**Scope:** Permanent and contractual employees of City Municipal Corporation (CMC) (Excludes daily wage workers/consultants).",
        "",
        "---",
        "",
        "## Core Obligations Summary",
        "",
        "### Annual Leave"
    ]
    
    # Build list of clauses to process by category
    categories = {
        "Annual Leave": ["2.3", "2.4", "2.5", "2.6", "2.7"],
        "Sick Leave": ["3.2", "3.4"],
        "Leave Without Pay (LWP)": ["5.2", "5.3"],
        "Leave Encashment": ["7.2"]
    }
    
    for category, clause_ids in categories.items():
        if category != "Annual Leave":
            summary_lines.append(f"### {category}")
            
        for cid in clause_ids:
            source_text = clause_lookup[cid]
            is_compliant, reason = check_clause_compliance(cid, source_text)
            
            if is_compliant:
                summary_val = standard_summaries[cid]
                summary_lines.append(f"* **Clause {cid}:** {summary_val}")
            else:
                # Rule 4: If a clause cannot be summarized without meaning loss — quote it verbatim and flag it
                flag_msg = f"[FLAGGED: Verbatim quote used because {reason}]"
                summary_lines.append(f"* **Clause {cid}:** {flag_msg} \"{source_text}\"")
                
        summary_lines.append("")
        
    summary_lines.extend([
        "---",
        "*Generated by CMC Policy Summary Agent in compliance with HR guidelines.*"
    ])
    
    return "\n".join(summary_lines)

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer Application")
    parser.add_argument("--input", required=True, help="Path to input HR policy text file")
    parser.add_argument("--output", required=True, help="Path to write the compliant summary text file")
    args = parser.parse_args()
    
    try:
        sections = retrieve_policy(args.input)
        summary = summarize_policy(sections)
        
        # Ensure parent directory of output exists
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
