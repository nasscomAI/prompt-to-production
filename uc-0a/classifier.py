import csv
import argparse

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "potholes"],
    "Flooding": ["flood", "flooded", "flooding", "rain", "waterlog"],
    "Streetlight": ["streetlight", "light", "lighting", "dark"],
    "Waste": ["waste", "garbage", "trash", "litter", "dump"],
    "Noise": ["noise", "drilling", "loud", "sound", "idling"],
    "Road Damage": ["road collapsed", "crater", "road damage", "collapsed"],
    "Heritage Damage": ["heritage", "charminar", "monument", "historic"],
    "Heat Hazard": ["heat", "fire", "burning"],
    "Drain Blockage": ["drain", "drainage", "stormwater", "sewer"],
}

def classify_complaint(description):
    desc_lower = description.lower()

    # Determine category
    category = "Other"
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in desc_lower for kw in keywords):
            category = cat
            break

    # Determine priority
    priority = "Standard"
    triggered_keyword = None
    for kw in URGENT_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            triggered_keyword = kw
            break

    # Determine reason
    if triggered_keyword:
        reason = f"Description contains '{triggered_keyword}', triggering Urgent priority."
    else:
        reason = f"Classified as {category} based on keywords in description."

    # Determine flag
    matches = [cat for cat, keywords in CATEGORY_KEYWORDS.items() if any(kw in desc_lower for kw in keywords)]
    flag = "NEEDS_REVIEW" if len(matches) > 1 else ""

    return {"category": category, "priority": priority, "reason": reason, "flag": flag}


def batch_classify(input_path, output_path):
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    output_rows = []
    for row in rows:
        print(f"Classifying {row['complaint_id']}...")
        result = classify_complaint(row["description"])
        output_rows.append({
            **row,
            "category": result["category"],
            "priority": result["priority"],
            "reason": result["reason"],
            "flag": result["flag"]
        })

    fieldnames = list(output_rows[0].keys())
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"\nDone! Results saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    batch_classify(args.input, args.output)
