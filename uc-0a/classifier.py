"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    description = row.get("description", "")
    desc_lower = description.lower()
    
    # Priority logic: Urgent if severity keywords present
    priority_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    found_priority_kw = None
    for kw in priority_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            found_priority_kw = kw
            break
            
    # Category logic: Exact strings only
    category = "Other"
    found_cat_kw = None
    
    if "pothole" in desc_lower:
        category = "Pothole"
        found_cat_kw = "pothole"
    elif "flood" in desc_lower:
        category = "Flooding"
        found_cat_kw = "flood"
    elif "streetlight" in desc_lower or "light" in desc_lower:
        category = "Streetlight"
        found_cat_kw = "streetlight" if "streetlight" in desc_lower else "light"
    elif "garbage" in desc_lower or "waste" in desc_lower or "bins" in desc_lower or "animal" in desc_lower:
        category = "Waste"
        found_cat_kw = next((w for w in ["garbage", "waste", "bins", "animal"] if w in desc_lower), "waste")
    elif "noise" in desc_lower or "music" in desc_lower:
        category = "Noise"
        found_cat_kw = "noise" if "noise" in desc_lower else "music"
    elif "drain" in desc_lower and ("block" in desc_lower or "overflow" in desc_lower):
        category = "Drain Blockage"
        found_cat_kw = "drain"
    elif "heritage" in desc_lower:
        category = "Heritage Damage"
        found_cat_kw = "heritage"
    elif "heat" in desc_lower:
        category = "Heat Hazard"
        found_cat_kw = "heat"
    elif "road" in desc_lower or "crack" in desc_lower or "surface" in desc_lower or "sinking" in desc_lower:
        category = "Road Damage"
        found_cat_kw = next((w for w in ["road", "crack", "surface", "sinking"] if w in desc_lower), "road")

    # Flag logic
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    
    # Reason logic: One sentence citing specific words
    if category != "Other":
        cite_cat = found_cat_kw
        reason = f"The complaint is classified as {category} because the description mentions {cite_cat}."
        if priority == "Urgent":
            reason = f"Urgent {category} case citing '{cite_cat}' and safety risk '{found_priority_kw}'."
    else:
        reason = "Category is genuinely ambiguous from the description provided."

    return {
        "complaint_id": row.get("complaint_id", "N/A"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row or not any(row.values()):
                    continue
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id')}: {e}")
                    results.append({
                        "complaint_id": row.get("complaint_id", "ERROR"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Processing failed: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return

    if not results:
        print("No results to write.")
        return

    keys = results[0].keys()
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
