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
    import re
    
    complaint_id = row.get("complaint_id", "").strip()
    description = row.get("description", "").strip()
    
    category = "Other"
    priority = "Standard"
    reason = ""
    flag = ""
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing or empty description.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = description.lower()
    matched_categories = []
    
    # Helper pattern checker
    def check_pattern(pattern_str):
        return re.search(pattern_str, desc_lower) is not None
        
    # Category detection rules using word boundaries to prevent false partial matches
    if check_pattern(r'\bpothole'):
        matched_categories.append(("Pothole", "pothole"))
        
    if check_pattern(r'\bflood') or check_pattern(r'\brainwater') or check_pattern(r'\brain water') or check_pattern(r'\brain\b'):
        matched_categories.append(("Flooding", "flooding"))
        
    if check_pattern(r'\bstreetlight') or check_pattern(r'\bstreet light') or check_pattern(r'\blamp post') or check_pattern(r'\bunlit') or check_pattern(r'\blights out') or check_pattern(r'\bdarkness'):
        matched_categories.append(("Streetlight", "lights/substation out"))
        
    if check_pattern(r'\bgarbage') or check_pattern(r'\bwaste') or check_pattern(r'\bdead animal') or check_pattern(r'\brefuse') or check_pattern(r'\bdumped') or check_pattern(r'\blitter'):
        matched_categories.append(("Waste", "garbage/waste"))
        
    if check_pattern(r'\bmusic') or check_pattern(r'\bdrilling') or check_pattern(r'\bnoise') or check_pattern(r'\bsound') or check_pattern(r'\bidling') or check_pattern(r'\bamplifier') or check_pattern(r'\bwedding band'):
        matched_categories.append(("Noise", "noise/music/drilling"))
        
    if check_pattern(r'\broad surface') or check_pattern(r'\bpaving') or check_pattern(r'\bfootpath') or check_pattern(r'\bcobblestones') or check_pattern(r'\bcrater') or check_pattern(r'\bsubsid') or check_pattern(r'\bcollaps') or check_pattern(r'\bbuckl') or check_pattern(r'\btiles broken') or check_pattern(r'\bstep well'):
        matched_categories.append(("Road Damage", "road/footpath/paving damage"))
        
    if check_pattern(r'\bheritage') or check_pattern(r'\bhistoric') or check_pattern(r'\bancient') or check_pattern(r'\bmuseum'):
        matched_categories.append(("Heritage Damage", "heritage area/structure"))
        
    if check_pattern(r'\bmelting') or check_pattern(r'\btemperature') or check_pattern(r'\bheat') or check_pattern(r'\bsun\b') or check_pattern(r'\bhot\b') or check_pattern(r'\bburn') or check_pattern(r'\bheatwave') or check_pattern(r'°c'):
        matched_categories.append(("Heat Hazard", "extreme heat/temperature"))
        
    if check_pattern(r'\bdrain') or check_pattern(r'\bmanhole') or check_pattern(r'\bsewer') or check_pattern(r'\bdrainage'):
        matched_categories.append(("Drain Blockage", "drain blockage"))
        
    # Refinement: Pothole is a specific type of Road Damage. If both match, drop Road Damage.
    category_names = [cat for cat, _ in matched_categories]
    if "Pothole" in category_names and "Road Damage" in category_names:
        matched_categories = [item for item in matched_categories if item[0] != "Road Damage"]
        
    # Finalize category selection and reason
    if len(matched_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Could not determine category from the description."
    elif len(matched_categories) == 1:
        category = matched_categories[0][0]
        reason = f"Classified as {category} based on keywords matching '{matched_categories[0][1]}'."
    else:
        category = matched_categories[0][0]
        flag = "NEEDS_REVIEW"
        matched_names = ", ".join([cat for cat, _ in matched_categories])
        reason = f"Ambiguous complaint matching multiple categories ({matched_names}); defaulted to {category}."
        
    # Priority checking based on severity keywords (word prefix matches)
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    found_severity = [kw for kw in severity_keywords if check_pattern(r'\b' + kw)]
    
    if found_severity:
        priority = "Urgent"
        reason += f" Set priority to Urgent due to severity keyword(s): {', '.join(found_severity)}."
    else:
        priority = "Standard"
        
    reason = reason.replace("..", ".").strip()
    if not reason.endswith("."):
        reason += "."
        
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
    output_fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    rows_to_write = []
    
    try:
        with open(input_path, mode="r", encoding="utf-8-sig") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                try:
                    result = classify_complaint(row)
                    rows_to_write.append(result)
                except Exception as e:
                    rows_to_write.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"Exception during classification: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except Exception as e:
        print(f"Critical read error: {e}")
        # Write at least headers to the output file to avoid complete crash
        with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
            writer.writeheader()
        return

    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(rows_to_write)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

