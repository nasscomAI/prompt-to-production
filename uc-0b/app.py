"""
UC-0B app.py — Policy Summariser
Skills: retrieve_policy, summarize_policy
Enforcement: clause completeness, condition preservation, no scope bleed.
"""
import argparse
import os
import re
import sys


# ── Skill: retrieve_policy ────────────────────────────────────────────────────

def retrieve_policy(filepath: str) -> dict[str, str]:
    """
    Load a .txt policy file and return its content as a dict of
    section_number -> section_text, keyed by top-level section header
    (e.g. "1", "2", "3" …).
    Raises FileNotFoundError if the path is invalid.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Policy file not found: {filepath}")

    with open(filepath, encoding="utf-8") as fh:
        raw = fh.read()

    # Split on the decorative separator lines so each section is isolated.
    sections: dict[str, str] = {}
    current_key = "header"
    current_lines: list[str] = []

    for line in raw.splitlines():
        # Detect section separator
        if re.match(r"^[═]{10,}", line):
            continue
        # Detect numbered section heading e.g. "1. PURPOSE AND SCOPE"
        heading_match = re.match(r"^(\d+)\.\s+[A-Z]", line)
        if heading_match:
            if current_lines:
                sections[current_key] = "\n".join(current_lines).strip()
            current_key = heading_match.group(1)
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        sections[current_key] = "\n".join(current_lines).strip()

    return sections


# ── Skill: summarize_policy ───────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are a policy compliance summariser for a government HR department.
Your role is to produce a precise, clause-referenced summary of a leave policy document.

ENFORCEMENT RULES — apply every rule without exception:
1. Every numbered clause in the source document must appear in the summary.
2. Multi-condition obligations must preserve ALL conditions exactly.
   Example: "requires approval from the Department Head AND the HR Director" —
   never reduce to "requires approval".
3. Never add any information not present in the source document.
   Do not use phrases like "as is standard practice", "typically", or "generally".
4. Preserve binding verbs exactly: must / will / requires / may / not permitted.
5. If a clause cannot be summarised without meaning loss, quote it verbatim
   and mark it [VERBATIM].
6. Output format: one bullet per clause, prefixed with the clause number.
   Group by section. Do not merge clauses.
"""

USER_PROMPT_TEMPLATE = """\
Summarise the following leave policy section by section.
Follow all enforcement rules from your system instructions.

POLICY TEXT:
{policy_text}
"""


def summarize_policy(sections: dict[str, str]) -> str:
    """
    Takes structured policy sections and returns a compliant summary string.
    Uses OpenAI chat completions if OPENAI_API_KEY is set; falls back to a
    rule-based verbatim extract so the script always produces output.
    """
    full_text = "\n\n".join(
        f"SECTION {k}:\n{v}" for k, v in sections.items() if k != "header"
    )

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if api_key:
        return _summarize_via_openai(full_text, api_key)

    print(
        "WARNING: OPENAI_API_KEY not set — producing verbatim clause extract.\n"
        "Set the environment variable and re-run to get an AI-generated summary.\n",
        file=sys.stderr,
    )
    return _summarize_verbatim(sections)


def _summarize_via_openai(policy_text: str, api_key: str) -> str:
    """Call OpenAI chat completions and return the model response text."""
    try:
        import openai  # type: ignore
    except ImportError:
        print(
            "ERROR: 'openai' package not installed. Run: pip install openai",
            file=sys.stderr,
        )
        sys.exit(1)

    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(policy_text=policy_text)},
        ],
        temperature=0,
    )
    return response.choices[0].message.content


def _summarize_verbatim(sections: dict[str, str]) -> str:
    """
    Fallback: extract every numbered clause line verbatim from each section.
    Ensures no clause is dropped even without an LLM.
    """
    lines_out: list[str] = ["POLICY SUMMARY (verbatim clause extract)\n"]
    clause_re = re.compile(r"^\s*(\d+\.\d+)\s+(.+)")

    for sec_num, sec_text in sections.items():
        if sec_num == "header":
            continue
        section_header = sec_text.splitlines()[0].strip()
        lines_out.append(f"\n## {section_header}")

        current_clause: str | None = None
        clause_text: list[str] = []

        def flush():
            if current_clause and clause_text:
                full = " ".join(clause_text).strip()
                lines_out.append(f"  • {current_clause}: {full}")

        for line in sec_text.splitlines():
            m = clause_re.match(line)
            if m:
                flush()
                current_clause = m.group(1)
                clause_text = [m.group(2).strip()]
            elif current_clause and line.strip():
                clause_text.append(line.strip())
        flush()

    return "\n".join(lines_out)


# ── CLI entry point ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="UC-0B: Policy Summariser")
    parser.add_argument("--input", required=True, help="Path to the policy .txt file")
    parser.add_argument("--output", required=True, help="Path for the summary output file")
    args = parser.parse_args()

    print(f"Reading policy: {args.input}")
    sections = retrieve_policy(args.input)
    print(f"Loaded {len(sections) - 1} sections.")  # exclude 'header'

    print("Generating summary …")
    summary = summarize_policy(sections)

    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(summary)

    print(f"Summary written to: {args.output}")


if __name__ == "__main__":
    main()

