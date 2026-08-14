"""
UC-0B app.py — Policy Summarizer with Condition Preservation
Implements retrieve_policy and summarize_policy skills per agents.md & skills.md
"""
import argparse
import re
from pathlib import Path
from typing import Dict, List, Any


def retrieve_policy(file_path: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Loads a .txt policy file and returns ONLY the required numbered clauses per UC-0B.
    Required clauses: 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2
    Returns: {clause_id, text, binding_verb, obligation}
    Fails explicitly if structure is ambiguous — no guessing.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {file_path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    content = path.read_text(encoding='utf-8')
    if not content.strip():
        raise ValueError(f"Policy file is empty: {file_path}")

    # Extract numbered clauses (e.g., "2.3 ", "3.2 ")
    # Pattern: line starts with digit.digit followed by clause text
    clause_pattern = r'^(\d+\.\d+)\s+(.+?)(?=\n\d+\.\d+\s+|\Z)'

    # Required clauses per UC-0B README enforcement rules
    required_clause_ids = {"2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}

    clauses = []
    for match in re.finditer(clause_pattern, content, re.MULTILINE | re.DOTALL):
        clause_id = match.group(1)

        # Skip clauses not in the required set (e.g., 1.1 is policy metadata, not enforcement scope)
        if clause_id not in required_clause_ids:
            continue

        text = match.group(2).strip()

        if not text:
            raise ValueError(f"Clause {clause_id} has empty content — structure ambiguous")

        # Extract binding verb (must, may, requires, will, not permitted, are forfeited)
        binding_verbs = ['must', 'may', 'requires', 'will', 'not permitted', 'are forfeited']
        binding_verb = None
        text_lower = text.lower()

        for verb in binding_verbs:
            if verb in text_lower:
                binding_verb = verb
                break

        if not binding_verb:
            raise ValueError(f"Clause {clause_id} has no recognized binding verb — cannot determine obligation strength")

        # Extract obligation (first line or sentence)
        obligation = text.split('\n')[0] if '\n' in text else text[:100]

        clauses.append({
            "clause_id": clause_id,
            "text": text,
            "binding_verb": binding_verb,
            "obligation": obligation
        })

    if not clauses:
        raise ValueError(f"None of the required clauses {sorted(required_clause_ids)} found in policy file: {file_path}")

    return {"clauses": clauses, "source": file_path, "required": required_clause_ids}


def summarize_policy(policy_data: Dict[str, Any]) -> str:
    """
    Takes structured policy sections and produces compliant summary.
    Preserves all clause conditions and binding verbs with clause references.
    Uses verbatim quotes for conditions at risk of meaning loss.
    Flags multi-condition clauses (e.g., 5.2) to prevent silent condition drops.
    """
    clauses = policy_data.get("clauses", [])

    if not clauses:
        raise ValueError("No clauses provided to summarize")

    # Required clauses per README enforcement rule 1
    required_clause_ids = {"2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}
    found_clause_ids = {c["clause_id"] for c in clauses}

    missing = required_clause_ids - found_clause_ids
    if missing:
        raise ValueError(f"Clause omission — missing required clauses: {sorted(missing)}")

    # Multi-condition clauses that need explicit preservation (enforcement rule 2)
    multi_condition_clauses = {
        "5.2": "MULTI-CONDITION: requires approval from BOTH Department Head AND HR Director",
        "5.3": "requires Municipal Commissioner approval (in addition to prior approvers)",
    }

    # Build summary with all conditions preserved
    summary_lines = [
        "HR LEAVE POLICY SUMMARY",
        "=" * 60,
        "\nCLAUSE-BY-CLAUSE BREAKDOWN (All conditions preserved):\n"
    ]

    # Sort clauses numerically for readability
    sorted_clauses = sorted(clauses, key=lambda c: tuple(map(int, c["clause_id"].split('.'))))

    for clause in sorted_clauses:
        clause_id = clause["clause_id"]
        text = clause["text"]
        binding_verb = clause["binding_verb"]

        # Format: [clause_id] BINDING_VERB: full text (preserves all conditions)
        summary_lines.append(f"[{clause_id}] {binding_verb.upper()}")
        summary_lines.append(f"  {text}\n")

        # Flag multi-condition clauses to prevent silent drops (enforcement rule 4)
        if clause_id in multi_condition_clauses:
            summary_lines.append(f"  ⚠️  FLAG: {multi_condition_clauses[clause_id]}\n")

    # Compliance verification
    summary_lines.extend([
        "=" * 60,
        "COMPLIANCE CHECKLIST:\n"
    ])

    for clause_id in sorted(required_clause_ids):
        found = any(c["clause_id"] == clause_id for c in clauses)
        status = "✓ Present" if found else "✗ MISSING"
        summary_lines.append(f"  {clause_id}: {status}")

    summary_lines.append("\n" + "=" * 60)
    summary_lines.append(f"Summary generated from: {policy_data.get('source', 'unknown')}")
    summary_lines.append(f"Total clauses: {len(clauses)}")

    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Policy Summarizer — Extracts and summarizes HR leave policy with multi-condition preservation."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input policy file (e.g., ../data/policy-documents/policy_hr_leave.txt)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output summary file (e.g., summary_hr_leave.txt)"
    )

    args = parser.parse_args()

    try:
        # Retrieve structured policy data (enforce strict parsing — no guessing)
        policy_data = retrieve_policy(args.input)

        # Generate compliant summary (preserve all conditions, flag multi-condition clauses)
        summary = summarize_policy(policy_data)

        # Write to output file
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(summary, encoding='utf-8')

        print(f"✓ Summary generated successfully")
        print(f"  Input:  {args.input}")
        print(f"  Output: {args.output}")
        print(f"  Clauses processed: {len(policy_data['clauses'])}")

    except FileNotFoundError as e:
        print(f"✗ Error: {e}", flush=True)
        exit(1)
    except ValueError as e:
        print(f"✗ Validation error: {e}", flush=True)
        exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}", flush=True)
        exit(1)


if __name__ == "__main__":
    main()
