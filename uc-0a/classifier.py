"""
UC-0A — Complaint Classifier
Classifies civic complaints per agents.md enforcement rules:
- Category must be exactly one of the allowed taxonomy strings
- Priority Urgent only when severity keywords are present in the description
- Every row gets a reason citing specific words from the description
- Ambiguous descriptions get flag=NEEDS_REVIEW
"""
import argparse
import csv
import re

CATEGORIES = [
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
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole", "pot hole", "crater"],
    "Flooding": ["flood", "waterlog", "submerged", "knee-deep", "in water", "waterlogged", "standing water"],
    "Streetlight": ["streetlight", "street light", "lights out", "lamp post", "lamppost", "sparking", "flickering"],
    "Waste": ["garbage", "waste", "bin", "dead animal", "litter", "refuse", "dump", "dumping", "smell"],
    "Noise": ["music", "noise", "loud", "noisy"],
    "Road Damage": ["road", "manhole", "footpath", "asphalt", "pavement", "cracked", "sinking", "surface"],
    "Heritage Damage": ["heritage", "monument", "historical"],
    "Heat Hazard": ["heat", "scorching", "unbearable", "heatwave"],
    "Drain Blockage": ["drain blocked", "blocked drain", "drainage", "sewer", "drainage system"],
}

# Substrings in a description that, combined with a different dominant
# category, make the row genuinely ambiguous and require NEEDS_REVIEW.
AMBIGUITY_TRIGGERS = ["heritage"]


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", text.lower())


def detect_category(description: str) -> str:
    norm = normalize(description)
    best = None
    best_score = 0
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in norm)
        if score > best_score:
            best = category
            best_score = score
    return best if best else "Other"


def should_flag_ambig(description: str, category: str) -> bool:
    norm = normalize(description)
    return any(trig in norm for trig in AMBIGUITY_TRIGGERS) and category != "Heritage Damage"


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "").strip()
    description = (row.get("description") or "").strip()

    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "description field was empty",
            "flag": "NEEDS_REVIEW",
        }

    norm = normalize(description)
    category = detect_category(description)
    has_severity = any(kw in norm for kw in SEVERITY_KEYWORDS)
    priority = "Urgent" if has_severity else "Standard"
    flag = "NEEDS_REVIEW" if should_flag_ambig(description, category) else ""

    cited = [kw for kw in CATEGORY_KEYWORDS.get(category, []) if kw in norm]
    if not cited:
        cited = description[:60]
    reason = f"description mentions '{', '.join(cited)}' which matches category {category}"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    results = []
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                results.append(classify_complaint(row))
            except Exception as e:
                cid = (row or {}).get("complaint_id", "?")
                print(f"WARN: row {cid} failed, skipped: {e}")

    if not results:
        print("No rows classified.")
        return

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"]
        )
        writer.writeheader()
        writer.writerows(results)

    counts = {}
    for r in results:
        counts[r["category"]] = counts.get(r["category"], 0) + 1
    print(f"Classified {len(results)} complaints.")
    for cat in CATEGORIES:
        if cat in counts:
            print(f"  {cat}: {counts[cat]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")