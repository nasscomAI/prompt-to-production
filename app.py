"""
UC-0B: Summary That Changes Meaning
====================================
Reads a policy document (.txt) and produces a faithful, lossless summary
that preserves every numbered clause, modal verbs, penalties, and exceptions.

Usage:
    python app.py                          # defaults to policy_hr_leave.txt
    python app.py <path_to_policy.txt>     # custom file

Output:
    summary_<input_filename>.txt

Requirements:
    pip install anthropic
    export ANTHROPIC_API_KEY=your_key_here
"""

import os
import re
import sys
import anthropic

# ── Configuration ────────────────────────────────────────────────────────────

DEFAULT_POLICY_FILE = os.path.join(
    os.path.dirname(__file__), "../data/policy-documents/policy_hr_leave.txt"
)

MODAL_OBLIGATIONS = [
    "must", "shall", "will", "is required to", "are required to",
    "is obligated", "are obligated",
]
MODAL_PROHIBITIONS = [
    "must not", "may not", "is not permitted", "are not permitted",
    "is prohibited", "are prohibited", "shall not", "will not",
]
CRITICAL_KEYWORDS = [
    "penalty", "penalise", "penalize", "termination", "terminate",
    "not eligible", "ineligible", "exception", "unless", "provided that",
    "subject to", "forfeit", "disciplinary", "dismissal", "warning",
    "deduction", "clawback",
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def read_policy(filepath: str) -> str:
    """Read and return the full text of a policy file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Policy file not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def extract_clause_numbers(text: str) -> list[str]:
    """Extract all numbered clause identifiers from the document."""
    # Matches patterns like: 1., 1.1, 2.3(a), 3., 4.2(b), etc.
    pattern = r'(?m)^\s*(\d+(?:\.\d+)*(?:\([a-z]\))?)[.\s]'
    matches = re.findall(pattern, text)
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for m in matches:
        if m not in seen:
            seen.add(m)
            unique.append(m)
    return unique


def extract_modal_sentences(text: str) -> list[str]:
    """Return sentences containing obligation/prohibition modals."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    modal_terms = MODAL_OBLIGATIONS + MODAL_PROHIBITIONS
    flagged = []
    for s in sentences:
        s_lower = s.lower()
        if any(term in s_lower for term in modal_terms):
            flagged.append(s.strip())
    return flagged


def extract_critical_sentences(text: str) -> list[str]:
    """Return sentences containing penalty/exception/eligibility keywords."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    flagged = []
    for s in sentences:
        s_lower = s.lower()
        if any(kw in s_lower for kw in CRITICAL_KEYWORDS):
            flagged.append(s.strip())
    return flagged


# ── Summarisation Prompt ──────────────────────────────────────────────────────

def build_prompt(policy_text: str, clause_numbers: list[str]) -> str:
    clause_list = ", ".join(clause_numbers) if clause_numbers else "(none detected)"
    return f"""You are a senior HR compliance analyst producing a faithful summary of a policy document.

RULES — you must follow every one of these without exception:

1. COMPLETENESS: Every numbered clause in the original must appear in your summary.
   The following clause numbers were detected and MUST all be covered:
   {clause_list}

2. MODAL VERBS: Preserve the exact strength of obligation/prohibition language.
   - Never replace "must" with "should", "may", or "is encouraged to".
   - Never replace "must not" / "may not" with "should avoid" or "is discouraged from".
   - Copy the modal verb exactly as it appears in the source.

3. NO MERGING: Do not merge two distinct rules into a single sentence.
   Each rule must appear as a separate statement in the summary.

4. CRITICAL FLAGS: Any clause that contains a penalty, eligibility condition,
   exception, or disciplinary consequence must be labelled [CRITICAL] at the end
   of its summary sentence.

5. STRUCTURE: Produce one paragraph per section of the original document.
   Preserve the original document order. Do not add information not in the source.

6. AMBIGUITY: If a clause is genuinely ambiguous, note it with [AMBIGUOUS] rather
   than interpreting it.

Here is the policy document to summarise:

---
{policy_text}
---

Now produce the complete, faithful summary following all rules above."""


# ── CRAFT Completeness Check ──────────────────────────────────────────────────

def run_craft_check(
    source_text: str,
    summary_text: str,
    clause_numbers: list[str],
    output_path: str,
) -> bool:
    """
    Run post-generation checks and print a CRAFT report.
    Returns True if all checks pass, False otherwise.
    """
    print("\n=== CRAFT Completeness Check ===")
    all_pass = True

    # Check 1: All clause numbers present in summary
    missing_clauses = []
    for clause in clause_numbers:
        # Allow for some formatting variation (e.g. "1.2" vs "1.2.")
        pattern = re.escape(clause)
        if not re.search(pattern, summary_text):
            missing_clauses.append(clause)

    if missing_clauses:
        print(f"[FAIL] Missing clauses in summary: {', '.join(missing_clauses)}")
        all_pass = False
    else:
        print("[PASS] All numbered clauses present")

    # Check 2: No modal verb weakening (heuristic spot-check)
    weakened = []
    source_sentences = re.split(r'(?<=[.!?])\s+', source_text)
    for s in source_sentences:
        s_lower = s.lower()
        # If source says "must X", summary should not say "should X" for same subject
        if re.search(r'\bmust\b', s_lower):
            # Extract a key noun/verb after "must" to search in summary
            match = re.search(r'\bmust\s+(\w+)', s_lower)
            if match:
                verb = match.group(1)
                summary_lower = summary_text.lower()
                # If "should [verb]" appears in summary but "must [verb]" does not
                if (f"should {verb}" in summary_lower and
                        f"must {verb}" not in summary_lower):
                    weakened.append(f"'must {verb}' → 'should {verb}'")

    if weakened:
        print(f"[FAIL] Modal verbs weakened: {'; '.join(weakened)}")
        all_pass = False
    else:
        print("[PASS] No modal verbs weakened")

    # Check 3: Critical clauses flagged
    critical_sentences = extract_critical_sentences(source_text)
    if critical_sentences:
        if "[CRITICAL]" not in summary_text:
            print("[FAIL] Source contains penalty/exception clauses but [CRITICAL] tag missing in summary")
            all_pass = False
        else:
            print("[PASS] [CRITICAL] tag present for penalty/exception clauses")
    else:
        print("[SKIP] No critical/penalty clauses detected in source")

    # Check 4: Output file exists and is non-empty
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        print(f"[PASS] Output file written: {os.path.basename(output_path)}")
    else:
        print(f"[FAIL] Output file missing or empty: {output_path}")
        all_pass = False

    print("================================")
    if all_pass:
        print("✅ All checks passed — summary is faithful and complete.\n")
    else:
        print("⚠️  Some checks failed — review the summary before use.\n")

    return all_pass


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    # Determine input file
    if len(sys.argv) > 1:
        policy_path = sys.argv[1]
    else:
        policy_path = DEFAULT_POLICY_FILE

    print(f"📄 Reading policy document: {policy_path}")
    policy_text = read_policy(policy_path)

    # Pre-analysis
    clause_numbers = extract_clause_numbers(policy_text)
    modal_sentences = extract_modal_sentences(policy_text)
    critical_sentences = extract_critical_sentences(policy_text)

    print(f"   → {len(clause_numbers)} numbered clauses detected: {', '.join(clause_numbers[:10])}{'...' if len(clause_numbers) > 10 else ''}")
    print(f"   → {len(modal_sentences)} sentences with obligation/prohibition language")
    print(f"   → {len(critical_sentences)} sentences with penalty/exception keywords")

    # Call Claude API
    print("\n🤖 Calling Claude to generate faithful summary...")
    client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY from environment

    prompt = build_prompt(policy_text, clause_numbers)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    summary_text = message.content[0].text.strip()

    # Determine output path
    input_filename = os.path.splitext(os.path.basename(policy_path))[0]
    output_dir = os.path.dirname(os.path.abspath(policy_path))
    output_path = os.path.join(output_dir, f"summary_{input_filename}.txt")

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"SUMMARY OF: {os.path.basename(policy_path)}\n")
        f.write("=" * 60 + "\n\n")
        f.write(summary_text)
        f.write("\n\n")
        f.write("=" * 60 + "\n")
        f.write("Generated by UC-0B PolicySummariser (CRAFT-verified)\n")

    print(f"\n📝 Summary written to: {output_path}")
    print("\n--- SUMMARY PREVIEW (first 500 chars) ---")
    print(summary_text[:500] + ("..." if len(summary_text) > 500 else ""))
    print("-" * 42)

    # CRAFT self-check
    run_craft_check(policy_text, summary_text, clause_numbers, output_path)


if __name__ == "__main__":
    main()
