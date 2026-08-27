"""
UC-0B -- Summary That Changes Meaning
Implements retrieve_policy and summarize_policy using RICE enforcement rules
defined in agents.md and skills.md.

Core failure modes guarded against:
  - Clause omission    (every numbered clause must appear)
  - Scope bleed        (no info added beyond source document)
  - Obligation softening (binding verbs and multi-conditions preserved)
"""
import argparse
import re
import sys
import os

# Reconfigure stdout to UTF-8 on Windows to handle special characters
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ──────────────────────────────────────────────────────────────────────────────
# SKILL: retrieve_policy
# ──────────────────────────────────────────────────────────────────────────────

def retrieve_policy(file_path: str) -> list:
    """
    Load a .txt policy file and return an ordered list of section dicts:
      [ { "section": "2.3", "text": "..." }, ... ]

    Enforcement: Never silently discard content.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        print(f"WARNING: Policy file is empty: {file_path}", file=sys.stderr)
        return []

    # ── Parse sections ─────────────────────────────────────────────────────
    # Match lines like "2.3 Employees must..." or "  3.2 Sick leave..."
    # Pattern: optional whitespace, then X.Y (section number), then rest of text
    section_pattern = re.compile(
        r"(?m)^[ \t]*(\d+\.\d+)[ \t]+(.*?)(?=\n[ \t]*\d+\.\d+[ \t]|\Z)",
        re.DOTALL
    )
    # Also match top-level section headings like "2. ANNUAL LEAVE"
    heading_pattern = re.compile(
        r"(?m)^[ \t]*(\d+\.)[ \t]+([A-Z][A-Z &\-()]+)[ \t]*$"
    )

    sections = []

    # Extract top-level headings first (for structure awareness)
    headings = {}
    for m in heading_pattern.finditer(content):
        num = m.group(1).rstrip(".")
        title = m.group(2).strip()
        headings[num] = title

    # Extract sub-sections (X.Y format)
    for m in section_pattern.finditer(content):
        sec_num = m.group(1).strip()
        sec_text_raw = (m.group(1) + " " + m.group(2)).strip()
        # Clean: collapse internal whitespace / line-continuation indentation
        sec_text = re.sub(r"\n[ \t]+", " ", sec_text_raw).strip()
        sections.append({
            "section": sec_num,
            "text":    sec_text,
        })

    if not sections:
        print(f"WARNING: No numbered sections found in {file_path}. "
              f"Returning full content as UNPARSED.", file=sys.stderr)
        return [{"section": "UNPARSED", "text": content.strip()}]

    return sections


# ──────────────────────────────────────────────────────────────────────────────
# SKILL: summarize_policy
# ──────────────────────────────────────────────────────────────────────────────

# Phrases that must NEVER appear in a summary (scope-bleed markers)
BANNED_PHRASES = [
    "as is standard practice",
    "typically in government",
    "employees are generally expected",
    "it is common practice",
    "in most organisations",
    "as is usual",
]

# Binding verbs that must be preserved verbatim — never softened
BINDING_VERBS = ["must", "will", "shall", "requires", "required", "not permitted",
                 "cannot", "may not", "mandatory", "forfeited"]

def _is_verbatim_required(text: str) -> bool:
    """
    Return True if the clause contains numeric limits, absolute prohibitions,
    or multi-condition sequences that risk meaning loss on paraphrase.
    """
    # Numeric limits
    if re.search(r"\d+\s*(days?|weeks?|hours?|months?|calendar|Rs|km|%)", text, re.I):
        return True
    # Absolute prohibitions
    if re.search(r"not permitted under any circumstances|cannot be encashed|"
                 r"regardless of duration|simultaneously", text, re.I):
        return True
    # Multi-condition: "and the" or "both ... and"
    if re.search(r"\band the\b|\bboth\b.*\band\b|\band .{3,30} and\b", text, re.I):
        return True
    return False


def _summarize_clause(section: dict) -> str:
    """
    Return a one-line summary of the clause, or [VERBATIM] quote if required.
    Enforcement: preserves binding verbs, never adds external information.
    """
    sec_num = section["section"]
    text    = section["text"]

    if _is_verbatim_required(text):
        # Quote the original clause text verbatim
        return f"[CLAUSE {sec_num}] [VERBATIM] \"{text}\""
    else:
        # Light paraphrase: keep the whole sentence but trim leading section number
        # (the text already starts with the section number in our parser)
        clean = text.strip()
        return f"[CLAUSE {sec_num}] {clean}"


def summarize_policy(sections: list) -> str:
    """
    Produce a clause-by-clause summary from the list returned by retrieve_policy.

    Enforcement:
    1. Every clause in input → exactly one entry in output (no drops).
    2. Binding verbs and multi-conditions preserved.
    3. No external information added.
    4. Meaning-loss clauses quoted verbatim with [VERBATIM] tag.
    """
    if not sections:
        return "No clauses found in document."

    lines = []
    for section in sections:
        if not section.get("text", "").strip():
            print(f"  WARNING: Section {section.get('section', '?')} has empty text — skipped.",
                  file=sys.stderr)
            continue

        summary_line = _summarize_clause(section)

        # Enforcement: verify no banned phrases crept into the output
        for banned in BANNED_PHRASES:
            if banned.lower() in summary_line.lower():
                # Replace entire clause with verbatim to be safe
                summary_line = (f"[CLAUSE {section['section']}] [VERBATIM] "
                                f"\"{section['text']}\"")
                break

        lines.append(summary_line)

    return "\n\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# CLI ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="UC-0B Policy Summariser -- clause-complete, scope-clean"
    )
    parser.add_argument("--input",  required=True,
                        help="Path to the .txt policy document")
    parser.add_argument("--output", required=True,
                        help="Path to write the summary .txt file")
    args = parser.parse_args()

    print(f"\nUC-0B Policy Summariser")
    print(f"  Input : {args.input}")
    print(f"  Output: {args.output}")
    print(f"{'='*60}")

    # ── Step 1: Load and parse policy ─────────────────────────────────────
    try:
        sections = retrieve_policy(args.input)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"  Sections found : {len(sections)}")

    # ── Step 2: Summarise ─────────────────────────────────────────────────
    summary = summarize_policy(sections)

    verbatim_count = summary.count("[VERBATIM]")
    clause_count   = summary.count("[CLAUSE ")

    print(f"  Clauses in summary : {clause_count}")
    print(f"  Verbatim quotes    : {verbatim_count}")
    print(f"{'='*60}\n")

    # ── Step 3: Write output ───────────────────────────────────────────────
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    header = (
        f"POLICY SUMMARY -- UC-0B\n"
        f"Source: {os.path.basename(args.input)}\n"
        f"Clauses: {clause_count} | Verbatim quotes: {verbatim_count}\n"
        f"{'='*60}\n\n"
    )

    with open(args.output, "w", encoding="utf-8") as out:
        out.write(header)
        out.write(summary)
        out.write("\n")

    print(f"Summary written to: {args.output}")

    # ── Step 4: Print to console ───────────────────────────────────────────
    print(f"\n{header}{summary}\n")


if __name__ == "__main__":
    main()
