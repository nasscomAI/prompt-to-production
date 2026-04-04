"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = (row.get("description", "") or "").strip()
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing complaint description; Unable to classify.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    categories = [
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
        "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
    ]

    category_keywords = {
        "Pothole": ["pothole", "sinkhole", "road pit"],
        "Flooding": ["flood", "waterlogged", "water logging", "waterlogged"],
        "Streetlight": ["streetlight", "street light", "lamp post", "light not working"],
        "Waste": ["garbage", "trash", "bin", "waste", "dump"],
        "Noise": ["noise", "loud", "sound pollution", "honking"],
        "Road Damage": ["broken road", "road damage", "cracks", "uneven road"],
        "Heritage Damage": ["heritage", "monument", "historical", "archaeological"],
        "Heat Hazard": ["heat", "scorching", "hot", "burning"],
        "Drain Blockage": ["drain", "drainage", "blocked drain", "sewer"]
    }

    selected_category = "Other"
    matches = []
    for cat, keys in category_keywords.items():
        for key in keys:
            if key in text:
                matches.append(cat)
                break

    if len(set(matches)) == 1:
        selected_category = matches[0]
    elif len(set(matches)) > 1:
        # If multiple category cues, prefer the first specific one with priority by rules
        selected_category = matches[0]

    # Severity keywords
    urgent_keywords = {
        "injury", "child", "school", "hospital", "ambulance", "fire",
        "hazard", "fell", "collapse"
    }

    found_urgent = [kw for kw in urgent_keywords if kw in text]
    if found_urgent:
        priority = "Urgent"
    else:
        priority = "Standard"

    # reason must cite specific words from description and be one sentence
    reason_terms = []
    for word in ["pothole", "flood", "streetlight", "waste", "noise", "road", "heritage", "heat", "drain", "injury", "child", "school", "hospital", "fire"]:
        if word in text:
            reason_terms.append(word)

    if reason_terms:
        reason = f"Complaint mentions {', '.join(reason_terms[:3])} and requires action."
    else:
        reason = "Complaint description has insufficient keyword signal; requires human review."

    flag = ""
    if selected_category == "Other" or len(set(matches)) > 1 or not reason_terms:
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": selected_category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    with open(input_path, newline='', encoding='utf-8') as fin:
        reader = csv.DictReader(fin)
        fieldnames = [
            "complaint_id", "category", "priority", "reason", "flag"
        ]
        rows = []
        for row in reader:
            try:
                classified = classify_complaint(row)
            except Exception as e:
                classified = {
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Error classifying row: {e}",
                    "flag": "NEEDS_REVIEW",
                }
            rows.append(classified)

    with open(output_path, 'w', newline='', encoding='utf-8') as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        for out_row in rows:
            writer.writerow(out_row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
