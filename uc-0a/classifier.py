"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", "fire",
    "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "tyre damage", "tire damage", "lane closure", "tyre blowouts", "wheel", "swallowed"],
    "Flooding": ["flooded", "flooding", "flood", "knee-deep", "stranded", "inaccessible", "waterlogged", "underpass floods", "abandoned", "channel rainwater", "flooding risk"],
    "Streetlight": ["streetlight", "street light", "lights out", "flickering", "sparking", "dark at night", "unlit", "wiring theft", "darkness", "substation tripped", "lamp post"],
    "Waste": ["garbage", "waste", "dumped", "dead animal", "overflowing bins", "smell", "not cleared", "bins overflowing", "overflowing", "piles", "photographing piles"],
    "Noise": ["music", "noise", "loud", "playing music", "past midnight", "audible at", "drilling", "wedding band", "amplifiers", "idling", "engines on", "construction drilling", "band playing"],
    "Road Damage": ["road surface", "cracked", "sinking", "footpath tiles", "broken", "upturned", "subsidence", "bubbling", "paving", "bench", "shelter roof", "cobblestones", "buckled", "subsided", "crater", "collapsed", "road collapsed", "road subsided", "gas pipeline", "cable laying"],
    "Heritage Damage": ["heritage", "old city", "heritage street", "ancient", "step well", "heritage area", "heritage zone", "tagore museum", "marble palace", "bow barracks", "heritage precinct", "heritage residential", "historic tram road", "utility work", "stone not replaced", "knocked over", "tram road", "cobblestones"],
    "Heat Hazard": ["heat", "temperature", "hot", "melting", "44°c", "45°c", "52°c", "burns", "storing heat", "unbearable", "dangerous temperatures", "exposed to full sun", "heatwave", "gas leak"],
    "Drain Blockage": ["drain blocked", "drain blockage", "manhole", "manhole cover", "irrigation", "stormwater drain", "construction debris", "mosquito breeding", "draining directly", "main drain blocked", "drain blocked"],
}


def classify_category(description: str) -> tuple[str, bool]:
    """Classify category based on description keywords. Returns (category, is_ambiguous)."""
    desc_lower = description.lower()
    matches = {}
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                matches[category] = matches.get(category, 0) + 1
    
    if not matches:
        return "Other", True
    
    max_count = max(matches.values())
    top_categories = [cat for cat, count in matches.items() if count == max_count]
    
    if len(top_categories) > 1:
        return "Other", True
    
    return top_categories[0], False


def classify_priority(description: str) -> str:
    """Classify priority based on severity keywords."""
    desc_lower = description.lower()
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            return "Urgent"
    
    urgent_indicators = ["risk", "danger", "serious", "emergency", "urgent", "critical"]
    for kw in urgent_indicators:
        if kw in desc_lower:
            return "Urgent"
    
    standard_indicators = ["affecting", "concern", "problem", "issue", "complaint"]
    for kw in standard_indicators:
        if kw in desc_lower:
            return "Standard"
    
    return "Low"


def generate_reason(description: str, category: str, priority: str) -> str:
    """Generate a one-sentence reason citing specific words from description."""
    desc_lower = description.lower()
    
    matched_keywords = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if cat == category:
            for kw in keywords:
                if kw in desc_lower:
                    matched_keywords.append(kw)
    
    severity_matched = []
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            severity_matched.append(kw)
    
    reason_parts = []
    if matched_keywords:
        reason_parts.append(f"category indicated by '{', '.join(matched_keywords)}'")
    if severity_matched:
        reason_parts.append(f"priority '{priority}' due to '{', '.join(severity_matched)}'")
    elif priority == "Urgent":
        for kw in ["risk", "danger", "serious", "emergency", "urgent", "critical"]:
            if kw in desc_lower:
                reason_parts.append(f"priority '{priority}' due to '{kw}'")
                break
    
    if not reason_parts:
        return f"Classified as {category} with {priority} priority based on description."
    
    return " ".join(reason_parts) + "."


def classify_complaint(row: dict) -> dict:
    """Classify a single complaint row."""
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")
    
    category, is_ambiguous = classify_category(description)
    priority = classify_priority(description)
    reason = generate_reason(description, category, priority)
    flag = "NEEDS_REVIEW" if is_ambiguous else ""
    
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """Read input CSV, classify each row, write results CSV."""
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    with open(input_path, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
    
    results = []
    for row in rows:
        try:
            result = classify_complaint(row)
            results.append(result)
        except Exception as e:
            results.append({
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification error: {str(e)}",
                "flag": "NEEDS_REVIEW"
            })
    
    with open(output_path, "w", encoding="utf-8", newline="") as outfile:
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