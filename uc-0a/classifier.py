"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using keyword scoring and RICE rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    # Define taxonomies and keywords
    categories = {
        "Pothole": ["pothole", "crater", "cavity", "tyre damage", "potholes", "manhole"],
        "Flooding": ["flooding", "flooded", "standing water", "submerged", "underpass flooded", "floods", "rain"],
        "Streetlight": ["streetlight", "lights out", "flickering", "dark", "lamp"],
        "Waste": ["garbage", "trash", "waste", "bins", "overflowing garbage", "dumped", "dead animal", "health"],
        "Noise": ["noise", "loud", "music", "midnight", "speakers"],
        "Road Damage": ["cracked", "sinking", "uneven", "damaged road", "surface", "footpath", "broken", "upturned", "tiles"],
        "Heritage Damage": ["heritage", "monument", "historic", "ancient"],
        "Heat Hazard": ["heat", "hot", "sunstroke", "exhaustion", "water station"],
        "Drain Blockage": ["drain", "sewage", "blocked", "clogged", "sewer"],
    }
    
    # Severity keywords (Urgent trigger)
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    
    # Determine Category
    best_category = "Other"
    max_matches = 0
    matched_words = []
    
    for category, keywords in categories.items():
        matches = []
        for word in keywords:
            # Match word with boundaries. Handle multi-word phrases by allowing spaces.
            if re.search(rf"\b{re.escape(word)}\b", description):
                matches.append(word)
        
        if len(matches) > max_matches:
            max_matches = len(matches)
            best_category = category
            matched_words = matches
        elif len(matches) == max_matches and matches:
            # Tie-breaking: keep the more specific ones or just common sense
            pass
            
    # Priority Logic
    priority = "Standard"
    is_urgent = any(re.search(rf"\b{re.escape(word)}\b", description) for word in severity_keywords)
    if is_urgent:
        priority = "Urgent"
        # Find which severity keyword triggered it for the reason
        trigger = next((word for word in severity_keywords if re.search(rf"\b{re.escape(word)}\b", description)), "safety risks")
        if trigger not in matched_words:
            matched_words.append(trigger)
    elif "low" in description or "minor" in description:
        priority = "Low"
        
    # Reason Generation (Must be one sentence, citing words)
    if best_category != "Other":
        citations = ", ".join(set(matched_word for matched_word in matched_words))
        reason = f"The complaint mentions {citations}, which directly indicates a {best_category} issue with potential {priority} implications."
    else:
        reason = "The description is generic or does not contain specific keywords from the defined taxonomy."
        
    # Flag Logic
    flag = ""
    if best_category == "Other" or not description or max_matches == 0:
        best_category = "Other"
        flag = "NEEDS_REVIEW"
        
    return {
        "complaint_id": complaint_id,
        "category": best_category,
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
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Error classifying row {row.get('complaint_id')}: {e}")
                    
        if not results:
            print("No results to write.")
            return

        keys = results[0].keys()
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
            
    except FileNotFoundError:
        print(f"Input file not found: {input_path}")
    except Exception as e:
        print(f"Batch processing error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
