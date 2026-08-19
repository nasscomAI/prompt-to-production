"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    description = row.get("description", "").lower()
    if not description:
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Low",
            "reason": "Missing description.",
            "flag": "NEEDS_REVIEW"
        }

    # Severity Check
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    found_urgent = None
    for kw in urgent_keywords:
        if kw in description:
            priority = "Urgent"
            found_urgent = kw
            break

    # Category Match
    category_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flood"],
        "Streetlight": ["streetlight", "lights out", "dark", "light "],
        "Waste": ["garbage", "waste", "dead animal", "smell"],
        "Noise": ["music", "noise", "loud"],
        "Road Damage": ["road surface", "footpath", "cracked", "sinking", "broken tiles"],
        "Heritage Damage": ["heritage"],
        "Heat Hazard": ["heat wave", "sun"],
        "Drain Blockage": ["drain", "manhole"]
    }

    matched_categories = []
    matched_word = ""
    for cat, kws in category_map.items():
        for kw in kws:
            if kw in description:
                matched_categories.append(cat)
                matched_word = kw
                break # Only need one match per category

    # Determine final category and flag
    flag = ""
    if len(matched_categories) == 1:
        category = matched_categories[0]
    elif len(matched_categories) > 1:
        # e.g., "flooded" and "drain blocked" -> Ambiguous if conflicting, but let's just pick first and flag it
        category = matched_categories[0]
        flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        matched_word = "unknown"

    # Generate reason
    if matched_word != "unknown":
        reason = f"Classified as {category} because the description mentions '{matched_word}'."
    else:
        reason = "Could not clearly identify a specific category from the description."
        
    if priority == "Urgent":
        reason += f" Priority escalated due to keyword '{found_urgent}'."

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f_in, open(output_path, 'w', encoding='utf-8', newline='') as f_out:
            reader = csv.DictReader(f_in)
            fieldnames = list(reader.fieldnames or []) + ["category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                try:
                    classification = classify_complaint(row)
                    row.update(classification)
                except Exception as e:
                    # Not crashing on bad rows
                    row["category"] = "Other"
                    row["priority"] = "Low"
                    row["reason"] = f"Error processing row: {str(e)}"
                    row["flag"] = "NEEDS_REVIEW"
                writer.writerow(row)
    except Exception as e:
        print(f"Failed to process batch: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
