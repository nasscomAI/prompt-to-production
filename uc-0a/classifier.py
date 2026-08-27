"""
UC-0A — Complaint Classifier
Updated according to RICE -> agents.md -> skills.md
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    """
    desc = row.get("description", "").lower()
    
    category = "Other"
    priority = "Standard"
    reason = "Unable to classify based on description."
    flag = "NEEDS_REVIEW"
    
    if not desc:
        return {"complaint_id": row.get("complaint_id", ""), "category": category, "priority": priority, "reason": reason, "flag": flag}
        
    found_category = False
    cited_word = ""

    # Category Mapping Logic
    if "pothole" in desc:
        category = "Pothole"
        cited_word = "pothole"
    elif "flood" in desc or "rain" in desc:
        category = "Flooding"
        cited_word = "flood/rain"
    elif "light" in desc or "dark" in desc:
        category = "Streetlight"
        cited_word = "light/dark"
    elif "waste" in desc or "garbage" in desc or "dead animal" in desc:
        category = "Waste"
        cited_word = "waste/garbage/animal"
    elif "noise" in desc or "music" in desc:
        category = "Noise"
        cited_word = "noise/music"
    elif "crack" in desc or "road surface" in desc or "footpath tiles" in desc:
        category = "Road Damage"
        cited_word = "crack/road/tiles"
    elif "heritage" in desc:
        category = "Heritage Damage"
        cited_word = "heritage"
    elif "drain" in desc or "manhole" in desc:
        category = "Drain Blockage"
        cited_word = "drain/manhole"
        
    if cited_word:
        found_category = True
        
    urgent_kw = next((kw for kw in URGENT_KEYWORDS if kw in desc), None)
    if urgent_kw:
        priority = "Urgent"

    if found_category:
        flag = ""
        reason = f"Categorized as {category} citing '{cited_word}'."
        if urgent_kw:
            reason += f" Marked Urgent citing '{urgent_kw}'."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "No definitive category keywords found in description."

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
    
    with open(input_path, 'r', encoding='utf-8') as fin:
        reader = csv.DictReader(fin)
        fieldnames = reader.fieldnames
        for i, row in enumerate(reader):
            try:
                classification = classify_complaint(row)
                out_row = dict(row)
                out_row["category"] = classification["category"]
                out_row["priority"] = classification["priority"]
                out_row["reason"] = classification["reason"]
                out_row["flag"] = classification["flag"]
                results.append(out_row)
            except Exception as e:
                print(f"Error on row {i}: {e}")
                # Don't crash, write empty row
                out_row = dict(row)
                out_row["category"] = "Other"
                out_row["priority"] = "Standard"
                out_row["reason"] = "Processing Error"
                out_row["flag"] = "NEEDS_REVIEW"
                results.append(out_row)
            
    if results:
        out_fields = fieldnames + ["category", "priority", "reason", "flag"]
        with open(output_path, 'w', encoding='utf-8', newline='') as fout:
            writer = csv.DictWriter(fout, fieldnames=out_fields)
            writer.writeheader()
            writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
