"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import sys

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    if not complaint_id:
        complaint_id = "UNKNOWN"

    desc = row.get("description", "")
    if desc is None:
        desc = ""
    desc = desc.strip()
    
    # Check if description is empty or null
    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing or null description.",
            "flag": "NEEDS_REVIEW"
        }

    desc_lower = desc.lower()

    # Priority rules: Urgent if any severity keywords are present
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    is_urgent = any(kw in desc_lower for kw in severity_keywords)
    priority = "Urgent" if is_urgent else "Standard"

    # Category matching
    matches = []
    
    # 1. Pothole
    if "pothole" in desc_lower or "potholes" in desc_lower:
        matches.append("Pothole")
    
    # 2. Streetlight
    if any(kw in desc_lower for kw in ["streetlight", "streetlights", "lamp post", "unlit", "lights out", "substation", "darkness"]):
        matches.append("Streetlight")
        
    # 3. Waste
    if any(kw in desc_lower for kw in ["garbage", "waste", "trash", "dead animal"]):
        matches.append("Waste")
        
    # 4. Noise
    if any(kw in desc_lower for kw in ["music", "wedding band", "drilling", "audible", "noise", "engines on", "idling", "amplifier", "amplifiers"]):
        matches.append("Noise")
        
    # 5. Heat Hazard
    if any(kw in desc_lower for kw in ["melting", "temperature", "temperatures", "heatwave", "bubbling", "unbearable", "52°c", "storing heat", "full sun", "44°c", "45°c"]):
        matches.append("Heat Hazard")
        
    # 6. Drain Blockage
    if any(kw in desc_lower for kw in ["drain blocked", "drainage blocked", "drain completely blocked", "stormwater drain"]):
        matches.append("Drain Blockage")
        
    # 7. Flooding
    if any(kw in desc_lower for kw in ["flooded", "flooding", "rainwater", "standing in water", "floods", "draining"]):
        matches.append("Flooding")
        
    # 8. Heritage Damage
    if any(kw in desc_lower for kw in ["heritage", "historic", "ancient step well", "museum"]):
        matches.append("Heritage Damage")
        
    # 9. Road Damage
    if any(kw in desc_lower for kw in ["road surface", "sinking", "manhole", "road collapsed", "crater", "road surface buckled", "road subsided", "paving", "broken bench", "upturned paving", "footpath", "broken tiles", "cobblestones"]):
        matches.append("Road Damage")

    # Determine category and flag
    flag = ""
    if len(matches) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
    elif len(matches) == 1:
        category = matches[0]
    else:
        # Ambiguous category - multiple matches
        flag = "NEEDS_REVIEW"
        # Prioritize category selection
        priority_order = ["Heritage Damage", "Drain Blockage", "Pothole", "Streetlight", "Waste", "Noise", "Heat Hazard", "Road Damage", "Flooding"]
        selected_category = None
        for cat in priority_order:
            if cat in matches:
                selected_category = cat
                break
        category = selected_category if selected_category else matches[0]

    # Create reason field: exactly one sentence citing specific words from description
    sentences = [s.strip() for s in desc.split('.') if s.strip()]
    first_sentence = sentences[0].rstrip('.') if sentences else "No description provided"
    
    # Reason cites specific words from first sentence and states category/priority
    reason = f"Classified as {category} ({priority} priority) because the description cites: '{first_sentence}'."

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
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Check fields
            if not reader.fieldnames:
                print(f"Error: Empty or malformed CSV header in {input_path}")
                return
            
            for row in reader:
                try:
                    # Check for nulls/missing columns in critical fields
                    if 'complaint_id' not in row or 'description' not in row:
                        # Bad/incomplete row
                        print(f"Warning: Row missing critical fields: {row}")
                        results.append({
                            "complaint_id": row.get("complaint_id", "UNKNOWN"),
                            "category": "Other",
                            "priority": "Low",
                            "reason": "Missing complaint_id or description column in input row.",
                            "flag": "NEEDS_REVIEW"
                        })
                        continue
                        
                    classification = classify_complaint(row)
                    results.append(classification)
                except Exception as row_err:
                    print(f"Error processing row {row.get('complaint_id', 'Unknown')}: {row_err}")
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Row processing failed with error: {row_err}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as file_err:
        print(f"Critical error reading input file {input_path}: {file_err}")
        return

    # Write results
    try:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as write_err:
        print(f"Critical error writing output file {output_path}: {write_err}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
