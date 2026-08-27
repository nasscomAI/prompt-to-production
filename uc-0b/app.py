"""
UC-0B app.py — Policy Summarisation Agent
Reads a structured HR leave policy document and produces a clause-faithful
summary following the enforcement rules defined in agents.md.

Run:
  python app.py --input ../data/policy-documents/policy_hr_leave.txt --output summary_hr_leave.txt
"""

import argparse
import os
import re
import sys
import time

# ── 10 tracked clauses from agents.md / README ──────────────────────────
TRACKED_CLAUSES = ["2.3", "2.4", "2.5", "2.6", "2.7",
                   "3.2", "3.4",
                   "5.2", "5.3",
                   "7.2"]

# ── Binding verbs per tracked clause (must be preserved unchanged) ──────
BINDING_VERBS = {
    "2.3": ["must"],
    "2.4": ["must"],
    "2.5": ["will"],
    "2.6": ["may", "are forfeited"],
    "2.7": ["must"],
    "3.2": ["requires"],
    "3.4": ["requires"],
    "5.2": ["requires"],
    "5.3": ["requires"],
    "7.2": ["not permitted"],
}

# ── Scope-bleed markers (forbidden phrases from agents.md context) ──────
SCOPE_BLEED_MARKERS = [
    "as is standard practice",
    "typically in government organisations",
    "employees are generally expected to",
]

# ── Models to try in order (fallback chain) ─────────────────────────────
MODEL_FALLBACK_CHAIN = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]


# ═════════════════════════════════════════════════════════════════════════
# SKILL 1: retrieve_policy
# ═════════════════════════════════════════════════════════════════════════

def retrieve_policy(file_path: str) -> dict[str, dict[str, str]]:
    """
    Loads a .txt policy file and returns its content parsed into structured,
    numbered sections keyed by clause number.

    Returns:
        A nested dict: { section_num: { "_title": ..., clause_id: text, ... } }
        Section hierarchy (chapter → clause) is preserved as nested keys.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Policy file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    if not raw_text.strip():
        raise ValueError("No numbered clauses detected — verify input file format.")

    section_pattern = re.compile(
        r"^═+\s*\n(\d+)\.\s+(.+?)\s*\n═+",
        re.MULTILINE
    )
    section_matches = list(section_pattern.finditer(raw_text))

    if not section_matches:
        raise ValueError("No numbered clauses detected — verify input file format.")

    section_blocks: list[tuple[str, str, str]] = []
    for i, match in enumerate(section_matches):
        sec_num = match.group(1)
        sec_title = match.group(2).strip()
        block_start = match.end()
        if i + 1 < len(section_matches):
            block_end = section_matches[i + 1].start()
        else:
            block_end = len(raw_text)
        block_text = raw_text[block_start:block_end].strip()
        section_blocks.append((sec_num, sec_title, block_text))

    clause_pattern = re.compile(r"^(\d+\.\d+)\s+", re.MULTILINE)
    structured: dict[str, dict[str, str]] = {}

    for sec_num, sec_title, block_text in section_blocks:
        clauses_in_section: dict[str, str] = {}
        matches = list(clause_pattern.finditer(block_text))

        for j, m in enumerate(matches):
            clause_id = m.group(1)
            start = m.start()
            if j + 1 < len(matches):
                end = matches[j + 1].start()
            else:
                end = len(block_text)
            clause_text = block_text[start:end].strip()
            clauses_in_section[clause_id] = clause_text

        structured[sec_num] = {
            "_title": sec_title,
            **clauses_in_section,
        }

    total_clauses = sum(
        len([k for k in v if k != "_title"]) for v in structured.values()
    )
    if total_clauses == 0:
        raise ValueError("No numbered clauses detected — verify input file format.")

    return structured


def _flatten_clauses(structured: dict[str, dict[str, str]]) -> dict[str, str]:
    flat: dict[str, str] = {}
    for sec_data in structured.values():
        for key, text in sec_data.items():
            if key != "_title":
                flat[key] = text
    return flat


# ═════════════════════════════════════════════════════════════════════════
# SKILL 2a: summarize_policy — LLM-based (primary)
# ═════════════════════════════════════════════════════════════════════════

def _build_system_prompt() -> str:
    return """You are a Policy Summarisation Agent. Your ONLY task is to produce a
concise summary of the HR Leave Policy document provided below.

ENFORCEMENT RULES — follow every rule without exception:

1. CLAUSE COMPLETENESS: Every numbered clause in the source document must be
   present in your summary. Omitting any clause is a hard failure.

2. CONDITION PRESERVATION: Multi-condition obligations must preserve ALL
   conditions. For example, Clause 5.2 requires approval from BOTH the
   Department Head AND the HR Director — dropping either approver is a
   condition-drop failure.

3. NO SCOPE BLEED: Never add information not present in the source document.
   Do NOT use phrases like "as is standard practice", "typically in government
   organisations", or "employees are generally expected to". Only state what
   the document states.

4. BINDING VERB PRESERVATION: These binding verbs must appear exactly as in
   the source — do NOT soften, strengthen, or substitute them:
   must, will, requires, not permitted, may, are forfeited

5. VERBATIM FALLBACK: If a clause cannot be summarised without meaning loss,
   quote it verbatim and flag it with [VERBATIM — summarisation would alter meaning].

6. ACTUAL SUMMARISATION: You must genuinely condense each clause — do not
   simply copy the source text. Remove redundant wording, combine related
   ideas, and shorten sentences while keeping the core obligation intact.
   The output must be noticeably shorter than the input.

OUTPUT FORMAT:
- Prefix each summarised clause with its clause reference, e.g. [2.3].
- Group clauses under their section headings.
- Use concise, precise language. Do not editorialize."""


def summarize_policy_llm(structured: dict[str, dict[str, str]]) -> str:
    from google import genai

    flat = _flatten_clauses(structured)
    missing = [c for c in TRACKED_CLAUSES if c not in flat]
    if missing:
        raise ValueError(
            f"Missing tracked clauses in input: {', '.join(missing)}. "
            "Cannot produce a compliant summary."
        )

    policy_text = "\n\n".join(
        f"[Clause {cid}] {text}" for cid, text in sorted(flat.items())
    )

    system_prompt = _build_system_prompt()
    user_prompt = f"""Summarise the following HR Leave Policy document. Follow every
enforcement rule in your instructions. Produce a GENUINE SUMMARY that is
noticeably shorter than the source — do NOT copy clauses verbatim unless
flagged with [VERBATIM].

--- BEGIN POLICY DOCUMENT ---
{policy_text}
--- END POLICY DOCUMENT ---"""

    client = genai.Client()
    last_error = None

    for model_name in MODEL_FALLBACK_CHAIN:
        for attempt in range(3):
            try:
                print(f"   Trying {model_name} (attempt {attempt + 1}/3)...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=user_prompt,
                    config=genai.types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.1,
                    ),
                )
                summary = response.text
                return summary

            except Exception as e:
                last_error = e
                error_str = str(e)
                if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
                    wait = 2 ** (attempt + 1)
                    print(f"   ⚠ Rate limited on {model_name}, retrying in {wait}s...", file=sys.stderr)
                    time.sleep(wait)
                    continue
                else:
                    print(f"   ⚠ {model_name} failed: {e}", file=sys.stderr)
                    break 

    raise RuntimeError(f"All models exhausted. Last error: {last_error}")


# ═════════════════════════════════════════════════════════════════════════
# SKILL 2b: summarize_policy — Rule-based fallback (no LLM)
# ═════════════════════════════════════════════════════════════════════════

_CONDENSATION_RULES = [
    (r"\s+of the City Municipal Corporation \(CMC\)", ""),
    (r"per calendar year", "per year"),
    (r"calendar\s+days", "days"),
    (r"from the date of joining", "from joining"),
    (r"is entitled to", "receives"),
    (r"are entitled to", "receive"),
    (r"in advance using Form HR-L1", "in advance (Form HR-L1)"),
    (r"to the following calendar year", "to the next year"),
    (r"the following year", "the next year"),
    (r"of the following year", "of the next year"),
    (r"from a registered medical practitioner", "from a registered practitioner"),
    (r"within 48 hours of returning to work", "within 48h of return"),
    (r"under any circumstances", "(no exceptions)"),
    (r"regardless of duration", "regardless of length"),
    (r"regardless of subsequent approval", "even if later approved"),
    (r"for the purposes of seniority, increments, or retirement benefits",
     "toward seniority/increments/retirement"),
    (r"working days", "days"),
    (r"exceptional circumstances are demonstrated in writing",
     "exceptional circumstances shown in writing"),
    (r"within 30 days of the child's birth", "within 30 days of birth"),
    (r"at the time of retirement or resignation", "at retirement/resignation"),
    (r"subject to a maximum of", "up to"),
    (r"^Each\s+", ""),
    (r"immediately before or after", "adjacent to"),
    (r"all applicable paid leave entitlements", "all paid leave"),
    (r"\.\s*Manager approval alone is not sufficient\.?",
     " (manager alone insufficient)."),
    (r"to be taken within", "usable within"),
]

def _condense_clause(clause_id: str, raw_text: str, is_tracked: bool) -> str:
    text = re.sub(r"^\d+\.\d+\s+", "", raw_text).strip()
    text = re.sub(r"\s+", " ", text)
    original_length = len(text)

    if is_tracked:
        # Enforce Rule 4: If a clause cannot be summarised without meaning loss, quote it verbatim and flag it.
        # Tracked clauses have explicit conditions/binding verbs we must not risk modifying heuristically,
        # so we default to [VERBATIM] tagging them per agents.md / skills.md specs.
        return f"[VERBATIM — summarisation would alter meaning] {text}"
    else:
        for pattern, replacement in _CONDENSATION_RULES:
            text = re.sub(pattern, replacement, text)
        
        # If it wasn't meaningfully condensed (e.g. less than 10% shorter), tag it VERBATIM too per Rule 4
        if len(text) > original_length * 0.9:
            return f"[VERBATIM — summarisation would alter meaning] {text}"
        
    return text.strip()


def summarize_policy_rulebased(structured: dict[str, dict[str, str]]) -> str:
    flat = _flatten_clauses(structured)
    missing = [c for c in TRACKED_CLAUSES if c not in flat]
    if missing:
        raise ValueError(f"Missing tracked clauses: {', '.join(missing)}")

    lines: list[str] = ["HR LEAVE POLICY — SUMMARY", "=" * 50, ""]

    for sec_num in sorted(structured.keys(), key=int):
        sec_data = structured[sec_num]
        title = sec_data.get("_title", f"SECTION {sec_num}")
        lines.append(f"{sec_num}. {title}")
        lines.append("-" * 40)

        clause_ids = sorted([k for k in sec_data if k != "_title"], key=lambda x: float(x))
        for clause_id in clause_ids:
            raw_text = sec_data[clause_id]
            is_tracked = clause_id in TRACKED_CLAUSES
            condensed = _condense_clause(clause_id, raw_text, is_tracked)
            lines.append(f"  [{clause_id}] {condensed}")
        lines.append("")

    summary = "\n".join(lines)
    return summary

# ═════════════════════════════════════════════════════════════════════════
# POST-GENERATION VALIDATION
# ═════════════════════════════════════════════════════════════════════════

def _validate_summary(summary: str, flat_clauses: dict[str, str]) -> None:
    errors_found = False

    for clause_id in TRACKED_CLAUSES:
        if f"[{clause_id}]" not in summary:
            print(f"⚠ HARD FAILURE: Tracked clause [{clause_id}] not found in summary.", file=sys.stderr)
            errors_found = True

    if "[5.2]" in summary:
        idx = summary.index("[5.2]")
        next_clause = summary.find("\n  [", idx + 5)
        section = summary[idx:next_clause] if next_clause > 0 else summary[idx:]
        section_lower = section.lower()
        if not ("department head" in section_lower and "hr director" in section_lower):
            print("⚠ CONDITION-DROP FAILURE: Clause [5.2] must mention BOTH Department Head AND HR Director.", file=sys.stderr)
            errors_found = True

    summary_lower = summary.lower()
    for marker in SCOPE_BLEED_MARKERS:
        if marker.lower() in summary_lower:
            print(f"⚠ SCOPE BLEED: Forbidden phrase: \"{marker}\"", file=sys.stderr)
            errors_found = True

    for clause_id, verbs in BINDING_VERBS.items():
        tag = f"[{clause_id}]"
        if tag in summary:
            idx = summary.index(tag)
            next_clause = summary.find("\n  [", idx + 5)
            clause_text = summary[idx:next_clause] if next_clause > 0 else summary[idx:]
            clause_lower = clause_text.lower()
            for verb in verbs:
                if verb.lower() not in clause_lower:
                    print(f"⚠ OBLIGATION SOFTENING: Binding verb \"{verb}\" missing from [{clause_id}].", file=sys.stderr)
                    errors_found = True

    if not errors_found:
        print("✓ All enforcement checks passed.", file=sys.stderr)


# ═════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="UC-0B: Policy Summarisation Agent"
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--no-llm", action="store_true")
    args = parser.parse_args()

    print(f"📄 Loading policy from: {args.input}")
    structured = retrieve_policy(args.input)
    flat = _flatten_clauses(structured)
    print(f"   Found {len(flat)} clauses across {len(structured)} sections.")

    present = [c for c in TRACKED_CLAUSES if c in flat]
    print(f"   Tracked clauses found: {len(present)}/{len(TRACKED_CLAUSES)}")

    if args.no_llm:
        print("📝 Generating summary (rule-based, no LLM)...")
        summary = summarize_policy_rulebased(structured)
    else:
        print("🤖 Generating summary (LLM-based)...")
        try:
            summary = summarize_policy_llm(structured)
            _validate_summary(summary, flat)
        except Exception as e:
            print(f"   ⚠ LLM failed: {e}", file=sys.stderr)
            print("   Falling back to rule-based summarisation...", file=sys.stderr)
            summary = summarize_policy_rulebased(structured)
            _validate_summary(summary, flat)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"✅ Summary written to: {args.output}")

if __name__ == "__main__":
    main()
