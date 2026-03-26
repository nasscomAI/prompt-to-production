"""
UC-0B — Summary That Changes Meaning
Policy Summarisation Agent

CRAFT Loop:
  C — Critique: LLM draft may omit clauses or soften obligations
  R — Refine:   Re-prompt with missing clause list if coverage check fails
  A — Assert:   Verify every numbered clause from source appears in summary
  F — Fix:      Inject missing clauses back via targeted re-prompt
  T — Test:     Run against all three policy documents; log results

Usage:
    python app.py --policy data/policy-documents/policy_hr_leave.txt
    python app.py --policy data/policy-documents/policy_it_acceptable_use.txt
    python app.py --policy data/policy-documents/policy_finance_reimbursement.txt
    python app.py --all
"""

import argparse
import os
import re
import json
import datetime
import anthropic

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
MODEL = "claude-opus-4-5"
MAX_TOKENS = 2000
OUTPUT_DIR = "uc-0b/output"
LOG_FILE = os.path.join(OUTPUT_DIR, "craft_log.txt")

POLICY_FILES = [
    "data/policy-documents/policy_hr_leave.txt",
    "data/policy-documents/policy_it_acceptable_use.txt",
    "data/policy-documents/policy_finance_reimbursement.txt",
]

# ---------------------------------------------------------------------------
# Skill 1 — Document Ingestion
# ---------------------------------------------------------------------------
def ingest_document(filepath: str) -> str:
    """Read policy document. Raises if missing or empty."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Policy file not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read().strip()
    if not text:
        raise ValueError(f"Policy file is empty: {filepath}")
    return text


# ---------------------------------------------------------------------------
# Skill 2 — Clause Inventory
# ---------------------------------------------------------------------------
def build_clause_inventory(text: str) -> list[str]:
    """
    Extract all numbered/lettered clause identifiers from the document.
    Matches patterns like: 1. / 1.1 / 1.1.1 / (a) / Section 3 / Clause 4
    Returns a deduplicated, ordered list of clause labels.
    """
    patterns = [
        r"^\s*(Section\s+\d+[\.\d]*)",          # Section 3 / Section 3.1
        r"^\s*(Clause\s+\d+[\.\d]*)",            # Clause 4
        r"^\s*(\d+\.\d+[\.\d]*)\s+\w",          # 1.1 / 1.1.1 followed by text
        r"^\s*(\d+\.)\s+[A-Z]",                  # 1. followed by capital letter
        r"^\s*\(([a-z])\)\s+\w",                 # (a) followed by text
    ]
    found = []
    seen = set()
    for line in text.splitlines():
        for pat in patterns:
            m = re.match(pat, line, re.IGNORECASE)
            if m:
                label = m.group(1).strip()
                if label not in seen:
                    seen.add(label)
                    found.append(label)
                break
    if len(found) < 3:
        print(f"  ⚠️  Warning: only {len(found)} clauses detected — check document format.")
    return found


# ---------------------------------------------------------------------------
# Skill 3 — Faithful Summarisation (LLM call)
# ---------------------------------------------------------------------------
SUMMARISE_PROMPT = """You are a Policy Summarisation Agent. Your job is to produce a faithful, complete summary of the policy document below.

STRICT RULES — follow every one:
1. Every numbered clause, section, or lettered sub-clause in the source document MUST appear in your summary. Do not skip any.
2. Preserve mandatory language exactly: "must" stays "must", "shall" stays "shall", "is prohibited" stays "is prohibited". Never soften obligations.
3. Do not add interpretation, examples, or context not present in the source.
4. Use the same section numbering and heading hierarchy as the source.
5. Derive content from this document only — do not blend with other policies.

CLAUSE INVENTORY (every clause you must cover):
{clause_inventory}

SOURCE DOCUMENT:
---
{document_text}
---

After the summary, add a section titled [CLAUSE COVERAGE] that lists each clause from the inventory and marks it ✓ (covered) or ✗ (missing).
"""

def summarise_document(text: str, clause_inventory: list[str]) -> str:
    """Call Claude to produce a faithful policy summary."""
    client = anthropic.Anthropic()
    prompt = SUMMARISE_PROMPT.format(
        clause_inventory="\n".join(f"  - {c}" for c in clause_inventory),
        document_text=text,
    )
    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


# ---------------------------------------------------------------------------
# Skill 4 — Completeness Verification
# ---------------------------------------------------------------------------
def verify_coverage(summary: str, clause_inventory: list[str]) -> tuple[bool, list[str]]:
    """
    Check that every clause from the inventory appears in the summary.
    Returns (all_covered: bool, missing_clauses: list[str]).
    """
    missing = []
    for clause in clause_inventory:
        # Search for the clause label anywhere in the summary (case-insensitive)
        pattern = re.escape(clause)
        if not re.search(pattern, summary, re.IGNORECASE):
            missing.append(clause)
    return (len(missing) == 0), missing


REFINE_PROMPT = """Your previous summary of the policy document was missing coverage for the following clauses:
{missing_clauses}

Please revise your summary to include these clauses. Apply the same strict rules as before:
- No meaning drift, no softening of obligations, no added interpretation.
- After the summary, include an updated [CLAUSE COVERAGE] section.

ORIGINAL SUMMARY:
---
{original_summary}
---

SOURCE DOCUMENT (for reference):
---
{document_text}
---
"""

def refine_summary(original_summary: str, missing: list[str], text: str) -> str:
    """Re-prompt the model to fix missing clauses."""
    client = anthropic.Anthropic()
    prompt = REFINE_PROMPT.format(
        missing_clauses="\n".join(f"  - {c}" for c in missing),
        original_summary=original_summary,
        document_text=text,
    )
    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


# ---------------------------------------------------------------------------
# Skill 5 — Output Writer
# ---------------------------------------------------------------------------
def write_output(summary: str, policy_path: str) -> str:
    """Write the summary to output/summary_[policy_name].txt"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    base = os.path.splitext(os.path.basename(policy_path))[0]
    out_path = os.path.join(OUTPUT_DIR, f"summary_{base}.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(summary)
    if os.path.getsize(out_path) == 0:
        raise RuntimeError(f"Output file is empty: {out_path}")
    return out_path


# ---------------------------------------------------------------------------
# Skill 6 — CRAFT Loop Logger
# ---------------------------------------------------------------------------
def log_craft(policy: str, clauses_found: int, missing_before: list[str],
              missing_after: list[str], refined: bool):
    """Append a structured CRAFT log entry."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "policy": policy,
        "clauses_detected": clauses_found,
        "missing_before_refinement": missing_before,
        "refined": refined,
        "missing_after_refinement": missing_after,
        "status": "PASS" if not missing_after else "PARTIAL",
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, indent=2) + "\n---\n")
    print(f"  📋 CRAFT log updated: {LOG_FILE}")


# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------
def process_policy(filepath: str):
    print(f"\n{'='*60}")
    print(f"📄 Processing: {filepath}")
    print(f"{'='*60}")

    # Skill 1 — Ingest
    print("  [1/5] Ingesting document...")
    text = ingest_document(filepath)
    print(f"        {len(text)} characters read.")

    # Skill 2 — Clause inventory
    print("  [2/5] Building clause inventory...")
    inventory = build_clause_inventory(text)
    print(f"        {len(inventory)} clauses found: {inventory[:6]}{'...' if len(inventory) > 6 else ''}")

    # Skill 3 — Summarise
    print("  [3/5] Calling Claude for faithful summary...")
    summary = summarise_document(text, inventory)

    # Skill 4 — Verify coverage
    print("  [4/5] Verifying clause coverage...")
    covered, missing = verify_coverage(summary, inventory)

    refined = False
    if not covered:
        print(f"        ⚠️  Missing clauses: {missing}")
        print("        🔁 Refining summary to recover missing clauses...")
        summary = refine_summary(summary, missing, text)
        _, missing_after = verify_coverage(summary, inventory)
        refined = True
        if missing_after:
            print(f"        ⚠️  Still missing after refinement: {missing_after}")
        else:
            print("        ✅ All clauses covered after refinement.")
    else:
        missing_after = []
        print("        ✅ All clauses covered.")

    # Skill 5 — Write output
    print("  [5/5] Writing output...")
    out_path = write_output(summary, filepath)
    print(f"        Saved → {out_path}")

    # Skill 6 — Log
    log_craft(filepath, len(inventory), missing, missing_after, refined)

    return out_path


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="UC-0B Policy Summariser")
    parser.add_argument("--policy", help="Path to a single policy .txt file")
    parser.add_argument("--all", action="store_true", help="Process all three policy documents")
    args = parser.parse_args()

    if args.all:
        outputs = []
        for p in POLICY_FILES:
            try:
                out = process_policy(p)
                outputs.append(out)
            except FileNotFoundError as e:
                print(f"  ❌ Skipped: {e}")
        print(f"\n✅ Done. {len(outputs)} summaries written.")
    elif args.policy:
        process_policy(args.policy)
        print("\n✅ Done.")
    else:
        # Default: run on HR leave policy for quick demo
        print("No --policy specified. Running on HR leave policy by default.")
        process_policy(POLICY_FILES[0])
        print("\n✅ Done.")


if __name__ == "__main__":
    main()
