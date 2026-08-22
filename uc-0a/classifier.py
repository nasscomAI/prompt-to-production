"""
UC-0A — Complaint Classifier
Classifies civic complaints by category and priority using rule-based keyword matching.
Enforcement: strict taxonomy, severity keywords trigger Urgent, reason cites description words.
"""
import argparse
import csv
import re


# ── Allowed categories and their keyword triggers ──────────────────────────
CATEGORY_KEYWORDS = {
    "Pothole":         ["pothole", "pot hole", "crater", "wheel", "tyre damage"],
    "Flooding":        ["flood", "flooded", "waterlog", "water logging", "submerge",
                        "inundat", "rainwater", "stormwater"],
    "Streetlight":     ["streetlight", "street light", "lamp post", "lamp-post",
                        "dark road", "no light", "bulb out", "light not working"],
    "Waste":           ["waste", "garbage", "trash", "rubbish", "litter", "dump",
                        "refuse", "debris pile", "not cleared"],
    "Noise":           ["noise", "drilling", "honking", "loud", "decibel",
                        "sound pollution", "idling", "engines on"],
    "Road Damage":     ["road damage", "road collapse", "collapsed", "cave in",
                        "cave-in", "sinkhole", "road crack", "broken road",
                        "road broke", "road surface"],
    "Heritage Damage": ["heritage", "monument", "historical", "archaeological",
                        "ancient structure"],
    "Heat Hazard":     ["heat", "heatwave", "heat wave", "sunstroke", "dehydrat",
                        "hot surface", "thermal"],
    "Drain Blockage":  ["drain block", "blocked drain", "drain clog", "clogged drain",
                        "choked drain", "drain choke", "drain overflow",
                        "mosquito breeding", "dengue"],
}

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]


def _match_category(description: str) -> tuple:
    """Return (category, matched_keywords) from description text."""
    desc_lower = description.lower()
    best_category = None
    best_count = 0
    best_matched = []
    all_matches = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        matched = [kw for kw in keywords if kw in desc_lower]
        if matched:
            all_matches[category] = matched
            if len(matched) > best_count:
                best_count = len(matched)
                best_category = category
                best_matched = matched

    # Check for ambiguity — multiple categories matched
    ambiguous = len(all_matches) > 1
    if best_category is None:
        return "Other", [], True  # No match → Other + NEEDS_REVIEW

    return best_category, best_matched, ambiguous and best_count == 1


def _check_severity(description: str) -> tuple:
    """Return (is_urgent, matched_severity_keywords)."""
    desc_lower = description.lower()
    matched = [kw for kw in SEVERITY_KEYWORDS if kw in desc_lower]
    return len(matched) > 0, matched


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()
    days_open = 0
    try:
        days_open = int(row.get("days_open", 0))
    except (ValueError, TypeError):
        pass

    # Handle empty description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }

    # Step 1: Determine category
    category, cat_keywords, is_ambiguous = _match_category(description)

    # Step 2: Determine priority via severity keywords
    is_urgent, sev_keywords = _check_severity(description)

    if is_urgent:
        priority = "Urgent"
    elif days_open < 7 and category == "Other":
        priority = "Low"
    else:
        priority = "Standard"

    # Step 3: Build reason citing specific words from description
    cited_words = cat_keywords + sev_keywords
    if cited_words:
        reason = (f"Description mentions '{', '.join(cited_words)}' "
                  f"→ classified as {category} with {priority} priority.")
    else:
        reason = (f"No strong keyword match in description "
                  f"→ classified as {category} with {priority} priority.")

    # Step 4: Flag ambiguous cases
    flag = "NEEDS_REVIEW" if is_ambiguous else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Handles errors per row without crashing the batch.
    """
    results = []
    with open(input_path, "r", newline="", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                # Log error but continue processing
                print(f"WARNING: Failed to classify row {row.get('complaint_id', '?')}: {e}")
                results.append({
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "",
                    "priority": "",
                    "reason": f"Classification error: {e}",
                    "flag": "NEEDS_REVIEW"
                })

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Classified {len(results)} complaints.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
