"""
UC-0B: Summary That Changes Meaning
====================================
Reads a policy document, generates a faithful AI summary using Claude,
detects clauses where meaning may have changed, and writes the output.

Usage:
    python app.py
    python app.py --policy ../data/policy-documents/policy_it_acceptable_use.txt
    python app.py --policy ../data/policy-documents/policy_finance_reimbursement.txt
"""

import os
import re
import sys
import argparse
import urllib.request
import json


# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────
DEFAULT_POLICY = "../data/policy-documents/policy_hr_leave.txt"
DEFAULT_OUTPUT = "summary_hr_leave.txt"
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-3-5-haiku-20241022"   # fast & cost-effective for this task
MAX_TOKENS = 2048


# ──────────────────────────────────────────────
# SKILL 1 — read_policy_document
# ──────────────────────────────────────────────
def read_policy_document(filepath: str) -> dict:
    """Load policy text and extract numbered/headed clauses."""
    if not os.path.exists(filepath):
        print(f"[ERROR] File not found: {filepath}")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    lines = raw.splitlines()
    clauses = []
    current_heading = "General"
    current_body = []

    heading_pattern = re.compile(
        r"^(\d+[\.\)]|[A-Z][A-Z\s]{4,}:|[A-Z][a-z].*:)\s*"
    )

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if heading_pattern.match(stripped) or stripped.isupper():
            if current_body:
                clauses.append({
                    "clause_id": len(clauses) + 1,
                    "heading": current_heading,
                    "body": " ".join(current_body).strip()
                })
                current_body = []
            current_heading = stripped
        else:
            current_body.append(stripped)

    if current_body:
        clauses.append({
            "clause_id": len(clauses) + 1,
            "heading": current_heading,
            "body": " ".join(current_body).strip()
        })

    print(f"[INFO] Loaded {len(clauses)} clauses from '{filepath}'")
    return {"raw": raw, "clauses": clauses, "filepath": filepath}


# ──────────────────────────────────────────────
# SKILL 2 — summarise_policy (calls Claude API)
# ──────────────────────────────────────────────
def call_claude(system_prompt: str, user_prompt: str) -> str:
    """Make a request to Anthropic Messages API."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("[WARN] ANTHROPIC_API_KEY not set — using rule-based fallback summary.")
        return None

    payload = {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}]
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["content"][0]["text"]
    except Exception as e:
        print(f"[ERROR] API call failed: {e}")
        return None


def summarise_policy(doc: dict) -> str:
    """Generate a faithful, clause-complete summary of the policy."""
    system_prompt = """You are a policy summarisation agent.
Your job is to produce a COMPLETE and FAITHFUL summary of the policy document provided.

STRICT RULES:
1. Every numbered or lettered clause MUST appear in your summary.
2. Never merge two clauses that have different conditions into one.
3. Preserve ALL numerical limits exactly (e.g., '10 days', '₹5000 cap').
4. Preserve modal verbs exactly — if the source says 'must', never write 'may'.
5. Preserve ALL eligibility conditions and exceptions.
6. Preserve ALL penalty or disciplinary clauses.
7. Write in plain English but do NOT change the legal meaning.
8. Structure your summary with the same headings as the source document.
9. At the end, add a line: "CLAUSE COUNT: X" where X = number of clauses you summarised.

A shorter summary that omits clauses is WORSE than a longer accurate one."""

    user_prompt = f"""Please summarise the following policy document faithfully:

---
{doc['raw']}
---

Remember: cover EVERY clause, preserve all numerical limits, all 'must/shall/cannot'
language, all eligibility conditions, and all exceptions."""

    print("[INFO] Calling Claude API for summary...")
    summary = call_claude(system_prompt, user_prompt)

    if summary is None:
        # Fallback: simple rule-based extraction
        summary = rule_based_summary(doc)

    return summary


def rule_based_summary(doc: dict) -> str:
    """Fallback summary when API key is not available — extracts clauses directly."""
    lines = ["POLICY SUMMARY (Rule-Based Extraction)", "=" * 50, ""]
    for c in doc["clauses"]:
        lines.append(f"[Clause {c['clause_id']}] {c['heading']}")
        if c["body"]:
            lines.append(f"  {c['body']}")
        lines.append("")
    lines.append(f"CLAUSE COUNT: {len(doc['clauses'])}")
    return "\n".join(lines)


# ──────────────────────────────────────────────
# SKILL 3 — detect_meaning_change
# ──────────────────────────────────────────────
SOFTENING_PAIRS = [
    ("must", "may"), ("must", "can"), ("must", "could"),
    ("shall", "may"), ("shall", "can"),
    ("cannot", "may not"), ("prohibited", "discouraged"),
    ("mandatory", "optional"), ("required", "recommended"),
    ("will not", "might not"), ("is not allowed", "is not recommended"),
]

NUMBER_PATTERN = re.compile(r'\b(\d+)\s*(days?|weeks?|months?|hours?|%|percent|rupees?|₹|inr)\b', re.IGNORECASE)


def detect_meaning_change(raw_source: str, summary: str, clauses: list) -> list:
    """Compare source and summary; return list of flagged issues."""
    flags = []
    src_lower = raw_source.lower()
    sum_lower = summary.lower()

    # 1. Softening detection
    for (strong, weak) in SOFTENING_PAIRS:
        if strong in src_lower and weak in sum_lower and strong not in sum_lower:
            flags.append({
                "issue_type": "SOFTENING",
                "detail": f"Source uses '{strong}' but summary uses '{weak}'",
                "risk_level": "HIGH"
            })

    # 2. Numerical cap loss detection
    source_numbers = NUMBER_PATTERN.findall(raw_source)
    for (num, unit) in source_numbers:
        pattern = re.compile(rf'\b{re.escape(num)}\s*{re.escape(unit)}', re.IGNORECASE)
        if not pattern.search(summary):
            flags.append({
                "issue_type": "CAP LOSS",
                "detail": f"Source mentions '{num} {unit}' but it is missing from summary",
                "risk_level": "HIGH"
            })

    # 3. Clause count check
    source_count = len(clauses)
    clause_count_match = re.search(r'CLAUSE COUNT:\s*(\d+)', summary)
    if clause_count_match:
        summary_count = int(clause_count_match.group(1))
        if summary_count < source_count:
            flags.append({
                "issue_type": "OMISSION",
                "detail": f"Source has {source_count} clauses, summary covers only {summary_count}",
                "risk_level": "MEDIUM"
            })

    # 4. Key policy words in source but absent in summary
    important_words = ["penalty", "disciplinary", "termination", "approval",
                       "exception", "prohibited", "mandatory", "eligible",
                       "ineligible", "encash", "carry forward", "lapse"]
    for word in important_words:
        if word in src_lower and word not in sum_lower:
            flags.append({
                "issue_type": "OMISSION",
                "detail": f"Important term '{word}' present in source but missing from summary",
                "risk_level": "MEDIUM"
            })

    return flags


# ──────────────────────────────────────────────
# SKILL 4 — write_summary_file
# ──────────────────────────────────────────────
def write_summary_file(summary: str, flags: list, output_path: str, source_path: str):
    """Write summary + review flags to output file."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"POLICY SUMMARY\n")
        f.write(f"Source: {source_path}\n")
        f.write("=" * 60 + "\n\n")
        f.write(summary)
        f.write("\n\n")
        f.write("=" * 60 + "\n")
        f.write("[REVIEW FLAGS — Potential Meaning Changes Detected]\n")
        f.write("=" * 60 + "\n")

        if not flags:
            f.write("✅ No meaning-change issues detected.\n")
        else:
            for i, flag in enumerate(flags, 1):
                f.write(f"\n[{i}] {flag['issue_type']} | Risk: {flag['risk_level']}\n")
                f.write(f"    {flag['detail']}\n")

        f.write("\n" + "=" * 60 + "\n")
        f.write(f"Total flags: {len(flags)}\n")

    print(f"[INFO] Summary written to '{output_path}'")
    if flags:
        print(f"[WARN] {len(flags)} meaning-change flag(s) detected — review before using.")
    else:
        print("[INFO] ✅ No meaning-change issues detected.")


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="UC-0B: Policy Summary Integrity")
    parser.add_argument("--policy", default=DEFAULT_POLICY,
                        help="Path to the policy .txt file")
    parser.add_argument("--output", default=DEFAULT_OUTPUT,
                        help="Output summary filename")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print("UC-0B: Policy Summary Integrity Agent")
    print(f"{'='*60}")

    # Step 1 — Read
    doc = read_policy_document(args.policy)

    # Step 2 — Summarise
    summary = summarise_policy(doc)

    # Step 3 — Detect meaning changes
    flags = detect_meaning_change(doc["raw"], summary, doc["clauses"])

    # Step 4 — Write output
    write_summary_file(summary, flags, args.output, args.policy)

    print(f"\n✅ Done! Output: {args.output}")
    print(f"   Clauses extracted : {len(doc['clauses'])}")
    print(f"   Review flags      : {len(flags)}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
