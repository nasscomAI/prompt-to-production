"""
UC-0A — Complaint Classifier
Refined and correctly aligned with the rules from agents.md and skills.md.
"""
import argparse
import csv
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def classify_complaint(description: str) -> dict:
    """
    Skill: classify_complaint
    Analyzes a single citizen complaint description to assign an exact category, 
    determine priority, generate a 1-sentence justifying reason, and set review flags.
    
    Returns a dictionary with keys: category, priority, reason, flag.
    """
    if not isinstance(description, str) or not description.strip():
        # Error handling fallback as defined in skills.md
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Input description was empty or invalid.",
            "flag": "NEEDS_REVIEW"
        }
        
    desc_lower = description.lower()
    
    # 1. Enforcement Rule 2: Determine Priority
    severity_keywords = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']
    priority = "Standard"
    matched_severity_word = None
    
    for word in severity_keywords:
        if word in desc_lower:
            priority = "Urgent"
            matched_severity_word = word
            break
            
    # 2. Enforcement Rule 1: Determine Category Exact Strings
    categories_map = {
        'pothole': 'Pothole',
        'flood': 'Flooding',
        'streetlight': 'Streetlight',
        'light': 'Streetlight',
        'waste': 'Waste',
        'garbage': 'Waste',
        'animal': 'Waste',
        'dump': 'Waste',
        'noise': 'Noise',
        'music': 'Noise',
        'crack': 'Road Damage',
        'sinking': 'Road Damage',
        'heritage': 'Heritage Damage',
        'heat': 'Heat Hazard',
        'drain': 'Drain Blockage',
        'blocked': 'Drain Blockage'
    }
    
    category = "Other"
    matched_cat_word = None
    matches = 0
    matched_categories = set()
    
    for key, val in categories_map.items():
        if key in desc_lower:
            # Prevent double-counting the same root category
            if val not in matched_categories:
                matched_categories.add(val)
                category = val
                matched_cat_word = key
                matches += 1
                
    # 3. Enforcement Rule 4: Flag Ambiguity
    flag = ""
    if matches > 1 or matches == 0:
        flag = "NEEDS_REVIEW"
        category = "Other" # Set to Other if completely ambiguous
        
    # 4. Enforcement Rule 3: 1-Sentence Reason citing specific words
    if matched_severity_word and matched_cat_word:
        reason = f"Description contains category keyword '{matched_cat_word}' and severity keyword '{matched_severity_word}'."
    elif matched_severity_word:
        reason = f"Priority marked Urgent because description includes '{matched_severity_word}'."
    elif matched_cat_word:
        reason = f"Classified based on the mention of the word '{matched_cat_word}'."
    else:
        reason = "Could not identify clear and specific keywords from the description to confidently classify."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Skill: batch_classify
    Reads an input CSV of raw complaints, applies classify_complaint per row, 
    and writes out the compiled classification results to a target CSV.
    """
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Guarantee exactly these columns are in the output structure
            fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            
            for row in reader:
                if not row:
                    continue
                
                complaint_id = row.get("complaint_id", "UNKNOWN")
                description = row.get("description", "")
                
                try:
                    # Execute the inner skill 
                    classified = classify_complaint(description)
                    classified["complaint_id"] = complaint_id
                    results.append(classified)
                except Exception as e:
                    logging.error(f"Error processing row {complaint_id}: {str(e)}")
                    # Error handling exactly per skills.md schema
                    results.append({
                        "complaint_id": complaint_id,
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"System error during classification: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
                    
    except FileNotFoundError:
        logging.error(f"Input file {input_path} not found.")
        return
        
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        logging.info(f"Successfully compiled classifying {len(results)} rows. Written to {output_path}")
    except Exception as e:
        logging.error(f"Error writing to output file {output_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to input test CSV")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
