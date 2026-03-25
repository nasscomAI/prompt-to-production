"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using the RICE rules from agents.md.
    """
    desc = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "N/A")
    
    # 1. Determine Priority
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    is_urgent = any(word in desc for word in urgent_keywords)
    priority = "Urgent" if is_urgent else "Standard"
    
    # 2. Determine Category and Reason
    # We'll use a keyword mapping for categories based on the taxonomy in agents.md
    category_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "waterlogged", "water-logged", "submerged", "inaccessible due to water"],
        "Streetlight": ["streetlight", "street light", "lamp", "lights out", "darkness", "sparking"],
        "Waste": ["waste", "garbage", "trash", "bins", "refuse", "dump", "animal carcass", "dead animal", "smell"],
        "Noise": ["noise", "loud", "music", "midnight", "decibel"],
        "Road Damage": ["cracked", "sinking", "uneven", "broken path", "tiles broken", "manhole"],
        "Heritage Damage": ["heritage", "historic", "statue", "old city wall"],
        "Heat Hazard": ["heat", "sunstroke", "exhaustion", "cooling"],
        "Drain Blockage": ["drain", "sewage", "gutter", "blockage", "clogged"]
    }
    
    category = "Other"
    reason = "The complaint description does not clearly match any predefined maintenance category."
    flag = ""
    
    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": priority,
            "reason": "Description is empty.",
            "flag": "NEEDS_REVIEW"
        }

    
    # Find matching category
    matched_categories = []
    for cat, keywords in category_map.items():
        for kw in keywords:
            if kw in desc:
                matched_categories.append((cat, kw))
                break # Move to next category
    
    if len(matched_categories) == 1:
        category, matched_kw = matched_categories[0]
        reason = f"Classified as {category} because the description mentions '{matched_kw}'."
    elif len(matched_categories) > 1:
        # Ambiguity between categories
        category = "Other"
        matched_str = ", ".join([c[0] for c in matched_categories])
        reason = f"Ambiguous description matching multiple categories: {matched_str}."
        flag = "NEEDS_REVIEW"
    else:
        # No match
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Could not determine a specific category from the description."

    # Priority override reason refinement
    if is_urgent:
        found_urgent = [w for w in urgent_keywords if w in desc][0]
        reason += f" Priority set to Urgent due to mention of '{found_urgent}'."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Ensures robustness and adherence to the specified schema.
    """
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id')}: {e}")
                    # Still add a placeholder if a row fails critically
                    results.append({
                        "complaint_id": row.get("complaint_id", "ERROR"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"System error during classification: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
        return

    # Write results to CSV
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
