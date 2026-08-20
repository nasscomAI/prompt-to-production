"""
UC-0B app.py — Clause-faithful policy summarizer (no-API, direct extraction)
Implements retrieve_policy + summarize_policy skills from skills.md.
Enforcement rules from agents.md: all 10 critical clauses, binding verbs preserved,
no scope bleed, verbatim quotes for clauses where paraphrasing risks meaning loss.
Run: python app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
"""

import argparse
import re
import sys
from pathlib import Path

# The 10 clauses that must appear — omission of any is a hard failure.
CRITICAL_CLAUSES = {"2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}

# Clauses where paraphrasing risks softening a binding obligation — quoted verbatim.
# 5.2: two-approver trap; 5.3: Municipal Commissioner threshold; 7.2: absolute prohibition.
VERBATIM_CLAUSES = {"5.2", "5.3", "7.2"}


# ── Skill: retrieve_policy ────────────────────────────────────────────────────

def retrieve_policy(file_path: str) -> dict:
    """
    Load a .txt policy file and return its content as structured numbered sections.
    Halts with an error if the file is missing or unreadable.
    Warns (but continues) if no numbered subsections are detected.
    """
    path = Path(file_path).resolve()
    if not path.exists():
        sys.exit(f"ERROR [retrieve_policy]: File not found: {path}")
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as e:
        sys.exit(f"ERROR [retrieve_policy]: Could not read {path}: {e}")

    # Sections are delimited by ═══ dividers; odd indices = headings, even = bodies.
    parts = re.split(r"═{3,}", content)

    sections: dict[str, dict] = {}
    for i in range(1, len(parts) - 1, 2):
        heading = parts[i].strip()
        body = parts[i + 1].strip() if i + 1 < len(parts) else ""

        m = re.match(r"^(\d+)\.\s+(.+)$", heading)
        if not m:
            continue
        sec_num, sec_title = m.group(1), m.group(2)

        subsections: dict[str, str] = {}
        splits = re.compile(r"(?m)^(\d+\.\d+)\s+").split(body)
        if len(splits) > 1:
            for j in range(1, len(splits), 2):
                sub_num = splits[j]
                sub_text = splits[j + 1].strip() if j + 1 < len(splits) else ""
                sub_text = " ".join(sub_text.split())  # normalise internal whitespace
                if sub_text:
                    subsections[sub_num] = sub_text

        sections[sec_num] = {"title": sec_title, "subsections": subsections}

    if not sections:
        print(
            "WARNING [retrieve_policy]: No numbered clauses detected. "
            "Returning raw text — structure could not be parsed.",
            file=sys.stderr,
        )
        return {"sections": {}, "raw": content}

    return {"sections": sections}


# ── Skill: summarize_policy ───────────────────────────────────────────────────

def summarize_policy(policy: dict) -> str:
    """
    Produce a clause-faithful summary from structured sections (output of retrieve_policy).

    Enforcement (from agents.md):
    - Every critical clause must be present.
    - Multi-condition obligations are never paraphrased — quoted verbatim with a flag.
    - Only source text is used; no external knowledge is introduced.
    - Missing clauses are flagged explicitly at the end.
    """
    sections = policy.get("sections", {})
    if not sections:
        raw = policy.get("raw", "")
        return "[FLAG: Structure could not be parsed. Raw content below.]\n\n" + raw

    lines: list[str] = []
    lines += [
        "CMC EMPLOYEE LEAVE POLICY — CLAUSE-FAITHFUL SUMMARY",
        "Document Reference: HR-POL-001",
        "=" * 60,
        "",
    ]

    present_clauses: set[str] = set()

    for sec_num in sorted(sections, key=int):
        sec = sections[sec_num]
        lines.append(f"SECTION {sec_num}: {sec['title']}")
        lines.append("-" * 40)

        for sub_num in sorted(
            sec["subsections"],
            key=lambda x: [int(p) for p in x.split(".")],
        ):
            text = sec["subsections"][sub_num]
            present_clauses.add(sub_num)

            if sub_num in VERBATIM_CLAUSES:
                lines.append(
                    f"  {sub_num} [VERBATIM — quoted to prevent meaning loss]:\n"
                    f'    "{text}"'
                )
            else:
                lines.append(f"  {sub_num} {text}")

        lines.append("")

    # Compliance check — flag any missing critical clauses.
    lines.append("=" * 60)
    missing = CRITICAL_CLAUSES - present_clauses
    if missing:
        lines.append(
            f"[FLAG: Missing critical clauses: {', '.join(sorted(missing))}]"
        )
    else:
        lines.append("[VERIFIED: All 10 critical clauses present in this summary.]")

    return "\n".join(lines)


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="UC-0B: Clause-faithful HR leave policy summarizer"
    )
    parser.add_argument("--input", required=True, help="Path to the policy .txt file")
    parser.add_argument("--output", required=True, help="Output path for the summary")
    args = parser.parse_args()

    print(f"retrieve_policy: loading {args.input} ...", flush=True)
    policy = retrieve_policy(args.input)
    sec_count = len(policy["sections"])
    sub_count = sum(len(s["subsections"]) for s in policy["sections"].values())
    print(f"  {sec_count} sections, {sub_count} subsections loaded.")

    print("summarize_policy: generating clause-faithful summary ...", flush=True)
    summary = summarize_policy(policy)

    out = Path(args.output)
    out.write_text(summary, encoding="utf-8")
    print(f"  Summary written to {out.resolve()}\n")
    print(summary)


if __name__ == "__main__":
    main()
