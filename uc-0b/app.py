"""
UC-0B app.py

Orchestrates two skills (per skills.md):
  - retrieve_policy: deterministic, non-AI parser that splits a raw policy
    .txt file into an ordered list of numbered clause records.
  - summarize_policy: the only LLM-calling skill. Takes the full ordered
    clause list and produces a compliant, clause-complete summary using
    system_prompt.md (agents.md's rules) as the system prompt.

CLI:
    python app.py --input <path> --output <path>

See README.md for the exact run command and expected behaviour.
"""
import argparse
import os
import re
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

# Matches a clause boundary: a line starting with an <n>.<n> marker, e.g.
# "2.3 Employees must submit ...". Captures the major/minor numbers and
# whatever text follows the marker on that same line.
_CLAUSE_RE = re.compile(r"^(\d+)\.(\d+)\s*(.*)$")

# Matches a single-level section header line, e.g. "2. ANNUAL LEAVE" — a
# single number followed by a dot and a space (no second number group, so
# this never collides with _CLAUSE_RE). Used only to derive a human-readable
# section_heading for each clause; it does not change boundary detection.
_SECTION_RE = re.compile(r"^(\d+)\.\s+(\S.*)$")

# Matches a purely decorative separator line (a row of box-drawing or ASCII
# rule characters used as a section divider, e.g. "════...════" or
# "----..."). Never contributes to any clause's text.
_SEPARATOR_RE = re.compile(r"^[\s=\-_─━═]+$")


def retrieve_policy(input_path):
    """Deterministic, non-AI parser (skills.md: retrieve_policy).

    Splits the raw policy .txt file at `input_path` into an ordered list of
    clause records: {"clause_number": str, "section_heading": str, "text": str}.

    Pure structural transform — no summarization or rewriting. A clause
    boundary is any line starting with an <n>.<n> marker; everything up to
    the next marker belongs to that clause. A stray number that doesn't
    match <n>.<n> (e.g. a section header like "2. ANNUAL LEAVE", a
    decorative separator line, or a blank line) is appended to the current
    clause's text rather than treated as a new boundary; before the first
    clause marker is found, such lines are preamble and are discarded.
    """
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
    except OSError as exc:
        raise OSError(
            f"retrieve_policy: unable to read policy file '{input_path}': {exc}"
        ) from exc

    if not raw_text.strip():
        raise ValueError(f"retrieve_policy: policy file '{input_path}' is empty.")

    lines = raw_text.splitlines()

    clauses = []
    current = None  # dict: clause_number, section_heading, text_lines
    current_section_heading = ""

    def finalize(clause_state):
        return {
            "clause_number": clause_state["clause_number"],
            "section_heading": clause_state["section_heading"],
            "text": "\n".join(clause_state["text_lines"]).strip(),
        }

    for line in lines:
        clause_match = _CLAUSE_RE.match(line)
        if clause_match:
            if current is not None:
                clauses.append(finalize(current))
            major, minor, rest = clause_match.groups()
            current = {
                "clause_number": f"{major}.{minor}",
                "section_heading": current_section_heading,
                "text_lines": [rest] if rest else [],
            }
            continue

        section_match = _SECTION_RE.match(line)
        if section_match:
            current_section_heading = section_match.group(2).strip()
            # Section headers belong to no clause — they set the heading for
            # whichever clause opens next, but must never be appended to the
            # clause that happens to be open when the header line is seen.
            continue

        if _SEPARATOR_RE.match(line):
            # Purely decorative divider line — never contributes to any
            # clause's text, regardless of whether a clause is open.
            continue

        # Any other non-boundary line (blank lines, indented continuation
        # text, stray numbers not matching <n>.<n>) belongs to whatever
        # clause is currently open. Before the first clause marker, there is
        # no open clause, so such lines are preamble and are dropped.
        if current is not None:
            current["text_lines"].append(line)

    if current is not None:
        clauses.append(finalize(current))

    if not clauses:
        raise ValueError(
            f"retrieve_policy: no recognizable clause markers ('<n>.<n>') "
            f"found in '{input_path}'."
        )

    return clauses


def _format_clauses_for_prompt(clause_list):
    """Render the clause list as a numbered, model-readable block."""
    blocks = []
    for clause in clause_list:
        number = clause.get("clause_number", "")
        heading = clause.get("section_heading") or ""
        text = clause.get("text") or ""
        label = f"Clause {number}"
        if heading:
            label += f" ({heading})"
        blocks.append(f"{label}\n{text}")
    return (
        "Below is the full ordered list of numbered clauses parsed from the "
        "source policy document. Produce your summary strictly according to "
        "your system instructions.\n\n" + "\n\n---\n\n".join(blocks)
    )


def summarize_policy(clause_list):
    """The only LLM-calling skill (skills.md: summarize_policy).

    Takes the full ordered clause list from retrieve_policy and produces a
    compressed summary that preserves every clause's obligations,
    conditions, and binding force, enforced at generation time via
    system_prompt.md (agents.md's rules).
    """
    if not clause_list:
        raise ValueError("summarize_policy: input clause list is empty.")

    clause_numbers = []
    for index, clause in enumerate(clause_list):
        number = clause.get("clause_number") if isinstance(clause, dict) else None
        if not number:
            raise ValueError(
                f"summarize_policy: clause at index {index} is missing a "
                f"'clause_number' field; refusing to summarize unstructured input."
            )
        clause_numbers.append(number)

    system_prompt_path = Path(__file__).resolve().parent / "system_prompt.md"
    try:
        system_prompt = system_prompt_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise OSError(
            f"summarize_policy: unable to load system prompt from "
            f"'{system_prompt_path}': {exc}"
        ) from exc

    if not system_prompt.strip():
        raise ValueError(
            f"summarize_policy: system prompt file '{system_prompt_path}' is empty."
        )

    load_dotenv()
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "summarize_policy: ANTHROPIC_API_KEY is not set. Add it to a .env "
            "file at the repo root or export it in the environment."
        )

    user_message = _format_clauses_for_prompt(clause_list)

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=8000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    output_text = "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    )

    if not output_text.strip():
        raise RuntimeError("summarize_policy: model returned an empty response.")

    missing = [number for number in clause_numbers if number not in output_text]
    if missing:
        raise RuntimeError(
            "summarize_policy: generation failed the completeness check — "
            f"the following clause numbers are missing from the output: "
            f"{', '.join(missing)}"
        )

    return output_text


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: deterministically parse an HR leave policy .txt "
        "file into numbered clauses, then produce a clause-complete summary."
    )
    parser.add_argument("--input", required=True, help="Path to the raw policy .txt file.")
    parser.add_argument("--output", required=True, help="Path to write the summary .txt file.")
    args = parser.parse_args()

    try:
        clauses = retrieve_policy(args.input)
        summary = summarize_policy(clauses)

        output_path = Path(args.output)
        output_path.write_text(summary, encoding="utf-8")
        print(f"Wrote summary for {len(clauses)} clauses to {output_path}")
    except Exception as exc:  # surface a clean error instead of a raw traceback
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
