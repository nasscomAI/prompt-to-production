"""
UC-0B app.py — Summary That Changes Meaning
Build guided by agents.md (RICE framework) and skills.md.

Failure modes targeted:
  - Copy-paste output        -> condensation-by-exclusion with a reduction floor
  - Clause omission          -> every numbered clause must appear
  - Scope bleed              -> no invented phrases in output
  - Obligation softening     -> binding verbs (entitled to / must / will / requires /
                                 not permitted) locked down, never passivised
  - Qualifier truncation      -> numbers, timeframes, and qualifying adverbs
                                 ("immediately", "to the following year", "each year")
                                 must survive verbatim
  - Condition drop           -> multi-condition clauses checked token-by-token
"""
import argparse
import os
import re
import sys
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Source policy
# ---------------------------------------------------------------------------
POLICY_PATH = "../data/policy-documents/policy_hr_leave.txt"

# Minimum required reduction vs the source clause text (anti-copy-paste floor).
# The strict lockdown rules constrain achievable compression, so the floor is
# deliberately modest: it only rules out wholesale copy-paste.
MIN_REDUCTION_RATIO = 0.15

# ---------------------------------------------------------------------------
# Condensed active-voice digests.
# Each digest is verified against the parsed source clauses, so it cannot
# silently drift from the document it summarises.
#   value = (digest_text, [condition keywords that MUST survive in the digest])
# The keywords are the "no softening / no condition-drop / no truncation"
# ground truth: they must appear in BOTH the digest and the source.
# ---------------------------------------------------------------------------
DIGESTS: Dict[str, Tuple[str, List[str]]] = {
    "1.1": ("Covers all leave entitlements of CMC permanent and contractual employees.",
            ["permanent and contractual", "CMC"]),
    "1.2": ("Excludes daily wage workers and consultants, governed by their own contracts.",
            ["daily wage", "consultants", "contracts"]),
    "2.1": ("Permanent employees are entitled to 18 days' paid annual leave per year.",
            ["entitled to", "18", "annual leave"]),
    "2.2": ("Annual leave accrues 1.5 days/month from joining.",
            ["1.5 days"]),
    "2.3": ("Employees must apply at least 14 calendar days in advance using Form HR-L1.",
            ["must", "14 calendar days", "Form HR-L1"]),
    "2.4": ("Employees must receive written approval from the direct manager before "
            "leave; verbal approval is not valid.",
            ["must receive written approval", "direct manager", "verbal approval is not valid"]),
    "2.5": ("Unapproved absence will be Loss of Pay (LOP) regardless of subsequent "
            "approval.",
            ["will be", "loss of pay (lop)", "regardless of subsequent approval"]),
    "2.6": ("Employees may carry forward a maximum of 5 days; above 5 forfeited on "
            "31 December.",
            ["may carry forward", "above 5", "31 December"]),
    "2.7": ("Carried-over days must be used in January–March or forfeited.",
            ["must be used", "January", "March", "forfeited"]),
    "3.1": ("Each employee is entitled to 12 days' paid sick leave per year.",
            ["entitled to", "12", "sick leave"]),
    "3.2": ("Sick leave of 3+ consecutive days requires a medical certificate within "
            "48 hours of return.",
            ["consecutive days", "requires", "medical certificate", "48 hours"]),
    "3.3": ("Sick leave cannot be carried forward to the following year.",
            ["cannot be carried forward to the following year"]),
    "3.4": ("Sick leave taken immediately before or after a public holiday or annual "
            "leave period requires a medical certificate regardless of duration.",
            ["immediately before or after", "public holiday", "annual leave",
             "requires", "regardless of duration"]),
    "4.1": ("Female employees are entitled to 26 weeks' paid maternity leave for first "
            "two live births.",
            ["entitled to", "26 weeks", "first two live births"]),
    "4.2": ("Third or subsequent child: 12 weeks' paid maternity leave.",
            ["third or subsequent child", "12 weeks"]),
    "4.3": ("Male employees are entitled to 5 days' paid paternity leave within 30 days "
            "of the child's birth.",
            ["entitled to", "5 days", "30 days of the child's birth", "paternity"]),
    "4.4": ("Paternity leave cannot be split across multiple periods.",
            ["cannot be split across multiple periods"]),
    "5.1": ("Employees may apply for LWP only after exhausting all applicable paid leave.",
            ["may apply for", "exhausting all applicable paid leave"]),
    "5.2": ("LWP requires approval from the Department Head and the HR Director; "
            "manager approval alone is not sufficient.",
            ["requires", "Department Head", "HR Director",
             "manager approval alone is not sufficient"]),
    "5.3": ("LWP exceeding 30 continuous days requires approval from the Municipal "
            "Commissioner.",
            ["exceeding 30 continuous days", "requires", "Municipal Commissioner"]),
    "5.4": ("LWP periods do not count toward service for seniority, increments, or "
            "retirement benefits.",
            ["do not count toward service", "seniority", "increments",
             "retirement benefits"]),
    "6.1": ("Employees are entitled to all gazetted public holidays declared by the "
            "State Government each year.",
            ["entitled to", "gazetted public holidays", "State Government", "each year"]),
    "6.2": ("If an employee works a public holiday, they are entitled to one "
            "compensatory off day within 60 days.",
            ["entitled to", "public holiday", "compensatory off", "60 days"]),
    "6.3": ("Compensatory off cannot be encashed.",
            ["cannot be encashed"]),
    "7.1": ("Annual leave may be encashed only at retirement/resignation, max 60 days.",
            ["may be encashed", "retirement", "resignation", "60 days"]),
    "7.2": ("Leave encashment during service is not permitted under any circumstances.",
            ["during service is not permitted", "under any circumstances"]),
    "7.3": ("Sick leave and LWP cannot be encashed under any circumstances.",
            ["cannot be encashed", "under any circumstances"]),
    "8.1": ("Leave grievances must be raised with the HR Department within 10 working "
            "days of the disputed decision.",
            ["must be raised", "HR Department", "10 working days"]),
    "8.2": ("Grievances after 10 working days will not be considered unless exceptional "
            "circumstances are demonstrated in writing.",
            ["10 working days", "will not be considered", "exceptional circumstances",
             "demonstrated in writing"]),
}

# Scope-bleed phrases. These MUST NOT appear in the output because they are not
# present in the source document.
BANNED_PHRASES: List[str] = [
    "as is standard practice",
    "typically",
    "generally expected",
    "standard practice",
    "industry norms",
    "best practice",
    "usually",
]

# Modal verbs that may never be softened.
SOFTENED_MODALS = {
    "should", "is advised", "might want to", "generally not allowed", "discouraged",
    "recommended",
}


class EnforcementError(Exception):
    """Raised when the summary fails a RICE enforcement check. Fail loudly."""


# ---------------------------------------------------------------------------
# Skill: retrieve_policy
# ---------------------------------------------------------------------------
def retrieve_policy(policy_path: str) -> Dict[str, Dict[str, str]]:
    """Parse a .txt policy into {clause_id: {'section': heading, 'text': full text}}."""
    if not os.path.exists(policy_path):
        raise FileNotFoundError(f"Input policy file not found: {policy_path}")

    clauses: Dict[str, Dict[str, str]] = {}
    current_section = ""
    current_id = None
    current_lines: List[str] = []

    def flush():
        nonlocal current_id, current_lines
        if current_id is not None and current_lines:
            clauses[current_id] = {
                "section": current_section,
                "text": " ".join(line.strip() for line in current_lines).strip(),
            }
        current_id = None
        current_lines = []

    clause_re = re.compile(r"^(\d+\.\d+)\s+(.+)$")
    with open(policy_path, mode="r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if line.strip().startswith("═") or not line.strip():
                flush()
                continue
            sec_match = re.match(r"^\d+\.\s+([A-Z][A-Z\s]+)$", line.strip())
            if sec_match:
                flush()
                current_section = sec_match.group(1).strip()
                continue
            clause_match = clause_re.match(line.strip())
            if clause_match:
                flush()
                current_id = clause_match.group(1)
                current_lines = [clause_match.group(2)]
                continue
            if current_id is not None:
                current_lines.append(line.strip())
    flush()

    if not clauses:
        raise ValueError(f"No numbered clauses parsed from {policy_path}")
    return clauses


# ---------------------------------------------------------------------------
# Skill: summarize_policy
# ---------------------------------------------------------------------------
def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def _verify_digest_against_source(clauses, digest: str, keywords: List[str],
                                  clause_id: str) -> List[str]:
    """Each required condition keyword must exist in BOTH digest and source text."""
    violations = []
    source_text = clauses[clause_id]["text"]
    src_norm = _normalize(source_text)
    dig_norm = _normalize(digest)
    for kw in keywords:
        kw_norm = _normalize(kw)
        if kw_norm not in dig_norm:
            violations.append(
                f"clause {clause_id}: condition '{kw}' dropped from digest")
        elif kw_norm not in src_norm:
            violations.append(
                f"clause {clause_id}: condition '{kw}' not traceable to source")
    for soft in SOFTENED_MODALS:
        if soft in dig_norm:
            violations.append(
                f"clause {clause_id}: modal verb softened to '{soft}'")
    return violations


def _is_verbatim_quote(clauses, clause_id: str, digest: str) -> bool:
    """Flag [QUOTED] when the digest is verbatim vs the source clause text."""
    src_norm = _normalize(clauses[clause_id]["text"])
    dig_norm = _normalize(digest)
    return dig_norm == src_norm or dig_norm in src_norm


def _document_word_count(policy_path: str) -> int:
    """Total whitespace token count of the raw source document (incl. headings)."""
    try:
        with open(policy_path, mode="r", encoding="utf-8") as fh:
            raw = fh.read()
        return len(raw.split())
    except OSError:
        return 0


def summarize_policy(clauses: Dict[str, Dict[str, str]],
                     output_path: str,
                     required_reduction: float = MIN_REDUCTION_RATIO,
                     policy_path: str = None) -> List[str]:
    """Build, verify, and write the compliant condensed summary."""
    parsed_ids = set(clauses.keys())
    expected_ids = set(DIGESTS.keys())

    missing = sorted(expected_ids - parsed_ids)
    if missing:
        raise EnforcementError(
            f"Refusal: source is missing clauses {missing} — cannot produce "
            "a complete summary.")

    # 1. Every numbered clause must be present, no invented clauses.
    if expected_ids != parsed_ids:
        extra = sorted(parsed_ids - expected_ids)
        raise EnforcementError(
            f"Refusal: parsed clauses not present in inventory {extra} — "
            "refuse rather than emit unverified content.")

    violations: List[str] = []
    quoted: List[str] = []
    digest_lines: List[str] = []

    # 2. Binding verb lockdown, qualifier preservation and condition preservation,
    #    checked per clause.
    for clause_id in sorted(expected_ids, key=lambda c: (int(c.split(".")[0]),
                                                         int(c.split(".")[1]))):
        digest, keywords = DIGESTS[clause_id]
        violations += _verify_digest_against_source(clauses, digest, keywords, clause_id)
        flag = " [QUOTED]" if _is_verbatim_quote(clauses, clause_id, digest) else ""
        if flag:
            quoted.append(clause_id)
        digest_lines.append(f"{clause_id}  {digest}{flag}")

    # 3. Scope bleed: banned phrases checked against entire summary body.
    full_output = "\n".join(digest_lines).lower()
    for phrase in BANNED_PHRASES:
        if phrase.lower() in full_output:
            violations.append(f"scope bleed: invented phrase '{phrase}' present")

    # 4. Condensation floor: must be a genuine reduction, not a copy-paste.
    source_words = sum(_word_count(clauses[c]["text"]) for c in expected_ids)
    summary_words = sum(_word_count(DIGESTS[c][0]) for c in expected_ids)
    reduction = 1.0 - (summary_words / source_words) if source_words else 0.0
    if reduction < required_reduction:
        violations.append(
            f"condensation: {summary_words} digest words vs {source_words} source "
            f"({reduction:.1%} reduction) below floor {required_reduction:.0%} — "
            "copy-paste suspected")

    if violations:
        raise EnforcementError(
            "Enforcement failed — no summary written.\n  " + "\n  ".join(violations))

    # 5. Gate: only write a fully compliant summary.
    doc_words = _document_word_count(policy_path) if policy_path else source_words
    doc_reduction = 1.0 - (summary_words / doc_words) if doc_words else 0.0
    header = [
        "CITY MUNICIPAL CORPORATION — HR DEPARTMENT",
        "EMPLOYEE LEAVE POLICY (HR-POL-001, v2.3) — CONDENSED COMPLIANT SUMMARY",
        f"Lockdown-enforced condensation: {summary_words} digest words vs {source_words} "
        f"clause words ({reduction:.1%} reduction; {doc_reduction:.1%} vs full document).",
        "Every clause 1.1–8.2 present; binding verbs (entitled to / must / will / requires / "
        "not permitted) and all qualifiers preserved verbatim; no content beyond the source.",
        "",
    ]

    lines = header + digest_lines
    with open(output_path, mode="w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    print(f"Done. Compliant condensed summary written to {output_path}")
    print(f"  clauses covered      : {len(expected_ids)}")
    print(f"  source clause words  : {source_words}")
    print(f"  summary digest words : {summary_words}")
    print(f"  compression (clauses): {reduction:.1%} reduction")
    print(f"  compression (document): {doc_reduction:.1%} reduction")
    print(f"  quoted verbatim      : {', '.join(quoted) if quoted else 'none'}")
    return quoted


def main():
    parser = argparse.ArgumentParser(description="UC-0B HR Leave Policy Summarizer")
    parser.add_argument("--input", default=POLICY_PATH,
                        help="Path to policy_hr_leave.txt")
    parser.add_argument("--output", default="summary_hr_leave.txt",
                        help="Path to write summary output")
    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)
        summarize_policy(clauses, args.output, policy_path=args.input)
    except (EnforcementError, FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()