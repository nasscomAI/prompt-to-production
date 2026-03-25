"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on RICE enforcement rules.
    Returns: dict with new keys: category, priority, reason, flag.
    """
    description = row.get("description", "")
    desc_lower = description.lower()
    
    # Defaults
    category = "Other"
    priority = "Standard"
    reason = ""
    flag = ""
    
    # 1. Enforce Priority (Urgent if severity keywords exist)
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    matched_severity = [kw for kw in severity_keywords if kw in desc_lower]
    if matched_severity:
        priority = "Urgent"
        
    # 2. Enforce Category mapping
    if re.search(r'\bpotholes?\b', desc_lower):
        category = "Pothole"
    elif re.search(r'\bflood(s|ed|ing)?\b', desc_lower):
        category = "Flooding"
    elif re.search(r'\b(streetlights?|lights? out)\b', desc_lower):
        category = "Streetlight"
    elif re.search(r'\b(garbage|waste|dead animal)\b', desc_lower):
        category = "Waste"
    elif re.search(r'\b(music|noise|loud)\b', desc_lower):
        category = "Noise"
    elif re.search(r'\b(cracked|tiles broken|road surface)\b', desc_lower):
        category = "Road Damage"
    elif re.search(r'\bheritage\b', desc_lower):
        category = "Heritage Damage"
    elif re.search(r'\bheat\b', desc_lower):
        category = "Heat Hazard"
    elif re.search(r'\b(drain|manhole)\b', desc_lower):
        category = "Drain Blockage"
        
    # 3. Enforce Reason
    sentences = [s.strip() + "." for s in re.split(r'(?<=[.!?]) +', description) if s.strip()]
    if not sentences:
        sentences = [description]
        
    if matched_severity:
        # Cite the sentence with the severity keyword
        for s in sentences:
            if any(kw in s.lower() for kw in matched_severity):
                reason = f"Citing '{matched_severity[0]}': {s}"
                break
    elif category != "Other":
        # Cite the sentence that mapped to the category
        reason = f"Citing description: {sentences[0]}"
        
    # 4. Ambiguity / Refusal condition
    if category == "Other":
        flag = "NEEDS_REVIEW"
        reason = "Category cannot be determined from description alone."
        priority = "Low"
        
    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Reads input CSV of complaints, applies classify_complaint to each row,
    and writes the structural classifications to the output CSV.
    """
    rows_out = []
    fieldnames = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as fin:
            reader = csv.DictReader(fin)
            fieldnames = list(reader.fieldnames or [])
            
            # Ensure new columns exist
            for col in ['category', 'priority', 'reason', 'flag']:
                if col not in fieldnames:
                    fieldnames.append(col)
                    
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    row.update(classified)
                except Exception as e:
                    # Error handling: write them as failed without crashing batch
                    row.update({
                        "category": "Other", 
                        "priority": "Low", 
                        "reason": f"Error parsing: {str(e)}", 
                        "flag": "NEEDS_REVIEW"
                    })
                rows_out.append(row)
    except Exception as e:
        print(f"Error reading input: {e}")
        return
        
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as fout:
            writer = csv.DictWriter(fout, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows_out)
    except Exception as e:
        print(f"Error writing output: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
