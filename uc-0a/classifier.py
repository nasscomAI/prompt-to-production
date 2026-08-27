"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    complaint_id = row.get("complaint_id", "Unknown")
    description = row.get("description", "")
    
    if not description or not isinstance(description, str):
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing or invalid description.",
            "flag": "NEEDS_REVIEW"
        }

    description_lower = description.lower()
    
    # Priority Keywords
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    for kw in severity_keywords:
        if kw in description_lower:
            priority = "Urgent"
            break

    # Category Mapping
    category_map = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "waterlogging", "water"],
        "Streetlight": ["light", "lamp", "street light"],
        "Waste": ["garbage", "waste", "rubbish", "trash", "bins"],
        "Noise": ["noise", "loud", "music", "sound"],
        "Road Damage": ["road damage", "crack", "sinking", "surface"],
        "Heritage Damage": ["heritage", "historic"],
        "Heat Hazard": ["heat", "hot", "sun"],
        "Drain Blockage": ["drain", "sewage", "blockage"]
    }

    matched_categories = []
    for cat, kws in category_map.items():
        for kw in kws:
            if kw in description_lower:
                matched_categories.append((cat, kw))
                break 

    category = "Other"
    flag = ""
    reason = ""

    if len(matched_categories) == 1:
        category, kw = matched_categories[0]
        cite_str = kw
        if priority == "Urgent":
            sev_kw = next((skw for skw in severity_keywords if skw in description_lower), "")
            cite_str += f" (severity: {sev_kw})"
        reason = f"Classified as {category} because the description mentions '{cite_str}'."
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Classification is ambiguous because multiple categories matched."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Classification is ambiguous because no clear category found."

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    fieldnames = ["category", "priority", "reason", "flag", "complaint_id"]
    
    try:
        results = []
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    results.append(classification)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id', 'Unknown')}: {e}")
                    results.append({
                        "complaint_id": row.get('complaint_id', 'Unknown'),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"System error during classification: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })

        with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
                
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
    except Exception as e:
        print(f"A critical error occurred: {e}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
