"""
UC-0B — Result Validator
Validates summary output against RICE enforcement rules from agents.md.
"""
import argparse
import re
import sys

CRITICAL_CLAUSES = {
    "2.3": {
        "keywords": ["14", "advance", "hr-l1"],
        "binding": ["must"],
        "label": "14-day advance notice required",
    },
    "2.4": {
        "keywords": ["written approval", "verbal", "not valid"],
        "binding": ["must"],
        "label": "Written approval required, verbal not valid",
    },
    "2.5": {
        "keywords": ["unapproved absence", "lop", "loss of pay", "regardless"],
        "binding": ["will"],
        "label": "Unapproved absence = LOP regardless of subsequent approval",
    },
    "2.6": {
        "keywords": ["carry forward", "5", "forfeited", "31 december"],
        "binding": ["may", "are forfeited"],
        "label": "Max 5 days carry-forward, above 5 forfeited on 31 Dec",
    },
    "2.7": {
        "keywords": ["carry-forward", "first quarter", "january", "march", "forfeited"],
        "binding": ["must"],
        "label": "Carry-forward days must be used Jan-Mar or forfeited",
    },
    "3.2": {
        "keywords": ["3", "consecutive", "medical certificate", "48"],
        "binding": ["requires"],
        "label": "3+ consecutive sick days requires medical cert within 48hrs",
    },
    "3.4": {
        "keywords": ["before", "after", "holiday", "medical certificate", "regardless"],
        "binding": ["requires"],
        "label": "Sick leave before/after holiday requires cert regardless of duration",
    },
    "5.2": {
        "keywords": ["department head", "hr director"],
        "binding": ["requires"],
        "label": "LWP requires Department Head AND HR Director approval (both required)",
    },
    "5.3": {
        "keywords": ["30", "municipal commissioner"],
        "binding": ["requires"],
        "label": "LWP >30 days requires Municipal Commissioner approval",
    },
    "7.2": {
        "keywords": ["encashment", "during service", "not permitted", "circumstances"],
        "binding": ["not permitted"],
        "label": "Leave encashment during service not permitted under any circumstances",
    },
}

HALLUCINATED_PHRASES = [
    "as is standard practice",
    "typically",
    "generally expected",
    "in most organisations",
    "common practice",
    "standard in",
    "usually",
    "it is customary",
    "as per norms",
]

ALL_CLAUSE_NUMS = [
    "1.1", "1.2", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.1", "3.2", "3.3", "3.4",
    "4.1", "4.2", "4.3", "4.4",
    "5.1", "5.2", "5.3", "5.4",
    "6.1", "6.2", "6.3",
    "7.1", "7.2", "7.3",
    "8.1", "8.2",
]


def validate(output_path: str, input_path: str) -> bool:
    errors = []

    try:
        with open(output_path, "r", encoding="utf-8") as f:
            summary = f.read()
    except Exception as e:
        print(f"FAIL: Could not read summary file: {e}")
        return False

    if not summary.strip():
        print("FAIL: Summary file is empty")
        return False

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception as e:
        print(f"FAIL: Could not read input file: {e}")
        return False

    summary_lower = summary.lower()

    # 1. Check all numbered clauses appear in summary
    for cn in ALL_CLAUSE_NUMS:
        pattern = rf"\[{re.escape(cn)}\]"
        if not re.search(pattern, summary):
            errors.append(f"Clause [{cn}] is missing from the summary")

    # 2. Check critical clauses have correct obligations
    for cn, spec in CRITICAL_CLAUSES.items():
        clause_pattern = rf"\[{re.escape(cn)}\]"
        clause_match = re.search(clause_pattern, summary)
        if not clause_match:
            continue
        start = clause_match.start()
        end = min(start + 400, len(summary))
        context = summary_lower[start:end]

        for kw in spec["keywords"]:
            if kw not in context:
                errors.append(
                    f"Clause [{cn}] ({spec['label']}): missing keyword '{kw}'"
                )

        for bv in spec["binding"]:
            if bv not in context:
                errors.append(
                    f"Clause [{cn}] ({spec['label']}): binding verb '{bv}' missing"
                )

    # 3. Check multi-condition obligation: 5.2 must name BOTH approvers
    clause_52_match = re.search(r"\[5\.2\].*?(?=\[\d+\.\d+\]|\Z)", summary, re.DOTALL)
    if clause_52_match:
        ctx_52 = clause_52_match.group(0).lower()
        has_dept_head = "department head" in ctx_52
        has_hr_director = "hr director" in ctx_52
        if not has_dept_head and not has_hr_director:
            errors.append(
                "Clause [5.2]: neither 'Department Head' nor 'HR Director' found. "
                "Both approvers must be named."
            )
        elif not has_dept_head:
            errors.append(
                "Clause [5.2]: 'Department Head' missing. "
                "Both Department Head AND HR Director approval required."
            )
        elif not has_hr_director:
            errors.append(
                "Clause [5.2]: 'HR Director' missing. "
                "Both Department Head AND HR Director approval required."
            )

    # 4. Check for hallucinated phrases
    for phrase in HALLUCINATED_PHRASES:
        if phrase in summary_lower:
            errors.append(
                f"Hallucinated phrase detected: '{phrase}'. "
                "Summary must not add information not in the source."
            )

    # 5. Check no prose outside clause references in key sections
    for cn in ["5.2", "5.3", "7.2"]:
        if cn not in summary:
            continue

    if not errors:
        print(f"PASS: Summary validated successfully ({len(ALL_CLAUSE_NUMS)} clauses checked)")
        return True

    print(f"FAIL: {len(errors)} validation error(s):")
    for err in errors:
        print(f"  - {err}")
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0B Result Validator")
    parser.add_argument("--output", required=True, help="Path to summary output file")
    parser.add_argument("--input", required=True, help="Path to original policy file")
    args = parser.parse_args()

    success = validate(args.output, args.input)
    sys.exit(0 if success else 1)
