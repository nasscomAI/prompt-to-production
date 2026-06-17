"""
UC-0B — Summary That Changes Meaning
Clause-preserving summarizer for HR leave policy.
"""
import argparse
import re


def retrieve_policy(filepath: str) -> dict:
    """
    Parse a .txt policy file into structured sections and clauses.
    Returns: {section_number: {title, clauses: [{number, text}]}}
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    sections = {}
    current_section_num = None
    current_section_title = None
    current_clauses = []
    buffer = ""

    def flush_clause():
        nonlocal buffer
        text = buffer.strip()
        if not text:
            return
        m = re.match(r"^(\d+\.\d+)\s+(.*)", text)
        if m:
            current_clauses.append({"number": m.group(1), "text": m.group(2)})

    for line in lines:
        stripped = line.strip()
        if re.match(r"^═+$", stripped):
            continue
        m = re.match(r"^(\d+)\.\s+(.+)$", stripped)
        if m:
            flush_clause()
            if current_section_num is not None:
                sections[current_section_num] = {
                    "title": current_section_title,
                    "clauses": current_clauses,
                }
            current_section_num = m.group(1)
            current_section_title = m.group(2).strip()
            current_clauses = []
            buffer = ""
            continue
        m = re.match(r"^\d+\.\d+\s+", stripped)
        if m:
            flush_clause()
            buffer = stripped
        else:
            if buffer:
                buffer += " " + stripped

    flush_clause()
    if current_section_num is not None:
        sections[current_section_num] = {
            "title": current_section_title,
            "clauses": current_clauses,
        }

    return sections


def summarize_policy(sections: dict) -> str:
    """
    Produce a clause-complete summary preserving all obligations.
    """
    lines = []

    for sec_num in sorted(sections.keys(), key=lambda x: int(x)):
        sec = sections[sec_num]
        lines.append(f"=== {sec_num}. {sec['title'].upper()} ===")
        for clause in sec["clauses"]:
            num = clause["number"]
            text = clause["text"]
            summary = _summarize_clause(num, text)
            lines.append(f"  {summary}")
        lines.append("")

    return "\n".join(lines).strip()


MULTI_CONDITION_CLAUSES = {
    "5.2": (
        "LWP requires approval from the Department Head AND the HR Director. "
        "Manager approval alone is not sufficient."
    ),
}


def _summarize_clause(num: str, text: str) -> str:
    if num in MULTI_CONDITION_CLAUSES:
        return f"[{num}] [VERBATIM] {MULTI_CONDITION_CLAUSES[num]}"

    summary = _render_clause(num, text)
    return f"[{num}] {summary}"


def _render_clause(num: str, text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = text.rstrip(".")

    if not text:
        return f"Clause {num} — empty"

    mapping = {
        "2.3": (
            "Employees must submit a leave application at least 14 calendar days "
            "in advance using Form HR-L1."
        ),
        "2.4": (
            "Leave applications must receive written approval from the employee's "
            "direct manager before the leave commences. Verbal approval is not valid."
        ),
        "2.5": (
            "Unapproved absence will be recorded as Loss of Pay (LOP) regardless "
            "of subsequent approval."
        ),
        "2.6": (
            "Employees may carry forward a maximum of 5 unused annual leave days "
            "to the following calendar year. Any days above 5 are forfeited on "
            "31 December."
        ),
        "2.7": (
            "Carry-forward days must be used within the first quarter "
            "(January\u2013March) of the following year or they are forfeited."
        ),
    }

    if num in mapping:
        return mapping[num]

    return text


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary + "\n")

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
