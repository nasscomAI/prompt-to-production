"""
UC-0B — Policy Document Summariser
Build this using the RICE → agents.md → skills.md → CRAFT workflow.

Skills implemented:
  1. retrieve_policy  — loads .txt file, returns structured numbered sections
  2. summarize_policy — sends sections to LLM with enforcement rules, returns compliant summary
"""
import argparse
import os
import re
import sys
import time

# pyrefly: ignore [missing-import]
from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
AGENTS_MD_PATH = os.path.join(os.path.dirname(__file__), "agents.md")
with open(AGENTS_MD_PATH, "r", encoding="utf-8") as f:
    SYSTEM_INSTRUCTION = f.read()

MAX_RETRIES = 5
INITIAL_BACKOFF = 15  # seconds

# Scope-bleed phrases that must never appear in a compliant summary
SCOPE_BLEED_PHRASES = [
    "as is standard practice",
    "typically",
    "generally",
    "in most organisations",
    "in most organizations",
    "employees are generally expected to",
    "as is common",
    "it is customary",
    "as per industry norms",
]


# ═══════════════════════════════════════════════════════════════════════════
# Skill 1: retrieve_policy
# ═══════════════════════════════════════════════════════════════════════════
def retrieve_policy(file_path: str) -> list[dict]:
    """
    Load a .txt policy file from disk and return its content as structured
    numbered sections preserving clause numbers and hierarchy.

    Each returned dict contains:
        clause_number : str   — e.g. "2.3"
        heading       : str   — section heading (e.g. "ANNUAL LEAVE"), or ""
        body          : str   — full text of the clause

    Error handling (per skills.md):
      - Invalid / missing / non-.txt → raises SystemExit with the exact path.
      - Empty or no identifiable clauses → returns a single unstructured block
        with a warning printed to stderr.
    """

    # --- Validate path ---
    if not file_path or not isinstance(file_path, str):
        print(f"ERROR: Invalid file path: '{file_path}'", file=sys.stderr)
        sys.exit(1)

    if not file_path.lower().endswith(".txt"):
        print(f"ERROR: Not a .txt file: '{file_path}'", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(file_path):
        print(f"ERROR: File not found: '{file_path}'", file=sys.stderr)
        sys.exit(1)

    # --- Read file ---
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    if not raw_text.strip():
        print(f"ERROR: File is empty: '{file_path}'", file=sys.stderr)
        sys.exit(1)

    # --- Parse into numbered sections ---
    # Pattern matches clause numbers like "1.1", "2.3", "5.2", etc.
    # at the start of a line (possibly after whitespace).
    clause_pattern = re.compile(
        r"^[ \t]*(\d+\.\d+)\s+(.*)", re.MULTILINE
    )

    # First, identify section headings (e.g. "2. ANNUAL LEAVE")
    heading_pattern = re.compile(
        r"^[ \t]*(\d+)\.\s+([A-Z][A-Z &/()]+(?:\([A-Z]+\))?)\s*$", re.MULTILINE
    )
    headings: dict[str, str] = {}
    for m in heading_pattern.finditer(raw_text):
        headings[m.group(1)] = m.group(2).strip()

    # Collect clause matches
    matches = list(clause_pattern.finditer(raw_text))

    if not matches:
        # No identifiable numbered clauses → return raw text as single block
        print(
            f"WARNING: No numbered clauses found in '{file_path}'. "
            "Returning raw text as a single unstructured block.",
            file=sys.stderr,
        )
        return [{"clause_number": "", "heading": "", "body": raw_text.strip()}]

    # Build sections: each clause extends from its start to the next clause
    # (or to the next section separator / end of file)
    sections: list[dict] = []
    for i, m in enumerate(matches):
        clause_num = m.group(1)
        first_line_text = m.group(2).strip()

        # Determine where this clause's body ends
        if i + 1 < len(matches):
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(raw_text)

        # Full body: first line + continuation lines up to end_pos
        full_body_raw = raw_text[m.start():end_pos]
        # Clean: remove the clause number prefix, collapse continuation indent
        body_lines = full_body_raw.strip().splitlines()
        cleaned_lines = []
        for line in body_lines:
            stripped = line.strip()
            # Skip separator lines
            if stripped and set(stripped) <= {"═", "─", "=", "-"}:
                continue
            # Skip section heading lines (e.g. "3. SICK LEAVE")
            if heading_pattern.match(line):
                continue
            cleaned_lines.append(stripped)
        body = " ".join(cleaned_lines)

        # Determine parent section heading
        parent_section = clause_num.split(".")[0]
        heading = headings.get(parent_section, "")

        sections.append({
            "clause_number": clause_num,
            "heading": heading,
            "body": body,
        })

    print(f"  Retrieved {len(sections)} clauses from '{file_path}'.")
    return sections


# ═══════════════════════════════════════════════════════════════════════════
# Skill 2: summarize_policy
# ═══════════════════════════════════════════════════════════════════════════
def summarize_policy(sections: list[dict]) -> str:
    """
    Takes structured numbered sections (from retrieve_policy) and produces
    a compliant clause-by-clause summary using the Gemini model.

    The system instruction (agents.md) contains all enforcement rules:
      - Every numbered clause present
      - Multi-condition obligations preserve ALL conditions
      - No added information / scope bleed
      - Binding verb strength preserved
      - Numeric thresholds exact
      - Named roles exact
      - Deadlines exact
      - Verbatim fallback for complex clauses

    Error handling (per skills.md):
      - Empty / malformed input → raises SystemExit.
      - Scope-bleed detection → strips offending phrases, flags clause.
      - Verbatim fallback handled by the model via enforcement rules.
    """

    # --- Validate input ---
    if not sections:
        print("ERROR: No sections provided to summarize_policy.", file=sys.stderr)
        sys.exit(1)

    # Check for the degenerate "no clauses found" case
    if len(sections) == 1 and sections[0]["clause_number"] == "":
        print(
            "ERROR: Cannot produce a clause-level summary from unstructured text. "
            "Input has no identifiable numbered clauses.",
            file=sys.stderr,
        )
        sys.exit(1)

    # --- Build the prompt from structured sections ---
    prompt_parts = [
        "Below is a municipal HR leave policy document, pre-parsed into numbered sections.",
        "Produce a clause-by-clause summary following ALL enforcement rules in your system instruction.",
        "Each entry must begin with its clause number (e.g., '2.3 —').",
        "",
        "=== POLICY SECTIONS ===",
        "",
    ]
    for section in sections:
        clause = section["clause_number"]
        heading = section["heading"]
        body = section["body"]
        header_line = f"[Clause {clause}]"
        if heading:
            header_line += f" (Section: {heading})"
        prompt_parts.append(header_line)
        prompt_parts.append(body)
        prompt_parts.append("")

    prompt_parts.append("=== END OF POLICY SECTIONS ===")
    prompt_parts.append("")
    prompt_parts.append(
        "Now produce the compliant summary. Remember: every clause must be present, "
        "all conditions preserved, all binding verbs kept at original strength, "
        "no information added, no clause omitted."
    )

    prompt_text = "\n".join(prompt_parts)

    # --- Call Gemini with retry logic ---
    client = genai.Client()
    summary_text = None

    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt_text,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.0,
                ),
            )
            summary_text = response.text
            break
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "503" in error_str or "UNAVAILABLE" in error_str:
                wait_time = INITIAL_BACKOFF * (2 ** attempt)
                print(
                    f"  Rate limited (attempt {attempt + 1}/{MAX_RETRIES}). "
                    f"Waiting {wait_time}s...",
                )
                time.sleep(wait_time)
            else:
                print(f"ERROR: Gemini API call failed: {e}", file=sys.stderr)
                sys.exit(1)

    if summary_text is None:
        print(
            f"ERROR: Failed to get a response after {MAX_RETRIES} retries.",
            file=sys.stderr,
        )
        sys.exit(1)

    # --- Post-processing: scope-bleed detection ---
    flagged_lines: list[str] = []
    cleaned_lines: list[str] = []
    for line in summary_text.splitlines():
        bleed_found = False
        cleaned_line = line
        for phrase in SCOPE_BLEED_PHRASES:
            if phrase.lower() in cleaned_line.lower():
                bleed_found = True
                # Strip the offending phrase (case-insensitive)
                pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                cleaned_line = pattern.sub("", cleaned_line)
                # Collapse double spaces left by removal
                cleaned_line = re.sub(r"  +", " ", cleaned_line).strip()

        if bleed_found:
            # Flag the clause for review
            cleaned_line = cleaned_line.rstrip()
            if cleaned_line:
                cleaned_line += " [SCOPE_BLEED_REMOVED — FLAGGED FOR REVIEW]"
            flagged_lines.append(line)

        cleaned_lines.append(cleaned_line)

    if flagged_lines:
        print("\n  ⚠ Scope bleed detected and removed from the following lines:")
        for fl in flagged_lines:
            print(f"    → {fl.strip()}")

    # --- Completeness check: verify all source clause numbers appear ---
    source_clauses = {
        s["clause_number"] for s in sections if s["clause_number"]
    }
    summary_joined = "\n".join(cleaned_lines)
    missing_clauses = [
        c for c in sorted(source_clauses)
        if c not in summary_joined
    ]
    if missing_clauses:
        print(
            f"\n  ⚠ WARNING: The following clauses may be missing from the summary: "
            f"{', '.join(missing_clauses)}",
            file=sys.stderr,
        )

    return "\n".join(cleaned_lines)


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(
        description="UC-0B — Policy Document Summariser"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the .txt policy file (e.g., ../data/policy-documents/policy_hr_leave.txt)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write the summary output (e.g., summary_hr_leave.txt)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("UC-0B — Policy Document Summariser")
    print("=" * 60)

    # Skill 1: retrieve_policy
    print(f"\n[1/2] Retrieving policy from: {args.input}")
    sections = retrieve_policy(args.input)

    # Skill 2: summarize_policy
    print(f"\n[2/2] Summarising {len(sections)} clauses...")
    summary = summarize_policy(sections)

    # Write output
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"\n✓ Summary written to: {args.output}")
    print(f"  Total clauses processed: {len(sections)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
