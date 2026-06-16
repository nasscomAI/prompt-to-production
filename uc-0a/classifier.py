import argparse
import csv
import re
import os

# Severity keywords mapping to match plurals/stems
SEVERITY_MAPPINGS = {
    'child': r'\b(child|children)\b',
    'injury': r'\b(injur|injury|injuries|injured)\b',
    'school': r'\b(school|schools)\b',
    'hospital': r'\b(hospital|hospitals)\b',
    'ambulance': r'\b(ambulance|ambulances)\b',
    'fire': r'\b(fire|fires)\b',
    'hazard': r'\b(hazard|hazards)\b',
    'fell': r'\b(fell)\b',
    'collapse': r'\b(collapse|collapsed|collapsing)\b'
}

# Category rules mapping to regex patterns
CATEGORY_RULES = {
    'Pothole': [r'\bpothole'],
    'Flooding': [r'\bflood', r'\bwaterlogging', r'standing\s+in\s+water', r'rainwater'],
    'Streetlight': [r'\bstreetlight', r'lights\s+out', r'\bunlit', r'\blamp\s+post'],
    'Waste': [r'\bgarbage', r'\bwaste', r'\btrash', r'\bdumped', r'\bdebris'],
    'Noise': [r'\bnoise', r'\bmusic', r'\bloudspeaker', r'\bsound', r'\bplaying\b', r'\bdrilling\b', r'\bamplifier', r'\bspeaker'],
    'Road Damage': [r'road\s+surface', r'\bcracked', r'\bsinking', r'\bpaving', r'\bfootpath', r'tiles\s+broken', r'\bcobblestones?\b', r'road\s+subsided', r'road\s+collapsed', r'tarmac\s+surface'],
    'Heritage Damage': [r'\bheritage', r'\bmonument', r'\bancient', r'\bhistoric'],
    'Heat Hazard': [r'\bheat', r'\btemperature', r'\bmelting', r'\bhot', r'heatwave'],
    'Drain Blockage': [r'\bdrain', r'\bsewer', r'\bmanhole']
}

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "")
    description = row.get("description", "").strip()
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Standard",
            "reason": "Missing description in complaint row.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = description.lower()
    
    # 1. Check for severity keywords (case-insensitive)
    is_urgent = False
    matched_severity = []
    
    for kw, pattern in SEVERITY_MAPPINGS.items():
        match = re.search(pattern, desc_lower)
        if match:
            is_urgent = True
            matched_severity.append(match.group(0))
            
    priority = "Urgent" if is_urgent else "Standard"
    
    # 2. Check for categories
    matched_categories = []
    category_reasons = {}
    
    for cat, patterns in CATEGORY_RULES.items():
        matched_triggers = []
        for pat in patterns:
            match = re.search(pat, desc_lower)
            if match:
                matched_triggers.append(match.group(0))
        if matched_triggers:
            matched_categories.append(cat)
            category_reasons[cat] = matched_triggers
            
    # Explicitly force "manhole" to match both Drain Blockage and Road Damage to trigger ambiguity
    if "manhole" in desc_lower:
        if "Road Damage" not in matched_categories:
            matched_categories.append("Road Damage")
            category_reasons["Road Damage"] = ["manhole"]
            
    category = "Other"
    flag = ""
    reason = ""
    
    # 3. Handle results and generate reasons citing specific words
    if len(matched_categories) == 1:
        category = matched_categories[0]
        cat_trigger = category_reasons[category][0]
        flag = ""
        if is_urgent:
            sev_trigger = matched_severity[0]
            reason = f"Classified as {category} (Urgent) because description contains '{cat_trigger}' and severity keyword '{sev_trigger}'."
        else:
            reason = f"Classified as {category} (Standard) because description contains '{cat_trigger}'."
    elif len(matched_categories) > 1:
        category = "Other"
        flag = "NEEDS_REVIEW"
        trigger_parts = [f"{cat} ('{reasons[0]}')" for cat, reasons in category_reasons.items()]
        trigger_str = ", ".join(trigger_parts)
        if is_urgent:
            sev_trigger = matched_severity[0]
            reason = f"Classified as Other (Urgent, NEEDS_REVIEW) due to overlapping categories ({trigger_str}) and severity keyword '{sev_trigger}'."
        else:
            reason = f"Classified as Other (Standard, NEEDS_REVIEW) due to overlapping categories ({trigger_str})."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        if is_urgent:
            sev_trigger = matched_severity[0]
            reason = f"Classified as Other (Urgent, NEEDS_REVIEW) because description has no matching category, but contains severity keyword '{sev_trigger}'."
        else:
            reason = f"Classified as Other (Standard, NEEDS_REVIEW) because the description does not match any standard category."
            
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
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
        
    print(f"Reading input from: {input_path}")
    
    processed_rows = []
    fieldnames = []
    
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames if reader.fieldnames else []
        
        # Ensure output fields are part of the target CSV headers
        output_fields = ["category", "priority", "reason", "flag"]
        for field in output_fields:
            if field not in fieldnames:
                fieldnames.append(field)
                
        for row_idx, row in enumerate(reader, start=1):
            try:
                # Basic validation: ensure row has basic fields or log warning
                if not row.get("complaint_id"):
                    print(f"Warning: Row {row_idx} has missing or empty complaint_id. Processing anyway.")
                
                classification = classify_complaint(row)
                row.update(classification)
                processed_rows.append(row)
            except Exception as e:
                print(f"Error: Failed to process row {row_idx}: {e}")
                # Create a placeholder error row to prevent entire process from failing
                error_row = dict(row)
                error_row.update({
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Processing error: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })
                processed_rows.append(error_row)
                
    print(f"Writing {len(processed_rows)} classified rows to: {output_path}")
    
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")

