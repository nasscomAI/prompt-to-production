"""
UC-0B app.py — Summary That Changes Meaning
Implements retrieve_policy and summarize_policy skills as defined in skills.md.
Agent behaviour enforced via system prompt as defined in agents.md.
Uses Amazon Bedrock (Claude) for LLM-backed summarisation.
"""
import argparse
import re
import json
import boto3

# ---------------------------------------------------------------------------
# AWS Bedrock configuration
# ---------------------------------------------------------------------------
AWS_ACCESS_KEY_ID     = "AKIA5FTZFLDKOFXLXKHQ"
AWS_SECRET_ACCESS_KEY = "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"
AWS_REGION            = "us-east-1"
BEDROCK_MODEL_ID      = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

# Clauses that MUST appear in the output (from agents.md enforcement rule 1)
REQUIRED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]

# ---------------------------------------------------------------------------
# System prompt derived strictly from agents.md (RICE)
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a policy summarisation agent. Your operational boundary is to produce a faithful, clause-by-clause summary of an HR policy document. You must not infer, generalise, or add any information that is not explicitly stated in the source document.

INTENT:
Produce a verifiable summary of the HR leave policy where:
- Every numbered clause is present and cited by its exact clause number.
- All binding obligations are preserved verbatim in meaning.
- Multi-condition rules retain ALL conditions (e.g. clause 5.2 requires BOTH Department Head AND HR Director approval — dropping either approver is a condition drop and is prohibited).
- No external information is introduced.

CONTEXT — WHAT YOU MAY USE:
Only the content of the policy document provided to you. You must not use general HR knowledge, government norms, or any information outside the source document.

PROHIBITED PHRASES (scope bleed — these do not exist in the source):
- "as is standard practice"
- "typically in government organisations"
- "employees are generally expected to"
- Any generalisation not explicitly in the document.

ENFORCEMENT RULES (never violate these):
1. Every numbered clause (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) must appear in the summary with its clause number cited exactly.
2. Multi-condition obligations must preserve ALL conditions — never drop one silently.
3. Never add any information not explicitly stated in the source document.
4. If a clause cannot be summarised without loss of meaning, quote it verbatim and prefix it with "VERBATIM QUOTE:".

OUTPUT FORMAT:
Produce a structured plain-text summary. For each clause group, begin with the section heading, then list each clause on its own line starting with its number. Example:

SECTION 2 — ANNUAL LEAVE
Clause 2.3: [summary]
Clause 2.4: [summary]
...
"""


# ---------------------------------------------------------------------------
# Skill 1: retrieve_policy
# ---------------------------------------------------------------------------
def retrieve_policy(file_path: str) -> dict:
    """
    Load a .txt policy file from disk and return its content as structured
    numbered sections.

    Returns:
        dict with keys:
            "raw_text"  : full file content as a string
            "sections"  : list of {"clause": str, "text": str} dicts
            "flagged"   : True if no numbered sections were found
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Policy file not found: '{file_path}'. "
            "Please check the path and try again."
        )
    except Exception as e:
        raise OSError(f"Could not read policy file '{file_path}': {e}")

    # Parse numbered clauses like "2.3", "5.2", etc.
    pattern = re.compile(
        r"(\d+\.\d+)\s+(.*?)(?=\n\s*\d+\.\d+|\n\s*[═=]{3,}|\Z)",
        re.DOTALL
    )
    matches = pattern.findall(raw_text)

    sections = []
    flagged = False

    if not matches:
        flagged = True
        print("WARNING: No numbered sections found in the document. "
              "Returning raw text for manual review.")
        sections = [{"clause": "RAW", "text": raw_text}]
    else:
        for clause_num, clause_text in matches:
            sections.append({
                "clause": clause_num.strip(),
                "text": clause_text.strip().replace("\r\n", "\n").replace("\n    ", " ")
            })

    return {"raw_text": raw_text, "sections": sections, "flagged": flagged}


# ---------------------------------------------------------------------------
# Skill 2: summarize_policy
# ---------------------------------------------------------------------------
def summarize_policy(policy_data: dict, output_path: str) -> None:
    """
    Take structured sections from retrieve_policy and produce a clause-by-clause
    compliant summary, enforced via LLM (Amazon Bedrock / Claude) with the
    RICE system prompt from agents.md.

    Writes the result to output_path.
    """
    sections = policy_data["sections"]
    raw_text = policy_data["raw_text"]
    flagged  = policy_data.get("flagged", False)

    # Warn on missing required clauses in the source
    found_clauses = {s["clause"] for s in sections}
    missing = [c for c in REQUIRED_CLAUSES if c not in found_clauses]
    incomplete_flag = ""
    if missing:
        print(f"WARNING: Required clauses missing from source: {missing}. "
              "Output will be flagged INCOMPLETE.")
        incomplete_flag = "\n\n⚠ INCOMPLETE: The following required clauses were not found in the source document: " + ", ".join(missing)

    # Build user message: pass the full raw document to the LLM
    user_message = (
        "Here is the HR Leave Policy document. "
        "Summarise it clause by clause following all enforcement rules in your system prompt.\n\n"
        "---BEGIN POLICY DOCUMENT---\n"
        + raw_text +
        "\n---END POLICY DOCUMENT---"
    )

    # Call Amazon Bedrock
    try:
        client = boto3.client(
            "bedrock-runtime",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "system": SYSTEM_PROMPT,
            "messages": [
                {"role": "user", "content": user_message}
            ]
        })

        response = client.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=body
        )

        response_body = json.loads(response["body"].read())
        summary_text = response_body["content"][0]["text"]

    except Exception as e:
        print(f"ERROR: Failed to call Amazon Bedrock: {e}")
        print("Falling back to structured local summary from parsed clauses.")
        summary_text = _local_fallback_summary(sections)

    # Append incomplete flag if needed
    summary_text += incomplete_flag

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary_text)

    print(f"Summary written to: {output_path}")


# ---------------------------------------------------------------------------
# Local fallback: structured summary without LLM (enforcement rule 4)
# ---------------------------------------------------------------------------
def _local_fallback_summary(sections: list) -> str:
    """
    Produce a plain-text clause-by-clause summary directly from parsed
    sections — used when the Bedrock API call fails.
    For clauses that are complex/multi-condition, emits a VERBATIM QUOTE.
    """
    VERBATIM_CLAUSES = {"2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"}
    lines = ["HR LEAVE POLICY — CLAUSE-BY-CLAUSE SUMMARY",
             "(Generated by local fallback — Bedrock unavailable)",
             "=" * 60, ""]

    for s in sections:
        clause = s["clause"]
        text   = s["text"]
        if clause == "RAW":
            lines.append("VERBATIM QUOTE: " + text)
        elif clause in VERBATIM_CLAUSES:
            lines.append(f"Clause {clause}: VERBATIM QUOTE: {text}")
        else:
            lines.append(f"Clause {clause}: {text}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--input",  required=True, help="Path to the .txt policy document")
    parser.add_argument("--output", required=True, help="Path to write the summary .txt file")
    args = parser.parse_args()

    # Skill 1: retrieve_policy
    print(f"Loading policy document: {args.input}")
    policy_data = retrieve_policy(args.input)
    print(f"Parsed {len(policy_data['sections'])} clause sections.")
    if policy_data["flagged"]:
        print("WARNING: Document flagged — no numbered sections detected.")

    # Skill 2: summarize_policy (calls Bedrock)
    print("Calling Amazon Bedrock to summarise...")
    summarize_policy(policy_data, args.output)
    print("Done.")


if __name__ == "__main__":
    main()
