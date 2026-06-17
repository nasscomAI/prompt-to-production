import argparse
import csv
import sys

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    comp_id = row.get("complaint_id", "").strip()
    desc = row.get("description", "").strip()
    
    if not desc:
        return {
            "complaint_id": comp_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Complaint description is empty.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = desc.lower()
    
    # Category keywords mapping
    categories_keywords = {
        "Pothole": ["pothole", "crater"],
        "Flooding": ["flood", "flooded", "floods", "waterlogging", "rainwater"],
        "Streetlight": ["streetlight", "street light", "lamp post", "unlit", "dark", "lights out", "wiring theft"],
        "Waste": ["garbage", "waste", "trash", "bins", "dead animal", "debris", "dumped"],
        "Noise": ["music", "wedding band", "drilling", "noise", "idling", "amplifiers"],
        "Road Damage": ["road surface cracked", "sinking", "uneven road", "footpath", "tiles broken", "manhole", "road surface buckled", "road collapsed", "road subsidence", "tarmac surface"],
        "Heritage Damage": ["heritage", "historic", "ancient step well"],
        "Heat Hazard": ["heatwave", "melting", "44°c", "45°c", "52°c", "temperature", "burns", "sun"],
        "Drain Blockage": ["drain blocked", "drainage", "sewer", "stormwater drain", "blocked"]
    }
    
    matched_categories = []
    for cat, keywords in categories_keywords.items():
        for kw in keywords:
            if kw in desc_lower:
                matched_categories.append(cat)
                break
                
    matched_categories = list(set(matched_categories))
    
    # Priority keywords detection
    priority_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    is_urgent = False
    matched_priority_kw = []
    for kw in priority_keywords:
        if kw in desc_lower:
            is_urgent = True
            matched_priority_kw.append(kw)
            
    priority = "Urgent" if is_urgent else "Standard"
    
    # Resolve category and review flags
    category = "Other"
    flag = ""
    
    if len(matched_categories) == 1:
        category = matched_categories[0]
        reason_cat = f"Classified as {category} because description mentions '{matched_categories[0].lower()}' keywords."
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_cat = f"Ambiguous complaint matching multiple categories ({', '.join(matched_categories)})."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason_cat = "Unable to determine category from the description alone."
        
    if is_urgent:
        reason_pri = f" Priority set to Urgent due to severity keyword '{matched_priority_kw[0]}'."
    else:
        reason_pri = ""
        
    reason = f"{reason_cat}{reason_pri}"
    
    return {
        "complaint_id": comp_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames:
                print(f"Error: Input file {input_path} has no headers.", file=sys.stderr)
                return
            
            results = []
            for row_idx, row in enumerate(reader, start=1):
                try:
                    classification = classify_complaint(row)
                    results.append(classification)
                except Exception as e:
                    print(f"Warning: Failed to classify row {row_idx}: {e}", file=sys.stderr)
                    # Add a placeholder row so we don't drop rows from input
                    results.append({
                        "complaint_id": row.get("complaint_id", f"UNKNOWN_{row_idx}"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"System error during classification: {e}",
                        "flag": "NEEDS_REVIEW"
                    })
                    
        # Write results
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
        print(f"Successfully processed {len(results)} rows.")
        
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}", file=sys.stderr)
    except Exception as e:
        print(f"Error: Unexpected error during batch classification: {e}", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
