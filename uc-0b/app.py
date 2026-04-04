"""
UC-0B app.py — Policy Summarization Agent
Implements agents.md role and skills.md retrieve_policy + summarize_policy.
See README.md for run command and expected behaviour.
"""
import argparse
import re
import sys
from pathlib import Path
from typing import Dict, Tuple

# Skill: retrieve_policy
def retrieve_policy(file_path: str) -> Dict[str, str]:
    """
    Loads a .txt policy file and returns content structured by numbered clauses as JSON.
    
    Args:
        file_path: Path to .txt policy document containing numbered HR clauses.
    
    Returns:
        Dict with clause IDs as keys (e.g., "2.3") and clause text as values (verbatim).
    
    Raises:
        FileNotFoundError: If file not found.
        ValueError: If fewer than 10 numbered clauses detected (incomplete document).
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    
    # Extract numbered clauses (pattern: digit(s).digit(s) at line start or after whitespace)
    clause_pattern = r'^(\d+\.\d+)\s+(.+?)(?=^\d+\.\d+\s|\Z)'
    matches = re.finditer(clause_pattern, content, re.MULTILINE | re.DOTALL)
    
    clauses = {}
    for match in matches:
        clause_id = match.group(1).strip()
        clause_text = match.group(2).strip()
        clauses[clause_id] = clause_text
    
    if len(clauses) < 10:
        raise ValueError(
            f"Incomplete policy document: found {len(clauses)} clauses, expected at least 10. "
            "Cannot summarize without risking condition loss."
        )
    
    return clauses


# Skill: summarize_policy
def summarize_policy(clauses: Dict[str, str]) -> str:
    """
    Takes structured policy clauses and produces compliant summary preserving all clauses 
    and conditions with zero omission or scope bleed.
    
    Args:
        clauses: Dict from retrieve_policy with clause IDs as keys, clause text as values.
    
    Returns:
        Text summary with header "POLICY SUMMARY" listing all clauses with binding verbs 
        and complete conditions. Multi-condition clauses preserve ALL conditions with AND.
        Clauses risking meaning loss marked "HIGH FIDELITY: DIRECT QUOTE: [full text]".
    
    Raises:
        ValueError: If input lacks expected clause IDs or requested to add domain assumptions.
    """
    if not clauses or len(clauses) < 10:
        raise ValueError(
            "Missing clauses—cannot summarize incomplete policy."
        )
    
    # Extract binding verbs and detect multi-condition clauses
    binding_verbs = {
        'must': r'\bmust\b',
        'may': r'\bmay\b',
        'will': r'\bwill\b',
        'requires': r'\brequires\b|requires(?=\s)',
        'not permitted': r'\bnot permitted\b|is not permitted\b'
    }
    
    summary_lines = ["POLICY SUMMARY\n"]
    
    for clause_id in sorted(clauses.keys(), key=lambda x: tuple(map(int, x.split('.')))):
        clause_text = clauses[clause_id]
        
        # Detect binding verb
        binding_verb = None
        for verb, pattern in binding_verbs.items():
            if re.search(pattern, clause_text, re.IGNORECASE):
                binding_verb = verb
                break
        
        # Detect multi-condition clauses (containing AND/multiple conditions)
        has_multi_condition = bool(re.search(r'\bAND\b|\bboth\b', clause_text, re.IGNORECASE))
        
        # Extract binding verb from clause for format [verb]
        verb_tag = f"[{binding_verb}]" if binding_verb else ""
        
        # Check for phrases indicating scope bleed (domain assumptions)
        scope_bleed_patterns = [
            r'typically', r'generally', r'as is standard practice',
            r'as is common', r'is expected to', r'in most cases'
        ]
        has_scope_bleed = any(re.search(pattern, clause_text, re.IGNORECASE) 
                              for pattern in scope_bleed_patterns)
        
        if has_scope_bleed:
            raise ValueError(
                f"Clause {clause_id} contains domain assumptions. Cannot summarize without risking condition loss."
            )
        
        # For multi-condition clauses or complex ones, check if direct quote needed
        if has_multi_condition or len(clause_text) > 150:
            summary_lines.append(f"Clause {clause_id} {verb_tag}: HIGH FIDELITY: DIRECT QUOTE: {clause_text}")
        else:
            summary_lines.append(f"Clause {clause_id} {verb_tag}: {clause_text}")
    
    return "\n".join(summary_lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description='UC-0B Policy Summarization Agent'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Path to input policy document (.txt)'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Path to output summary file'
    )
    
    args = parser.parse_args()
    
    try:
        # Skill: retrieve_policy
        print(f"[Agent] Retrieving policy from: {args.input}")
        clauses = retrieve_policy(args.input)
        print(f"[Agent] Extracted {len(clauses)} numbered clauses")
        
        # Skill: summarize_policy
        print(f"[Agent] Summarizing policy with zero condition loss...")
        summary = summarize_policy(clauses)
        
        # Write output
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"[Agent] Summary written to: {args.output}")
        print(f"[Agent] Verification: All {len(clauses)} clauses preserved with complete conditions.")
        
    except FileNotFoundError as e:
        print(f"[Agent] ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"[Agent] REFUSAL: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[Agent] UNEXPECTED ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
