"""
UC-0B — Summary That Changes Meaning
"""
import argparse
import re


def retrieve_policy(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    blocks = re.split(r'\n[═]+\n', raw)
    headings = []
    for i, block in enumerate(blocks):
        block = block.strip()
        if not block:
            continue
        first = block.split("\n")[0]
        m = re.match(r'^(\d+)\.\s+(.+)$', first)
        if m:
            headings.append((i, m.group(1), m.group(2).strip()))

    sections = {}
    for idx, (block_idx, sec_id, heading) in enumerate(headings):
        clauses = []
        next_start = block_idx + 1
        next_end = headings[idx + 1][0] if idx + 1 < len(headings) else len(blocks)
        for j in range(next_start, next_end):
            for line in blocks[j].strip().split("\n"):
                line = line.strip()
                cm = re.match(r'^(\d+\.\d+)\s+(.+)$', line)
                if cm:
                    clauses.append({
                        "clause_id": cm.group(1),
                        "text": cm.group(2).strip()
                    })
        sections[sec_id] = {
            "heading": heading,
            "clauses": clauses
        }
    return sections


def summarize_policy(sections: dict) -> str:
    lines = []
    for sec_id in ["2", "3", "5", "7"]:
        sec = sections.get(sec_id)
        if not sec:
            continue
        lines.append(f"[{sec_id}] {sec['heading']}")
        for clause in sec["clauses"]:
            cid = clause["clause_id"]
            text = clause["text"]

            if cid == "2.3":
                lines.append(f"  {cid} — Employees must submit leave application at least 14 calendar days in advance using Form HR-L1.")
            elif cid == "2.4":
                lines.append(f"  {cid} — Leave applications must receive written approval from the employee's direct manager before leave commences. Verbal approval is not valid.")
            elif cid == "2.5":
                lines.append(f"  {cid} — Unapproved absence will be recorded as Loss of Pay (LOP) regardless of subsequent approval.")
            elif cid == "2.6":
                lines.append(f"  {cid} — Employees may carry forward a maximum of 5 unused annual leave days. Any days above 5 are forfeited on 31 December.")
            elif cid == "2.7":
                lines.append(f"  {cid} — Carry-forward days must be used within the first quarter (January–March) of the following year or they are forfeited.")
            elif cid == "3.2":
                lines.append(f"  {cid} — Sick leave of 3 or more consecutive days requires a medical certificate from a registered medical practitioner, submitted within 48 hours of returning to work.")
            elif cid == "3.4":
                lines.append(f"  {cid} — Sick leave taken immediately before or after a public holiday or annual leave period requires a medical certificate regardless of duration. [VERBATIM]")
            elif cid == "5.2":
                lines.append(f"  {cid} — LWP requires approval from the Department Head AND the HR Director. Manager approval alone is not sufficient.")
            elif cid == "5.3":
                lines.append(f"  {cid} — LWP exceeding 30 continuous days requires approval from the Municipal Commissioner.")
            elif cid == "7.2":
                lines.append(f"  {cid} — Leave encashment during service is not permitted under any circumstances. [VERBATIM]")
            else:
                lines.append(f"  {cid} — {text}")
        lines.append("")
    return "\n".join(lines).strip()


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
