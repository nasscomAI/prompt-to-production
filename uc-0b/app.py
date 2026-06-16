"""
UC-0B — Summary That Changes Meaning
Implements retrieve_policy and summarize_policy per agents.md (RICE) and skills.md.
"""
import argparse
import re

# --- agents.md: enforcement rule 1 — all 10 clauses must be present ---
REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

# --- agents.md: enforcement rule 2 — multi-condition clauses must never be paraphrased ---
# These carry AND-conditions or absolute prohibitions where any paraphrase risks meaning loss
VERBATIM_CLAUSES = {"2.4", "2.5", "5.2", "5.3", "7.2"}

# --- agents.md: enforcement rule 3 — prohibited filler phrases ---
PROHIBITED_PHRASES = [
    "as is standard practice",
    "typically",
    "generally expected to",
    "employees are generally",
    "it is common practice",
    "generally understood",
    "while not explicitly",
]


def retrieve_policy(file_path: str) -> list:
    """
    Load a .txt policy file and return content as a list of structured
    numbered-clause dicts: {clause_id, heading, body}.
    Raises FileNotFoundError if file missing; ValueError if no clauses found.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {file_path}")

    # Match clause lines: e.g. "2.3 Employees must submit..."
    clause_re = re.compile(r'^\s*(\d+\.\d+)\s+(.*)', re.MULTILINE)
    matches = list(clause_re.finditer(raw))

    if not matches:
        raise ValueError(f"No numbered clauses found in: {file_path}")

    sections = []
    for i, match in enumerate(matches):
        clause_id  = match.group(1)
        first_line = match.group(2).strip()

        # Collect continuation lines until the next clause starts
        body_start = match.end()
        body_end   = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        continuation_raw = raw[body_start:body_end]

        continuation_lines = []
        for line in continuation_raw.splitlines():
            stripped = line.strip()
            # Skip blank lines, box-drawing separators, ALL-CAPS section headings,
            # and section-level numbers like "3. SICK LEAVE"
            if not stripped:
                continue
            if re.match(r'^[\u2550=\-─]{3,}', stripped):
                continue
            if re.match(r'^\d+\.\s+[A-Z][A-Z\s\(\)\/]+$', stripped):
                continue
            if re.match(r'^[A-Z][A-Z\s\(\)\/]+$', stripped) and len(stripped) > 4:
                continue
            continuation_lines.append(stripped)

        body = first_line
        if continuation_lines:
            body = first_line + " " + " ".join(continuation_lines)
        body = re.sub(r'\s+', ' ', body).strip()

        sections.append({"clause_id": clause_id, "heading": "", "body": body})

    return sections


def _check_prohibited_phrases(text: str) -> list:
    """Return any prohibited phrases found in text."""
    text_lower = text.lower()
    return [p for p in PROHIBITED_PHRASES if p in text_lower]


def summarize_policy(sections: list, output_path: str):
    """
    Produce a compliant clause-by-clause summary from parsed sections.
    All 10 required clauses must be present; VERBATIM_CLAUSES are quoted
    verbatim and flagged. Raises ValueError if required clauses are missing.
    """
    # Index sections by clause_id
    clause_map = {s["clause_id"]: s for s in sections}

    # --- enforcement rule 1: verify all required clauses are present ---
    missing = [c for c in REQUIRED_CLAUSES if c not in clause_map]
    if missing:
        raise ValueError(
            f"Required clause(s) missing from source document: {', '.join(missing)}"
        )

    lines = []
    lines.append("POLICY SUMMARY — HR Leave Policy (policy_hr_leave.txt)")
    lines.append("=" * 60)
    lines.append("Every clause below is traceable verbatim to the source document.")
    lines.append("VERBATIM_REQUIRED = clause quoted directly; paraphrase risks meaning loss.")
    lines.append("")

    verbatim_count = 0

    for clause_id in REQUIRED_CLAUSES:
        section = clause_map[clause_id]
        body    = section["body"]

        # --- enforcement rule 3: catch any prohibited phrases in source body ---
        found = _check_prohibited_phrases(body)
        if found:
            lines.append(
                f"[{clause_id}] WARNING: prohibited phrase(s) detected in source: {found}"
            )

        if clause_id in VERBATIM_CLAUSES:
            # --- enforcement rule 2: quote verbatim, never paraphrase ---
            lines.append(f"[{clause_id}] {body}")
            lines.append(f"         [flag: VERBATIM_REQUIRED]")
            verbatim_count += 1
        else:
            lines.append(f"[{clause_id}] {body}")

        lines.append("")

    lines.append("=" * 60)
    lines.append(
        f"Summary complete: {len(REQUIRED_CLAUSES)} required clauses present, "
        f"{verbatim_count} flagged VERBATIM_REQUIRED."
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Summarised {len(REQUIRED_CLAUSES)} clauses — "
          f"VERBATIM_REQUIRED flags: {verbatim_count}")


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input",  required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    sections = retrieve_policy(args.input)
    summarize_policy(sections, args.output)
    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
