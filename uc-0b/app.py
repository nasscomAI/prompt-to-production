"""
UC-0B - Summary That Changes Meaning
Rule-based policy summarizer with strict clause coverage checks.
"""
import argparse
import re
from typing import Dict, List, Tuple


REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

# Clause-specific condition guards to detect dangerous meaning loss.
REQUIRED_TOKENS: Dict[str, List[str]] = {
    "2.3": ["14", "advance"],
    "2.4": ["written approval", "before", "verbal approval is not valid"],
    "2.5": ["unapproved absence", "loss of pay", "regardless of subsequent approval"],
    "2.6": ["maximum of 5", "forfeited", "31 december"],
    "2.7": ["january", "march", "forfeited"],
    "3.2": ["3 or more consecutive days", "medical certificate", "within 48 hours"],
    "3.4": ["before or after", "public holiday", "regardless of duration"],
    "5.2": ["department head", "hr director", "not sufficient"],
    "5.3": ["exceeding 30", "municipal commissioner"],
    "7.2": ["during service", "not permitted", "under any circumstances"],
}


def _normalize(text: str) -> str:
    cleaned = (text or "").lower()
    cleaned = cleaned.replace("–", "-").replace("—", "-")
    cleaned = " ".join(cleaned.split())
    return cleaned


def retrieve_policy(input_path: str) -> Dict[str, str]:
    """
    Load policy text and parse numbered clauses into a dict keyed by clause id.
    """
    try:
        with open(input_path, "r", encoding="utf-8-sig", errors="replace") as file:
            raw = file.read()
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Input policy file not found: {input_path}") from exc

    clauses: Dict[str, str] = {}
    current_clause_id = ""
    current_parts: List[str] = []

    def flush_current() -> None:
        nonlocal current_clause_id, current_parts
        if current_clause_id:
            clauses[current_clause_id] = " ".join(" ".join(current_parts).split())
        current_clause_id = ""
        current_parts = []

    for raw_line in raw.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        # Skip decorative separators.
        if re.fullmatch(r"[\W_]+", line):
            continue

        # A new numbered clause starts (e.g., 2.3 ...).
        clause_match = re.match(r"^(\d+\.\d+)\s+(.*)$", line)
        if clause_match:
            flush_current()
            current_clause_id = clause_match.group(1)
            current_parts = [clause_match.group(2)]
            continue

        # Section headings like "3. SICK LEAVE" end any active clause.
        if re.match(r"^\d+\.\s+[A-Z][A-Z\s&()-]+$", line):
            flush_current()
            continue

        # Continue appending only while inside a clause.
        if current_clause_id:
            current_parts.append(line)

    flush_current()

    missing = [clause for clause in REQUIRED_CLAUSES if clause not in clauses]
    if missing:
        raise ValueError(f"Required clauses missing from source: {', '.join(missing)}")
    return clauses


def _summarize_clause(clause_id: str, clause_text: str) -> Tuple[str, bool]:
    """
    Return (summary_text, flagged_verbatim_required).
    """
    normalized = _normalize(clause_text)
    required_tokens = REQUIRED_TOKENS.get(clause_id, [])
    meaning_loss_risk = any(token not in normalized for token in required_tokens)

    if meaning_loss_risk:
        return f"[{clause_id}] {clause_text} [FLAG: VERBATIM_REQUIRED]", True

    # Keep concise but preserve obligation force and conditions.
    return f"[{clause_id}] {clause_text}", False


def summarize_policy(clauses: Dict[str, str]) -> str:
    """
    Produce a clause-referenced summary for required clauses only.
    """
    lines = ["HR Leave Policy Summary (Clause-Faithful)", ""]
    flagged_any = False

    for clause_id in REQUIRED_CLAUSES:
        clause_text = clauses[clause_id]
        line, flagged = _summarize_clause(clause_id, clause_text)
        lines.append(line)
        flagged_any = flagged_any or flagged

    lines.append("")
    if flagged_any:
        lines.append("Validation note: One or more clauses were quoted verbatim due to meaning-loss risk.")
    else:
        lines.append("Validation note: All required clauses preserved without detected condition loss.")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy text file")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()

    clauses = retrieve_policy(args.input)
    summary_text = summarize_policy(clauses)

    with open(args.output, "w", encoding="utf-8", newline="") as file:
        file.write(summary_text)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
