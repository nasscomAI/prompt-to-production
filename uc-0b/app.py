"""
UC-0B app.py — Summary That Changes Meaning
CRAFT-tested policy summarizer that preserves every clause, condition,
binding verb, and numeric value from the source document.

Run:
    python app.py --input ../data/policy-documents/policy_hr_leave.txt \
                  --output summary_hr_leave.txt

Requires:
    GROQ_API_KEY environment variable
    pip install openai
"""

import argparse
import os
import re
import sys

# ---------------------------------------------------------------------------
# SYSTEM PROMPT — built from agents.md RICE
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a Policy Compliance Summarizer for a municipal HR department.
Your output is used by employees and managers to make binding leave decisions.
An incomplete or softened summary is a compliance failure — not a quality issue.

OPERATIONAL BOUNDARY
Summarize only what is explicitly written in the source document.
Do not infer, extend, or contextualise beyond the text provided.

BANNED PHRASES (scope bleed signals — never use these)
- "as is standard practice"
- "typically in government organisations"
- "employees are generally expected to"
- "in line with common HR norms"
- "it is generally understood that"

BEFORE WRITING THE SUMMARY
1. Read the entire document.
2. Build an internal clause inventory: list every numbered clause ID found.
3. Note the total clause count. This is your completeness target.

WHILE WRITING THE SUMMARY
4. Every numbered clause MUST appear in the summary, identified by its clause number.
   Format each clause as: "Clause X.Y: <summary text>"
5. Multi-condition obligations MUST preserve ALL conditions.
   WRONG: "LWP requires approval"
   RIGHT: "Clause 5.2: LWP requires approval from BOTH the Department Head AND
           the HR Director. Approval from only one is not sufficient."
6. Binding verbs MUST NOT be weakened:
   - must  -> never becomes should / is expected to
   - will  -> never becomes may / might
   - requires -> never becomes recommends / suggests
   - not permitted -> never becomes discouraged / not advised
7. Preserve all numeric values exactly: days, dates, durations, deadlines, limits.
8. Mark every clause containing conditional logic (if / unless / provided that /
   subject to / except when / only if) with [CONDITIONAL].
9. If a clause cannot be summarised without meaning loss, reproduce it verbatim
   and append: [VERBATIM — paraphrase would lose meaning]

AFTER THE SUMMARY
Append a section exactly as follows:

## Completeness Check
| Clause | Present | Conditions Intact |
|--------|---------|-------------------|
| X.Y    | YES/NO  | FULL/CONDITION DROPPED |

Clauses in source: N
Clauses in summary: N
Verdict: PASS (all present, all conditions intact) or FAIL (state reason)"""


# ---------------------------------------------------------------------------
# SKILL: retrieve_policy
# ---------------------------------------------------------------------------

def retrieve_policy(file_path: str) -> dict:
    """
    Load a .txt policy file and return its raw text plus detected clause IDs.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    if not raw_text.strip():
        raise ValueError(
            "Input file is empty — cannot summarise without source content."
        )

    clause_ids = sorted(
        set(re.findall(r"\b(\d+\.\d+)\b", raw_text)),
        key=lambda x: [int(p) for p in x.split(".")]
    )

    if not clause_ids:
        raise ValueError(
            "No numbered clauses found in source. Aborting — "
            "summarising without structure risks silent omission."
        )

    return {
        "raw_text": raw_text,
        "clause_ids": clause_ids,
        "clause_count": len(clause_ids),
    }


# ---------------------------------------------------------------------------
# SKILL: summarize_policy
# ---------------------------------------------------------------------------

def summarize_policy(policy: dict, api_key: str, model: str) -> str:
    """
    Call Groq via the openai-compatible SDK and return the summary text.
    """
    from openai import OpenAI

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )

    user_message = (
        f"Summarize the following HR policy document.\n\n"
        f"Source clause IDs detected: {', '.join(policy['clause_ids'])}\n"
        f"Total clauses to cover: {policy['clause_count']}\n\n"
        f"DOCUMENT:\n{policy['raw_text']}"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
        max_tokens=4096,
        temperature=0.0,
    )

    summary_text = response.choices[0].message.content

    # ------------------------------------------------------------------
    # POST-GENERATION VALIDATION
    # ------------------------------------------------------------------
    missing = [
        cid for cid in policy["clause_ids"]
        if not re.search(rf"\b{re.escape(cid)}\b", summary_text)
    ]

    if missing:
        warning_block = (
            "\n\n## WARNING — MISSING CLAUSES DETECTED\n"
            "The following clause IDs from the source document were NOT found\n"
            "in the summary above. Review before using this output:\n"
            + "\n".join(f"  - Clause {cid}" for cid in missing)
            + "\n\nThis summary has NOT been verified as complete."
        )
        summary_text += warning_block
        print(
            f"\n  WARNING: {len(missing)} clause(s) not found in summary: "
            + ", ".join(missing),
            file=sys.stderr,
        )
    else:
        print(
            f"  All {policy['clause_count']} clause IDs present in summary.",
            file=sys.stderr,
        )

    return summary_text


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: Summarize HR policy documents with clause fidelity."
    )
    parser.add_argument("--input",  required=True, help="Path to source .txt policy document")
    parser.add_argument("--output", required=True, help="Path for output summary .txt file")
    parser.add_argument("--model",  default="llama-3.3-70b-versatile",
                        help="Groq model to use (default: llama-3.3-70b-versatile)")
    args = parser.parse_args()

    # -- API key -------------------------------------------------------
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print(
            "ERROR: GROQ_API_KEY environment variable not set.\n"
            "Set it before running:\n"
            "  PowerShell:  $env:GROQ_API_KEY = \"gsk_...\"\n"
            "  Mac/Linux:   export GROQ_API_KEY=gsk_...",
            file=sys.stderr,
        )
        sys.exit(1)

    # -- SKILL 1: retrieve_policy -------------------------------------
    print(f"Loading: {args.input}", file=sys.stderr)
    try:
        policy = retrieve_policy(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(
        f"Detected {policy['clause_count']} clause(s): "
        + ", ".join(policy["clause_ids"]),
        file=sys.stderr,
    )

    # -- SKILL 2: summarize_policy ------------------------------------
    print(f"Calling {args.model} via Groq ...", file=sys.stderr)
    try:
        summary = summarize_policy(policy, api_key=api_key, model=args.model)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # -- Write output -------------------------------------------------
    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"  Summary written to: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()