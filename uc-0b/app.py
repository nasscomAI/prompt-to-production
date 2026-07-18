"""
UC-0B — Summary That Changes Meaning
Summarizes HR leave policy preserving every clause, all conditions, and binding verbs.
Strategy: LLM-first (Groq or Gemini) with structured fallback.
"""
import argparse
import os
import re

# ---------------------------------------------------------------------------
# System prompt for LLM (derived from agents.md enforcement rules)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a policy summarization agent for a City Municipal Corporation.
Your job is to summarize HR policy documents with absolute fidelity.

RULES — you must follow every one:
1. Every numbered clause (e.g., 1.1, 2.3, 5.2) in the source must appear in your summary with its clause number. No clause may be silently omitted.
2. Multi-condition obligations must preserve ALL conditions. For example, if a clause requires approval from BOTH Department Head AND HR Director, you must include both approvers. Dropping either is a condition drop.
3. Binding verbs must be preserved exactly: "must" stays "must", "requires" stays "requires", "not permitted" stays "not permitted". Never soften to "should", "is expected to", or "generally not allowed".
4. Do NOT add any information not present in the source document. No phrases like "as is standard practice", "typically in government organisations", or "employees are generally expected to".
5. If a clause cannot be summarised without meaning loss, quote it verbatim and flag it with [VERBATIM].
6. Output format: plain text, grouped by section heading, each clause summarized on its own line prefixed with its clause number.

Return ONLY the summary text. No markdown formatting, no preamble, no commentary."""

# ---------------------------------------------------------------------------
# LLM client initialization (same as UC-0A)
# ---------------------------------------------------------------------------

def _get_llm_client():
    """Try to initialize an LLM client. Priority: Groq > Gemini."""
    try:
        from groq import Groq
        api_key = os.environ.get("GROQ_API_KEY")
        if api_key:
            return Groq(api_key=api_key), "groq"
    except ImportError:
        pass

    try:
        from google import genai
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if api_key:
            return genai.Client(api_key=api_key), "gemini"
    except ImportError:
        pass

    return None, None


# ---------------------------------------------------------------------------
# retrieve_policy — loads and parses the policy file
# ---------------------------------------------------------------------------

def retrieve_policy(input_path: str) -> str:
    """Load policy file and return its content."""
    with open(input_path, "r", encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# summarize_policy — LLM-based summarization
# ---------------------------------------------------------------------------

def summarize_policy_llm(policy_text: str, client, provider: str) -> str:
    """Summarize policy using LLM."""
    prompt = f"Summarize the following policy document faithfully:\n\n{policy_text}"

    try:
        if provider == "groq":
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
            )
            return response.choices[0].message.content.strip()
        else:
            response = client.models.generate_content(
                model="gemini-2.0-flash-lite",
                config={"system_instruction": SYSTEM_PROMPT},
                contents=prompt,
            )
            return response.text.strip()
    except Exception as e:
        print(f"  LLM error: {e}")
        return None


# ---------------------------------------------------------------------------
# summarize_policy — structured fallback (no LLM)
# ---------------------------------------------------------------------------

def summarize_policy_fallback(policy_text: str) -> str:
    """
    Fallback: extract and reproduce every clause with its number.
    Preserves binding verbs and all conditions by keeping clauses near-verbatim.
    """
    lines = policy_text.splitlines()
    sections = []
    current_section = None
    current_clause = []
    current_clause_num = None

    for line in lines:
        stripped = line.strip()

        # Section headers (lines with ═ separators are decorative)
        if stripped.startswith("═"):
            continue

        # Detect section headers (all caps, like "2. ANNUAL LEAVE")
        section_match = re.match(r"^(\d+)\.\s+([A-Z][A-Z\s()]+)$", stripped)
        if section_match:
            # Save previous clause
            if current_clause_num and current_clause:
                sections.append(("clause", current_clause_num, " ".join(current_clause)))
                current_clause = []
                current_clause_num = None
            current_section = stripped
            sections.append(("section", current_section, ""))
            continue

        # Detect clause numbers (e.g., "2.3 Employees must...")
        clause_match = re.match(r"^(\d+\.\d+)\s+(.*)", stripped)
        if clause_match:
            # Save previous clause
            if current_clause_num and current_clause:
                sections.append(("clause", current_clause_num, " ".join(current_clause)))
            current_clause_num = clause_match.group(1)
            current_clause = [clause_match.group(2)]
            continue

        # Continuation of current clause (indented lines)
        if current_clause_num and stripped:
            current_clause.append(stripped)

    # Save last clause
    if current_clause_num and current_clause:
        sections.append(("clause", current_clause_num, " ".join(current_clause)))

    # Build summary
    output_lines = []
    output_lines.append("POLICY SUMMARY — HR-POL-001 Employee Leave Policy")
    output_lines.append("=" * 55)
    output_lines.append("")

    for entry_type, identifier, text in sections:
        if entry_type == "section":
            output_lines.append("")
            output_lines.append(identifier)
            output_lines.append("-" * len(identifier))
        elif entry_type == "clause":
            output_lines.append(f"  {identifier}: {text}")

    return "\n".join(output_lines)


# ---------------------------------------------------------------------------
# Validation — check that critical clauses are present
# ---------------------------------------------------------------------------

CRITICAL_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

CRITICAL_TERMS = {
    "2.3": ["14", "advance", "HR-L1"],
    "2.4": ["written", "verbal"],
    "2.5": ["unapproved", "loss of pay"],
    "2.6": ["5", "carry", "forfeited", "31 december"],
    "2.7": ["january", "march", "forfeited"],
    "3.2": ["3", "medical certificate", "48 hours"],
    "3.4": ["holiday", "medical certificate", "regardless"],
    "5.2": ["department head", "hr director"],
    "5.3": ["30", "municipal commissioner"],
    "7.2": ["not permitted"],
}


def validate_summary(summary: str) -> list:
    """Check summary for missing clauses and dropped conditions."""
    warnings = []
    summary_lower = summary.lower()

    for clause in CRITICAL_CLAUSES:
        if clause not in summary:
            warnings.append(f"MISSING: Clause {clause} not found in summary.")
        else:
            terms = CRITICAL_TERMS.get(clause, [])
            for term in terms:
                if term.lower() not in summary_lower:
                    warnings.append(f"CONDITION DROP: Clause {clause} may be missing '{term}'.")

    return warnings


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summarizer")
    parser.add_argument("--input", required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Path to write summary .txt file")
    args = parser.parse_args()

    # Step 1: Retrieve policy
    policy_text = retrieve_policy(args.input)
    print(f"Loaded policy: {len(policy_text)} characters")

    # Step 2: Summarize
    client, provider = _get_llm_client()
    summary = None

    if client:
        print(f"Using {provider.upper()} (LLM) for summarization.")
        summary = summarize_policy_llm(policy_text, client, provider)

    if not summary:
        if not client:
            print("No LLM available. Using structured fallback.")
        else:
            print("LLM failed. Using structured fallback.")
        summary = summarize_policy_fallback(policy_text)

    # Step 3: Validate
    warnings = validate_summary(summary)
    if warnings:
        print(f"\nValidation warnings ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("Validation passed: all 10 critical clauses and conditions present.")

    # Step 4: Write output
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"\nDone. Summary written to {args.output}")


if __name__ == "__main__":
    main()
