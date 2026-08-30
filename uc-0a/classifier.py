"""
UC-0A — Complaint Classifier
Built using RICE → agents.md → skills.md → CRAFT workflow.
Enforces: fixed taxonomy, severity-keyword Urgent detection, mandatory reason field, NEEDS_REVIEW flagging.
"""
import argparse
import csv
import sys
import re

# ─── Classification Schema (from agents.md) ─────────────────────────────────

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords that MUST trigger Urgent (enforcement rule 2)
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# Category keyword mapping — deterministic, ordered by specificity
CATEGORY_RULES = [
    # (category, list of keywords to match in description)
    ("Drain Blockage",   ["drain blocked", "drain completely blocked", "stormwater drain", "main drain blocked", "drain blocked"]),
    ("Flooding",         ["flood", "flooded", "flooding", "floodwater", "waterlogged", "inundated", "submerged"]),
    ("Pothole",          ["pothole", "potholes", "crater", "wheel", "vehicles sinking"]),
    ("Road Damage",      ["road collapsed", "road collapse", "collapsed", "road damage", "road broken", "road caved", "road sinking", "road deteriorat"]),
    ("Streetlight",      ["streetlight", "street light", "lamp", "light not working", "dark road", "no lighting"]),
    ("Waste",            ["garbage", "waste", "trash", "rubbish", "litter", "dumping", "dump", "debris", "refuse"]),
    ("Noise",            ["noise", "drilling", "construction noise", "loud", "sound", "idling", "engine on"]),
    ("Heritage Damage",  ["heritage", "monument", "historical", "ancient", "old city", "heritage zone"]),
    ("Heat Hazard",      ["heat", "temperature", "hot", "heatwave", "heat hazard", "heat stress"]),
]


def detect_severity(description: str) -> bool:
    """Return True if any severity keyword is present in description (case-insensitive)."""
    desc_lower = description.lower()
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            return True
    return False


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag

    Enforcement (from agents.md):
    1. Category must be exactly one of 10 allowed values.
    2. Priority = Urgent if any severity keyword in description.
    3. Reason must quote specific words from description.
    4. Flag = NEEDS_REVIEW if genuinely ambiguous.
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()

    # Handle missing description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided — cannot classify.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = description.lower()

    # ── Step 1: Determine category using keyword rules ──────────────────────
    matched_category = None
    matched_keyword = None

    for category, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in desc_lower:
                matched_category = category
                matched_keyword = kw
                break
        if matched_category:
            break

    flag = ""
    if matched_category is None:
        matched_category = "Other"
        flag = "NEEDS_REVIEW"

    # ── Step 2: Determine priority using severity keywords (enforcement rule 2) ──
    is_urgent = detect_severity(description)

    if is_urgent:
        priority = "Urgent"
        # Find the actual keyword that triggered Urgent for the reason field
        urgent_word = next(kw for kw in SEVERITY_KEYWORDS if kw in desc_lower)
    else:
        # Standard = clear infrastructure failure; Low = minor/nuisance
        # Heuristic: if multiple complaints or high days_open, Standard
        # Default to Standard for reported infrastructure issues
        days_open = row.get("days_open", "0")
        try:
            days = int(days_open)
        except (ValueError, TypeError):
            days = 0

        # Noise/minor complaints with low impact → Low
        if matched_category in ("Noise",) and days < 5:
            priority = "Low"
        else:
            priority = "Standard"
        urgent_word = None

    # ── Step 3: Build reason field quoting specific words from description ──
    # Extract a meaningful fragment from the actual description
    # Find the first sentence or significant phrase
    sentences = re.split(r'[.!?]', description)
    first_meaningful = sentences[0].strip() if sentences else description[:80]

    if is_urgent:
        reason = (
            f"Description contains severity keyword '{urgent_word}': "
            f"\"{first_meaningful}\" — classified Urgent per enforcement rules."
        )
    elif matched_category == "Other":
        reason = (
            f"Description \"{first_meaningful}\" does not match any defined category — "
            f"flagged for manual review."
        )
    else:
        reason = (
            f"Description contains '{matched_keyword}': "
            f"\"{first_meaningful}\" — classified as {matched_category}."
        )

    return {
        "complaint_id": complaint_id,
        "category": matched_category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Handles bad rows without crashing — logs errors to stderr.
    """
    results = []
    error_count = 0

    try:
        with open(input_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Could not read input file: {e}", file=sys.stderr)
        sys.exit(1)

    for i, row in enumerate(rows, start=1):
        try:
            result = classify_complaint(row)
            results.append(result)
        except Exception as e:
            error_count += 1
            complaint_id = row.get("complaint_id", f"row_{i}")
            print(f"ERROR: Row {i} ({complaint_id}): {e}", file=sys.stderr)
            results.append({
                "complaint_id": complaint_id,
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification error: {e}",
                "flag": "NEEDS_REVIEW"
            })

    # Write output CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} complaints ({error_count} errors).")
    if error_count > 0:
        print(f"Check stderr for {error_count} classification errors.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
