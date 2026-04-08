"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    desc = str(row.get('description', '')).lower()
    
    category = "Other"
    flag = ""
    priority = "Normal"
    reason = "Could not map to exact category"
    
    if not desc:
        return {
            "complaint_id": row.get('complaint_id', ''),
            "category": "Other",
            "priority": "Normal",
            "reason": "Empty description",
            "flag": "NEEDS_REVIEW"
        }

    desc_words = set(re.findall(r'\b\w+\b', desc))

    # Category Mapping
    if any(word in desc_words for word in ['tarmac', 'road', 'pothole', 'paving', 'subsidence', 'bridge', 'path', 'highway', 'surface']):
        category = "Infrastructure"
        reason = "Description mentions road/paving/infrastructure terms."
    elif any(word in desc_words for word in ['heat', 'temperature', 'sun', '44', '45', '52', 'hot', 'heatwave']):
        category = "Heat Extremes"
        reason = "Description mentions heat or temperatures."
    elif any(word in desc_words for word in ['tree', 'trees', 'grass', 'irrigation', 'park', 'branch', 'branches']):
        category = "Park & Flora"
        reason = "Description mentions park/flora terms like 'tree' or 'grass'."
    elif any(word in desc_words for word in ['unlit', 'wiring', 'light', 'electric', 'electrical']):
        category = "Electrical"
        reason = "Description mentions wiring/lighting."
    elif any(word in desc_words for word in ['waste', 'rubbish', 'garbage', 'bin', 'bins']) or "health risk" in desc:
        category = "Waste & Health"
        reason = "Description mentions waste/bins."
    elif any(word in desc_words for word in ['music', 'audible', 'noise', 'loud']):
        category = "Noise"
        reason = "Description mentions noise/music."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # Priority Mapping
    urgent_keywords = ['injury', 'school', 'child', 'unsafe', 'burns', 'health risk', 'dangerous', 'broken', 'fall risk']
    for kw in urgent_keywords:
        if kw in desc:
            priority = "Urgent"
            reason += f" Contains urgent keyword: '{kw}'."
            break

    return {
        "complaint_id": row.get('complaint_id', ''),
        "category": category,
        "priority": priority,
        "reason": reason.strip(),
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    
    TODO: Build this using your AI tool.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    results.append({
                        "complaint_id": row.get('complaint_id', 'UNKNOWN'),
                        "category": "ERROR",
                        "priority": "ERROR",
                        "reason": f"Exception raised: {str(e)}",
                        "flag": "PROCESSING_ERROR"
                    })
    except FileNotFoundError:
        print(f"Error: Could not find input file at {input_path}")
        return

    if results:
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
