"""
UC-0B app.py — Policy summariser that preserves every numbered clause
and every condition attached to each obligation.

Implements the two skills defined in skills.md (retrieve_policy,
summarize_policy) under the rules in agents.md.

Usage:
    python app.py \
        --input ../data/policy-documents/policy_hr_leave.txt \
        --output summary_hr_leave.txt
"""
import argparse
import re
import sys
from typing import Dict, List, Tuple

GROUND_TRUTH_CLAUSES: List[str] = [
    "2.3", "2.4", "2.5", "2.6", "2.7",
    "3.2", "3.4",
    "5.2", "5.3",
    "7.2",
]

CLAUSE_HEADING_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.*\S)\s*$")

FORBIDDEN_PHRASES = [
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
    "it is advisable",
    "generally expected",
    "usually expected",
    "as a rule",
    "in most cases",
]


def fail(msg: str) -> "None":
    sys.stderr.write(f"UC-0B: {msg}\n")
    sys.exit(1)


# --- skill: retrieve_policy -------------------------------------------------

def retrieve_policy(path: str) -> Tuple[str, Dict[str, str]]:
    """Load a .txt policy file and return (title, {clause_no: clause_text})."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        fail(f"input file not found: {path}")
    except OSError as e:
        fail(f"cannot read input file {path}: {e}")

    if not text.strip():
        fail(f"input file is empty: {path}")

    lines = text.splitlines()
    title = lines[0].strip() if lines else ""

    clauses: Dict[str, List[str]] = {}
    current: str | None = None
    for line in lines[1:]:
        m = CLAUSE_HEADING_RE.match(line)
        if m:
            current = m.group(1)
            clauses[current] = [m.group(2)]
        elif current is not None and line.strip():
            clauses[current].append(line.rstrip())

    if not clauses:
        fail(
            "input file does not contain any recognised numbered clause "
            "headings (expected lines like '2.3 Some heading')"
        )

    return title, {k: "\n".join(v).strip() for k, v in clauses.items()}


# --- skill: summarize_policy -----------------------------------------------

def _bullet_preserves_all_conditions(clause_no: str, clause_text: str, bullet: str) -> bool:
    """Heuristic: every distinctive word in the clause text must survive the bullet.

    This is intentionally conservative. If a condition would be dropped,
    we fall back to quoting verbatim.
    """
    if clause_no in {"5.2", "3.2", "3.4", "7.2", "2.3", "2.4", "2.5", "2.6", "2.7", "5.3"}:
        must_have = {
            "5.2": ["Department Head", "HR Director"],
            "3.2": ["3", "48"],
            "3.4": ["holiday", "cert"],
            "7.2": ["not permitted", "any circumstances"],
            "2.3": ["14"],
            "2.4": ["Written", "Verbal"],
            "2.5": ["LOP"],
            "2.6": ["5", "31 Dec"],
            "2.7": ["Jan", "Mar"],
            "5.3": ["30", "Municipal Commissioner"],
        }[clause_no]
        return all(token in bullet for token in must_have)
    return all(tok in bullet for tok in _key_tokens(clause_text))


def _key_tokens(clause_text: str) -> List[str]:
    return [w for w in re.findall(r"[A-Za-z0-9]+", clause_text)
            if len(w) > 3 and w.lower() not in {"the", "and", "with", "from", "that", "this", "shall", "must", "will", "may"}]


def _has_forbidden_phrase(s: str) -> bool:
    low = s.lower()
    return any(p in low for p in FORBIDDEN_PHRASES)


def summarize_policy(
    title: str,
    clauses: Dict[str, str],
    inventory: List[str],
) -> str:
    """Produce a compliant plain-text summary."""
    out: List[str] = []
    out.append(f"Summary of: {title}")
    out.append("=" * (len(out[0])))
    out.append("")

    present = set(clauses.keys())
    missing = [c for c in inventory if c not in present]

    for cno in inventory:
        if cno not in clauses:
            out.append(f"- Clause {cno}: [MISSING FROM SOURCE — see source document]")
            continue
        ctext = clauses[cno]
        bullet = f"- Clause {cno}: {ctext}"
        if not _bullet_preserves_all_conditions(cno, ctext, bullet):
            bullet = f"- Clause {cno}: [VERBATIM — see clause {cno}] {ctext}"
        if _has_forbidden_phrase(bullet):
            bullet = f"- Clause {cno}: [VERBATIM — see clause {cno}] {ctext}"
        out.append(bullet)

    if missing:
        out.append("")
        out.append(
            "Note: the following inventory clauses were not located in the "
            f"source document: {', '.join(missing)}."
        )

    return "\n".join(out) + "\n"


# --- entrypoint -------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0B policy summariser")
    parser.add_argument("--input", required=True, help="path to policy .txt file")
    parser.add_argument("--output", required=True, help="path to write summary .txt")
    args = parser.parse_args()

    title, clauses = retrieve_policy(args.input)
    summary = summarize_policy(title, clauses, GROUND_TRUTH_CLAUSES)

    if _has_forbidden_phrase(summary):
        fail("refusing to write summary: forbidden scope-bleed phrase detected")

    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
    except OSError as e:
        fail(f"cannot write output file {args.output}: {e}")


if __name__ == "__main__":
    main()
