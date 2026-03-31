"""
UC-0A — Complaint Classifier
"""
import argparse
import csv

CATEGORIES = {
    "Pothole": ["pothole", "crater", "wheel swallowed", "tyre damage"],
    "Flooding": ["flood", "flooded", "underpass flooded", "stranded", "water", "abandoned"],
    "Streetlight": ["streetlight", "street light", "lights out", "dark at night", "flickering", "sparking"],
    "Waste": ["garbage", "waste", "overflowing", "smell", "not cleared", "animal not removed", "dead animal", "waste dumped", "dumped on"],
    "Noise": ["noise", "music", "drilling", "idling"],
    "Road Damage": ["road collapsed", "road surface", "cracking", "sinking", "tiles broken", "footpath", "manhole", "manhole cover"],
    "Heritage Damage": ["heritage", "old city", "heritage zone"],
    "Heat Hazard": ["heat", "hot surface", "scalding", "burning"],
    "Drain Blockage": ["drain blocked", "drainage", "drain", "stormwater drain", "mosquito"],
}

URGENT_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

STANDARD_SIGNALS = ["cm", "m wide", "metre", "meter", "hours", "days", "week", "affected", "vehicles", "passengers", "commuters", "entire"]


def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")
    days_open = row.get("days_open", "0")

    # Handle missing/empty description
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Description is empty or missing",
            "flag": "NEEDS_REVIEW",
        }

    desc_lower = description.lower().strip()

    # Parse days_open safely
    try:
        days = int(days_open)
    except (ValueError, TypeError):
        days = 0

    # --- Category ---
    category = "Other"
    trigger_word = ""
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in desc_lower:
                category = cat
                trigger_word = kw
                break
        if category != "Other":
            break

    # Check Drain Blockage separately for more specific matching
    # (it overlaps with Flooding on "drain")
    if category == "Flooding" and "drain" in desc_lower:
        category = "Drain Blockage"
        trigger_word = "drain"

    # --- Priority ---
    priority = "Low"
    priority_trigger = ""

    # Check Urgent first
    for kw in URGENT_KEYWORDS:
        if kw in desc_lower:
            priority = "Urgent"
            priority_trigger = kw
            break

    # If not Urgent, check Standard signals
    if priority != "Urgent":
        for kw in STANDARD_SIGNALS:
            if kw in desc_lower:
                priority = "Standard"
                priority_trigger = kw
                break

    # Escalate by days_open
    if days >= 14 and priority == "Low":
        priority = "Standard"

    # --- Reason ---
    parts = []
    if trigger_word:
        parts.append(f'"{trigger_word}" indicates {category}')
    if priority_trigger and priority != "Low":
        parts.append(f'"{priority_trigger}" triggers {priority} priority')
    if not parts:
        parts.append(f"Categorized as {category}")
    reason = "; ".join(parts)

    # --- Flag ---
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
    results = []

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip rows with missing complaint_id
            if not row.get("complaint_id", "").strip():
                continue
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception as e:
                print(f"Warning: failed to classify {row.get('complaint_id', 'unknown')}: {e}")
                continue

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
