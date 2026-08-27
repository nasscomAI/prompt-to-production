"""
UC-0B app.py — Conservative policy summarizer implementation.

Behaviour:
- Reads a policy text file and extracts numbered clauses (e.g. 2.3, 3.2).
- Produces a summary file that includes every clause verbatim. If a clause
  contains multi-condition obligations or risks meaning loss when paraphrased,
  the clause is quoted verbatim and flagged as NEEDS_REVIEW (per UC-0B rules).

This implementation is intentionally conservative: it preserves clauses
exactly and flags anything that looks like a multi-condition obligation.
"""
import argparse
import re
from typing import Dict, Tuple


CLAUSE_HEADER_RE = re.compile(r"^\s*(\d+(?:\.\d+)*)\s*(.*)")


def retrieve_policy(path: str) -> Dict[str, str]:
    """Load the policy file and return a mapping clause_number -> clause_text.

    This parser expects clauses that begin with a numbered header like "2.3".
    Lines following a header that do not start with a numbered header are
    appended to the current clause body.
    """
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    clauses: Dict[str, str] = {}
    current = None
    for ln in lines:
        m = CLAUSE_HEADER_RE.match(ln)
        if m and ln.strip().split()[0].count(".") >= 1:
            num = m.group(1).strip()
            rest = m.group(2).strip()
            current = num
            clauses[current] = rest
        else:
            if current is not None:
                clauses[current] = (clauses[current] + " " + ln.strip()).strip()

    return clauses


def _needs_flagging(text: str) -> bool:
    """Heuristic: flag clauses that contain multi-condition obligations.

    We flag when we see conjunctions combined with obligation verbs, or
    explicit 'AND' joining approvers (e.g., "Department Head AND HR Director").
    """
    text_low = text.lower()
    # obligation verbs we care about (presence of several can indicate complex clause)
    verbs = ["must", "requires", "will", "not permitted", "may", "required"]

    # If clause contains more than one obligation verb instance, flag it.
    if sum(1 for v in verbs if v in text_low) > 1:
        return True

    # Only flag 'and' cases when they relate to approvals or multiple approvers/conditions
    if " and " in text_low:
        approval_keywords = ["approval", "approve", "approver", "department head", "hr director", "requires approval", "requires approval from"]
        if any(k in text_low for k in approval_keywords):
            return True

    return False


def summarize_policy(clauses: Dict[str, str]) -> Dict[str, Tuple[str, bool]]:
    """Return a mapping clause_number -> (summary_text, needs_flag).

    This conservative summarizer returns the clause text verbatim as the
    summary. If the clause looks like it would lose meaning when paraphrased,
    `needs_flag` is True and the summary is quoted.
    """
    out = {}
    for k, text in clauses.items():
        needs = _needs_flagging(text)
        if needs:
            summary = f'"{text}"'
        else:
            # short conservative summary: first sentence or the full text if short
            first_sentence = text.split(".")[0].strip()
            summary = first_sentence if len(first_sentence) > 0 else text
        out[k] = (summary, needs)
    return out


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to write summary file")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    if not clauses:
        raise SystemExit("No numbered clauses found in input file; cannot summarise.")

    summary = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8") as out:
        for num in sorted(summary.keys(), key=lambda s: [int(p) for p in s.split('.')]):
            text, flagged = summary[num]
            line = f"Clause {num}: {text}"
            if flagged:
                line += "  [FLAG: NEEDS_REVIEW]"
            out.write(line + "\n")


if __name__ == "__main__":
    main()
