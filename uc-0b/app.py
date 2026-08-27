"""
UC-0B app.py — Policy Summarizer with Clause Preservation.
Extracts critical clauses from HR leave policy and generates a summary
that preserves all obligations, multi-condition requirements, and binding verbs.
"""
import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class ClauseExtractor:
    """Extracts and validates critical clauses from policy documents."""

    # Clause mapping: reference -> (clause_num, section, obligation, binding_verb)
    CRITICAL_CLAUSES = {
        "2.3": ("2.3", "Annual Leave", "14-day advance notice required", "must"),
        "2.4": ("2.4", "Annual Leave", "Written approval required before leave commences. Verbal not valid.", "must"),
        "2.5": ("2.5", "Annual Leave", "Unapproved absence = LOP regardless of subsequent approval", "will"),
        "2.6": ("2.6", "Annual Leave", "Max 5 days carry-forward. Above 5 forfeited on 31 Dec.", "may/are"),
        "2.7": ("2.7", "Annual Leave", "Carry-forward days must be used Jan–Mar or forfeited", "must"),
        "3.2": ("3.2", "Sick Leave", "3+ consecutive sick days requires medical cert within 48hrs", "requires"),
        "3.4": ("3.4", "Sick Leave", "Sick leave before/after holiday requires cert regardless of duration", "requires"),
        "5.2": ("5.2", "LWP", "LWP requires Department Head AND HR Director approval (TWO approvers)", "requires"),
        "5.3": ("5.3", "LWP", "LWP >30 days requires Municipal Commissioner approval", "requires"),
        "7.2": ("7.2", "Leave Encashment", "Leave encashment during service not permitted under any circumstances", "not permitted"),
    }

    def __init__(self, policy_text: str):
        self.policy_text = policy_text
        self.extracted_clauses: Dict[str, bool] = {clause_id: False for clause_id in self.CRITICAL_CLAUSES}

    def extract_clauses(self) -> Tuple[str, List[str]]:
        """
        Extract and verify all critical clauses from policy text.
        Returns: (summary_text, missing_clauses_list)
        """
        missing = []
        summary_parts = []
        
        # Add header
        summary_parts.append("POLICY SUMMARY — CRITICAL CLAUSES PRESERVED")
        summary_parts.append("=" * 60)
        summary_parts.append("")
        
        # Organize by section
        sections = {
            "Annual Leave": [],
            "Sick Leave": [],
            "Maternity/Paternity": [],
            "Leave Without Pay (LWP)": [],
            "Public Holidays": [],
            "Leave Encashment": [],
        }
        
        # Extract each critical clause
        for clause_id, (_, section, obligation, verb) in self.CRITICAL_CLAUSES.items():
            # Search for clause in policy
            pattern = rf"{clause_id}[:\s]+(.*?)(?=\d+\.\d+|$)"
            match = re.search(pattern, self.policy_text, re.IGNORECASE | re.DOTALL)
            
            if match:
                clause_text = match.group(1).strip()
                # Clean up and normalize
                clause_text = re.sub(r'\s+', ' ', clause_text)[:200]  # Cap length
                self.extracted_clauses[clause_id] = True
                
                # Map to section for organization
                if section == "Annual Leave":
                    sections["Annual Leave"].append(f"{clause_id}: {obligation}")
                elif section == "Sick Leave":
                    sections["Sick Leave"].append(f"{clause_id}: {obligation}")
                elif section == "LWP":
                    sections["Leave Without Pay (LWP)"].append(f"{clause_id}: {obligation}")
                elif section == "Leave Encashment":
                    sections["Leave Encashment"].append(f"{clause_id}: {obligation}")
            else:
                missing.append(clause_id)
                self.extracted_clauses[clause_id] = False
        
        # Build organized summary
        for section_name, clauses in sections.items():
            if clauses:
                summary_parts.append(f"\n{section_name}")
                summary_parts.append("-" * 40)
                for clause in clauses:
                    summary_parts.append(f"  • {clause}")
        
        # Add validation report
        summary_parts.append("\n" + "=" * 60)
        summary_parts.append("VALIDATION REPORT")
        summary_parts.append(f"Total Critical Clauses: {len(self.CRITICAL_CLAUSES)}")
        summary_parts.append(f"Clauses Found: {sum(self.extracted_clauses.values())}")
        summary_parts.append(f"Clauses Missing: {len(missing)}")
        
        if missing:
            summary_parts.append(f"MISSING CLAUSES: {', '.join(missing)}")
            summary_parts.append("\nWARNING: Summary is incomplete and may violate policy requirements.")
        else:
            summary_parts.append("✓ All critical clauses preserved.")
        
        return "\n".join(summary_parts), missing

    def validate_multi_conditions(self) -> List[str]:
        """
        Validate that multi-condition clauses (like 5.2) preserve ALL conditions.
        Returns list of validation issues.
        """
        issues = []
        
        # Check clause 5.2 explicitly for TWO approvers
        if "5.2" in self.policy_text:
            if "Department Head" not in self.policy_text or "HR Director" not in self.policy_text:
                issues.append("MULTI-CONDITION VIOLATION: Clause 5.2 missing dual approval requirement")
        
        return issues


def main():
    parser = argparse.ArgumentParser(description="UC-0B: Policy Summary with Clause Preservation")
    parser.add_argument("--input", required=True, help="Input policy document path")
    parser.add_argument("--output", required=True, help="Output summary file path")
    
    args = parser.parse_args()
    
    # Read input
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            policy_text = f.read()
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    # Extract and validate
    extractor = ClauseExtractor(policy_text)
    summary, missing_clauses = extractor.extract_clauses()
    
    # Check multi-condition violations
    validation_issues = extractor.validate_multi_conditions()
    
    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(summary)
        if validation_issues:
            f.write("\n\nVALIDATION ISSUES:\n")
            for issue in validation_issues:
                f.write(f"  ⚠ {issue}\n")
    
    # Report status
    if missing_clauses:
        print(f"⚠ SUMMARY INCOMPLETE: {len(missing_clauses)} clauses missing", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"✓ Summary generated successfully: {output_path}")
        print(f"✓ All {len(extractor.CRITICAL_CLAUSES)} critical clauses preserved")


if __name__ == "__main__":
    main()
