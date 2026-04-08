"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md → CRAFT workflow.
Enforcement rules are directly reflected in classify_complaint().
"""
import argparse
import csv
import sys

# --- Enforcement: exact allowed categories (from agents.md) ---
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

# --- Enforcement: keywords that must trigger Urgent priority ---
URGENT_KEYWORDS = [
    "injury", "injured", "child", "children", "school",
    "hospital", "ambulance", "fire", "hazard", "fell",
    "fall", "collapse", "collapsed", "risk", "danger",
    "stranded", "electrical",
]

# --- Category keyword mapping (order matters: most specific first) ---
CATEGORY_RULES = [
    ("Heritage Damage",  ["heritage", "historic", "monument", "heritage street"]),
    ("Flooding",         ["flood", "flooded", "flooding", "waterlogged", "inundated", "knee-deep"]),
    ("Drain Blockage",   ["drain", "drainage", "blocked drain", "drain blocked", "sewage"]),
    ("Pothole",          ["pothole", "pot hole", "pothole"]),
    ("Streetlight",      ["streetlight", "street light", "light out", "lights out", "sparking", "flickering"]),
    ("Waste",            ["garbage", "waste", "rubbish", "trash", "litter", "overflowing bin", "dead animal"]),
    ("Noise",            ["noise", "music", "loud", "sound", "playing music"]),
    ("Road Damage",      ["road", "road surface", "cracked", "sinking", "footpath", "tiles", "manhole", "broken pavement"]),
    ("Heat Hazard",      ["heat", "temperature", "hot"]),
]


def _detect_category(description: str) -> tuple[str, bool]:
    """Return (category, is_ambiguous) based on description keywords."""
    desc_lower = description.lower()
    matched = []
    for category, keywords in CATEGORY_RULES:
        if any(kw in desc_lower for kw in keywords):
            matched.append(category)

    if len(matched) == 1:
        return matched[0], False
    elif len(matched) > 1:
        # Return the first (highest priority) match but flag ambiguity
        return matched[0], True
    else:
        return "Other", True


def _detect_priority(description: str) -> str:
    """Return Urgent, Standard, or Low based on description keywords."""
    desc_lower = description.lower()
    if any(kw in desc_lower for kw in URGENT_KEYWORDS):
        return "Urgent"
    # Standard: a clear civic issue but no safety keywords
    return "Standard"


def _build_reason(description: str, category: str, priority: str) -> str:
    """Build a reason sentence citing specific words from the description."""
    desc_lower = description.lower()

    # Find an urgent keyword cited if priority is Urgent
    urgent_word = next((kw for kw in URGENT_KEYWORDS if kw in desc_lower), None)
    # Find a category keyword cited
    cat_keywords = next((kws for cat, kws in CATEGORY_RULES if cat == category), [])
    cat_word = next((kw for kw in cat_keywords if kw in desc_lower), None)

    parts = []
    if cat_word:
        parts.append(f'"{cat_word}" maps to {category}')
    if urgent_word:
        parts.append(f'"{urgent_word}" triggers Urgent priority')

    if parts:
        return "; ".join(parts) + "."
    return f'Classified as {category}/{priority} based on description content.'


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Enforcement rules from agents.md:
    1. Category is one of the 9 allowed values or Other.
    2. Priority = Urgent if description contains any severity keyword.
    3. Every row has a reason citing specific words from the description.
    4. Ambiguous categories → Other + NEEDS_REVIEW flag.
    """
    description = (row.get("description") or "").strip()
    complaint_id = row.get("complaint_id", "UNKNOWN")

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description missing — cannot classify.",
            "flag": "NEEDS_REVIEW",
        }

    category, is_ambiguous = _detect_category(description)
    priority = _detect_priority(description)
    reason = _build_reason(description, category, priority)
    flag = "NEEDS_REVIEW" if is_ambiguous else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Never crashes on a bad row — errors are logged and written as ERROR rows.
    Prints summary: total processed, NEEDS_REVIEW count, error count.
    """
    total = 0
    needs_review = 0
    errors = 0
    results = []

    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        print(f"[ERROR] Could not read input file: {e}", file=sys.stderr)
        sys.exit(1)

    for row in rows:
        total += 1
        try:
            result = classify_complaint(row)
        except Exception as e:
            print(f"[WARN] Row {row.get('complaint_id', '?')} failed: {e}", file=sys.stderr)
            result = {
                "complaint_id": row.get("complaint_id", "UNKNOWN"),
                "category": "ERROR",
                "priority": "Low",
                "reason": "Classification failed — see logs.",
                "flag": "NEEDS_REVIEW",
            }
            errors += 1

        # Merge original row with classification result
        out_row = dict(row)
        out_row.update(result)
        results.append(out_row)

        if result.get("flag") == "NEEDS_REVIEW":
            needs_review += 1

    # Determine output fieldnames
    if results:
        fieldnames = list(results[0].keys())
    else:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Summary
    print(f"Classification complete.")
    print(f"  Total rows processed : {total}")
    print(f"  NEEDS_REVIEW flagged : {needs_review}")
    print(f"  Errors               : {errors}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
