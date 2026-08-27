"""
UC-0A — Complaint Classifier
Implements classify_complaint and batch_classify as defined in skills.md,
governed by the RICE enforcement rules in agents.md.

Usage:
    python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv
"""
import argparse
import csv
import re
import sys


# ─── Classification Constants ────────────────────────────────────────────────

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

SEVERITY_KEYWORDS = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]


# ─── Category Classification Rules ───────────────────────────────────────────

# Each rule is a tuple: (keywords_to_match, category_if_matched)
# Rules are evaluated in order — first match wins.
# Keywords are case-insensitive.
CATEGORY_RULES = [
    # Pothole — look for pothole(s), crater
    (r"\bpotholes?\b", "Pothole"),
    (r"\bcrater\b", "Pothole"),
    # Flooding — standing water, submerged, waterlogged
    (r"\bflood(?:ed|s|ing)?\b", "Flooding"),
    (r"\bunderwater\b", "Flooding"),
    (r"\bknee.deep\b", "Flooding"),
    # Heritage Damage — heritage structure, historical site damage
    (r"\bheritage\b", "Heritage Damage"),
    (r"\bhistorical\b.*\b(?:damage|vandal|broken)\b", "Heritage Damage"),
    # Drain Blockage — blocked drain, drain clogged, drainage issue
    (r"\bdrain\b.*\b(?:blocked?|clogged?|choked?)\b", "Drain Blockage"),
    (r"\bblocked?\b.*\bdrain\b", "Drain Blockage"),
    (r"\bdrainage\b.*\b(?:blocked?|issue|problem)\b", "Drain Blockage"),
    # Streetlight — streetlight, light out, lamp post
    (r"\bstreetlight", "Streetlight"),
    (r"\blights?\s+out\b", "Streetlight"),
    (r"\blamp\s+post\b", "Streetlight"),
    (r"\bflickering\b.*\blight", "Streetlight"),
    (r"\bspark", "Streetlight"),
    # Waste — garbage, waste, dead animal, bin overflow
    (r"\bgarbage\b", "Waste"),
    (r"\bwaste\b", "Waste"),
    (r"\bdead\s+animal\b", "Waste"),
    (r"\bbins?\b.*\b(?:overflow|full|spill)\b", "Waste"),
    (r"\boverflowing\b.*\b(?:bin|garbage|waste)\b", "Waste"),
    # Noise — noise, loud music, band, amplifiers, disturbance
    (r"\bnoise\b", "Noise"),
    (r"\b(?:band|amplifier)\b", "Noise"),
    (r"\bmusic\b.*\b(?:loud|past\s+midnight|late|2am|11pm|audible)\b", "Noise"),
    (r"\b(?:loud|audible)\b.*\b(?:music|sound)\b", "Noise"),
    # Road Damage — road cracked, road sinking, footpath broken
    (r"\broad\b.*\b(?:cracked?|sinking|damage|broken|buckled|subsided?)\b", "Road Damage"),
    (r"\b(?:cracked?|sinking|buckled|subsided?)\b.*\broad\b", "Road Damage"),
    (r"\bfootpath\b.*\b(?:broken?|damage|upturned)\b", "Road Damage"),
    (r"\broad\s+surface\b", "Road Damage"),
    # Heat Hazard — extreme heat, melting, temperature, burns
    (r"\bheat\b", "Heat Hazard"),
    (r"\b(?:melting|melt)\b", "Heat Hazard"),
    (r"\btemperature", "Heat Hazard"),
    (r"\b(?:44|45|52)\s*°?\s*C\b", "Heat Hazard"),
    (r"\bburns?\b", "Heat Hazard"),
    # Manhole cover missing → Other (not a standard road category)
    (r"\bmanhole\b", "Other"),
]


# ─── Ambiguity Detection ─────────────────────────────────────────────────────

# Patterns that suggest genuine ambiguity between categories
AMBIGUITY_PATTERNS = [
    # Heritage + lights combination (Heritage Damage vs Streetlight)
    (r"\bheritage\b.*\blights?\b", {"Heritage Damage", "Streetlight"}),
    (r"\bheritage\b.*\b(?:street|light|lamppost)\b", {"Heritage Damage", "Streetlight"}),
    # Flooding + drain (Flooding vs Drain Blockage)
    (r"\bflood(?:ed|s|ing)?\b.*\bdrain\b", {"Flooding", "Drain Blockage"}),
]


# ─── classify_complaint ──────────────────────────────────────────────────────

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row per skills.md and agents.md.

    Args:
        row: dict with at minimum 'complaint_id' and 'description' keys.

    Returns:
        dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = (row.get("description") or "").strip()

    # Handle empty description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Empty description — cannot determine category",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower()

    # ── Step 1: Check for severity keywords → Urgent priority ──
    is_urgent = False
    severity_word_found = None
    for kw in SEVERITY_KEYWORDS:
        if re.search(rf"\b{re.escape(kw)}\b", desc_lower):
            is_urgent = True
            severity_word_found = kw
            break

    priority = "Urgent" if is_urgent else "Standard"

    # ── Step 2: Determine category ──
    category = None
    for pattern, cat in CATEGORY_RULES:
        match = re.search(pattern, desc_lower)
        if match:
            category = cat
            break

    if category is None:
        category = "Other"

    # ── Step 3: Check for ambiguity → NEEDS_REVIEW flag ──
    flag = ""
    ambiguous_categories = set()
    for pattern, ambig_set in AMBIGUITY_PATTERNS:
        if re.search(pattern, desc_lower):
            ambiguous_categories = ambig_set
            flag = "NEEDS_REVIEW"
            break

    # ── Step 4: Generate reason ──
    if flag == "NEEDS_REVIEW":
        ambig_desc = " or ".join(sorted(ambiguous_categories))
        phrase = extract_key_phrase(description, 10)
        reason = (
            f"Complaint describes '{phrase}' — "
            f"ambiguous between {ambig_desc}. Set to '{category}' pending review."
        )
    elif is_urgent and severity_word_found:
        phrase = extract_key_phrase(description, 12)
        reason = (
            f"Description mentions '{severity_word_found}' ({phrase}) "
            f"— classified as {category} with Urgent priority."
        )
    else:
        phrase = extract_key_phrase(description, 12)
        reason = (
            f"Description indicates {category.lower()} issue: '{phrase}'."
        )

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def extract_key_phrase(text: str, max_words: int = 10) -> str:
    """Extract a short representative phrase from the beginning of the text."""
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."


# ─── batch_classify ──────────────────────────────────────────────────────────

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.

    Args:
        input_path: Path to the input CSV file.
        output_path: Path to write the results CSV file.

    Per skills.md: never crashes on bad data, processes all rows,
    reports per-row errors, prints summary stats.
    """
    rows = []
    total = 0
    classified = 0
    flagged = 0

    # Read input
    try:
        with open(input_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                total += 1
                try:
                    result = classify_complaint(row)
                    rows.append(result)
                    classified += 1
                    if result["flag"] == "NEEDS_REVIEW":
                        flagged += 1
                except Exception as e:
                    # Per skills.md: never crash on bad row data
                    complaint_id = row.get("complaint_id", "UNKNOWN")
                    rows.append({
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Error processing row: {e}",
                        "flag": "NEEDS_REVIEW",
                    })
                    classified += 1
                    flagged += 1
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Input file not found: {input_path}. "
            f"Ensure the file exists at the specified path."
        )

    # Write output
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Summary stats per skills.md
    print(f"Total rows read:     {total}")
    print(f"Rows classified:     {classified}")
    print(f"Rows flagged:        {flagged}")
    print(f"Results written to:  {output_path}")


# ─── Main Entry Point ────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print("Done.")