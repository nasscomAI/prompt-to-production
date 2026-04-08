"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using rule-based logic from agents.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "Unknown")
    
    # 1. Category Logic
    category_map = {
        "Pothole": ["pothole", "pitting"],
        "Flooding": ["flood", "waterlogging", "water", "inundated"],
        "Streetlight": ["streetlight", "lamp", "light", "dark"],
        "Waste": ["garbage", "trash", "waste", "bins", "dumping", "dead animal"],
        "Noise": ["noise", "loud", "music", "sound"],
        "Road Damage": ["road surface", "cracked", "sinking", "utility work"],
        "Heritage Damage": ["heritage", "historic", "ancient"],
        "Heat Hazard": ["heat", "hot", "sun", "shade"],
        "Drain Blockage": ["drain", "sewage", "blocked"],
    }
    
    category = "Other"
    found_category_keyword = ""
    for cat, keywords in category_map.items():
        for kw in keywords:
            if kw in description:
                category = cat
                found_category_keyword = kw
                break
        if category != "Other":
            break
            
    # 2. Priority Logic
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    found_priority_keyword = ""
    for kw in urgent_keywords:
        if kw in description:
            priority = "Urgent"
            found_priority_keyword = kw
            break
            
    # 3. Reason & Flag Logic
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"
        reason = "No predefined category keywords found in description."
    else:
        # Find the sentence containing the keyword for citation
        sentences = row.get("description", "").split('.')
        citation = ""
        for s in sentences:
            if found_category_keyword in s.lower() or found_priority_keyword in s.lower():
                citation = s.strip()
                break
        if not citation:
            citation = row.get("description", "")[:100] + "..."
            
        reason = f"Classified as {category} ({priority}) based on words: '{found_category_keyword or found_priority_keyword}'. Description mentions: {citation}"

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
    """
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row.get("description"):
                    results.append({
                        "complaint_id": row.get("complaint_id", "Unknown"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Empty description.",
                        "flag": "NEEDS_REVIEW"
                    })
                    continue
                
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Error processing row {row.get('complaint_id')}: {e}")
                    
        # Write results
        if results:
            keys = results[0].keys()
            with open(output_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(results)
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
