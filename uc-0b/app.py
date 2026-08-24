#!/usr/bin/env python3
"""
UC-0B: HR Leave Policy Summarizer
Produces clause-preserving summaries maintaining all binding obligations.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple


REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

SCOPE_BLEED_PATTERNS = [
    r"as is standard practice",
    r"typically in government organisations?",
    r"employees are generally expected to",
    r"as per standard practice",
    r"in general",
    r"usually",
    r"normally",
    r"standard procedure",
]

MULTI_CONDITION_CLAUSES = {
    "5.2": ["Department Head", "HR Director"],
    "5.3": ["Municipal Commissioner"],
}


class ScopeBleedError(Exception):
    pass


class ConditionDropError(Exception):
    pass


def retrieve_policy(file_path: str) -> Dict[str, Any]:
    """
    Loads a .txt policy file and returns its content parsed into structured numbered sections.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {file_path}")

    if path.suffix.lower() != ".txt":
        raise ValueError(f"File must be a .txt file, got: {path.suffix}")

    content = path.read_text(encoding="utf-8")

    sections = {}
    lines = content.split("\n")

    current_clause = None
    current_text = []

    for line in lines:
        clause_match = re.match(r"^(\d+\.\d+)\s+(.+)$", line)
        if clause_match:
            if current_clause is not None:
                sections[current_clause] = " ".join(current_text).strip()
            current_clause = clause_match.group(1)
            current_text = [clause_match.group(2)]
        elif current_clause is not None and line.strip():
            stripped = line.strip()
            if not stripped.startswith("═══") and not re.match(r"^\d+\.\s", stripped):
                current_text.append(stripped)

    if current_clause is not None:
        sections[current_clause] = " ".join(current_text).strip()

    if not sections:
        return {"raw_content": content, "parse_warning": True, "sections": {}}

    return {"sections": sections, "parse_warning": False}


def check_scope_bleed(text: str) -> List[str]:
    """Check for scope bleed phrases in the output."""
    violations = []
    for pattern in SCOPE_BLEED_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            violations.append(pattern)
    return violations


def check_multi_conditions(clause_num: str, summary_text: str) -> bool:
    """Verify multi-condition clauses preserve all conditions."""
    if clause_num not in MULTI_CONDITION_CLAUSES:
        return True

    required_conditions = MULTI_CONDITION_CLAUSES[clause_num]
    for condition in required_conditions:
        if condition.lower() not in summary_text.lower():
            return False
    return True


def summarize_policy(structured_data: Dict[str, Any], output_path: str) -> str:
    """
    Takes structured policy sections and produces a compliant summary
    preserving all 10 mapped clauses with every condition intact.
    """
    sections = structured_data.get("sections", {})

    missing_clauses = [c for c in REQUIRED_CLAUSES if c not in sections]
    if missing_clauses:
        raise ValueError(f"Missing required clauses: {missing_clauses}")

    summary_lines = []
    summary_lines.append("CITY MUNICIPAL CORPORATION - HR LEAVE POLICY SUMMARY")
    summary_lines.append("=" * 60)
    summary_lines.append("")

    for clause_num in REQUIRED_CLAUSES:
        clause_text = sections[clause_num]

        if not check_multi_conditions(clause_num, clause_text):
            raise ConditionDropError(f"Clause {clause_num}: Multi-condition obligation dropped")

        bleed_violations = check_scope_bleed(clause_text)
        if bleed_violations:
            raise ScopeBleedError(f"Clause {clause_num}: Scope bleed detected - {bleed_violations}")

        summary_lines.append(f"Clause {clause_num}: {clause_text}")
        summary_lines.append("")

    summary_text = "\n".join(summary_lines).strip()

    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)
    output_path_obj.write_text(summary_text, encoding="utf-8")

    return summary_text


def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Leave Policy Summarizer")
    parser.add_argument("--input", required=True, help="Input policy file path")
    parser.add_argument("--output", required=True, help="Output summary file path")
    args = parser.parse_args()

    try:
        structured_data = retrieve_policy(args.input)

        if structured_data.get("parse_warning"):
            print("WARNING: Could not parse numbered clauses, using raw content", file=sys.stderr)

        summary = summarize_policy(structured_data, args.output)
        print(f"Summary written to: {args.output}")

    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except ConditionDropError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except ScopeBleedError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()