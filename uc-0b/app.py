"""
UC-0B app.py — Policy Summarisation Agent
Uses the RICE framework defined in agents.md to summarise policy documents
while preserving all clauses, conditions, and binding obligations.
"""
import argparse
import os
import re
import sys

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install openai")
    sys.exit(1)


# ─── Skill: retrieve_policy ─────────────────────────────────────────────────
def retrieve_policy(file_path: str) -> list[dict]:
    """
    Loads a .txt policy file and returns its content as structured numbered sections.
    Each section contains clause_number, heading, and text.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")
    if not file_path.endswith(".txt"):
        raise ValueError(f"Expected a .txt file, got: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        raise ValueError(f"Policy file is empty: {file_path}")

    # Split into major sections by the separator line
    sections = []
    current_heading = None
    current_clauses = []

    lines = content.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Detect section headings (lines like "1. PURPOSE AND SCOPE")
        heading_match = re.match(r"^(\d+)\.\s+(.+)$", line)
        if heading_match:
            # Save previous section
            if current_heading and current_clauses:
                sections.append({
                    "heading": current_heading,
                    "clauses": current_clauses
                })
            current_heading = line
            current_clauses = []
            i += 1
            continue

        # Detect clause lines (lines starting with X.Y pattern)
        clause_match = re.match(r"^(\d+\.\d+)\s+(.*)$", line)
        if clause_match:
            clause_num = clause_match.group(1)
            clause_text = clause_match.group(2)
            # Gather continuation lines (indented lines that follow)
            i += 1
            while i < len(lines) and lines[i].startswith("    ") and not re.match(r"^\s*\d+\.\d+", lines[i]):
                clause_text += " " + lines[i].strip()
                i += 1
            current_clauses.append({
                "clause_number": clause_num,
                "text": clause_text.strip()
            })
            continue

        i += 1

    # Don't forget the last section
    if current_heading and current_clauses:
        sections.append({
            "heading": current_heading,
            "clauses": current_clauses
        })

    if not sections:
        raise ValueError("No numbered clauses found in the policy document.")

    return sections


# ─── Skill: summarize_policy ────────────────────────────────────────────────
def summarize_policy(sections: list[dict]) -> str:
    """
    Takes structured policy sections and produces a compliant summary
    using an LLM guided by the RICE enforcement rules.
    """
    # Build the structured input for the LLM
    policy_text = ""
    for section in sections:
        policy_text += f"\n{section['heading']}\n"
        for clause in section["clauses"]:
            policy_text += f"  {clause['clause_number']} {clause['text']}\n"

    system_prompt = """You are a Government Policy Summarisation Agent specialising in HR leave policies for municipal organisations.

Your operational boundary is strictly limited to summarising policy documents clause-by-clause without interpretation, inference, or external knowledge injection. You do not provide legal advice or commentary.

ENFORCEMENT RULES (you must follow ALL of these):
1. Every numbered clause in the source document must appear in the summary — no clause may be silently omitted.
2. Multi-condition obligations must preserve ALL conditions (e.g., if a clause requires approval from BOTH Department Head AND HR Director, you must state both — never reduce to just "requires approval").
3. Never add information, qualifiers, or context not explicitly present in the source document — no scope bleed. Do NOT use phrases like "as is standard practice", "typically in government organisations", or "employees are generally expected to" unless they appear verbatim in the source.
4. Binding verbs (must, will, requires, not permitted) must not be softened to weaker language (should, may, can, generally).
5. If a clause cannot be summarised without meaning loss, quote it verbatim and flag it with [VERBATIM — meaning loss risk].
6. If the input is not a policy document or is unreadable, refuse to summarise and state the reason.

OUTPUT FORMAT:
- Produce a clause-by-clause summary.
- Each entry must reference its source clause number (e.g., "Clause 2.3:").
- Group clauses under their section headings.
- Keep summaries concise but preserve ALL conditions, thresholds, deadlines, and approvers."""

    user_prompt = f"""Summarise the following policy document clause-by-clause. Follow all enforcement rules strictly.

SOURCE DOCUMENT:
{policy_text}"""

    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        client = OpenAI(
            api_key=gemini_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    else:
        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY")
        )
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0
    )

    return response.choices[0].message.content


# ─── Main ────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: Policy Summarisation Agent"
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to the .txt policy document"
    )
    parser.add_argument(
        "--output", required=True,
        help="Path for the output summary file"
    )
    args = parser.parse_args()

    # Check for API key
    if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("GEMINI_API_KEY"):
        print("Error: Neither OPENAI_API_KEY nor GEMINI_API_KEY environment variable is set.")
        print("Set one of them to proceed. E.g.:")
        print("  Set-Item Env:GEMINI_API_KEY \"your-api-key\"  (PowerShell)")
        print("  export GEMINI_API_KEY=your-api-key          (Bash/Zsh)")
        sys.exit(1)

    print(f"[retrieve_policy] Loading: {args.input}")
    try:
        sections = retrieve_policy(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    total_clauses = sum(len(s["clauses"]) for s in sections)
    print(f"[retrieve_policy] Parsed {len(sections)} sections, {total_clauses} clauses")

    print("[summarize_policy] Generating compliant summary...")
    summary = summarize_policy(sections)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"[done] Summary written to: {args.output}")
    print(f"\nVerify: Check all {total_clauses} clauses are present and no conditions were dropped.")


if __name__ == "__main__":
    main()
