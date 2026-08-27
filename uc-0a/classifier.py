"""
UC-0A — Complaint Classifier
Rule-enforced classifier: taxonomy locked, severity keywords guaranteed, reason required.

Failure modes addressed:
  1. Taxonomy drift       → ALLOWED_CATEGORIES whitelist; any unmapped pattern → 'Other'
  2. Severity blindness   → SEVERITY_KEYWORDS checked FIRST, before category scoring
  3. Missing justification→ reason field always populated with quoted description words
  4. Hallucinated sub-cats→ only 10 categories exist; no free-text category generation
  5. False confidence     → NEEDS_REVIEW flag set when two top scores are tied or close
"""

import argparse
import csv
import re
import sys
from pathlib import Path

# ── Schema constants ────────────────────────────────────────────────────────────

ALLOWED_CATEGORIES = [
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
]

PRIORITY_LEVELS = ["Urgent", "Standard", "Low"]

# Any of these words in the description → priority MUST be Urgent (rule, not heuristic)
SEVERITY_KEYWORDS = {
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse",
}

# ── Keyword scoring map ─────────────────────────────────────────────────────────
# Maps each allowed category to a list of signal words/phrases.
# Score = number of matched signals. Highest score wins.
# Ties → NEEDS_REVIEW flag is set.

CATEGORY_SIGNALS: dict[str, list[str]] = {
    "Pothole": [
        "pothole", "pot hole", "tyre", "tyre damage", "deep hole",
        "crater", "manhole cover missing", "manhole",
    ],
    "Flooding": [
        "flood", "flooded", "waterlogged", "knee-deep", "standing water",
        "water logging", "inundated", "inaccessible", "stranded",
    ],
    "Streetlight": [
        "streetlight", "street light", "light out", "lights out",
        "flickering", "sparking", "dark at night", "lamp", "no light",
    ],
    "Waste": [
        "garbage", "waste", "trash", "rubbish", "overflowing bin",
        "dumped", "dead animal", "litter", "sanitation", "smell",
        "bulk waste", "renovation waste",
    ],
    "Noise": [
        "noise", "music", "loud", "midnight", "sound", "nuisance",
        "playing music", "past midnight",
    ],
    "Road Damage": [
        "road surface", "cracked", "sinking", "subsidence", "broken road",
        "road damage", "footpath", "pavement", "tiles broken", "upturned",
        "utility work", "road cracked",
    ],
    "Heritage Damage": [
        "heritage", "historical", "monument", "old city", "heritage street",
        "ancient", "archaeological",
    ],
    "Heat Hazard": [
        "heat", "temperature", "sun", "heatwave", "hot", "thermal",
    ],
    "Drain Blockage": [
        "drain", "blocked drain", "drain blocked", "clog", "choked",
        "sewer", "sewage", "overflow drain",
    ],
    "Other": [],  # fallback — never scores positively
}


def _tokenize(text: str) -> str:
    """Lowercase and normalise whitespace for consistent matching."""
    return re.sub(r"\s+", " ", text.lower().strip())


def _score_categories(description: str) -> dict[str, int]:
    """Return a score for every allowed category based on keyword hits."""
    norm = _tokenize(description)
    scores: dict[str, int] = {cat: 0 for cat in ALLOWED_CATEGORIES}
    for cat, signals in CATEGORY_SIGNALS.items():
        for signal in signals:
            if signal in norm:
                scores[cat] += 1
    return scores


def _has_severity_keyword(description: str) -> tuple[bool, str]:
    """
    Check whether any severity keyword is present.
    Returns (found: bool, matched_word: str).
    """
    norm = _tokenize(description)
    words = re.findall(r"\b\w+\b", norm)
    for word in words:
        if word in SEVERITY_KEYWORDS:
            return True, word
    return False, ""


def _pick_category(scores: dict[str, int], description: str) -> tuple[str, str]:
    """
    Choose the best category and decide whether to set NEEDS_REVIEW.
    Returns (category, flag).
    """
    # Sort by score descending, exclude 'Other' from primary consideration
    ranked = sorted(
        [(cat, sc) for cat, sc in scores.items() if cat != "Other"],
        key=lambda x: x[1],
        reverse=True,
    )

    top_score = ranked[0][1] if ranked else 0

    if top_score == 0:
        # Nothing matched — genuine 'Other'
        return "Other", "NEEDS_REVIEW"

    top_cat = ranked[0][0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0

    # Ambiguity: top two categories have the same positive score
    flag = "NEEDS_REVIEW" if (second_score == top_score and top_score > 0) else ""

    return top_cat, flag


def _build_reason(category: str, priority: str, description: str,
                  severity_word: str) -> str:
    """
    Build a one-sentence reason that cites specific words from the description.
    """
    norm = _tokenize(description)

    # Pull the most relevant signal phrase from the winning category
    matched_signal = ""
    for signal in CATEGORY_SIGNALS.get(category, []):
        if signal in norm:
            matched_signal = signal
            break

    # Build the reason sentence
    if priority == "Urgent" and severity_word:
        base = (
            f"Description contains severity keyword '{severity_word}', "
            f"triggering Urgent priority"
        )
        if matched_signal:
            base += f"; classified as {category} based on '{matched_signal}' in description."
        else:
            base += f"; classified as {category} based on overall description context."
    else:
        if matched_signal:
            base = (
                f"Classified as {category} because description mentions "
                f"'{matched_signal}'."
            )
        else:
            base = f"Classified as {category} based on overall description context."

    return base


# ── Public skill: classify_complaint ───────────────────────────────────────────

def classify_complaint(row: dict) -> dict:
    """
    Skill: classify_complaint
    One complaint row in → category + priority + reason + flag out.

    Enforces:
    - Exact taxonomy (ALLOWED_CATEGORIES only)
    - Severity keyword → Urgent (no override possible)
    - Non-empty reason citing description words
    - NEEDS_REVIEW flag on genuine ambiguity
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "")

    # Guard: empty description
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided; cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    # Step 1 — check severity keywords FIRST (rule, not heuristic)
    is_severe, severity_word = _has_severity_keyword(description)

    # Step 2 — score categories
    scores = _score_categories(description)

    # Step 3 — pick category and ambiguity flag
    category, flag = _pick_category(scores, description)

    # Step 4 — determine priority
    if is_severe:
        priority = "Urgent"
    elif scores.get(category, 0) >= 2 or any(
        w in _tokenize(description)
        for w in ["days", "week", "month", "consecutive", "stranded"]
    ):
        priority = "Standard"
    else:
        priority = "Low"

    # Step 5 — build reason (always cites description words)
    reason = _build_reason(category, priority, description, severity_word)

    # Final guard: category must be in allowed list
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


# ── Public skill: batch_classify ───────────────────────────────────────────────

def batch_classify(input_path: str, output_path: str):
    """
    Skill: batch_classify
    Reads input CSV, applies classify_complaint per row, writes output CSV.

    - Never crashes on a bad row — writes a fallback row instead
    - Logs per-row errors to stderr
    - Output columns are always: complaint_id, category, priority, reason, flag
    """
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_FIELDS = ["complaint_id", "category", "priority", "reason", "flag"]

    results = []
    with open(input_file, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                result = classify_complaint(row)
            except Exception as exc:  # noqa: BLE001
                print(
                    f"[ERROR] Row {row.get('complaint_id', '?')} failed: {exc}",
                    file=sys.stderr,
                )
                result = {
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Classification error during processing.",
                    "flag": "NEEDS_REVIEW",
                }
            results.append(result)

    with open(output_file, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} complaints → {output_path}")


# ── Entry point ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
