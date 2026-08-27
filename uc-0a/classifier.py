"""
UC-0A — Complaint Classifier
Implemented based on the R.I.C.E. rules defined in agents.md and the skill specifications in skills.md.
"""
import argparse
import csv

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Implemented based on the R.I.C.E. enforcement rules in agents.md and the classify_complaint skill in skills.md.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "").strip()
    complaint_id = row.get("complaint_id", "")
    
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "The complaint description is empty.",
            "flag": "NEEDS_REVIEW"
        }
    
    desc_lower = description.lower()
    
    # Allowed categories mapping
    category_mapping = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "waterlog", "inundat", "rainwater", "rain water"],
        "Streetlight": ["streetlight", "street light", "lamp", "light", "unlit", "darkness"],
        "Waste": ["garbage", "waste", "trash", "dump", "dead animal", "litter", "debris"],
        "Noise": ["noise", "music", "loudspeaker", "sound", "band playing", "amplifiers", "drilling"],
        "Road Damage": ["road surface", "footpath", "pavement", "tiles", "cracked", "sinking", "subsid", "buckled", "crater", "paving", "collapsed", "collapse"],
        "Heritage Damage": ["heritage", "historic", "monument", "ancient"],
        "Heat Hazard": ["heat", "hot", "temperature", "sunstroke", "heatwave", "melting", "bubbling", "burns"],
        "Drain Blockage": ["drain", "manhole", "sewer", "gutter", "catch basin"]
    }
    
    matched_categories = []
    matched_keywords = {}
    
    # We want to identify all categories that match
    for cat, keywords in category_mapping.items():
        for kw in keywords:
            if kw in desc_lower:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                    matched_keywords[cat] = kw
                break
                
    # Deduplicate Pothole and Road Damage (Pothole takes precedence)
    if "Pothole" in matched_categories and "Road Damage" in matched_categories:
        matched_categories.remove("Road Damage")
        matched_keywords.pop("Road Damage", None)
        
    flag = ""
    category = "Other"
    keyword = ""
    
    if len(matched_categories) == 1:
        category = matched_categories[0]
        keyword = matched_keywords[category]
    elif len(matched_categories) > 1:
        # Ambiguous case: multiple matches
        category = matched_categories[0] # Pick first match
        keyword = matched_keywords[category]
        flag = "NEEDS_REVIEW"
    else:
        # No matches
        category = "Other"
        flag = "NEEDS_REVIEW"
        
    # Severity keywords check for Urgent priority
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    is_urgent = False
    for kw in severity_keywords:
        if kw in desc_lower:
            is_urgent = True
            break
            
    priority = "Urgent" if is_urgent else "Standard"
    
    # Extract one-sentence reason citing description words
    sentences = [s.strip() for s in description.split(".") if s.strip()]
    cited_sentence = ""
    if keyword:
        for s in sentences:
            if keyword in s.lower():
                cited_sentence = s
                break
    if not cited_sentence and sentences:
        cited_sentence = sentences[0]
        
    # Clean the cited sentence of internal or trailing punctuation
    cited_sentence = cited_sentence.replace(".", "").replace(";", "").replace(":", "").strip()
    
    if category == "Other":
        if flag == "NEEDS_REVIEW":
            reason = "The complaint is classified as Other and flagged for review because no standard category keywords were matched in the description."
        else:
            reason = "The complaint is classified as Other."
    else:
        reason = f"Classified as {category} because the description cites '{cited_sentence}'."
        
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
    Implemented based on the batch_classify skill defined in skills.md.
    """
    results = []
    try:
        with open(input_path, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    results.append({
                        "complaint_id": row.get("complaint_id", "ERROR"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Error classifying row: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        raise
    except Exception as e:
        print(f"Error reading input file: {e}")
        raise

    # Write output
    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["complaint_id", "category", "priority", "reason", "flag"])
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output file {output_path}: {e}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
