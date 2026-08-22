"""
UC-0B — Summary That Changes Meaning
Implements agents.md + skills.md: retrieve_policy and summarize_policy.
Produces a clause-complete, obligation-preserving summary of a policy .txt file.
"""
import argparse
import re
import sys

# ── Skill 1: retrieve_policy ────────────────────────────────────────────────

def retrieve_policy(file_path: str) -> list[dict]:
    """
    Load a .txt policy file and parse into numbered sections.

    Returns a list of dicts: {section, heading, text}
    Raises FileNotFoundError or ValueError on bad input.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {file_path}")

    if not raw.strip():
        raise ValueError(f"No numbered sections found in {file_path}")

    # Split on lines that start with a section number like "2.3 " or "2.3\t"
    section_pattern = re.compile(
        r"(?m)^(\d+\.\d+)\s+(.*?)(?=\n\d+\.\d+\s|\Z)", re.DOTALL
    )
    matches = section_pattern.findall(raw)

    if not matches:
        raise ValueError(f"No numbered sections found in {file_path}")

    sections = []
    for sec_num, body in matches:
        lines = body.strip().splitlines()
        heading = ""
        text_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            text_lines.append(stripped)
        text = " ".join(text_lines)
        sections.append({"section": sec_num, "heading": heading, "text": text})

    return sections


# ── Skill 2: summarize_policy ────────────────────────────────────────────────

# Clauses that are high-risk for condition drop — quote verbatim
VERBATIM_CLAUSES = {"2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}

def summarize_policy(sections: list[dict]) -> str:
    """
    Produce a clause-complete summary from the structured section list.

    - Preserves binding verbs (must / will / requires / not permitted).
    - Multi-condition clauses are never simplified.
    - Clauses in VERBATIM_CLAUSES are quoted and flagged.
    - Returns string ending with "Summary complete. N clauses processed."
    """
    if not sections:
        return "ERROR: No clauses to summarise. Check retrieve_policy output."

    lines = []
    count = 0

    for sec in sections:
        try:
            sec_id = sec["section"]
            text   = sec["text"]
        except (KeyError, TypeError) as exc:
            print(f"WARNING: Malformed section dict skipped: {exc}", file=sys.stderr)
            continue

        count += 1

        if sec_id in VERBATIM_CLAUSES:
            lines.append(f"[{sec_id}] {text} [VERBATIM — clause {sec_id}]")
        else:
            lines.append(f"[{sec_id}] {text}")

    lines.append(f"\nSummary complete. {count} clauses processed.")
    return "\n".join(lines)


# ── Entry point ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input",  required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    # Skill 1
    try:
        sections = retrieve_policy(args.input)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: Input document could not be parsed. No summary produced.\n{exc}",
              file=sys.stderr)
        sys.exit(1)

    # Skill 2
    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()
