"""
UC-0A — Complaint Classifier
Civic Tech Edition: Implements deterministic classification guided by agents.md and skills.md.
"""
import argparse
import csv
import re
import os

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
    "injured",
    "child",
    "children",
    "school",
    "hospital",
    "hospitalised",
    "hospitalized",
    "ambulance",
    "fire",
    "hazard",
    "hazardous",
    "fell",
    "collapse",
    "collapsed",
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes", "crater", "craters", "tyre damage", "blowout", "blowouts"],
    "Flooding": ["flood", "floods", "flooded", "flooding", "waterlogging", "underpass flooded", "rainwater", "rain", "stranded"],
    "Streetlight": ["streetlight", "streetlights", "lights out", "dark at night", "unlit", "darkness", "sparking", "flickering", "substation tripped", "lamp post"],
    "Waste": ["garbage", "waste", "bins", "overflowing garbage", "dead animal", "dumped", "smell affecting", "smell"],
    "Noise": ["music", "wedding", "drilling", "amplifiers", "idling with engines on", "idling", "audible at residential", "5am daily"],
    "Road Damage": ["road surface", "road collapsed", "cracked", "sinking", "subsidence", "buckled", "footpath", "broken bench", "paving", "manhole"],
    "Heritage Damage": ["heritage", "historic", "tram road", "cobblestones", "museum", "billboard", "step well", "ancient"],
    "Heat Hazard": ["melting", "temperature", "temperatures", "heatwave", "burning", "burns", "44°c", "45°c", "52°c", "heat", "full sun"],
    "Drain Blockage": ["drain", "drains", "stormwater drain", "blocked", "blockage", "drainage", "mosquito breeding", "dengue"],
}

LOW_PRIORITY_KEYWORDS = [
    "music",
    "wedding",
    "past midnight",
    "idling",
    "grass dying",
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()
    desc_lower = description.lower()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing or empty description in input record.",
            "flag": "NEEDS_REVIEW",
        }

    # 1. Detect severity keywords for Urgent priority
    matched_severity = []
    for kw in SEVERITY_KEYWORDS:
        pattern = r"\b" + re.escape(kw) + r"\b"
        if re.search(pattern, desc_lower):
            matched_severity.append(kw)

    if matched_severity:
        priority = "Urgent"
        priority_reason = f"severity triggers '{', '.join(matched_severity)}'"
    elif any(re.search(r"\b" + re.escape(kw) + r"\b", desc_lower) for kw in LOW_PRIORITY_KEYWORDS):
        priority = "Low"
        priority_reason = "routine or nuisance complaint with no safety impact"
    else:
        priority = "Standard"
        priority_reason = "standard municipal issue requiring routine resolution"

    # 2. Score categories based on keyword presence
    category_matches = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        found = [kw for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", desc_lower)]
        if found:
            category_matches[cat] = found

    # 3. Determine best category and ambiguity
    flag = ""
    if not category_matches:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Description does not match standard taxonomy keywords; requires human assessment ({priority_reason})."
    else:
        # Sort by number of matched keywords
        sorted_cats = sorted(category_matches.items(), key=lambda item: len(item[1]), reverse=True)
        top_cat, top_keywords = sorted_cats[0]
        category = top_cat

        # Check for ambiguity: multiple categories matched with significant evidence
        if len(sorted_cats) > 1:
            second_cat, second_keywords = sorted_cats[1]
            # If both have evidence or if specific cross-domain terms (e.g. heritage + streetlight/waste) occur
            if len(top_keywords) == len(second_keywords) or "heritage" in desc_lower:
                flag = "NEEDS_REVIEW"
                reason = (
                    f"Classified as {category} based on '{top_keywords[0]}', but flagged NEEDS_REVIEW due to "
                    f"secondary match '{second_cat}' ('{second_keywords[0]}'); priority set to {priority} via {priority_reason}."
                )
                return {
                    "complaint_id": complaint_id,
                    "category": category,
                    "priority": priority,
                    "reason": reason,
                    "flag": flag,
                }

        reason = f"Classified as {category} citing '{top_keywords[0]}' from description; priority set to {priority} via {priority_reason}."

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
    Guarantees that results are written even if individual rows fail.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    classified_rows = []
    fieldnames = ["complaint_id", "date_raised", "city", "ward", "location", "description", "reported_by", "days_open", "category", "priority", "reason", "flag"]

    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                res = classify_complaint(row)
                out_row = dict(row)
                out_row.update(res)
                classified_rows.append(out_row)
            except Exception as e:
                # Do not crash; record fallback with error
                out_row = dict(row)
                out_row.update({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Classification error: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })
                classified_rows.append(out_row)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(classified_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
