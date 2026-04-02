import argparse
import csv
import os
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "pot hole", "crater", "pit on road"],
    "Flooding": ["flood", "waterlogging", "water logging", "inundated", "submerged"],
    "Streetlight": ["streetlight", "street light", "lamp post", "light not working", "dark street", "no light"],
    "Waste": ["garbage", "waste", "trash", "dumping", "litter", "rubbish", "bin"],
    "Noise": ["noise", "loud", "sound", "music", "honking", "disturbance"],
    "Road Damage": ["road damage", "broken road", "damaged road", "road crack", "road collapsed"],
    "Heritage Damage": ["heritage", "monument", "historical", "ancient", "temple damage"],
    "Heat Hazard": ["heat", "temperature", "hot", "summer", "heat wave"],
    "Drain Blockage": ["drain", "drainage", "sewer", "blocked drain", "overflow", "manhole"],
}

def classify_complaint(description):
    if not description or not description.strip():
        return {"category": "Other", "priority": "Low", "reason": "No description provided", "flag": "NEEDS_REVIEW"}

    desc_lower = description.lower()

    # Determine priority
    urgent_hit = next((w for w in URGENT_KEYWORDS if w in desc_lower), None)
    priority = "Urgent" if urgent_hit else "Standard"

    # Determine category
    best_category = None
    best_hits = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        hits = [kw for kw in keywords if kw in desc_lower]
        if len(hits) > len(best_hits):
            best_hits = hits
            best_category = cat

    # Check ambiguity
    matched_cats = [cat for cat, keywords in CATEGORY_KEYWORDS.items()
                    if any(kw in desc_lower for kw in keywords)]

    if not best_category:
        category = "Other"
        reason = f"No specific category keywords found in: '{description[:80]}'"
        flag = "NEEDS_REVIEW"
    elif len(matched_cats) > 1:
        category = best_category
        reason = f"Classified as {best_category} based on '{best_hits[0]}' in description"
        flag = "NEEDS_REVIEW"
    else:
        category = best_category
        reason = f"Classified as {best_category} based on '{best_hits[0]}' in description"
        flag = ""

    if urgent_hit:
        reason += f"; marked Urgent due to '{urgent_hit}'"

    return {"category": category, "priority": priority, "reason": reason, "flag": flag}

def batch_classify(input_path, output_path):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    out_fields = list(fieldnames) + ["category", "priority", "reason", "flag"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        for row in rows:
            desc = row.get("description", row.get("complaint", ""))
            result = classify_complaint(desc)
            row.update(result)
            writer.writerow(row)

    print(f"Done! Results written to: {output_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.output)
    batch_classify(args.input, output_path)

if __name__ == "__main__":
    main()
