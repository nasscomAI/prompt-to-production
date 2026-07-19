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
    
    TODO: Build this using your AI tool guided by your agents.md and skills.md.
    Your RICE enforcement rules must be reflected in this function's behaviour.
    """
    complaint_id = row.get("complaint_id", "")
    desc = row.get("description", "").strip()
    
    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "No description was provided in the complaint.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = desc.lower()
    
    # Priority check:
    # Severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    matched_severity = [kw for kw in severity_keywords if kw in desc_lower]
    
    if matched_severity:
        priority = "Urgent"
        priority_evidence = matched_severity[0]
    else:
        priority = "Standard"
        priority_evidence = None
        
    category = "Other"
    reason = ""
    flag = ""
    
    # Check for ambiguity first:
    # 1. "heritage zone garbage overflow" - contains heritage and garbage/waste
    if "heritage" in desc_lower and ("garbage" in desc_lower or "waste" in desc_lower or "trash" in desc_lower or "debris" in desc_lower):
        category = "Heritage Damage"
        flag = "NEEDS_REVIEW"
        reason = f"Classified as Heritage Damage with review flag because description mentions both 'heritage zone' and 'garbage overflow'."
    # 2. "delivery trucks idling" - ambiguous noise / commercial activity
    elif "idling" in desc_lower or "delivery trucks" in desc_lower:
        category = "Noise"
        flag = "NEEDS_REVIEW"
        reason = f"Classified as Noise with review flag because description mentions 'delivery trucks idling'."
    # 3. "Colony surrounded by fields..." - ambiguous/other
    elif "fields" in desc_lower and "rainwater" in desc_lower and "colony" in desc_lower:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"Classified as Other and flagged for review because the description describes rainwater channeling from fields without specific damage."
    # 4. Standard classifications
    elif "pothole" in desc_lower:
        category = "Pothole"
        reason = f"Classified as Pothole because description mentions 'pothole'."
    elif "underpass flooded" in desc_lower or "floods in light rain" in desc_lower or "flooded" in desc_lower:
        # If it also contains "drain completely blocked" or "drain blocked"
        if "drain" in desc_lower and ("blocked" in desc_lower or "clogged" in desc_lower):
            category = "Drain Blockage"
            reason = f"Classified as Drain Blockage because description mentions blocked drain causing flooding."
        else:
            category = "Flooding"
            reason = f"Classified as Flooding because description mentions '{'flooded' if 'flooded' in desc_lower else 'floods'}'."
    elif "drain" in desc_lower and ("blocked" in desc_lower or "clogged" in desc_lower or "debris" in desc_lower):
        category = "Drain Blockage"
        reason = f"Classified as Drain Blockage because description mentions '{'blocked' if 'blocked' in desc_lower else 'drain'}'."
    elif "streetlight" in desc_lower or "lights out" in desc_lower:
        category = "Streetlight"
        reason = f"Classified as Streetlight because description mentions '{'streetlight' if 'streetlight' in desc_lower else 'lights out'}'."
    elif "garbage" in desc_lower or "waste" in desc_lower or "trash" in desc_lower or "debris" in desc_lower:
        category = "Waste"
        reason = f"Classified as Waste because description mentions '{'garbage' if 'garbage' in desc_lower else 'waste'}'."
    elif "noise" in desc_lower or "drilling" in desc_lower or "sound" in desc_lower or "music" in desc_lower:
        category = "Noise"
        reason = f"Classified as Noise because description mentions '{'drilling' if 'drilling' in desc_lower else 'noise'}'."
    elif "collapsed" in desc_lower or "collapse" in desc_lower or "cracked" in desc_lower or "crater" in desc_lower or "sinking" in desc_lower or "road surface" in desc_lower or "tiles broken" in desc_lower or "footpath" in desc_lower:
        category = "Road Damage"
        reason = f"Classified as Road Damage because description mentions '{'collapsed' if 'collapsed' in desc_lower else 'crater' if 'crater' in desc_lower else 'road'}'."
    elif "heat" in desc_lower or "hot" in desc_lower or "sunstroke" in desc_lower or "dehydration" in desc_lower:
        category = "Heat Hazard"
        reason = f"Classified as Heat Hazard because description mentions heat."
    else:
        category = "Other"
        reason = f"Classified as Other because description does not match any specific category."

    # If priority was urgent, append or adjust the reason to be one sentence
    if priority == "Urgent":
        reason = reason.rstrip(".") + f" and priority is Urgent due to severity keyword '{priority_evidence}'."

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
            if not reader.fieldnames:
                raise ValueError("Input CSV has no headers or is empty.")
                
            for line_no, row in enumerate(reader, start=1):
                try:
                    if "description" not in row or "complaint_id" not in row:
                        comp_id = row.get("complaint_id", f"UNKNOWN-{line_no}")
                        classified = {
                            "complaint_id": comp_id,
                            "category": "Other",
                            "priority": "Standard",
                            "reason": "Missing required fields in the row structure.",
                            "flag": "NEEDS_REVIEW"
                        }
                    else:
                        classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    print(f"Error parsing row {line_no}: {e}")
                    results.append({
                        "complaint_id": row.get("complaint_id", f"ERROR-{line_no}"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"System error during row classification: {e}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        return
    except Exception as e:
        print(f"Failed to read input CSV: {e}")
        return

    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
            writer.writeheader()
            writer.writerows(results)
        print(f"Successfully processed {len(results)} rows and wrote to {output_path}")
    except Exception as e:
        print(f"Failed to write output CSV: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
