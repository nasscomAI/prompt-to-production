"""
UC-0A — Complaint Classifier
Implementation based on RICE prompt, agents.md, skills.md, and README.md schema enforcement.
"""
import argparse
import csv
import re
import os

# Allowed categories exact strings
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
    "Other"
]

# Severity keywords that must trigger Urgent priority (including word form variations)
SEVERITY_KEYWORDS = [
    "injury", "injuries", "injured", "injuring",
    "child", "children",
    "school", "schools",
    "hospital", "hospitals", "hospitalised", "hospitalized", "hospitalisation", "hospitalization",
    "ambulance", "ambulances",
    "fire", "fires",
    "hazard", "hazards", "hazardous",
    "fell", "fall", "falling", "falls",
    "collapse", "collapses", "collapsed", "collapsing"
]

SEVERITY_PATTERN = re.compile(
    r'\b(' + '|'.join(SEVERITY_KEYWORDS) + r')\b',
    re.IGNORECASE
)


def format_reason(category: str, priority: str, desc: str, triggered_word: str = None) -> str:
    """
    Format rationale as exactly one sentence citing specific words from description.
    Guarantees clean punctuation without duplicate trailing periods or quotes.
    """
    clean_desc = desc.strip()
    if len(clean_desc) > 85:
        quote = clean_desc[:82].rstrip() + "..."
    else:
        quote = clean_desc.rstrip(".")

    if triggered_word:
        return f"Classified as {category} with Urgent priority due to severity keyword '{triggered_word}' in quote '{quote}'."
    else:
        return f"Classified as {category} with {priority} priority citing '{quote}'."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns dictionary containing original fields plus: category, priority, reason, flag
    """
    desc = (row.get("description") or "").strip()
    days_open_val = row.get("days_open", 0)
    try:
        days_open = int(days_open_val)
    except (ValueError, TypeError):
        days_open = 0

    category = "Other"
    priority = "Standard"
    flag = ""

    # Check for missing or empty description
    if not desc:
        return {
            **row,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing or empty complaint description.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = desc.lower()

    # Category matching precedence rules based on exact schema
    if any(k in desc_lower for k in ["pothole", "potholes", "pit in road"]):
        category = "Pothole"
    elif any(k in desc_lower for k in ["drain blocked", "drainage blocked", "stormwater drain", "main drain", "drain clogging", "manhole"]):
        category = "Drain Blockage"
    elif any(k in desc_lower for k in ["flood", "floods", "flooded", "flooding", "waterlogging", "waterlogged", "water standing", "rainwater", "underpass flooded", "inundated"]):
        category = "Flooding"
    elif any(k in desc_lower for k in ["streetlight", "streetlights", "lights out", "unlit", "darkness", "flickering", "wiring theft"]):
        category = "Streetlight"
    elif any(k in desc_lower for k in ["waste", "garbage", "bins overflowing", "dumped", "dead animal", "litter", "rubbish"]):
        category = "Waste"
    elif any(k in desc_lower for k in ["music", "drilling", "amplifier", "amplifiers", "noise", "loud", "wedding band"]):
        category = "Noise"
    elif any(k in desc_lower for k in ["melting", "44°c", "45°c", "52°c", "heatwave", "surface temperature", "dividers storing heat", "full sun", "temperatures"]):
        category = "Heat Hazard"
    elif any(k in desc_lower for k in ["heritage", "historic", "ancient step well", "heritage stone", "tagore museum", "cobblestones broken", "billboard"]):
        category = "Heritage Damage"
    elif any(k in desc_lower for k in ["cracked", "sinking", "subsided", "subsidence", "collapsed", "crater", "buckled", "footpath", "road surface", "paving"]):
        category = "Road Damage"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Enforce priority rule based on severity keywords
    severity_match = SEVERITY_PATTERN.search(desc)
    if severity_match:
        priority = "Urgent"
        triggered_word = severity_match.group(0)
        reason = format_reason(category, priority, desc, triggered_word=triggered_word)
    else:
        if days_open < 5:
            priority = "Low"
        else:
            priority = "Standard"
        reason = format_reason(category, priority, desc)

    # Set review flag if category is Other
    if category == "Other":
        flag = "NEEDS_REVIEW"

    # Construct clean result dictionary preserving all input columns
    result = dict(row)
    result["category"] = category
    result["priority"] = priority
    result["reason"] = reason
    result["flag"] = flag

    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Handles missing fields, avoids crashing on bad rows, and outputs all records.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results = []
    fieldnames = []

    with open(input_path, mode="r", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        fieldnames = list(reader.fieldnames or [])

        # Ensure output fieldnames include category, priority, reason, flag
        for col in ["category", "priority", "reason", "flag"]:
            if col not in fieldnames:
                fieldnames.append(col)

        for row in reader:
            try:
                classified_row = classify_complaint(row)
                results.append(classified_row)
            except Exception as e:
                # Fallback for corrupt rows to prevent batch execution failure
                row_copy = dict(row)
                row_copy["category"] = "Other"
                row_copy["priority"] = "Low"
                row_copy["reason"] = f"Processing error: {str(e)}"
                row_copy["flag"] = "NEEDS_REVIEW"
                results.append(row_copy)

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
