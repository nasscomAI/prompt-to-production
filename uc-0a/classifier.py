"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on the explicit rules in agents.md.
    Returns: dict with keys: category, priority, reason, flag
    """
    description = row.get("description", "")
    desc_lower = description.lower()
    
    # Context: Determine Priority based on severity keywords ONLY
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    triggered_sev = [kw for kw in severity_keywords if re.search(r'\b' + kw + r'\b', desc_lower)]
    priority = "Urgent" if triggered_sev else "Standard"
    
    # Enforcement: Category matching to explicit schema
    cat_rules = {
        'Pothole': ['pothole', 'potholes', 'crater'],
        'Flooding': ['flood', 'flooded', 'floods', 'waterlogged'],
        'Streetlight': ['streetlight', 'lights out', 'dark', 'sparking', 'lamp'],
        'Waste': ['garbage', 'waste', 'dead animal', 'dumped', 'trash', 'smell'],
        'Noise': ['noise', 'music', 'loud', 'midnight'],
        'Road Damage': ['road surface cracked', 'sinking', 'footpath tiles broken', 'manhole cover missing', 'manhole'],
        'Heritage Damage': ['heritage', 'monument'],
        'Heat Hazard': ['heatwave', 'heat', 'sun'],
        'Drain Blockage': ['drain blocked', 'drain', 'sewer']
    }
    
    found_cats = []
    matched_kws = []
    for cat, kws in cat_rules.items():
        for kw in kws:
            if kw in desc_lower:
                if cat not in found_cats:
                    found_cats.append(cat)
                    matched_kws.append(kw)
    
    # Enforcement: NEEDS_REVIEW for genuinely ambiguous
    if len(found_cats) == 1:
        category = found_cats[0]
        flag = ""
        reason = f"The description explicitly mentions '{matched_kws[0]}'."
    else:
        category = "Other"
        flag = "NEEDS_REVIEW"
        if len(found_cats) == 0:
            reason = "The description lacks specific keywords mapping to a category."
        else:
            reason = f"Ambiguous categories detected: {', '.join(found_cats)}."
            
    # Enforcement: Single-sentence reason
    if triggered_sev:
        if len(found_cats) != 1:
            reason = ""
        reason += f" Priority escalated to Urgent due to severity keyword '{triggered_sev[0]}'."
        reason = reason.strip()
        
    return {
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            if not fieldnames:
                raise ValueError("Empty CSV file")
            outputs = []
            for row in reader:
                try:
                    result = classify_complaint(row)
                    row.update(result)
                except Exception as e:
                    row.update({
                        'category': 'Other',
                        'priority': 'Low',
                        'reason': 'Execution failure on row.',
                        'flag': 'NEEDS_REVIEW'
                    })
                outputs.append(row)
                
        out_fields = fieldnames + ['category', 'priority', 'reason', 'flag']
        out_fields = list(dict.fromkeys(out_fields)) 
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=out_fields)
            writer.writeheader()
            writer.writerows(outputs)
    except Exception as e:
        print(f"Error processing batch: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
