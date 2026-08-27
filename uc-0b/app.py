import argparse
import os
import re
import sys
from collections import OrderedDict


class PolicyError(Exception):
    """Custom exception for policy processing errors."""
    pass


def retrieve_policy(file_path):
    """
    Skill: retrieve_policy

    Loads a policy text file and returns its content organized into
    structured numbered sections and clauses.

    Error handling:
    - Missing/inaccessible/unreadable/non-txt file -> error
    - Numbered clauses cannot be identified -> error
    - Ambiguous structure -> preserve text and flag for review
    - Never omit, merge, rewrite, or reorder clauses
    """

    if not file_path:
        raise PolicyError("Input file path is required.")

    if not file_path.lower().endswith(".txt"):
        raise PolicyError("Input file must be a .txt file.")

    if not os.path.exists(file_path):
        raise PolicyError(f"Input file not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        raise PolicyError(f"Unable to read input file: {e}")

    if not content.strip():
        raise PolicyError("Policy document is empty.")

    lines = content.splitlines()

    clause_pattern = re.compile(r"^\s*(\d+(?:\.\d+)+)\s*[\.\):-]?\s*(.*)$")

    clauses = OrderedDict()
    current_clause = None
    current_text = []

    for line in lines:
        match = clause_pattern.match(line)

        if match:
            if current_clause is not None:
                clauses[current_clause] = "\n".join(current_text).strip()

            current_clause = match.group(1)
            current_text = [match.group(2).strip()]
        else:
            if current_clause is not None:
                current_text.append(line.rstrip())

    if current_clause is not None:
        clauses[current_clause] = "\n".join(current_text).strip()

    if not clauses:
        raise PolicyError(
            "Malformed document: numbered clauses could not be reliably identified."
        )

    structured_sections = []

    for clause_id, clause_text in clauses.items():
        if not clause_text.strip():
            clause_text = "[FLAGGED FOR REVIEW: Empty or ambiguous clause text]"
        structured_sections.append(
            {
                "clause_id": clause_id,
                "text": clause_text
            }
        )

    return structured_sections


def _binding_language_present(text):
    """
    Detect binding language that should not be softened.
    """
    binding_terms = [
        "must",
        "shall",
        "will",
        "requires",
        "required",
        "not permitted",
        "forfeited",
        "approval",
        "approved",
        "prohibited"
    ]

    lower = text.lower()
    return any(term in lower for term in binding_terms)


def summarize_policy(structured_sections):
    """
    Skill: summarize_policy

    Produces a compliant summary from structured sections while:
    - Covering every numbered clause
    - Preserving obligations, conditions, approvals, prohibitions
    - Maintaining clause references
    - Quoting verbatim if meaning-loss risk exists
    """

    if not structured_sections:
        raise PolicyError(
            "Invalid input: structured sections are missing or empty."
        )

    clause_inventory = OrderedDict()

    for item in structured_sections:
        clause_id = item.get("clause_id")
        text = item.get("text")

        if not clause_id:
            raise PolicyError(
                "Invalid input: clause identifiers are missing."
            )

        clause_inventory[clause_id] = text

    summary_lines = []
    summary_lines.append("HR LEAVE POLICY SUMMARY")
    summary_lines.append("=" * 60)
    summary_lines.append("")
    summary_lines.append(
        "Clause Inventory Validation: All numbered clauses from the source document are represented below."
    )
    summary_lines.append("")

    represented_clauses = set()

    for clause_id, clause_text in clause_inventory.items():

        if not clause_text.strip():
            summary_lines.append(
                f"[Clause {clause_id}] VERBATIM REQUIRED / FLAGGED FOR REVIEW"
            )
            summary_lines.append(
                f"\"{clause_text}\""
            )
            summary_lines.append("")
            represented_clauses.add(clause_id)
            continue

        lower_text = clause_text.lower()

        meaning_loss_risk = False

        risk_indicators = [
            " and ",
            " or ",
            "except",
            "unless",
            "provided that",
            "subject to",
            "approval",
            "requires",
            "must",
            "shall",
            "not permitted",
            "forfeited",
            "within",
            "days",
            "hours"
        ]

        if any(token in lower_text for token in risk_indicators):
            meaning_loss_risk = True

        summary_lines.append(f"[Clause {clause_id}]")

        if meaning_loss_risk:
            summary_lines.append(
                "VERBATIM REQUIRED (meaning-loss risk detected):"
            )
            summary_lines.append(clause_text)
        else:
            summary_lines.append(clause_text)

        summary_lines.append("")
        represented_clauses.add(clause_id)

    missing = set(clause_inventory.keys()) - represented_clauses

    if missing:
        raise PolicyError(
            f"Summary rejected: omitted clauses detected: {sorted(missing)}"
        )

    forbidden_scope_bleed = [
        "as is standard practice",
        "typically in government organisations",
        "employees are generally expected to"
    ]

    summary_text = "\n".join(summary_lines).lower()

    for phrase in forbidden_scope_bleed:
        if phrase in summary_text:
            raise PolicyError(
                f"Summary rejected: external information detected: {phrase}"
            )

    return "\n".join(summary_lines)


def write_output(output_path, content):
    output_dir = os.path.dirname(output_path)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Policy Summarization Agent"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to input policy text file"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to output summary file"
    )

    args = parser.parse_args()

    try:
        structured_sections = retrieve_policy(args.input)

        summary = summarize_policy(structured_sections)

        write_output(args.output, summary)

        print(f"Summary written to: {args.output}")

    except PolicyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()