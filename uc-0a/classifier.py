"""
UC-0A — Complaint Classifier
Built using RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
import sys

# ───────────────────────────────────────────────────────────────
# Output column order
# ───────────────────────────────────────────────────────────────
OUTPUT_COLUMNS = ["complaint_id", "category", "priority", "reason", "flag"]

# ───────────────────────────────────────────────────────────────
# Allowed category strings (exact, case-sensitive)
# ───────────────────────────────────────────────────────────────
CATEGORIES = (
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other",
)

# ───────────────────────────────────────────────────────────────
# Severity keywords that must trigger Urgent priority
# (case-insensitive substring match on the description)
# ───────────────────────────────────────────────────────────────
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
]

# ───────────────────────────────────────────────────────────────
# Category → list of phrase patterns (lowercase, substring/regex)
# Each pattern is compiled at module load.  The first matching
# phrase provides the verbatim snippet used in the output reason.
# ───────────────────────────────────────────────────────────────
CATEGORY_PATTERNS = {
    "Pothole":      [r"\bpotholes?\b"],
    "Flooding":     [r"\bflood\w*\b", r"\bknee-deep\b", r"\bstanding in water\b",
                     r"\binundat\w*\b", r"\bwater\s+logg\w*\b"],
    "Streetlight":  [r"\blights?\s+out\b", r"\bstreet[-\s]?lights?\b",
                     r"\blamp\s?post\w*\b", r"\bstreet\s+lighting\b"],
    "Waste":        [r"\bgarbage\b", r"\bwaste\b", r"\btrash\b",
                     r"\blitter\w*\b", r"\bdump(?:ed|ing)?\b", r"\bbins?\b",
                     r"\bdead\s+animal\b", r"\bcarcass\w*\b"],
    "Noise":        [r"\bnoise\b", r"\bnoisy\b", r"\bloud\b",
                     r"\bmusic\b", r"\bamplifier\w*\b", r"\bhonk\w*\b"],
    "Road Damage":  [r"\bcrack\w*\b", r"\bsinking\b", r"\bsubsided\b",
                     r"\buckl\w*\b", r"\bcave-in\b", r"\bmanhole\s+cover\w*\b",
                     r"\bsinkhole\w*\b", r"\broad\s+surface\w*\b"],
    "Heritage Damage": [r"\bheritage\b"],  # post-filter enforces damage-word co-occurrence
    "Heat Hazard":  [r"\bheat\w*\b", r"\bheatwave\w*\b", r"\bheat\s+wave\w*\b",
                     r"\bscorch\w*\b", r"\b44°C\b", r"\b52°C\b", r"\bmelting\b",
                     r"\bburn\w*\b", r"\btemperature\b"],
    "Drain Blockage": [r"\bdrain\w*\b", r"\bblocked\b", r"\bclog\w*\b",
                       r"\boverflow\w*\b", r"\bsewer\w*\b", r"\bdrainage\w*\b"],
}

# Precompile regexes (case‑insensitive) for speed
COMPILED_PATTERNS = {}
for cat, patterns in CATEGORY_PATTERNS.items():
    COMPILED_PATTERNS[cat] = [re.compile(p, re.IGNORECASE) for p in patterns]

# ───────────────────────────────────────────────────────────────
# Helper sets for priority tiering (when NOT Urgent)
# ───────────────────────────────────────────────────────────────
COSMETIC_WORDS = {
    "minor", "cosmetic", "small", "slight", "superficial",
    "aesthetic", "cosmetically",
}


# ───────────────────────────────────────────────────────────────
# Helper: count how many compiled regexes match the lowered text
# ───────────────────────────────────────────────────────────────
def _count_matches(desc_lower: str, compiled: list) -> int:
    return sum(1 for r in compiled if r.search(desc_lower))


# ───────────────────────────────────────────────────────────────
# Helper: return the verbatim text of the first matching regex
# ───────────────────────────────────────────────────────────────
def _first_match(desc_lower: str, compiled: list) -> str | None:
    for r in compiled:
        m = r.search(desc_lower)
        if m:
            return m.group(0)
    return None


# ───────────────────────────────────────────────────────────────
# Helper: true if any word from word_set appears as substring in text
# ───────────────────────────────────────────────────────────────
def _any_word_present(text: str, word_set: set) -> bool:
    return any(w in text for w in word_set)


# ───────────────────────────────────────────────────────────────
# Heritage Damage post-filter: only count the category when BOTH
# "heritage" appears AND a damage indicator word is also present.
# This prevents "heritage" from being treated as location flavour
# (e.g. "Heritage lamp post", "Heritage area affected").
# ───────────────────────────────────────────────────────────────
def _apply_heritage_filter(scores: dict, desc_lower: str) -> dict:
    if "Heritage Damage" not in scores:
        return scores
    has_heritage = "heritage" in desc_lower
    heritage_damage_indicators = {
        "knocked", "toppled", "overturned", "crumbl", "defac",
        "collaps", "deteriorat", "erod", "break", "shatter",
    }
    has_damage = any(ind in desc_lower for ind in heritage_damage_indicators)
    if not (has_heritage and has_damage):
        scores["Heritage Damage"] = 0
    return scores


# ───────────────────────────────────────────────────────────────
# Build a one-sentence reason citing a word/phrase from the
# description.  The reason must be exactly one sentence.
# ───────────────────────────────────────────────────────────────
def _reason_clear(category: str, matched_phrase: str | None) -> str:
    if matched_phrase:
        # Matched phrases from regex are typically single words/short phrases
        # with no internal periods, so the sentence stays simple.
        return f'The description mentions "{matched_phrase}", which indicates {category}.'
    # Fallback: pick the first word from the original description
    first_word = (desc_original.split()[0] if "desc_original" in dir() else "detail")
    return f'The description cites "{first_word}", indicating {category}.'


def _reason_other() -> str:
    """No standard category applies – cite a word from the description."""
    # We'll pass the description words in from classify_complaint;
    # this signature is kept for possible alternative use.
    return 'No standard category applies; description includes detail.'


# ───────────────────────────────────────────────────────────────
def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.

    Returns a dict with keys: complaint_id, category, priority, reason, flag.

    Enforcement (from agents.md):
    - category must be exactly one of the 10 allowed values
    - priority is Urgent if any severity keyword appears in the description,
      otherwise Standard (ongoing harm) or Low (minor / cosmetic)
    - reason is one sentence quoting at least one word from the description
    - flag is NEEDS_REVIEW exactly when the description does not determine
      a single category (tie or no matches), otherwise blank
    """
    complaint_id = str(row.get("complaint_id", "")).strip()
    description = row.get("description")
    desc_original = description if description else ""
    desc_lower = desc_original.lower()

    # ── Empty / missing description ───────────────────────────────────────
    if not desc_original or not desc_original.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No usable detail was provided in the description.",
            "flag": "NEEDS_REVIEW",
        }

    # ── Priority: Urgent if any severity keyword present ──────────────────
    urgency = any(kw in desc_lower for kw in SEVERITY_KEYWORDS)
    priority = "Urgent" if urgency else None  # determine later

    # ── Score every category via pattern matches ──────────────────────────
    scores = {}
    first_phrases = {}  # cat → first matched verbatim phrase
    for cat, compiled in COMPILED_PATTERNS.items():
        cnt = _count_matches(desc_lower, compiled)
        scores[cat] = cnt
        if cnt > 0:
            m = _first_match(desc_lower, compiled)
            if m:
                first_phrases[cat] = m

    # ── Apply Heritage Damage filter (heritage + damage word required) ────
    scores = _apply_heritage_filter(scores, desc_lower)

    # ── Determine top category / tie ──────────────────────────────────────
    max_score = max(scores.values()) if scores else 0
    top_categories = [cat for cat, s in scores.items() if s == max_score]

    if max_score == 0:
        # Nothing matched any pattern → genuine ambiguity / no signal
        category = "Other"
        tie = False
        flag = "NEEDS_REVIEW"
        reason = _reason_other_generic(desc_original)
    elif len(top_categories) == 1:
        category = top_categories[0]
        tie = False
        flag = ""
        mp = first_phrases.get(category)
        reason = _reason_clear(category, mp)
    else:
        # Genuine ambiguity between two or more categories
        category = "Other"
        tie = True
        flag = "NEEDS_REVIEW"
        # Pick a phrase from any top category for the reason
        mp = None
        for cat in top_categories:
            if cat in first_phrases:
                mp = first_phrases[cat]
                break
        reason = _reason_other_with_phrase(desc_original, mp)

    # ── Priority: Urgent overrides; else Standard / Low ─────────────────────
    if urgency:
        priority = "Urgent"
    else:
        has_cosmetic = _any_word_present(desc_lower, COSMETIC_WORDS)
        if has_cosmetic:
            priority = "Low"
        else:
            priority = "Standard"

    # ── Final return ───────────────────────────────────────────────────────
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def _reason_other_generic(desc_original: str) -> str:
    """No pattern matched – cite first substantive word from the description."""
    words = [w for w in desc_original.split() if len(w) > 2]
    if words:
        return f'No standard category applies; description includes "{words[0]}".'
    return 'No standard category applies; description includes detail.'


def _reason_other_with_phrase(desc_original: str, mp: str | None) -> str:
    if mp:
        return f'No standard category applies; description includes "{mp}".'
    return _reason_other_generic(desc_original)


# ───────────────────────────────────────────────────────────────
def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    # Fast‑fail if input file cannot be opened – before any output is written
    try:
        f_in = open(input_path, newline="", encoding="utf-8-sig")
    except FileNotFoundError:
        sys.exit(f"Error: input file not found: {input_path}")
    except OSError as e:
        sys.exit(f"Error: cannot read input file '{input_path}': {e}")

    # Check for empty file
    first_line = f_in.readline()
    if not first_line.strip():
        f_in.close()
        with open(output_path, "w", newline="", encoding="utf-8") as f_out:
            f_out.write("complaint_id,category,priority,reason,flag\n")
        print("No rows to process; empty output written.")
        return

    # Prepare reader and output
    reader = csv.DictReader(f_in)
    f_in.seek(0)  # reset to start for full re‑read by DictReader

    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=OUTPUT_COLUMNS)
            writer.writeheader()

            processed = 0
            flagged = 0

            for row in reader:
                processed += 1
                try:
                    result = classify_complaint(row)
                except Exception as e:
                    # Unexpected error on a row – fall back to a safe Other row
                    result = {
                        "complaint_id": row.get("complaint_id", "").strip() or f"row-{processed}",
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Row could not be classified: {e}",
                        "flag": "NEEDS_REVIEW",
                    }

                writer.writerow(result)
                if result["flag"] == "NEEDS_REVIEW":
                    flagged += 1
    except OSError as e:
        sys.exit(f"Error: could not write output file '{output_path}': {e}")
    finally:
        f_in.close()

    print(f"Processed {processed} rows ({flagged} flagged NEEDS_REVIEW). Results written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)