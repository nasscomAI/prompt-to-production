import argparse
import csv

SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

CATEGORY_RULES = [
    ("Pothole", ["pothole", "tyre damage", "tire damage"]),
    ("Flooding", ["flooded", "flood", "knee-deep", "standing in water"]),
    ("Streetlight", ["streetlight", "light out", "flickering", "sparking", "lights out"]),
    ("Waste", ["garbage", "waste", "bin", "dead animal", "smell", "overflowing"]),
    ("Noise", ["music", "noise", "loud", "past midnight"]),
    ("Road Damage", ["road surface", "cracked", "sinking", "road damage"]),
    ("Heritage Damage", ["heritage street", "heritage"]),
    ("Heat Hazard", ["heat", "heatwave", "extreme temperature"]),
    ("Drain Blockage", ["drain blocked", "drainage", "drain"]),
]

def classify_complaint(row: dict) -> dict:
    description = (row.get("description") or "").lower()
    complaint_id = row.get("complaint_id", "")

    category = "Other"
    for cat, keywords in CATEGORY_RULES:
        if any(kw in description for kw in keywords):
            category = cat
            break

    is_urgent = any(kw in description for kw in SEVERITY_KEYWORDS)
    if is_urgent:
        priority = "Urgent"
    else:
        priority = "Standard"

    reason_words = []
    if category != "Other":
        for kw in [k for cat, ks in CATEGORY_RULES for k in ks]:
            if kw in description:
                reason_words.append(kw)
                break
    if is_urgent:
        for kw in SEVERITY_KEYWORDS:
            if kw in description:
                reason_words.append(kw)
                break

    reason = f"Categorized as {category} based on keywords: {', '.join(reason_words)}." if reason_words else f"No clear category match found."
    if is_urgent:
        reason += f" Urgent due to severity keyword: {next(kw for kw in SEVERITY_KEYWORDS if kw in description)}."

    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    rows = []
    skipped = 0
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            if not row.get("description", "").strip():
                skipped += 1
                continue
            result = classify_complaint(row)
            rows.append(result)

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Processed {len(rows)} complaints, skipped {skipped} rows. Written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
