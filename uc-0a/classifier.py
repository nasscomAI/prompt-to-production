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
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "")
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing complaint description.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = description.lower()
    
    # Severity keywords detection for priority
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    matched_severity = [kw for kw in severity_keywords if kw in desc_lower]
    
    priority = "Urgent" if matched_severity else "Standard"
    
    # Category detection based on keywords
    matched_categories = []
    
    # 1. Pothole
    if "pothole" in desc_lower:
        matched_categories.append(("Pothole", "pothole"))
        
    # 2. Drain Blockage
    if any(kw in desc_lower for kw in ["drain", "manhole", "sewer"]):
        matched_kw = next(kw for kw in ["drain", "manhole", "sewer"] if kw in desc_lower)
        matched_categories.append(("Drain Blockage", matched_kw))
        
    # 3. Streetlight
    if any(kw in desc_lower for kw in ["streetlight", "light", "unlit", "darkness", "substation"]):
        matched_kw = next(kw for kw in ["streetlight", "light", "unlit", "darkness", "substation"] if kw in desc_lower)
        matched_categories.append(("Streetlight", matched_kw))
        
    # 4. Waste
    if any(kw in desc_lower for kw in ["garbage", "waste", "trash", "dumped", "animal", "cleared"]):
        matched_kw = next(kw for kw in ["garbage", "waste", "trash", "dumped", "animal", "cleared"] if kw in desc_lower)
        matched_categories.append(("Waste", matched_kw))
        
    # 5. Noise
    if any(kw in desc_lower for kw in ["music", "noise", "sound", "drilling", "idling", "amplifier", "band"]):
        matched_kw = next(kw for kw in ["music", "noise", "sound", "drilling", "idling", "amplifier", "band"] if kw in desc_lower)
        matched_categories.append(("Noise", matched_kw))
        
    # 6. Heat Hazard
    if any(kw in desc_lower for kw in ["heat", "temperature", "temp", "celsius", "°c", "melting", "bubbling", "sun"]):
        matched_kw = next(kw for kw in ["heat", "temperature", "temp", "celsius", "°c", "melting", "bubbling", "sun"] if kw in desc_lower)
        matched_categories.append(("Heat Hazard", matched_kw))
        
    # 7. Road Damage
    if any(kw in desc_lower for kw in ["road", "footpath", "tile", "paving", "pavement", "collapsed", "sinking", "subside", "cracked", "bridge"]):
        matched_kw = next(kw for kw in ["road", "footpath", "tile", "paving", "pavement", "collapsed", "sinking", "subside", "cracked", "bridge"] if kw in desc_lower)
        matched_categories.append(("Road Damage", matched_kw))
        
    # 8. Flooding
    if any(kw in desc_lower for kw in ["flood", "water", "rain", "underpass"]):
        matched_kw = next(kw for kw in ["flood", "water", "rain", "underpass"] if kw in desc_lower)
        matched_categories.append(("Flooding", matched_kw))

    # 9. Heritage Damage
    if "heritage" in desc_lower or "historic" in desc_lower:
        matched_kw = "heritage" if "heritage" in desc_lower else "historic"
        matched_categories.append(("Heritage Damage", matched_kw))
        
    # Determine primary category and flags
    flag = ""
    
    # Check for ambiguity: multiple categories matched
    unique_categories = list(set(cat for cat, _ in matched_categories))
    
    if len(unique_categories) > 1:
        # We have a conflict or multiple matches.
        # Let's check for specific overlaps to resolve or flag.
        # E.g. "heritage zone garbage overflow" -> Waste (primary), flag NEEDS_REVIEW
        # "Heritage street, lights out" -> Streetlight (primary), flag NEEDS_REVIEW
        # "Bus stand flooded... Drain blocked." -> Drain Blockage (primary), flag NEEDS_REVIEW
        flag = "NEEDS_REVIEW"
        
        # Precedence order to resolve primary category
        precedence = ["Pothole", "Drain Blockage", "Streetlight", "Waste", "Noise", "Heat Hazard", "Flooding", "Road Damage", "Heritage Damage"]
        primary_category = next((c for c in precedence if c in unique_categories), unique_categories[0])
    elif len(unique_categories) == 1:
        primary_category = unique_categories[0]
        # Some specific single-category cases might still want NEEDS_REVIEW
        if "manhole" in desc_lower or "animal" in desc_lower or "heritage" in desc_lower or "historic" in desc_lower:
            flag = "NEEDS_REVIEW"
    else:
        primary_category = "Other"
        if matched_severity:
            flag = "NEEDS_REVIEW"
            
    # Find matching snippet in original description for citation
    matched_word = ""
    if matched_categories:
        for cat, kw in matched_categories:
            if cat == primary_category:
                matched_word = kw
                break
    else:
        matched_word = "general issue"
        
    # Try to find the exact case match in the description
    import re
    if matched_word != "general issue":
        pattern = re.compile(re.escape(matched_word), re.IGNORECASE)
        match = pattern.search(description)
        if match:
            matched_word_exact = match.group(0)
        else:
            matched_word_exact = matched_word
    else:
        matched_word_exact = "general issue"
        
    # Construct a single sentence reason citing specific words
    if matched_severity:
        severity_words = ", ".join(f"'{s}'" for s in matched_severity)
        reason = f"Classified as {primary_category} due to description mentioning '{matched_word_exact}', and marked Urgent because of severity indicator(s): {severity_words}."
    else:
        reason = f"Classified as {primary_category} because the description mentions '{matched_word_exact}'."

    return {
        "complaint_id": complaint_id,
        "category": primary_category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            output_fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            results = []
            
            for row in reader:
                try:
                    if not row.get('complaint_id'):
                        continue
                    
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as row_error:
                    results.append({
                        "complaint_id": row.get('complaint_id', 'UNKNOWN'),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Row processing failed: {str(row_error)}",
                        "flag": "NEEDS_REVIEW"
                    })
                    
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
            writer.writeheader()
            for res in results:
                writer.writerow(res)
                
    except FileNotFoundError:
        print(f"Error: The input file {input_path} does not exist.")
        raise
    except Exception as e:
        print(f"Error during batch classification: {e}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
