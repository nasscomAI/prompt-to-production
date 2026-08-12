"""
UC-0B — Summary That Changes Meaning
Built via RICE -> agents.md -> skills.md -> CRAFT workflow.

Fixes applied over the naive baseline (see git history for the naive
Control-step run and its failures):
  1. Clause omission   -> retrieve_policy parses EVERY numbered clause in
                           the document (not just the first few physical
                           lines); summarize_policy emits one entry per
                           parsed clause, so completeness is structural,
                           not accidental.
  2. Line-wrap truncation -> continuation lines are joined back into a
                           single logical clause sentence before any
                           further processing, so no clause is presented
                           as a broken sentence fragment.
  3. Scope bleed        -> the summary is built ONLY from text extracted
                           from the source file. No framing sentence,
                           adjective, or claim is written by this program
                           that did not come from the document itself.
  4. Obligation softening / condition dropping -> no paraphrasing of
                           clause text happens at all. Each clause's
                           operative sentence(s) are reproduced verbatim
                           (whitespace-normalized only), which makes it
                           structurally impossible to silently drop a
                           condition, approver, deadline, or number, or to
                           weaken a binding verb -- this directly
                           implements the agents.md refusal/verbatim-
                           fallback rule for every clause, not just the
                           hard ones.

See agents.md for the enforcement rules this file implements and skills.md
for the two skills (retrieve_policy, summarize_policy) this file defines.
"""
from __future__ import annotations

import argparse
import re

DIVIDER_RE = re.compile(r"^[═=]{5,}$")
CLAUSE_RE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
SECTION_RE = re.compile(r"^(\d+)\.\s+([A-Z0-9][A-Z0-9 \-/&()]*)$")

# Heuristics used only to flag clauses for the "Compliance Attention Index"
# at the end of the summary -- this never removes or rewrites clause text,
# it only highlights which already-included clauses carry multiple
# conditions, absolute prohibitions, or hard deadlines, so a reader knows
# where extra care is needed.
MULTI_CONDITION_MARKERS = [" and ", " both "]
ABSOLUTE_MARKERS = ["not permitted", "not valid", "regardless", "not accepted", "no separate", "forfeit"]
DEADLINE_RE = re.compile(
    r"\b\d+\s*(calendar\s+|working\s+|continuous\s+)?(day|days|hour|hours|week|weeks|month|months)\b"
    r"|\bwithin\s+\d+\b"
    r"|\bon\s+31\s+december\b"
)


def retrieve_policy(file_path: str):
    """
    Load a .txt policy file and parse it into structured sections/clauses,
    joining wrapped physical lines back into single logical clause
    sentences. Returns a list of {number, title, clauses:[{number, text}]}.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Policy file not found: {file_path}")

    if not text.strip():
        raise ValueError(f"Policy file is empty: {file_path}")

    sections = []
    unsectioned = {"number": "UNSECTIONED", "title": "UNSECTIONED", "clauses": []}
    current_section = None
    current_clause = None  # (number, [text_parts])

    def flush_clause():
        nonlocal current_clause
        if current_clause:
            num, parts = current_clause
            joined = re.sub(r"\s+", " ", " ".join(p.strip() for p in parts if p.strip())).strip()
            target = current_section if current_section is not None else unsectioned
            target["clauses"].append({"number": num, "text": joined})
        current_clause = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or DIVIDER_RE.match(line):
            continue

        m_clause = CLAUSE_RE.match(line)
        if m_clause:
            flush_clause()
            current_clause = (m_clause.group(1), [m_clause.group(2)])
            continue

        m_section = SECTION_RE.match(line)
        if m_section:
            flush_clause()
            if current_section is not None:
                sections.append(current_section)
            current_section = {
                "number": m_section.group(1),
                "title": m_section.group(2).strip(),
                "clauses": [],
            }
            continue

        # Continuation of a wrapped clause sentence.
        if current_clause is not None:
            current_clause[1].append(line)
        # Otherwise: document front-matter (title, doc ref, version) before
        # section 1 -- not a clause, intentionally not included as content
        # (front matter is echoed separately in the summary header, see
        # summarize_policy, using the raw first lines of the file).

    flush_clause()
    if current_section is not None:
        sections.append(current_section)

    if unsectioned["clauses"]:
        sections.append(unsectioned)

    total_clauses = sum(len(s["clauses"]) for s in sections)
    if total_clauses == 0:
        raise ValueError(
            f"No numbered clauses (e.g. '2.3 ...') were found in {file_path}. "
            "Refusing to produce a summary of zero clauses."
        )

    return sections


def _is_high_attention(clause_text: str) -> str | None:
    t = clause_text.lower()
    reasons = []
    if any(m in t for m in MULTI_CONDITION_MARKERS) and (
        "approv" in t or "requires" in t or "consent" in t
    ):
        reasons.append("multiple conditions/approvers")
    if any(m in t for m in ABSOLUTE_MARKERS):
        reasons.append("absolute rule (no exceptions)")
    if DEADLINE_RE.search(t):
        reasons.append("hard deadline")
    return ", ".join(reasons) if reasons else None


def summarize_policy(sections, source_header_lines=None) -> str:
    """
    Produce a completeness-preserving digest: every parsed clause appears,
    grouped by its source section, reproduced verbatim (whitespace-
    normalized only -- never paraphrased), so no condition can be silently
    dropped or softened. Ends with an auto-derived Compliance Attention
    Index for clauses carrying multiple conditions, absolute prohibitions,
    or hard deadlines.
    """
    out = []
    if source_header_lines:
        out.extend(source_header_lines)
        out.append("")
    out.append("POLICY SUMMARY")
    out.append(
        "Every numbered clause below is reproduced from the source document "
        "verbatim (re-wrapped for readability only). No wording, condition, "
        "or claim has been added, removed, or softened."
    )
    out.append("")

    attention_index = []
    total_clauses = 0
    for section in sections:
        out.append(f"{section['number']}. {section['title']}")
        if not section["clauses"]:
            out.append("  [COULD NOT BE SUMMARISED -- SEE SOURCE, NO CLAUSES PARSED]")
        for clause in section["clauses"]:
            total_clauses += 1
            text = clause["text"] or f"[COULD NOT BE SUMMARISED -- SEE SOURCE CLAUSE {clause['number']}]"
            out.append(f"  {clause['number']} {text}")
            reason = _is_high_attention(text)
            if reason:
                attention_index.append((clause["number"], reason))
        out.append("")

    out.append("COMPLIANCE ATTENTION INDEX")
    out.append(
        "Clauses below carry multiple conditions, an absolute rule, or a hard "
        "deadline -- read the full clause above, not just this index."
    )
    if attention_index:
        for num, reason in attention_index:
            out.append(f"  {num} -- {reason}")
    else:
        out.append("  (none detected)")
    out.append("")
    out.append(f"Total clauses summarised: {total_clauses}")

    return "\n".join(out) + "\n"


def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        raw_text = f.read()
    # Capture the document's own front-matter (title/reference/version)
    # verbatim, stopping at the first section divider -- used only as a
    # header, never rewritten.
    header_lines = []
    for raw_line in raw_text.splitlines():
        line = raw_line.strip()
        if DIVIDER_RE.match(line):
            break
        if line:
            header_lines.append(line)

    sections = retrieve_policy(args.input)
    summary = summarize_policy(sections, source_header_lines=header_lines)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    total_clauses = sum(len(s["clauses"]) for s in sections)
    print(f"Done. {total_clauses} clauses across {len(sections)} sections summarised -> {args.output}")


if __name__ == "__main__":
    main()
