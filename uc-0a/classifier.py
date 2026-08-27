"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

KEYWORDS_MAP = {
    "Pothole": ["pothole", "pit", "hole"],
    "Drain Blockage": ["drain", "sewer", "blocked"],
    "Flooding": ["flood", "water", "overflow", "waterlogging"],
    "Streetlight": ["light", "streetlight", "lamp"],
    "Waste": ["garbage", "waste", "trash", "animal", "dead"],
    "Noise": ["noise", "loud", "sound"],
    "Road Damage": ["crack", "broken", "tiles", "footpath", "sink"],
    "Heritage Damage": ["heritage", "monument"],
    "Heat Hazard": ["heat", "hot", "temperature"]
}


def classify_complaint(row: dict) -> dict:
    text = (row.get("description") or "").lower()

    category = "Other"
    matched_word = None

    # Category detection (order matters)
    for cat, words in KEYWORDS_MAP.items():
        for word in words:
            if word in text:
                category = cat
                matched_word = word
                break
        if category != "Other":
            break

    # Priority
    priority = "Standard"
    for word in URGENT_KEYWORDS:
        if word in text:
            priority = "Urgent"
            break

    # Reason (STRICT: must cite word)
    if matched_word:
        reason = f"Contains '{matched_word}'"
    else:
        # fallback: still cite something from text
        words = text.split()
        reason = f"Contains '{words[0]}'" if words else "Contains 'unknown'"

    # Flag
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    results = []

    with open(input_path, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            try:
                result = classify_complaint(row)
                results.append(result)
            except Exception:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Contains 'error'",
                    "flag": "NEEDS_REVIEW"
                })

    with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
