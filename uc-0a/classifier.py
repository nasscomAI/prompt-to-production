import argparse
import csv
import sys
import re

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on the strict RICE enforcement rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "")
    if not description:
        description = ""
    description_lower = description.lower()
    
    # Default values
    category = "Other"
    priority = "Standard"
    flag = ""
    
    # 1. Category matching logic
    categories_map = {
        "Pothole": [r"\bpothole\b"],
        "Flooding": [r"\bflood(s|ed|ing)?\b", r"\bwater\b"],
        "Streetlight": [r"\bstreetlight\b", r"\blights? out\b", r"\bdark\b"],
        "Waste": [r"\bgarbage\b", r"\bwaste\b", r"\bsmell\b", r"\bdead animal\b", r"\bdump(ed)?\b"],
        "Noise": [r"\bmusic\b", r"\bnoise\b"],
        "Road Damage": [r"\bcrack(ed)?\b", r"\bsinking\b", r"\bbroken\b", r"road surface"],
        "Heritage Damage": [r"\bheritage\b"],
        "Heat Hazard": [r"\bheat\b"],
        "Drain Blockage": [r"\bdrain\b", r"\bmanhole\b"]
    }
    
    matched_cat_words = []
    for cat, patterns in categories_map.items():
        found = False
        for pattern in patterns:
            match = re.search(pattern, description_lower)
            if match:
                category = cat
                matched_cat_words.append(match.group(0))
                found = True
                break
        if found:
            break
            
    # Ambiguity check
    if category == "Other":
        flag = "NEEDS_REVIEW"
        
    # 2. Priority matching logic
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    matched_sev_words = []
    
    for word in severity_keywords:
        if re.search(rf"\b{word}\b", description_lower):
            matched_sev_words.append(word)
            
    if matched_sev_words:
        priority = "Urgent"

    # 3. Reason generation (must be one sentence citing specific words)
    reason_parts = []
    if matched_cat_words:
        reason_parts.append(f"categorized as {category} because it mentions '{matched_cat_words[0]}'")
    else:
        reason_parts.append("categorized as Other because no clear category keywords were found")
        
    if matched_sev_words:
        reason_parts.append(f"marked Urgent due to the presence of '{matched_sev_words[0]}'")
    else:
        reason_parts.append("marked Standard as no severity keywords were detected")
        
    reason = f"This complaint was {reason_parts[0]} and {reason_parts[1]}."

    return {
        "complaint_id": row.get("complaint_id", "UNKNOWN"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Safely handles empty/missing values so the batch doesn't crash.
    """
    results = []
    try:
        with open(input_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            
            for row in reader:
                try:
                    classified = classify_complaint(row)
                    results.append(classified)
                except Exception as e:
                    # In case of malformed row error
                    results.append({
                        "complaint_id": row.get("complaint_id", "ERROR"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": f"System encountered an error processing this row: {e}",
                        "flag": "NEEDS_REVIEW"
                    })
                    
        with open(output_path, mode="w", encoding="utf-8", newline="") as out_f:
            writer = csv.DictWriter(out_f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except FileNotFoundError:
        print(f"Error: Could not find input file at {input_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Critical Error processing file {input_path}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Classified results successfully written to {args.output}")
