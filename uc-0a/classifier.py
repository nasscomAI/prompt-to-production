"""
UC-0A — Complaint Classifier
"""
import argparse
import csv

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_RULES = {
    "Pothole": ["pothole", "potholes", "tyre blowout", "tyre damage"],
    "Flooding": ["flooded", "flood", "flooding", "knee-deep", "submerged", "stranded in water"],
    "Streetlight": ["streetlight", "street light", "lights out", "unlit", "darkness", "flickering light", "lamp post"],
    "Waste": ["garbage", "waste", "overflowing bin", "dead animal", "dumped waste", "not cleared", "smell"],
    "Noise": ["noise", "music", "amplifier", "drilling", "loud", "band playing", "idling with engines"],
    "Road Damage": ["road surface", "cracked", "sinking", "subsided", "collapsed", "crater", "buckled", "bubbling"],
    "Heritage Damage": ["heritage", "historic", "cobblestone", "tram", "defaced", "heritage stone", "heritage zone", "heritage residential"],
    "Heat Hazard": ["melting", "heat", "temperature", "44°", "45°", "52°", "burns on contact", "dangerous temperature"],
    "Drain Blockage": ["drain blocked", "drainage", "drain 100%", "channel rainwater", "stormwater drain", "construction debris"],
}


def has_severity_keyword(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in SEVERITY_KEYWORDS)


def classify_category(description: str) -> tuple:
    desc_lower = description.lower()

    scores = {}
    for cat, keywords in CATEGORY_RULES.items():
        score = sum(1 for kw in keywords if kw in desc_lower)
        if score > 0:
            scores[cat] = score

    if not scores:
        return "Other", "No matching category keywords found in description"

    best = max(scores, key=scores.get)
    matched_kws = [kw for kw in CATEGORY_RULES[best] if kw in desc_lower]
    reason = f"Description contains '{matched_kws[0]}' indicating {best.lower()} issue"
    return best, reason


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")

    if not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided",
            "flag": "NEEDS_REVIEW"
        }

    category, reason = classify_category(description)

    priority = "Urgent" if has_severity_keyword(description) else "Standard"

    flagged_kws = [kw for kw in SEVERITY_KEYWORDS if kw in description.lower()]
    if flagged_kws:
        reason = f"Description contains '{flagged_kws[0]}' — {priority} priority assigned"

    ambiguous_keywords = ["concern", "risk", "reported"]
    desc_words = description.lower().split()
    ambiguous_count = sum(1 for w in ambiguous_keywords if w in desc_words)
    flag = "NEEDS_REVIEW" if ambiguous_count >= 2 or category == "Other" else ""

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    results = []
    errors = []

    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                errors.append(f"Row {row.get('complaint_id', '?')}: {e}")

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    if errors:
        print(f"Errors encountered: {len(errors)}")
        for err in errors:
            print(f"  - {err}")

    print(f"Classified {len(results)} complaints.")
    urgent_count = sum(1 for r in results if r["priority"] == "Urgent")
    flagged_count = sum(1 for r in results if r["flag"] == "NEEDS_REVIEW")
    print(f"Urgent: {urgent_count} | Needs Review: {flagged_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
