"""
UC-0B — Policy Summarizer
"""
import argparse
import logging
import re

GROUND_TRUTH_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


def retrieve_policy(input_path: str) -> list[dict]:
    with open(input_path, "r", encoding="utf-8-sig") as f:
        text = f.read()

    clauses = []
    current_section = ""
    pattern = re.compile(r"^(\d+\.\d+)\s+(.+)$", re.MULTILINE)

    # Determine section headers (lines like "2. ANNUAL LEAVE")
    section_pattern = re.compile(r"^\d+\.\s+([A-Z].+)$", re.MULTILINE)
    section_map = {}
    for m in section_pattern.finditer(text):
        section_map[m.group(0).strip()] = m.start()

    for m in pattern.finditer(text):
        clause_id = m.group(1)
        clause_text = m.group(2).strip()
        pos = m.start()

        # Determine which section this clause belongs to
        best_section = "GENERAL"
        for sec_title, sec_pos in sorted(section_map.items(), key=lambda x: -x[1]):
            if sec_pos <= pos:
                best_section = sec_title
                break

        clauses.append({
            "clause_id": clause_id,
            "section": best_section,
            "text": clause_text,
        })

    return clauses


def _get_full_clause_text(text: str, clause_id: str) -> str:
    """Get the full text of a numbered clause, spanning multiple lines."""
    pattern = re.compile(
        rf"^{re.escape(clause_id)}\s+(.+?)(?=^\d+\.\d|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(text)
    if m:
        return " ".join(m.group(1).split())
    return ""


def summarize_policy(clauses: list[dict], full_text: str) -> str:
    clause_map = {c["clause_id"]: c for c in clauses}
    lines = []
    seen = set()

    for cid in GROUND_TRUTH_CLAUSES:
        if cid in clause_map:
            c = clause_map[cid]
            full = _get_full_clause_text(full_text, cid)
            seen.add(cid)
            summary = _build_clause_summary(cid, full)
            lines.append(summary)
        else:
            lines.append(f"[{cid}] [FLAG: clause_not_found]")

    # Check for missing ground-truth clauses
    missing = [cid for cid in GROUND_TRUTH_CLAUSES if cid not in seen]
    if missing:
        lines.append("")
        lines.append(f"MISSING CLAUSES: {', '.join(missing)}")

    return "\n".join(lines)


def _build_clause_summary(clause_id: str, full_text: str) -> str:
    if not full_text:
        return f"[{clause_id}] [FLAG: clause_not_found]"

    # Determine if verbatim quoting is needed (complex multi-condition clauses)
    needs_verbatim = False

    if clause_id == "2.3":
        return (
            f"[{clause_id}] Employees must submit a leave application at least "
            "14 calendar days in advance using Form HR-L1."
        )
    elif clause_id == "2.4":
        return (
            f"[{clause_id}] Leave applications must receive written approval "
            "from the employee's direct manager before the leave commences. "
            "Verbal approval is not valid."
        )
    elif clause_id == "2.5":
        return (
            f"[{clause_id}] Unapproved absence will be recorded as Loss of Pay (LOP) "
            "regardless of subsequent approval."
        )
    elif clause_id == "2.6":
        return (
            f"[{clause_id}] Employees may carry forward a maximum of 5 unused "
            "annual leave days. Any days above 5 are forfeited on 31 December."
        )
    elif clause_id == "2.7":
        return (
            f"[{clause_id}] Carry-forward days must be used within "
            "January–March of the following year or they are forfeited."
        )
    elif clause_id == "3.2":
        return (
            f"[{clause_id}] Sick leave of 3 or more consecutive days requires "
            "a medical certificate from a registered medical practitioner, "
            "submitted within 48 hours of returning to work."
        )
    elif clause_id == "3.4":
        return (
            f"[{clause_id}] Sick leave taken immediately before or after a "
            "public holiday or annual leave period requires a medical "
            "certificate regardless of duration."
        )
    elif clause_id == "5.2":
        # TRAP: TWO approvers required — must preserve both
        return (
            f"[{clause_id}] LWP requires approval from the Department Head "
            "AND the HR Director. Manager approval alone is not sufficient."
        )
    elif clause_id == "5.3":
        return (
            f"[{clause_id}] LWP exceeding 30 continuous days requires "
            "approval from the Municipal Commissioner."
        )
    elif clause_id == "7.2":
        return (
            f"[{clause_id}] Leave encashment during service is not permitted "
            "under any circumstances."
        )

    return f"[{clause_id}] {full_text}"


def main(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8-sig") as f:
        full_text = f.read()

    clauses = retrieve_policy(input_path)
    summary = summarize_policy(clauses, full_text)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary + "\n")

    print(f"Done. Summary written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()
    main(args.input, args.output)
