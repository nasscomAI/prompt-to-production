"""
UC-0A — Complaint Classifier
Built using RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
import sys

# Enforcement: exact allowed categories — no variations, synonyms, or sub-categories
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Enforcement: severity keywords that must trigger Urgent (case-insensitive)
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# Keyword-to-category mapping based on description content
CATEGORY_KEYWORDS = {
    "Pothole":         ["pothole", "potholes", "manhole"],
    "Flooding":        ["flood", "flooding", "flooded", "submerged", "waterlog", "waterlogged",
                        "inundated", "rainwater", "knee-deep"],
    "Streetlight":     ["streetlight", "street light", "lamp post", "lamp-post", "light pole",
                        "substation", "tripped", "darkness", "power outage", "no light",
                        "lights out", "unlit"],
    "Waste":           ["waste", "garbage", "trash", "rubbish", "litter", "overflowing",
                        "dumping", "sewage", "dead animal", "not removed", "not cleared"],
    "Noise":           ["noise", "loud", "amplifier", "amplifiers", "band playing", "decibel",
                        "honking", "blaring", "music", "drilling", "idling"],
    "Road Damage":     ["road surface", "road damage", "road subsided", "road collapsed",
                        "buckled", "sinking", "broken road", "footpath broken", "paving removed",
                        "road broken", "tyre blowout", "blowouts", "crack", "cracked road",
                        "crater", "collapsed", "tiles broken", "upturned", "subsidence",
                        "broken and sinking", "broken bench"],
    "Heritage Damage": ["heritage", "historic", "monument", "museum", "cobblestone",
                        "cobblestones", "defaced", "billboard"],
    "Heat Hazard":     ["heat", "heatstroke", "sunstroke", "dehydration", "temperature",
                        "melting", "°c", "burns on contact", "full sun"],
    "Drain Blockage":  ["drain", "drainage", "draining", "blocked drain", "clogged",
                        "stormwater", "sewer"],
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using only the description field.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()

    # Error handling: empty or missing description
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = description.lower()

    # Determine priority based on severity keywords
    matched_urgent_keywords = [kw for kw in URGENT_KEYWORDS if kw in desc_lower]
    if matched_urgent_keywords:
        priority = "Urgent"
    else:
        priority = "Standard"

    # Determine category by matching keywords from description
    matched_categories = []
    matched_evidence = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                    matched_evidence[cat] = kw
                break

    # Resolve category
    if len(matched_categories) == 1:
        category = matched_categories[0]
        flag = ""
        reason_keyword = matched_evidence[category]
    elif len(matched_categories) > 1:
        # Pick the first match but flag for review since it's ambiguous
        category = matched_categories[0]
        flag = "NEEDS_REVIEW"
        reason_keyword = matched_evidence[category]
    else:
        # No category matched
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_keyword = None

    # Build reason citing specific words from description
    if reason_keyword:
        if priority == "Urgent":
            urgent_cited = ", ".join(f"'{kw}'" for kw in matched_urgent_keywords)
            reason = (f"Description mentions '{reason_keyword}' indicating {category}, "
                      f"and contains severity keyword(s) {urgent_cited} triggering Urgent priority.")
        else:
            reason = (f"Description mentions '{reason_keyword}' indicating {category}.")
    else:
        reason = "Description does not clearly match any known category."

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
    Continues processing if individual rows fail. Output row count equals input row count.
    """
    try:
        with open(input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)

    results = []
    for row in rows:
        try:
            result = classify_complaint(row)
            results.append(result)
        except Exception as e:
            cid = row.get("complaint_id", "UNKNOWN")
            print(f"Warning: Failed to classify {cid}: {e}", file=sys.stderr)
            results.append({
                "complaint_id": cid,
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification failed: {e}",
                "flag": "NEEDS_REVIEW"
            })

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
