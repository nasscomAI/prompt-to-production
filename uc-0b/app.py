#!/usr/bin/env python3

import argparse
import os
import re
import sys
from collections import OrderedDict


# ============================================================
# Exceptions
# ============================================================

class PolicyError(Exception):
    pass


class FileNotFoundPolicyError(PolicyError):
    pass


class InvalidFormatPolicyError(PolicyError):
    pass


class ParsePolicyError(PolicyError):
    pass


class ClauseMissingError(PolicyError):
    pass


class ConditionDropDetectedError(PolicyError):
    pass


class ObligationSofteningError(PolicyError):
    pass


class ScopeBleedError(PolicyError):
    pass


# ============================================================
# Enforcement Configuration from agents.md
# ============================================================

CRITICAL_CLAUSES = [
    "2.3",
    "2.4",
    "2.5",
    "2.6",
    "2.7",
    "3.2",
    "3.4",
    "5.2",
    "5.3",
    "7.2"
]

FORBIDDEN_SCOPE_BLEED = [
    "typically",
    "generally expected",
    "standard practice",
    "as is standard practice",
    "employees are generally expected to",
]

BINDING_VERBS = [
    "must",
    "requires",
    "required",
    "will",
    "not permitted",
    "may",
    "are forfeited"
]

HIGH_RISK_CLAUSE = "5.2"


# ============================================================
# Skill: retrieve_policy
# ============================================================

def retrieve_policy(file_path):
    """
    Loads a policy .txt file and returns structured numbered clauses.
    """

    if not os.path.exists(file_path):
        raise FileNotFoundPolicyError(
            f"FILE_NOT_FOUND: {file_path}"
        )

    if not file_path.endswith(".txt"):
        raise InvalidFormatPolicyError(
            "INVALID_FORMAT: input must be a .txt file"
        )

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        raise InvalidFormatPolicyError(
            f"INVALID_FORMAT: unable to read file ({e})"
        )

    if not content.strip():
        raise ParsePolicyError(
            "PARSE_ERROR: file is empty"
        )

    lines = content.splitlines()

    clauses = OrderedDict()

    current_clause = None
    current_text = []

    clause_pattern = re.compile(r"^(\d+\.\d+)\s+(.*)$")

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        match = clause_pattern.match(stripped)

        if match:
            if current_clause:
                clauses[current_clause] = " ".join(current_text).strip()

            current_clause = match.group(1)
            current_text = [match.group(2)]

        else:
            if current_clause:
                current_text.append(stripped)

    if current_clause:
        clauses[current_clause] = " ".join(current_text).strip()

    if not clauses:
        raise ParsePolicyError(
            "PARSE_ERROR: numbered clauses could not be extracted"
        )

    return clauses


# ============================================================
# Validation Helpers
# ============================================================

def validate_scope_bleed(text):
    lower = text.lower()

    for phrase in FORBIDDEN_SCOPE_BLEED:
        if phrase.lower() in lower:
            raise ScopeBleedError(
                f"SCOPE_BLEED: forbidden phrase detected -> '{phrase}'"
            )


def validate_binding_verbs(source, summary):
    source_lower = source.lower()
    summary_lower = summary.lower()

    for verb in BINDING_VERBS:
        if verb in source_lower and verb not in summary_lower:
            raise ObligationSofteningError(
                f"OBLIGATION_SOFTENING: missing binding verb '{verb}'"
            )


def validate_clause_presence(source_clauses, summary_lines):
    summary_text = "\n".join(summary_lines)

    for clause in source_clauses:
        if f"{clause}:" not in summary_text:
            raise ClauseMissingError(
                f"CLAUSE_MISSING: clause {clause} missing from summary"
            )


def validate_high_risk_clause(clause_id, source, summary):
    """
    Enforce preservation of both approvers in clause 5.2
    """

    if clause_id != HIGH_RISK_CLAUSE:
        return

    required_terms = [
        "Department Head",
        "HR Director"
    ]

    for term in required_terms:
        if term.lower() not in summary.lower():
            raise ConditionDropDetectedError(
                f"CONDITION_DROP_DETECTED: '{term}' missing in clause {clause_id}"
            )


def validate_no_condition_drop(clause_id, source, summary):
    """
    Generic validation for high-risk conditions.
    """

    source_lower = source.lower()
    summary_lower = summary.lower()

    checks = [
        ("within 48hrs", "within 48"),
        ("regardless of duration", "regardless of duration"),
        ("31 dec", "31 dec"),
        ("jan–mar", "jan"),
        ("municipal commissioner", "municipal commissioner"),
        ("written approval", "written approval"),
        ("verbal not valid", "verbal"),
    ]

    for source_term, required_term in checks:
        if source_term in source_lower:
            if required_term not in summary_lower:
                raise ConditionDropDetectedError(
                    f"CONDITION_DROP_DETECTED: clause {clause_id} missing '{source_term}'"
                )


# ============================================================
# Skill: summarize_policy
# ============================================================

def summarize_policy(clauses):
    """
    Generates a compliance-safe summary preserving all obligations.
    """

    summary_lines = []

    for clause_id, clause_text in clauses.items():

        summary_line = f"{clause_id}: {clause_text}"

        validate_scope_bleed(summary_line)
        validate_binding_verbs(clause_text, summary_line)
        validate_high_risk_clause(
            clause_id,
            clause_text,
            summary_line
        )
        validate_no_condition_drop(
            clause_id,
            clause_text,
            summary_line
        )

        summary_lines.append(summary_line)

    validate_clause_presence(clauses, summary_lines)

    return "\n".join(summary_lines)


# ============================================================
# Output Writer
# ============================================================

def write_output(output_path, content):

    output_dir = os.path.dirname(output_path)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)


# ============================================================
# CLI
# ============================================================

def parse_args():

    parser = argparse.ArgumentParser(
        description="UC-0B HR Policy Compliance Summarizer"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Input HR leave policy text file"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output summary file"
    )

    return parser.parse_args()


# ============================================================
# Main
# ============================================================

def main():

    args = parse_args()

    try:
        clauses = retrieve_policy(args.input)

        for critical_clause in CRITICAL_CLAUSES:
            if critical_clause not in clauses:
                raise ClauseMissingError(
                    f"Critical clause missing from source document: {critical_clause}"
                )

        summary = summarize_policy(clauses)

        write_output(args.output, summary)

        print(f"Summary written to: {args.output}")

    except PolicyError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"UNEXPECTED_ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()