"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on rules defined in RICE output.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "").lower()
    
    # Predefined allowed categories mappings
    category_mapping = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "streetlight": "Streetlight",
        "lights out": "Streetlight",
        "waste": "Waste",
        "garbage": "Waste",
        "noise": "Noise",
        "music": "Noise",
        "road surface": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "drain": "Drain Blockage",
        "manhole": "Drain Blockage"
    }
    
    # Priority severity triggers
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    
    # Determine Category
    category = "Other"
    matched_word = ""
    for key, cat in category_mapping.items():
        if key in desc:
            category = cat
            matched_word = key
            break
            
    # Determine Priority
    priority = "Standard"
    sev_word_found = ""
    for word in severity_keywords:
        if word in desc:
            priority = "Urgent"
            sev_word_found = word
            break
            
    # Assign Reason & Flag
    if matched_word and sev_word_found:
        reason = f"Classified based on '{matched_word}' and escalated due to '{sev_word_found}'."
    elif matched_word:
        reason = f"Matched against predefined keyword: '{matched_word}'."
    elif sev_word_found:
        reason = f"Could not determine exact category, but severity elevated due to '{sev_word_found}'."
    else:
        reason = "Could not definitively classify based on description text."
        
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    
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
        with open(input_path, "r", encoding="utf-8") as fin:
            reader = csv.DictReader(fin)
            for row in reader:
                if not row: continue
                try:
                    res = classify_complaint(row)
                    results.append(res)
                except Exception as e:
                    print(f"Skipping row {row.get('complaint_id', 'Unknown')} due to error: {e}")
                    
        if results:
            with open(output_path, "w", encoding="utf-8", newline="") as fout:
                fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
                writer = csv.DictWriter(fout, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
    except Exception as e:
        print(f"Failed to process batch: {e}")


if __name__ == "__main__":
    import os
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--city", help="City name to process automatically (e.g. pune, hyderabad)")
    parser.add_argument("--input", help="Optional explicit input CSV path")
    parser.add_argument("--output", help="Optional explicit output CSV path")
    args = parser.parse_args()

    base_dir = r"c:\Users\kanna\OneDrive\Desktop\Nasscom AI workshop\prompt-to-production"

    if args.city:
        city = args.city.lower()
        in_path = os.path.join(base_dir, "data", "city-test-files", f"test_{city}.csv")
        out_path = os.path.join(base_dir, "uc-0a", f"results_{city}.csv")
        
        if os.path.exists(in_path):
            batch_classify(in_path, out_path)
            print(f"Processed '{city}' -> written to {out_path}")
        else:
            print(f"Error: Data for '{city}' not found at {in_path}")
            
    elif args.input and args.output:
        batch_classify(args.input, args.output)
        print(f"Done. Results written to {args.output}")
        
    else:
        print("No specific arguments provided. Processing all workshop cities by default...")
        cities = ["pune", "hyderabad", "kolkata", "ahmedabad"]
        
        for city in cities:
            in_path = os.path.join(base_dir, "data", "city-test-files", f"test_{city}.csv")
            out_path = os.path.join(base_dir, "uc-0a", f"results_{city}.csv")
            
            if os.path.exists(in_path):
                batch_classify(in_path, out_path)
                print(f"Processed '{city}' -> written to {out_path}")
            else:
                print(f"Warning: Input file not found for {city}: {in_path}")
