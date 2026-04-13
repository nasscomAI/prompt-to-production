"""
UC-0B app.py — Summary That Changes Meaning
Two-mode policy summariser: naive baseline vs. enforced two-agent pipeline.

Run command (enforced — production):
    python app.py \
        --input ../data/policy-documents/policy_hr_leave.txt \
        --output summary_hr_leave.txt

Run command (naive — captures failure baseline):
    python app.py \
        --input ../data/policy-documents/policy_hr_leave.txt \
        --output naive_summary_hr_leave.txt \
        --naive
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

# Load environment variables from .env file
load_dotenv()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
MODEL = "gemini-3-flash-preview"
OUTPUT_DIR = Path("uc-0b")
OUTPUT_DIR.mkdir(exist_ok=True)
MAX_RETRIES = 2
API_RETRY_DELAY = 2  # seconds, exponential backoff

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
client = genai.GenerativeModel(MODEL)

# ---------------------------------------------------------------------------
# Mandatory Clause Registry  (source of truth — mirrors agents.md)
# ---------------------------------------------------------------------------
REGISTRY = [
    {
        "clause": "2.3",
        "obligation": "14-day advance notice required; Form HR-L1 must be used",
        "conditions": ["14 calendar days", "Form HR-L1"],
        "verb": "must",
    },
    {
        "clause": "2.4",
        "obligation": "Written approval required before leave commences; verbal not valid",
        "conditions": ["written approval", "before the leave commences", "verbal approval is not valid"],
        "verb": "must",
    },
    {
        "clause": "2.5",
        "obligation": "Unapproved absence recorded as LOP regardless of subsequent approval",
        "conditions": ["loss of pay", "lop", "regardless of subsequent"],
        "verb": "will",
    },
    {
        "clause": "2.6",
        "obligation": "Max 5 carry-forward days; excess forfeited on 31 December",
        "conditions": ["maximum of 5", "forfeited on 31 december"],
        "verb": "are forfeited",
    },
    {
        "clause": "2.7",
        "obligation": "Carry-forward days must be used January–March or forfeited",
        "conditions": ["january", "march", "forfeited"],
        "verb": "must",
    },
    {
        "clause": "3.2",
        "obligation": "3+ consecutive sick days requires medical cert within 48 hrs",
        "conditions": ["3 or more consecutive", "48 hours"],
        "verb": "requires",
    },
    {
        "clause": "3.4",
        "obligation": "Sick leave adjacent to public holiday requires cert regardless of duration",
        "conditions": ["regardless of duration"],
        "verb": "requires",
    },
    {
        "clause": "5.2",
        "obligation": "LWP requires BOTH Department Head AND HR Director; one alone insufficient",
        "conditions": ["department head", "hr director", "alone is not sufficient"],
        "verb": "requires",
    },
    {
        "clause": "5.3",
        "obligation": "LWP >30 continuous days requires Municipal Commissioner approval",
        "conditions": ["30 continuous days", "municipal commissioner"],
        "verb": "requires",
    },
    {
        "clause": "7.2",
        "obligation": "Leave encashment during service not permitted under any circumstances",
        "conditions": ["not permitted", "any circumstances"],
        "verb": "not permitted",
    },
]

REGISTRY_PROMPT = "\n".join(
    f"  [{r['clause']}] {r['obligation']}\n"
    f"        Conditions that MUST appear: {', '.join(repr(c) for c in r['conditions'][:3])}"
    for r in REGISTRY
)

BANNED_PHRASES = [
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
    "it is customary",
    "in line with industry norms",
]


# ---------------------------------------------------------------------------
# Skill: retrieve_policy
# ---------------------------------------------------------------------------
def retrieve_policy(path: str) -> dict:
    """
    Load a .txt policy file and return structured content.
    Output: { raw, sections, metadata }
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Policy file not found: {path}")

    text = p.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"Policy file is empty: {path}")

    lines = text.splitlines()
    sections: dict[str, str] = {}
    current_key: str | None = None
    buffer: list[str] = []

    for line in lines:
        stripped = line.strip()
        if re.match(r"^[═\-=]{3,}", stripped):   # decorative dividers
            continue
        m = re.match(r"^(\d+\.\d+)\s+(.*)", stripped)
        if m:
            if current_key is not None:
                sections[current_key] = " ".join(buffer).strip()
            current_key = m.group(1)
            buffer = [m.group(2)]
        elif current_key and stripped:
            buffer.append(stripped)

    if current_key and buffer:
        sections[current_key] = " ".join(buffer).strip()

    if not sections:
        raise ValueError("No numbered clauses detected in policy file.")

    header = "\n".join(lines[:10])
    metadata = {
        "title":     _re_extract(header, r"^(.+(?:CORPORATION|AUTHORITY).+)$", "Unknown"),
        "reference": _re_extract(header, r"Document Reference:\s*(\S+)", "Unknown"),
        "version":   _re_extract(header, r"Version:\s*([^\|]+)", "Unknown"),
        "effective": _re_extract(header, r"Effective:\s*(.+)", "Unknown"),
    }

    return {"raw": text, "sections": sections, "metadata": metadata}


def _re_extract(text: str, pattern: str, default: str) -> str:
    m = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
    return m.group(1).strip() if m else default


# ---------------------------------------------------------------------------
# Skill: summarize_policy — naive mode (baseline, expected to fail)
# ---------------------------------------------------------------------------
def summarize_policy_naive(structured: dict) -> dict:
    """Single-turn, no enforcement. Captures failure baseline."""
    response = _api_call([
        {
            "role": "user",
            "content": f"Summarize the following policy document.\n\n{structured['raw']}",
        }
    ], max_tokens=1000)

    return {
        "summary": response,
        "verification": "(naive mode — verification not run)",
        "verdict": "UNVERIFIED",
        "mode": "naive",
        "retries": 0,
    }


# ---------------------------------------------------------------------------
# Skill: summarize_policy — enforced mode (production)
# ---------------------------------------------------------------------------
def summarize_policy_enforced(structured: dict) -> dict:
    """
    Two-pass pipeline:
      Pass 1 (summarize_agent) — drafts summary with full clause registry injected
      Pass 2 (verify_agent)    — audits draft; triggers retry on FAIL
    Max retries: MAX_RETRIES (default 2)
    """
    raw = structured["raw"]
    ref = structured["metadata"].get("reference", "HR-POL-001")
    last_failures = ""

    for attempt in range(MAX_RETRIES + 1):
        _log(f"Pass 1 — summarize_agent (attempt {attempt + 1}/{MAX_RETRIES + 1})")

        retry_block = ""
        if attempt > 0:
            retry_block = (
                f"\nRETRY #{attempt} — your previous attempt failed verification:\n"
                f"{last_failures}\n"
                "Fix every listed failure. Do not introduce new ones.\n"
            )

        # ── Pass 1: summarize_agent ──────────────────────────────────────
        draft_prompt = f"""You are a policy compliance summariser for a municipal HR department.
Your operational boundary is strictly the source document provided.
Do not draw on external knowledge, general HR practice, or industry norms.
{retry_block}
HARD RULES — violating any rule is a critical failure:
1. Every clause in the MANDATORY CLAUSE REGISTRY must appear, cited as **[X.Y]**.
2. Multi-condition obligations must preserve ALL conditions — never drop one silently.
   Clause 5.2 specifically requires BOTH "Department Head" AND "HR Director" named,
   plus the phrase "alone is not sufficient". Dropping either approver is a condition drop.
3. Binding verbs must not be softened:
     must        → must  (not: should / may / is expected to)
     will        → will  (not: may result in)
     requires    → requires  (not: should submit)
     not permitted → not permitted  (not: discouraged / not usually)
4. Do not add information absent from the source document.
   Banned phrases: {", ".join(repr(p) for p in BANNED_PHRASES)}
5. If a clause cannot be summarised without meaning loss, quote it verbatim
   and append [VERBATIM — meaning loss risk].

MANDATORY CLAUSE REGISTRY — all 10 must appear:
{REGISTRY_PROMPT}

OUTPUT FORMAT — use exactly this structure:
# HR Leave Policy — Compliance Summary
Document Reference: {ref}

## Section 2 — Annual Leave
**[2.3]** <summary>
**[2.4]** <summary>
**[2.5]** <summary>
**[2.6]** <summary>
**[2.7]** <summary>

## Section 3 — Sick Leave
**[3.2]** <summary>
**[3.4]** <summary>

## Section 5 — Leave Without Pay
**[5.2]** <summary>
**[5.3]** <summary>

## Section 7 — Leave Encashment
**[7.2]** <summary>

---
SOURCE DOCUMENT:
{raw}"""

        draft = _api_call([{"role": "user", "content": draft_prompt}], max_tokens=2000)

        # ── Pass 2: verify_agent ─────────────────────────────────────────
        _log("Pass 2 — verify_agent auditing draft")

        verify_prompt = f"""You are a policy verification agent. You audit summaries — you do not write them.

For each of the 10 mandatory clauses below, check the DRAFT SUMMARY and report:
1. Present? — Is the clause number cited as **[X.Y]**?
2. Conditions intact? — Are ALL listed conditions preserved in the draft?
3. Verb strength? — Has any binding verb been softened?
4. Scope bleed? — Has any information not in the source been added?

MANDATORY CLAUSE REGISTRY:
{REGISTRY_PROMPT}

SOURCE DOCUMENT (ground truth):
{raw}

DRAFT SUMMARY TO AUDIT:
{draft}

OUTPUT FORMAT — use exactly this structure:
## Verification Report

### PASS ✓
- [X.Y] — <brief reason>

### FAIL ✗
- [X.Y] — REASON: <what is missing or wrong>
  Source: "<relevant source text>"
  Draft:  "<what the draft says>"

### Scope Bleed Detected
- <phrase> — not in source  (or: None)

### Verdict
PASS
"""

        verification = _api_call(
            [{"role": "user", "content": verify_prompt}], max_tokens=2000
        )

        verdict = _parse_verdict(verification)
        _log(f"Verdict: {verdict}")

        if verdict == "PASS":
            return {
                "summary": draft,
                "verification": verification,
                "verdict": "PASS",
                "mode": "enforced",
                "retries": attempt,
            }

        last_failures = _extract_failures(verification)

    # Exhausted retries
    _log("Max retries exhausted — writing partial output with UNRESOLVED flags")
    flagged = draft + "\n\n[UNRESOLVED] — summary did not pass verification after max retries.\n"
    return {
        "summary": flagged,
        "verification": verification,
        "verdict": "FAIL",
        "mode": "enforced",
        "retries": MAX_RETRIES,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _api_call(messages: list, max_tokens: int = 1500) -> str:
    try:
        # Extract the user content from the messages list
        # For single-turn interactions, get the last user message content
        content = messages[-1]["content"] if messages else ""
        
        retry_attempt = 0
        while retry_attempt <= 2:
            try:
                response = client.generate_content(
                    content,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=max_tokens,
                        temperature=1.0,
                    )
                )
                return response.text
            except ResourceExhausted as rate_err:
                retry_attempt += 1
                if retry_attempt > 2:
                    raise
                # Exponential backoff with jitter
                wait_time = API_RETRY_DELAY * (2 ** (retry_attempt - 1)) + 2
                _log(f"Rate limited. Retrying in {wait_time}s... (attempt {retry_attempt}/3)")
                time.sleep(wait_time)
    except Exception as e:
        raise RuntimeError(f"Gemini API error: {e}") from e


def _parse_verdict(verification: str) -> str:
    """Extract PASS/FAIL from verify_agent output."""
    m = re.search(r"###\s*Verdict\s*\n\s*(PASS|FAIL)", verification, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    # Fallback: if any FAIL ✗ section has content, it's a fail
    fail_section = re.search(r"###\s*FAIL\s*✗\s*\n(.+?)(?=###|\Z)", verification, re.DOTALL)
    if fail_section and fail_section.group(1).strip() and fail_section.group(1).strip() != "None":
        return "FAIL"
    return "PASS"


def _extract_failures(verification: str) -> str:
    """Pull the FAIL section out for retry injection."""
    m = re.search(r"###\s*FAIL\s*✗\s*\n(.+?)(?=###|\Z)", verification, re.DOTALL)
    return m.group(1).strip() if m else verification


def _log(msg: str) -> None:
    print(f"  → {msg}")


# ---------------------------------------------------------------------------
# Output writer
# ---------------------------------------------------------------------------
def write_output(result: dict, output_path: Path, input_path: str) -> None:
    mode_label = "NAIVE (baseline)" if result["mode"] == "naive" else "ENFORCED (production)"
    retry_label = f"{result['retries']} retr{'y' if result['retries'] == 1 else 'ies'}"

    content = "\n".join([
        "=" * 80,
        "UC-0B — HR Leave Policy Summary",
        f"Mode:    {mode_label}",
        f"Input:   {input_path}",
        f"Verdict: {result['verdict']}",
        f"Retries: {retry_label}",
        "=" * 80,
        "",
        result["summary"],
        "",
        "=" * 80,
        "VERIFICATION REPORT",
        "=" * 80,
        "",
        result["verification"],
        "",
    ])

    output_path.write_text(content, encoding="utf-8")
    print(f"\n✓ Written: {output_path}")
    print(f"  Verdict: {result['verdict']}  |  Mode: {result['mode']}  |  Retries: {result['retries']}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="UC-0B — HR Leave Policy Summariser")
    parser.add_argument("--input",  required=True, help="Path to policy .txt file")
    parser.add_argument("--output", required=True, help="Output filename (written to uc-0b/)")
    parser.add_argument("--naive",  action="store_true",
                        help="Run naive single-pass baseline (captures failure modes)")
    args = parser.parse_args()

    divider = "=" * 60
    print(f"\n{divider}")
    print("UC-0B — Policy Summariser")
    print(f"Mode:  {'NAIVE (baseline)' if args.naive else 'ENFORCED (production)'}")
    print(f"Input: {args.input}")
    print(divider + "\n")

    # Skill: retrieve_policy
    print("retrieve_policy: loading and parsing...")
    try:
        structured = retrieve_policy(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"  {len(structured['sections'])} clauses detected")
    print(f"  Reference: {structured['metadata']['reference']}\n")

    # Skill: summarize_policy
    if args.naive:
        print("summarize_policy [naive]: single-pass, no enforcement...")
        result = summarize_policy_naive(structured)
    else:
        print("summarize_policy [enforced]: two-pass pipeline...")
        result = summarize_policy_enforced(structured)

    # Write output
    output_path = OUTPUT_DIR / args.output
    write_output(result, output_path, args.input)

    sys.exit(0 if result["verdict"] in ("PASS", "UNVERIFIED") else 1)


if __name__ == "__main__":
    main()