"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using heuristic keyword matching.
    """
    description = row.get("description", "").lower()
    
    # Category Keywords mapping
    category_map = {
        "pothole": "Pothole",
        "flooding": "Flooding",
        "flood": "Flooding",
        "rain": "Flooding",
        "water": "Flooding",
        "drain": "Drain Blockage",
        "streetlight": "Streetlight",
        "light": "Streetlight",
        "dark": "Streetlight",
        "garbage": "Waste",
        "waste": "Waste",
        "smell": "Waste",
        "bin": "Waste",
        "music": "Noise",
        "noise": "Noise",
        "midnight": "Noise",
        "crack": "Road Damage",
        "sink": "Road Damage",
        "surface": "Road Damage",
        "heritage": "Heritage Damage"
    }
    
    # Urgent Keywords
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    
    # Determine Category
    category = "Other"
    for kw, cat in category_map.items():
        if kw in description:
            category = cat
            break
            
    # Determine Priority
    priority = "Standard"
    if any(kw in description for kw in urgent_keywords):
        priority = "Urgent"
    elif "low" in description or "minor" in description:
        priority = "Low"
        
    # Generate Reason
    # Simple extraction of the first phrase containing a keyword or first 10 words
    reason = f"Classified as {category} because description mentions '{description[:50]}...'"
    
    # Ambiguity Flag
    flag = ""
    if category == "Other" or len(description) < 20:
        flag = "NEEDS_REVIEW"
        
    return {
        "complaint_id": row.get("complaint_id", "UNKNOWN"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
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
                    
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Batch processing failed: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
