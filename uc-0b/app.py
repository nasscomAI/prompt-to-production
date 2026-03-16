"""
UC-0B app.py — Policy Summarization Agent
Built using agents.md + skills.md enforcement rules.
See README.md for run command and expected behaviour.

Run:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
"""

import argparse
import os
import re
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


# ---------------------------------------------------------------------------
# Skill: retrieve_policy
# ---------------------------------------------------------------------------
def retrieve_policy(file_path: str) -> dict[str, str]:
    """
    Load a .txt policy file and return its content as a dict of
    {clause_number: clause_text} for every numbered section found.

    Raises FileNotFoundError if the file does not exist.
    Raises ValueError if no numbered sections can be detected.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(
            f"[retrieve_policy] File not found: '{file_path}'. "
            "Please provide a valid path to the policy .txt document."
        )

    # Split on clause headings like "2.3", "3.4", "5.2", etc.
    pattern = re.compile(r"(?=\b(\d+\.\d+)\b)", re.MULTILINE)
    positions = [(m.start(), m.group(1)) for m in pattern.finditer(raw)]

    if not positions:
        raise ValueError(
            "[retrieve_policy] No numbered sections (e.g. '2.3', '5.2') found. "
            "Please provide a valid policy document with numbered clauses."
        )

    sections: dict[str, str] = {}
    for i, (pos, clause_id) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(raw)
        sections[clause_id] = raw[pos:end].strip()

    return sections


# ---------------------------------------------------------------------------
# Skill: summarize_policy
# ---------------------------------------------------------------------------
def summarize_policy(sections: dict[str, str]) -> str:
    """
    Takes structured policy sections and produces a compliant summary.

    Enforcement rules (from agents.md):
      1. Every numbered clause must be present in the summary.
      2. Multi-condition obligations must preserve ALL conditions.
      3. Never add information not in the source document.
      4. If a clause cannot be summarised without meaning loss — quote verbatim and flag it.
    """
    clause_list = "\n\n".join(
        f"[Clause {cid}]\n{text}" for cid, text in sorted(sections.items())
    )

    system_prompt = """You are a Policy Summarization Agent.

ROLE: Parse and summarize the HR leave policy document provided. You strictly operate within the bounds of the provided text. Never assume standard practices.

INTENT: Produce a complete and accurate summary where:
- Every numbered clause is preserved with its clause number.
- All multi-condition obligations retain EVERY condition — never drop one silently.
- No external information or assumptions are introduced.

CONTEXT: Use ONLY the contents of the provided policy document. You are explicitly excluded from using general HR knowledge, standardized policies, or arbitrary assumptions not present in the source text.

ENFORCEMENT RULES (non-negotiable):
1. Every numbered clause must appear in the summary.
2. Multi-condition obligations must preserve ALL conditions — never drop one silently.
3. Never add information not present in the source document.
4. If a clause cannot be summarised without meaning loss — quote it verbatim and flag it with [VERBATIM — meaning loss risk].

SCOPE BLEED WARNING: Do NOT use phrases like \"as is standard practice\", \"typically in government organisations\", or \"employees are generally expected to\". Only use language from the source document."""

    user_prompt = f"""Summarize the following HR leave policy clauses according to your enforcement rules.
Each clause must appear in the output with its clause number.

{clause_list}"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
        ),
    )
    return response.text


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="UC-0B — HR Leave Policy Summarization Agent"
    )
    parser.add_argument(
        "--input", required=True, help="Path to the policy .txt file"
    )
    parser.add_argument(
        "--output", required=True, help="Path to write the summary output"
    )
    args = parser.parse_args()

    # Skill 1: retrieve_policy
    print(f"[retrieve_policy] Loading policy from: {args.input}")
    try:
        sections = retrieve_policy(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[retrieve_policy] Found {len(sections)} clause(s): {', '.join(sorted(sections))}")

    # Skill 2: summarize_policy
    print("[summarize_policy] Generating compliant summary...")
    summary = summarize_policy(sections)

    # Write output
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"[done] Summary written to: {args.output}")


if __name__ == "__main__":
    main()
