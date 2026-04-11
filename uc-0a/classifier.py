"""
UC-0A — Complaint Classifier
Implemented using the RICE → agents.md → skills.md workflow.
"""
import argparse
import csv
import os

# Taxonomy defined in agents.md
VALID_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Safety keywords that trigger URGENT priority
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with original keys plus: category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    
    # 1. Determine Category (Keyword-based simulation of LLM taxonomy)
    category = "Other"
    reason_snippet = "No specific category keywords found."
    
    mapping = {
        "Pothole": ["pothole", "crater"],
        "Flooding": ["flood", "waterlog", "ponding", "knee-deep", "rain water"],
        "Streetlight": ["streetlight", "street light", "lamp", "dark", "flickering"],
        "Waste": ["garbage", "trash", "waste", "debris", "litter", "bin", "dumping", "smell", "dead animal"],
        "Noise": ["noise", "loud", "music", "sound", "midnight"],
        "Road Damage": ["crack", "sinking", "uneven", "footpath", "tiles broken"],
        "Heritage Damage": ["heritage", "old city", "historical"],
        "Heat Hazard": ["heat", "sun", "shade", "dehydration"],
        "Drain Blockage": ["drain", "sewage", "gutter", "manhole"]
    }
    
    for cat, keywords in mapping.items():
        for kw in keywords:
            if kw in description:
                category = cat
                reason_snippet = f"description mentions '{kw}'"
                break
        if category != "Other":
            break

    # 2. Determine Priority
    priority = "Standard"
    for kw in URGENT_KEYWORDS:
        if kw in description:
            priority = "Urgent"
            reason_snippet += f" and safety-critical term '{kw}'"
            break
            
    # 3. Justification (Reason)
    reason = f"Classified as {category} because {reason_snippet}."
    
    # 4. Ambiguity Flag
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    
    # Update row with new fields
    result = row.copy()
    result.update({
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    })
    return result


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    fieldnames = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
            for row in reader:
                try:
                    results.append(classify_complaint(row))
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id', 'unknown')}: {e}")
                    # Create a failed entry to preserve count
                    row.update({"category": "Other", "priority": "Standard", "reason": f"Error: {str(e)}", "flag": "NEEDS_REVIEW"})
                    results.append(row)

        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Fatal error during batch processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
