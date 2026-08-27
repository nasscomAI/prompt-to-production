"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import re

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_RULES = [
    ("Pothole", ["pothole", "crater"]),
    ("Flooding", ["flooded", "flooding", "flood", "submerged", "knee-deep"]),
    ("Streetlight", ["streetlight", "street light", "lights out", "flickering", "sparking", "lamp post"]),
    ("Waste", ["garbage", "waste", "trash", "rubbish", "bins", "bin", "dead animal", "smell", "health concern"]),
    ("Noise", ["noise", "music", "loud", "wedding venue"]),
    ("Road Damage", ["road surface", "cracked", "sinking", "footpath", "broken", "upturned", "manhole cover"]),
    ("Heritage Damage", ["heritage"]),
    ("Heat Hazard", ["heat", "temperature", "sun"]),
    ("Drain Blockage", ["drain", "drainage", "blocked"]),
]

URGENT_PATTERN = re.compile("|".join(SEVERITY_KEYWORDS), re.IGNORECASE)

def classify_complaint(row: dict) -> dict:
    description = (row.get("description") or "").lower()
    complaint_id = row.get("complaint_id", "")

    priority = "Standard"
    if URGENT_PATTERN.search(description):
        priority = "Urgent"

    matched_categories = []
    for cat_name, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in description:
                matched_categories.append(cat_name)
                break

    category = "Other"
    flag = ""
    if len(matched_categories) == 1:
        category = matched_categories[0]
    elif len(matched_categories) > 1:
        category = matched_categories[0]
        flag = "NEEDS_REVIEW"
    elif "manhole" in description or "cover" in description:
        if "missing" in description:
            category = "Road Damage"

    if "heritage" in description and ("light" in description or "streetlight" in description or "lights" in description):
        category = "Heritage Damage"
        flag = "NEEDS_REVIEW"

    desc_sentences = row.get("description", "").split(".")
    words_cited = []
    for word in SEVERITY_KEYWORDS:
        if word in description and word not in words_cited:
            words_cited.append(word)
    for cat_name, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in description and kw not in words_cited:
                words_cited.append(kw)
                break

    if words_cited:
        reason = f"Description contains: {', '.join(words_cited[:3])}"
    else:
        first_sentence = desc_sentences[0].strip() if desc_sentences else ""
        reason = f"Complaint about {category.lower()}: \"{first_sentence[:80]}\""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }

def batch_classify(input_path: str, output_path: str):
    rows = []
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    results = []
    for row in rows:
        try:
            result = classify_complaint(row)
            results.append(result)
        except Exception:
            results.append({
                "complaint_id": row.get("complaint_id", ""),
                "category": "Other",
                "priority": "Standard",
                "reason": "Error processing row",
                "flag": "NEEDS_REVIEW",
            })

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
