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
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get('description', '').lower()
    
    # Priority defaults
    severity_keywords = ["injury", "child", "school"]
    urgent_words = [kw for kw in severity_keywords if kw in desc]
    priority = "Urgent" if urgent_words else "Normal"
    
    # Categorization and Keywords extraction
    category = "Other"
    cite_words = []

    if "pothole" in desc:
        category = "Pothole"
        cite_words.append("pothole")
    elif "flood" in desc or "water" in desc:
        category = "Flooding"
        cite_words.extend([w for w in ["flood", "water"] if w in desc])
    elif "infrastructure" in desc or "crack" in desc or "damage" in desc or "road" in desc or "bridge" in desc or "light" in desc or "drain" in desc or "manhole" in desc:
        category = "Infrastructure Damage"
        cite_words.extend([w for w in ["infrastructure", "crack", "damage", "road", "bridge", "light", "drain", "manhole"] if w in desc])
    elif "noise" in desc or "music" in desc or "loud" in desc:
        category = "Noise"
        cite_words.extend([w for w in ["noise", "music", "loud"] if w in desc])
    elif "traffic" in desc or "car" in desc or "vehicle" in desc or "block" in desc:
        category = "Traffic"
        cite_words.extend([w for w in ["traffic", "car", "vehicle", "block"] if w in desc])
    elif "garbage" in desc or "waste" in desc or "trash" in desc or "smell" in desc or "dump" in desc:
        category = "Garbage"
        cite_words.extend([w for w in ["garbage", "waste", "trash", "smell", "dump"] if w in desc])
        
    if urgent_words:
        cite_words.extend(urgent_words)

    # Compile Reason
    if cite_words:
        # Deduplicate preserving order
        unique_cites = list(dict.fromkeys(cite_words))
        cites_str = ", ".join(f"'{w}'" for w in unique_cites)
        reason = f"Keywords: {cites_str}"
    else:
        reason = "Unable to extract specific keywords."

    # Flag
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    # Build Output Dict
    out = dict(row)
    out["category"] = category
    out["priority"] = priority
    out["reason"] = reason
    out["flag"] = flag
    
    return out


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    headers = []
    
    with open(input_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        headers = list(reader.fieldnames or [])
        
        for row in reader:
            try:
                classified_row = classify_complaint(row)
                results.append(classified_row)
            except Exception as e:
                # Flag bad rows but do not crash
                print(f"Skipping bad row: {e}")
                continue
                
    # Add new headers
    for col in ["category", "priority", "reason", "flag"]:
        if col not in headers:
            headers.append(col)
            
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
