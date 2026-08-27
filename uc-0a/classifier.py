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
    desc = str(row.get("description", "")).lower()
    
    # Default values
    category = "Other"
    priority = "Standard"
    reason = "Could not determine category from description alone"
    flag = "NEEDS_REVIEW"
    
    # Check for empty/null description
    if not desc or desc.strip() == "none" or desc.strip() == "null":
        return {
            "complaint_id": row.get("complaint_id", ""),
            "category": "Other",
            "priority": "Low",
            "reason": "Null or missing description",
            "flag": "NEEDS_REVIEW"
        }

    # Category matching heuristics
    cat_keywords = {
        "Pothole": ["pothole", "crater"],
        "Flooding": ["flood", "waterlogging", "water", "drain", "blocked"],
        "Streetlight": ["streetlight", "lights out", "darkness", "sparking", "bulb"],
        "Waste": ["garbage", "waste", "dead animal", "smell", "dumped"],
        "Noise": ["music", "noise", "loud", "speaker"],
        "Road Damage": ["crack", "road surface", "broken road", "footpath tiles"],
        "Heritage Damage": ["heritage", "monument"],
        "Heat Hazard": ["heat", "sun", "temperature"],
        "Drain Blockage": ["manhole"]
    }
    
    matched_word = ""
    for cat, keywords in cat_keywords.items():
        if category != "Other":
            break
        for kw in keywords:
            if kw in desc:
                category = cat
                flag = ""  # Clear flag if category is determined
                matched_word = kw
                reason = f"Description contains category keyword: '{kw}'"
                break

    # If category could not be determined, override to Low priority
    if category == "Other":
        priority = "Low"
        
    # Priority scaling based on severity keywords
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    for kw in urgent_keywords:
        if kw in desc:
            priority = "Urgent"
            if flag == "NEEDS_REVIEW":
                reason += f", but contains severity keyword: '{kw}'"
            else:
                reason += f" and severity keyword: '{kw}'"
            break
            
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
    """
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    results.append({
                        "complaint_id": row.get("complaint_id", ""),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Processing error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Failed to read input file: {e}")
        return
        
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Failed to write output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
