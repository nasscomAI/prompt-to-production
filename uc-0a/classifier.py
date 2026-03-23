import argparse
import csv

def classify_complaint(row: dict) -> dict:
    description = row.get("description", "").lower()
    
    # Priority
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    matched_urgent_kw = None
    for kw in urgent_keywords:
        if kw in description:
            priority = "Urgent"
            matched_urgent_kw = kw
            break
            
    # Category
    cats_found = []
    if "pothole" in description: cats_found.append("Pothole")
    if "flood" in description: cats_found.append("Flooding")
    if "streetlight" in description or "lights out" in description: cats_found.append("Streetlight")
    if "garbage" in description or "waste" in description or "animal" in description: cats_found.append("Waste")
    if "music" in description or "noise" in description: cats_found.append("Noise")
    if "road surface" in description or "tiles broken" in description or "footpath" in description: cats_found.append("Road Damage")
    if "heritage" in description and "damage" in description: cats_found.append("Heritage Damage")
    if "drain" in description or "manhole" in description: cats_found.append("Drain Blockage")
    
    if len(cats_found) == 1:
        category = cats_found[0]
        flag = ""
    elif len(cats_found) > 1:
        # Resolve ambiguity
        if "flood" in description and "drain" in description:
            category = "Flooding" # Bus stand flooded. Drain blocked.
            flag = "NEEDS_REVIEW"
        else:
            category = "Other"
            flag = "NEEDS_REVIEW"
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # Reason
    if priority == "Urgent":
        reason = f"Classified as Urgent because the description mentions '{matched_urgent_kw}'."
    else:
        # Extract a snippet
        words = description.split()
        snippet = " ".join(words[:4]) if words else ""
        reason = f"Classified as {category} because it mentions '{snippet}'."
        
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }

def batch_classify(input_path: str, output_path: str):
    with open(input_path, 'r', encoding='utf-8') as fin, \
         open(output_path, 'w', encoding='utf-8', newline='') as fout:
        
        reader = csv.DictReader(fin)
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            try:
                res = classify_complaint(row)
                writer.writerow(res)
            except Exception as e:
                writer.writerow({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Error formatting row",
                    "flag": "NEEDS_REVIEW"
                })

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
