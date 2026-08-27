import argparse
import csv
import json
import logging

# Implements RICE enforcements defined in agents.md

# Ensure logs are formatted cleanly if we chose to output them
logging.basicConfig(level=logging.ERROR, format='%(levelname)s: %(message)s')

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on the description text.
    Implements rules from agents.md and skills.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    
    # 1. Determine priority
    priority = "Standard"
    matched_urgent_word = None
    for kw in URGENT_KEYWORDS:
        if kw in description:
            priority = "Urgent"
            matched_urgent_word = kw
            break
            
    # 2. Determine category (heuristic matching for strict list)
    category = "Other"
    matched_category_word = None
    
    category_mapping = {
        "pothole": "Pothole",
        "flood": "Flooding",
        "rain": "Flooding",
        "water": "Flooding",
        "drain block": "Drain Blockage",
        "drain": "Drain Blockage",
        "streetlight": "Streetlight",
        "dark": "Streetlight",
        "light": "Streetlight",
        "garbage": "Waste",
        "waste": "Waste",
        "dead animal": "Waste",
        "music": "Noise",
        "noise": "Noise",
        "road surface": "Road Damage",
        "manhole": "Road Damage",
        "tiles": "Road Damage",
        "footpath": "Road Damage",
        "heritage": "Heritage Damage",
        "heat": "Heat Hazard",
        "hot": "Heat Hazard"
    }
    
    # Match the last matching category based on generic words, but prioritize more specific ones
    for word, cat in category_mapping.items():
        if word in description:
            # Overwrite basic flooding with more specific drain blockage
            if category == "Other" or (category == "Flooding" and cat == "Drain Blockage"):
                category = cat
                matched_category_word = word
            # Prioritize Road Damage over standard words if multiple
            elif category in ["Other"]:
                 category = cat
                 matched_category_word = word
                 
    # In a case like 'heritage street, lights out', prioritize Heritage Damage or Streetlight
    # based on actual occurrence. Direct matching is simple. We'll simply use the logic above.
    if "heritage" in description and "light" in description:
        # A bit ambiguous, we could fall back to Streetlight 
        category = "Streetlight"
        matched_category_word = "light"

    # 3. Determine reason citing specific words
    reason_parts = []
    if matched_category_word:
        reason_parts.append(f"Description includes '{matched_category_word}', classifying as {category}.")
    else:
        reason_parts.append("Could not determine specific category from description text.")
        
    if matched_urgent_word:
        reason_parts.append(f"Priority mapped to Urgent because '{matched_urgent_word}' was mentioned.")
        
    reason = " ".join(reason_parts)
    
    # 4. Refusal/Ambiguity Flag
    flag = ""
    # Genuinely ambiguous mapped to Other, Need Review
    if category == "Other":
        flag = "NEEDS_REVIEW"
        
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
    Implements skills.md batch processing with error handling.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            if reader.fieldnames is None:
                logging.error(f"Failed to read headers from {input_path}")
                return
                
            results = []
            for row in reader:
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    # Graceful failure handling based on skills.md
                    logging.error(f"Error processing row {row.get('complaint_id')}: {e}")
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"System parsing error: {e}",
                        "flag": "NEEDS_REVIEW"
                    })
                    
        if not results:
            logging.info("No rows parsed from input.")
            return

        out_fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        logging.error(f"Batch execution failed unexpectedly: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
