"""UC-0B policy summarizer with clause-faithful verification."""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


MISSING_CLAUSE = "MISSING_CLAUSE"
CONDITION_DROP = "CONDITION_DROP"
OBLIGATION_SOFTENING = "OBLIGATION_SOFTENING"
SCOPE_BLEED = "SCOPE_BLEED"

BANNED_SCOPE_PHRASES = [
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
    "typically",
    "generally expected",
]

REQUIRED_CLAUSES = {
    "2.3": {
        "binding": ["must"],
    },
    "2.4": {
        "binding": ["must"],
    },
    "2.5": {
        "binding": ["will"],
    },
    "2.6": {
        "binding": ["may", "forfeited"],
    },
    "2.7": {
        "binding": ["must", "forfeited"],
    },
    "3.2": {
        "binding": ["requires"],
    },
    "3.4": {
        "binding": ["requires"],
    },
    "5.2": {
        "binding": ["requires"],
    },
    "5.3": {
        "binding": ["requires"],
    },
    "7.2": {
        "binding": ["not permitted"],
    },
}


@dataclass
class ClauseRecord:
    clause_id: str
    raw_text: str
    obligation: str
    binding_verbs: List[str]
    conditions: List[str]


@dataclass
class VerificationIssue:
    clause_id: str
    failure_type: str
    details: str


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def is_noise_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if re.fullmatch(r"[═=\-_*]{3,}", stripped):
        return True
    if re.fullmatch(r"\d+\.\s+[A-Z][A-Z\s/&()-]*", stripped):
        return True
    if "════════" in stripped:
        return True
    return False


def extract_numbered_clauses(policy_text: str) -> Dict[str, str]:
    clause_pattern = re.compile(r"(?m)^\s*(\d+\.\d+)\s*[:.)-]?\s*(.*)$")
    matches = list(clause_pattern.finditer(policy_text))
    extracted: Dict[str, str] = {}

    for index, match in enumerate(matches):
        clause_id = match.group(1)
        start_pos = match.start()
        end_pos = matches[index + 1].start() if index + 1 < len(matches) else len(policy_text)
        block = policy_text[start_pos:end_pos].strip()

        lines = block.splitlines()
        if not lines:
            continue

        first_line = re.sub(r"^\s*\d+\.\d+\s*[:.)-]?\s*", "", lines[0]).strip()
        remaining_lines = [line.strip() for line in lines[1:] if not is_noise_line(line)]
        clause_text = "\n".join([first_line] + remaining_lines).strip()
        extracted[clause_id] = clause_text

    return extracted


def extract_binding_verbs(text: str) -> List[str]:
    lowered = text.lower()
    detected = []
    for verb in ["must", "requires", "will", "not permitted", "forfeited", "may"]:
        if verb in lowered:
            detected.append(verb)
    return detected


def extract_conditions(text: str) -> List[str]:
    parts = re.split(r"(?<=[.;])\s+", text)
    markers = ("if", "before", "after", "within", "regardless", "unless", "or", "and")
    conditions: List[str] = []
    for part in parts:
        lowered = part.lower()
        if any(marker in lowered for marker in markers):
            conditions.append(normalize_spaces(part))
    if not conditions:
        conditions.append(normalize_spaces(text))
    return conditions


def retrieve_policy(input_path: Path) -> Dict[str, ClauseRecord]:
    policy_text = input_path.read_text(encoding="utf-8")
    parsed = extract_numbered_clauses(policy_text)
    records: Dict[str, ClauseRecord] = {}

    for clause_id, clause_text in parsed.items():
        normalized_text = normalize_spaces(clause_text)
        records[clause_id] = ClauseRecord(
            clause_id=clause_id,
            raw_text=normalized_text,
            obligation=normalized_text,
            binding_verbs=extract_binding_verbs(normalized_text),
            conditions=extract_conditions(normalized_text),
        )

    return records


def summarize_policy(clauses: Dict[str, ClauseRecord]) -> Dict[str, str]:
    summary_map: Dict[str, str] = {}
    for clause_id in REQUIRED_CLAUSES:
        record = clauses.get(clause_id)
        if record:
            summary_map[clause_id] = f"{clause_id}: {record.raw_text}"
    return summary_map


def verify_summary(summary_map: Dict[str, str], clauses: Dict[str, ClauseRecord]) -> List[VerificationIssue]:
    issues: List[VerificationIssue] = []

    for clause_id, rules in REQUIRED_CLAUSES.items():
        line = summary_map.get(clause_id)
        source_record = clauses.get(clause_id)

        if not source_record:
            issues.append(
                VerificationIssue(
                    clause_id=clause_id,
                    failure_type=MISSING_CLAUSE,
                    details="Required clause not found in source policy.",
                )
            )
            continue

        if not line:
            issues.append(
                VerificationIssue(
                    clause_id=clause_id,
                    failure_type=MISSING_CLAUSE,
                    details="Required clause missing from summary output.",
                )
            )
            continue

        line_lower = line.lower()

        for phrase in BANNED_SCOPE_PHRASES:
            if phrase in line_lower:
                issues.append(
                    VerificationIssue(
                        clause_id=clause_id,
                        failure_type=SCOPE_BLEED,
                        details=f"Contains out-of-scope phrase: '{phrase}'.",
                    )
                )

        for binding_verb in rules["binding"]:
            if binding_verb not in line_lower:
                issues.append(
                    VerificationIssue(
                        clause_id=clause_id,
                        failure_type=OBLIGATION_SOFTENING,
                        details=f"Missing binding force token '{binding_verb}'.",
                    )
                )

        source_text = source_record.raw_text.lower()
        if source_text not in line_lower and "flag_verbatim:" not in line_lower:
            issues.append(
                VerificationIssue(
                    clause_id=clause_id,
                    failure_type=CONDITION_DROP,
                    details="Summary line is not source-faithful and may have dropped conditions.",
                )
            )

        if clause_id == "5.2":
            if "department head" not in line_lower or "hr director" not in line_lower:
                issues.append(
                    VerificationIssue(
                        clause_id=clause_id,
                        failure_type=CONDITION_DROP,
                        details="Clause 5.2 must explicitly include both Department Head and HR Director.",
                    )
                )

    return issues


def regenerate_failed_lines(
    summary_map: Dict[str, str],
    clauses: Dict[str, ClauseRecord],
    issues: List[VerificationIssue],
) -> Dict[str, str]:
    failed_clause_ids = {issue.clause_id for issue in issues}
    rebuilt = dict(summary_map)

    for clause_id in failed_clause_ids:
        record = clauses.get(clause_id)
        if not record:
            continue
        rebuilt[clause_id] = f"{clause_id}: FLAG_VERBATIM: {record.raw_text}"

    return rebuilt


def write_summary(output_path: Path, summary_map: Dict[str, str]) -> None:
    ordered_lines = [summary_map[clause_id] for clause_id in REQUIRED_CLAUSES if clause_id in summary_map]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(ordered_lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="UC-0B legally faithful policy summarizer")
    parser.add_argument("--input", required=True, help="Path to source policy .txt file")
    parser.add_argument("--output", required=True, help="Path to output summary file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        return 1

    clauses = retrieve_policy(input_path)
    summary_map = summarize_policy(clauses)
    issues = verify_summary(summary_map, clauses)

    if issues:
        summary_map = regenerate_failed_lines(summary_map, clauses, issues)
        issues = verify_summary(summary_map, clauses)

    if issues:
        serialized = [issue.__dict__ for issue in issues]
        print(json.dumps(serialized, indent=2), file=sys.stderr)
        return 1

    write_summary(output_path, summary_map)
    print(f"Summary written to: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
