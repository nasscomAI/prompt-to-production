import csv
import argparse

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse", "hospitalised", "risk", "lives at risk"
]

def classify_complaint(row):
    desc = row.get("description", "").lower()

    # Priority
    priority = "Standard"
    triggered_keyword = None
    for kw in SEVERITY_KEYWORDS:
        if kw in desc:
            priority = "Urgent"
            triggered_keyword = kw
            break

    # Category
    flag = ""
    drain_blocked = "drain" in desc and "blocked" in desc
    flooding_primary = "flood" in desc or "flooded" in desc or "flooding" in desc
    if drain_blocked:
        category = "Drain Blockage"
    elif flooding_primary:
        category = "Flooding"
        if "drain" in desc:
            flag = "NEEDS_REVIEW"
    elif "pothole" in desc or "potholes" in desc:
        category = "Pothole"
        if "road" in desc and "collapse" in desc:
            flag = "NEEDS_REVIEW"
    elif "road collapsed" in desc or "crater" in desc or "collapsed" in desc:
        category = "Road Damage"
    elif "heritage" in desc or "charminar" in desc or "old city" in desc or "tourist" in desc:
        category = "Heritage Damage"
    elif "waste" in desc or "garbage" in desc or "litter" in desc:
        category = "Waste"
        if "heritage" in desc or "charminar" in desc or "tourist" in desc:
            flag = "NEEDS_REVIEW"
    elif "noise" in desc or "drilling" in desc or "idling" in desc or "trucks" in desc:
        category = "Noise"
    elif "streetlight" in desc or "light" in desc:
        category = "Streetlight"
    elif "heat" in desc or "temperature" in desc:
        category = "Heat Hazard"
    else:
        category = "Other"

    # Reason
    # Pick the most relevant phrase from description
    original_desc = row.get("description", "")
    if triggered_keyword:
        reason = f"Description contains '{triggered_keyword}' triggering Urgent priority; classified as {category} based on complaint content."
    else:
        # Use first sentence or full desc if short
        snippet = original_desc.split(".")[0]
        reason = f"Classified as {category} based on '{snippet}' in description."

    return {
        "complaint_id": row["complaint_id"],
        "date_raised": row["date_raised"],
        "city": row["city"],
        "ward": row["ward"],
        "location": row["location"],
        "description": row["description"],
        "reported_by": row["reported_by"],
        "days_open": row["days_open"],
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path, output_path):
    results = []
    with open(input_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            classified = classify_complaint(row)
            results.append(classified)

    fieldnames = [
        "complaint_id", "date_raised", "city", "ward", "location",
        "description", "reported_by", "days_open",
        "category", "priority", "reason", "flag"
    ]

    with open(output_path, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. {len(results)} rows classified → {output_path}")

    # Print summary for review
    print("\n--- Classification Summary ---")
    for r in results:
        print(f"{r['complaint_id']} | {r['category']} | {r['priority']} | {r['flag']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    batch_classify(args.input, args.output)