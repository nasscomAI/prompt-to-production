"""
UC-0A — Complaint Classifier
Implementation based on RICE enforcement rules and schema defined in README.md, agents.md, and skills.md.
"""
import argparse
import csv
import re

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

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()
    days_open_raw = row.get("days_open", "0").strip()
    
    try:
        days_open = int(days_open_raw)
    except ValueError:
        days_open = 0

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing description text in complaint row.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = description.lower()

    # 1. Determine Priority based on severity keywords
    urgent_triggers = []
    for kw in SEVERITY_KEYWORDS:
        if kw == "injury" and ("injur" in desc_lower):
            urgent_triggers.append("injury")
        elif kw == "hospital" and ("hospital" in desc_lower):
            urgent_triggers.append("hospital")
        elif kw == "fell" and ("fell" in desc_lower or "fall" in desc_lower):
            urgent_triggers.append("fell")
        elif kw == "collapse" and ("collaps" in desc_lower):
            urgent_triggers.append("collapse")
        elif kw in desc_lower:
            urgent_triggers.append(kw)

    if urgent_triggers:
        priority = "Urgent"
    else:
        priority = "Standard"

    # 2. Category matching logic
    cat_scores = {cat: 0 for cat in ALLOWED_CATEGORIES}

    # Pothole
    if "pothole" in desc_lower:
        cat_scores["Pothole"] += 5

    # Flooding
    if any(w in desc_lower for w in ["flood", "waterlog", "water standing", "inundat", "submerged"]):
        cat_scores["Flooding"] += 4

    # Drain Blockage
    if ("drain" in desc_lower and any(w in desc_lower for w in ["block", "clog", "debris", "overflow", "mosquito"])) or "stormwater drain" in desc_lower:
        cat_scores["Drain Blockage"] += 4

    # Streetlight
    if any(w in desc_lower for w in ["streetlight", "lamp post", "unlit", "substation tripped", "wiring theft"]) or ("light" in desc_lower and ("out" in desc_lower or "flicker" in desc_lower or "dark" in desc_lower)):
        cat_scores["Streetlight"] += 4

    # Waste
    if any(w in desc_lower for w in ["garbage", "waste", "trash", "dumped", "dead animal", "refuse", "bins overflowing"]):
        cat_scores["Waste"] += 4

    # Noise
    if any(w in desc_lower for w in ["music", "noise", "amplifier", "drilling", "club", "loud"]):
        cat_scores["Noise"] += 4

    # Heritage Damage
    if any(w in desc_lower for w in ["heritage", "historic", "ancient", "museum", "precinct"]):
        cat_scores["Heritage Damage"] += 4

    # Heat Hazard
    if any(w in desc_lower for w in ["heat", "temperature", "44°c", "45°c", "52°c", "melting", "bubbling", "burns", "sun", "heatwave"]):
        cat_scores["Heat Hazard"] += 4

    # Road Damage
    if any(w in desc_lower for w in ["road surface", "cracked", "sinking", "road collapse", "footpath", "tiles", "subsidence", "tarmac", "manhole", "crater", "cobblestones"]):
        cat_scores["Road Damage"] += 3

    # Filter categories with non-zero scores
    active_cats = {c: s for c, s in cat_scores.items() if s > 0 and c != "Other"}

    flag = ""
    if not active_cats:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(active_cats) > 1:
        sorted_cats = sorted(active_cats.items(), key=lambda x: x[1], reverse=True)
        if sorted_cats[0][1] > sorted_cats[1][1]:
            category = sorted_cats[0][0]
            if sorted_cats[1][1] >= 3:
                flag = "NEEDS_REVIEW"
        else:
            category = sorted_cats[0][0]
            flag = "NEEDS_REVIEW"
    else:
        category = list(active_cats.keys())[0]

    if category == "Other":
        flag = "NEEDS_REVIEW"

    # 3. Formulate one-sentence reason citing description terms
    phrases = description.split(".")
    first_clause = phrases[0].strip() if phrases else description

    if urgent_triggers:
        reason = f"Classified as {category} with Urgent priority due to '{urgent_triggers[0]}' safety trigger in '{first_clause}'."
    else:
        reason = f"Classified as {category} with {priority} priority based on description phrase '{first_clause}'."

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
    """
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    results = []

    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified_row = classify_complaint(row)
            except Exception as e:
                classified_row = {
                    "complaint_id": row.get("complaint_id", "UNKNOWN"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Processing error encountered: {str(e)}.",
                    "flag": "NEEDS_REVIEW"
                }
            results.append(classified_row)

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
