import argparse
import csv
# Allowed schema
CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard",
    "Drain Blockage", "Other"
]
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital",
    "ambulance", "fire", "hazard", "fell", "collapse"
]
CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "waterlogging"],
    "Streetlight": ["streetlight", "light"],
    "Waste": ["garbage", "waste", "trash"],
    "Noise": ["noise", "loud"],
    "Road Damage": ["road", "crack", "broken"],
    "Heritage Damage": ["heritage", "monument"],
    "Heat Hazard": ["heat", "hot"],
    "Drain Blockage": ["drain", "sewage", "blocked"]
}
def safe_contains(text, keyword):
    """Match whole words only to avoid false positives."""
    return f" {keyword} " in f" {text} "
def classify_complaint(row: dict) -> dict:
    description = row.get("description", "")
    desc = description.lower()
    # Handle missing description
    if not desc.strip():
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW"
        }
    matches = []
    matched_keywords = []
    # Category detection
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if safe_contains(desc, kw):
                matches.append(category)
                matched_keywords.append(kw)
    unique_matches = list(set(matches))
    # Category decision + ambiguity handling
    if len(unique_matches) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Multiple category keywords found: {unique_matches}"
    elif len(unique_matches) == 1:
        category = unique_matches[0]
        flag = ""
        reason = f"Classified as {category} due to keyword '{matched_keywords[0]}'."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"No category keywords found in description: '{description[:50]}...'"
    # Priority detection
    priority = "Standard"
    urgent_word = None
    for kw in SEVERITY_KEYWORDS:
        if safe_contains(desc, kw):
            priority = "Urgent"
            urgent_word = kw
            break
    # Override reason if urgent
    if priority == "Urgent":
        reason = f"Marked Urgent due to keyword '{urgent_word}' in description."
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
                    "reason": "Error processing row.",
                    "flag": "NEEDS_REVIEW"
                })
    with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
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
