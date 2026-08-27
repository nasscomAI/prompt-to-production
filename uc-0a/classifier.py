"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with all original keys plus: category, priority, reason, flag
    """
    import re
    # Create a copy to avoid mutating the original dict in-place
    res = dict(row)
    
    # Retrieve the description
    description = res.get("description", "")
    if not description:
        # Flag nulls
        res["category"] = "Other"
        res["priority"] = "Standard"
        res["reason"] = "Missing or empty complaint description."
        res["flag"] = "NEEDS_REVIEW"
        return res
        
    desc_lower = description.lower()
    
    # Severity keywords detection
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    is_urgent = any(kw in desc_lower for kw in severity_keywords)
    
    # Define taxonomy rules
    category_patterns = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "flooded", "water standing", "rainwater", "water accumulation"],
        "Streetlight": ["streetlight", "streetlights", "unlit", "lights out", "lamp post", "sparking", "flickering"],
        "Waste": ["garbage", "waste", "trash", "dead animal", "dumped", "refuse"],
        "Noise": ["music", "noise", "drilling", "audible", "idling", "amplifier", "amplifiers", "wedding band"],
        "Road Damage": ["road surface", "sinking", "subsidence", "subside", "subsided", "collapsed", "road collapsed", "tiles broken", "road dividers", "tarmac surface", "metal road", "paving", "bridge approach", "footpath", "crater", "cobblestones", "broken bench", "upturned paving"],
        "Heritage Damage": ["heritage", "historic", "ancient", "museum"],
        "Heat Hazard": ["melting", "temperatures", "heatwave", "bubbling", "temperature reads", "storing heat", "burns on contact", "full sun", "exposed to full sun"],
        "Drain Blockage": ["drain", "sewer", "manhole"]
    }
    
    matched_categories = []
    matched_triggers = {}
    
    # Find all matches
    for cat, patterns in category_patterns.items():
        for pattern in patterns:
            if pattern in desc_lower:
                matched_categories.append(cat)
                matched_triggers[cat] = pattern
                break # Move to next category
                
    # Helper to find the sentence containing a pattern
    def get_citation(desc: str, pattern: str) -> str:
        # Split by sentence boundaries, typical periods or commas
        parts = re.split(r'[.,;?!]', desc)
        for part in parts:
            if pattern.lower() in part.lower():
                return part.strip()
        return desc.strip()

    # Determine final category, priority, flag, reason
    flag = ""
    if len(matched_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        priority = "Urgent" if is_urgent else "Standard"
        reason = "Flagged as NEEDS_REVIEW because the description does not fit any defined taxonomy category."
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        priority = "Urgent" if is_urgent else "Standard"
        # Extract citations for the first two matched categories
        cat1, cat2 = matched_categories[0], matched_categories[1]
        trig1, trig2 = matched_triggers[cat1], matched_triggers[cat2]
        cite1 = get_citation(description, trig1)
        cite2 = get_citation(description, trig2)
        reason = f"Flagged as NEEDS_REVIEW because description cites '{cite1}' and '{cite2}', matching multiple categories ({cat1}, {cat2})."
    else:
        category = matched_categories[0]
        # Map priority
        if is_urgent:
            priority = "Urgent"
            matched_severity = next((kw for kw in severity_keywords if kw in desc_lower), "")
            sev_cite = get_citation(description, matched_severity)
            trig = matched_triggers[category]
            cite = get_citation(description, trig)
            if cite == sev_cite:
                reason = f"Classified as {category} (Urgent) because description cites '{cite}' with severity keyword '{matched_severity}'."
            else:
                reason = f"Classified as {category} (Urgent) because description cites '{cite}' and severity is flagged by '{sev_cite}'."
        else:
            priority = "Low" if category == "Noise" else "Standard"
            trig = matched_triggers[category]
            cite = get_citation(description, trig)
            reason = f"Classified as {category} ({priority}) because description cites '{cite}'."
            
    res["category"] = category
    res["priority"] = priority
    res["reason"] = reason
    res["flag"] = flag
    return res


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    processed_count = 0
    success_count = 0
    fail_count = 0
    flagged_count = 0
    
    category_counts = {}
    priority_counts = {}
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if not fieldnames:
                raise ValueError("Input CSV has no headers or is empty.")
            
            # Ensure our new columns are in fieldnames
            new_cols = ["category", "priority", "reason", "flag"]
            out_fieldnames = list(fieldnames)
            for col in new_cols:
                if col not in out_fieldnames:
                    out_fieldnames.append(col)
                    
            for row in reader:
                processed_count += 1
                try:
                    classified_row = classify_complaint(row)
                    results.append(classified_row)
                    
                    # Compute stats
                    cat = classified_row.get("category", "Other")
                    prio = classified_row.get("priority", "Standard")
                    flg = classified_row.get("flag", "")
                    
                    category_counts[cat] = category_counts.get(cat, 0) + 1
                    priority_counts[prio] = priority_counts.get(prio, 0) + 1
                    if flg:
                        flagged_count += 1
                    success_count += 1
                except Exception as e:
                    fail_count += 1
                    print(f"Error classifying row {processed_count}: {e}")
                    # Fallback row to prevent losing data
                    fallback = dict(row)
                    fallback["category"] = "Other"
                    fallback["priority"] = "Standard"
                    fallback["reason"] = f"Failed to classify due to error: {e}"
                    fallback["flag"] = "NEEDS_REVIEW"
                    results.append(fallback)
                    
        # Write output CSV
        with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
        print("=== Classification Summary ===")
        print(f"Total Rows Processed: {processed_count}")
        print(f"Successfully Processed: {success_count}")
        print(f"Failed Rows: {fail_count}")
        print(f"Flagged for Review: {flagged_count}")
        print("\nCategories:")
        for cat, cnt in sorted(category_counts.items()):
            print(f"  - {cat}: {cnt}")
        print("\nPriorities:")
        for prio, cnt in sorted(priority_counts.items()):
            print(f"  - {prio}: {cnt}")
            
    except Exception as e:
        print(f"Fatal error in batch_classify: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
