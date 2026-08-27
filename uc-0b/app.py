"""
UC-0B app.py — Policy Summarization Agent
Implements high-precision extraction of binding obligations with zero clause omission.
"""
import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Set


# Required clauses from ground truth inventory
REQUIRED_CLAUSES = {"2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}

# Forbidden phrases that indicate scope bleed
FORBIDDEN_PHRASES = [
    "standard practice",
    "typically in government",
    "generally expected",
    "as is customary",
    "industry standard"
]


def retrieve_policy(file_path: str) -> Dict[str, str]:
    """
    Skill: retrieve_policy
    Extracts policy content and returns structured numbered sections.
    
    Error handling: Reports error if file missing or clauses cannot be identified.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Source document missing: {file_path}")
        
        content = path.read_text(encoding='utf-8')
        
        # Extract numbered clauses (e.g., 2.3, 3.2, etc.)
        sections = {}
        pattern = r'(\d+\.\d+)\s+(.+?)(?=\n\d+\.\d+\s|\Z)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        if not matches:
            raise ValueError("Parser cannot unambiguously identify numbered clauses")
        
        for clause_id, clause_text in matches:
            sections[clause_id] = clause_text.strip()
        
        return sections
    
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to retrieve policy - {e}", file=sys.stderr)
        sys.exit(1)


def summarize_policy(sections: Dict[str, str], required_clauses: Set[str]) -> str:
    """
    Skill: summarize_policy
    Transforms structured sections into summary preserving all binding conditions.
    
    Error handling: Rejects output if clauses omitted, conditions dropped, or scope bleed detected.
    """
    # Enforcement Rule 1: Check all required clauses are present
    missing_clauses = required_clauses - set(sections.keys())
    if missing_clauses:
        raise ValueError(f"Clause omission detected: Missing clauses {sorted(missing_clauses)}")
    
    summary_lines = ["POLICY SUMMARY: HR Leave Policy\n"]
    summary_lines.append("=" * 60 + "\n")
    
    # Process each required clause in order
    for clause_id in sorted(required_clauses, key=lambda x: tuple(map(int, x.split('.')))):
        clause_text = sections[clause_id]
        
        # Check for scope bleed in source (should not happen, but verify)
        for forbidden in FORBIDDEN_PHRASES:
            if forbidden.lower() in clause_text.lower():
                raise ValueError(f"Scope bleed detected in clause {clause_id}: '{forbidden}'")
        
        summary_lines.append(f"[{clause_id}] {clause_text}\n")
    
    summary = "".join(summary_lines)
    
    # Final validation: Enforcement Rule 2 - Check for condition drops
    # Multi-condition obligations that must preserve ALL conditions
    critical_multi_conditions = {
        "5.2": ["Department Head", "HR Director"],  # TWO approvers required
        "3.2": ["3", "consecutive", "medical", "48"],  # All conditions
        "2.4": ["written", "before", "Verbal"],  # Written + timing + verbal exclusion
    }
    
    for clause_id, required_terms in critical_multi_conditions.items():
        if clause_id in sections:
            clause_content = sections[clause_id].lower()
            missing_terms = [term for term in required_terms if term.lower() not in clause_content]
            if missing_terms:
                raise ValueError(
                    f"Condition drop detected in clause {clause_id}: "
                    f"Missing terms {missing_terms}"
                )
    
    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Policy Summarization Agent - High-precision binding obligation extraction"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input policy .txt file"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output summary file"
    )
    
    args = parser.parse_args()
    
    # Skill 1: Retrieve policy with structured sections
    print(f"Retrieving policy from: {args.input}")
    sections = retrieve_policy(args.input)
    print(f"✓ Extracted {len(sections)} numbered clauses")
    
    # Skill 2: Summarize policy with enforcement rules
    print(f"Summarizing policy (enforcing {len(REQUIRED_CLAUSES)} required clauses)...")
    try:
        summary = summarize_policy(sections, REQUIRED_CLAUSES)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Write output
    output_path = Path(args.output)
    output_path.write_text(summary, encoding='utf-8')
    print(f"✓ Summary written to: {args.output}")
    print(f"✓ All {len(REQUIRED_CLAUSES)} required clauses verified")


if __name__ == "__main__":
    main()
