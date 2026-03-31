"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with new keys: category, priority, reason, flag added to the original row.
    """
    description = row.get("description", "").lower()
    
    # Predefined Category Taxonomy
    category_keywords = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "water"],
        "Heritage Damage": ["heritage"],
        "Road Damage": ["road surface", "crack", "sinking", "broken", "tiles"],
        "Streetlight": ["streetlight", "light", "dark"],
        "Waste": ["waste", "garbage", "trash", "dump", "animal"],
        "Noise": ["noise", "music", "loud"],
        "Heat Hazard": ["heat"],
        "Drain Blockage": ["drain", "block", "clog"]
    }
    
    # 1. Determine Category
    category = "Other"
    cited_cat_word = None
    
    # Order matters: check more specific multi-word tokens or explicit context first if needed,
    # Here we just iterate and break on first match for simplicity based on dictionary order.
    for cat, keywords in category_keywords.items():
        found = False
        for kw in keywords:
            if kw in description:
                category = cat
                cited_cat_word = kw
                found = True
                break
        if found:
            break
            
    # Ambiguity Check
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    # 2. Determine Priority
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    cited_sev_word = None
    
    for word in severity_keywords:
        # Match severity word with word boundaries to avoid partial matches
        if re.search(rf'\b{re.escape(word)}\b', description):
            priority = "Urgent"
            cited_sev_word = word
            break
            
    # 3. Formulate Reason
    if flag == "NEEDS_REVIEW":
        reason = "The category is genuinely ambiguous as no predefined taxonomy keywords were found in the description."
    elif priority == "Urgent":
        reason = f"Classified as {category} with Urgent priority because the text explicitly cites the word '{cited_sev_word}'."
    else:
        reason = f"Classified as {category} with Standard priority because the description mentions '{cited_cat_word}'."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Safely skips errors row-by-row and guarantees partial output on failure.
    """
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fs = reader.fieldnames
            fieldnames = [f for f in fs] if fs is not None else []
            # Ensure our newly added fieldnames are present in the output schema
            for new_field in ["category", "priority", "reason", "flag"]:
                if new_field not in fieldnames:
                    fieldnames.append(new_field)
            
            for index, row in enumerate(reader):
                try:
                    # Apply classification
                    classification = classify_complaint(row)
                    row.update(classification)
                    results.append(row)
                except Exception as e:
                    print(f"Warning: Failed to classify row {index}. Error: {e}")
                    row.update({
                        "category": "Other", 
                        "priority": "Low", 
                        "reason": "System error during evaluation.", 
                        "flag": "NEEDS_REVIEW"
                    })
                    results.append(row)
                    
        # Write output
        with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except Exception as e:
        print(f"Critical error processing batch: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
