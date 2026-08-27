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
    desc = row.get("description", "").strip()
    desc_lower = desc.lower()
    
    # Define exact category keywords to match against the description
    rules = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "rainwater", "water"],
        "Streetlight": ["streetlight", "light", "unlit", "darkness", "dark"],
        "Waste": ["garbage", "waste", "trash", "refuse", "animal", "dumped", "bins"],
        "Noise": ["music", "noise", "amplifier", "drilling", "loud"],
        "Road Damage": ["road surface", "cracked", "sinking", "subsidence", "footpath", "paving", "tarmac", "divider"],
        "Heritage Damage": ["heritage", "ancient", "historic"],
        "Heat Hazard": ["heat", "temperature", "melting", "sun", "hot"],
        "Drain Blockage": ["drain", "blockage", "blocked"]
    }
    
    matched_categories = []
    matched_words = []
    
    for cat, keywords in rules.items():
        for kw in keywords:
            if kw in desc_lower:
                matched_categories.append(cat)
                # Capture the exact word with casing from original description
                idx = desc_lower.find(kw)
                matched_words.append(desc[idx:idx+len(kw)])
                break # Match only one keyword per category to prevent duplicate hits
                
    # Extra check for manhole in the text
    if "manhole" in desc_lower:
        idx = desc_lower.find("manhole")
        matched_words.append(desc[idx:idx+len("manhole")])
        
    flag = ""
    category = "Other"
    
    if not matched_categories:
        if "manhole" in desc_lower:
            category = "Other"
            flag = "NEEDS_REVIEW"
        else:
            category = "Other"
    elif len(matched_categories) == 1:
        category = matched_categories[0]
        if "manhole" in desc_lower:
            flag = "NEEDS_REVIEW"
    else:
        # Genuinely ambiguous cases where multiple category rules matched
        flag = "NEEDS_REVIEW"
        # Disambiguate default choice based on priority rules
        if "drain" in desc_lower or "blocked" in desc_lower:
            category = "Drain Blockage"
        elif "heritage" in desc_lower:
            category = "Heritage Damage"
        else:
            category = matched_categories[0]
            
    # Severity keywords that must trigger Urgent
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    found_severity = []
    
    for kw in severity_keywords:
        if kw in desc_lower:
            found_severity.append(kw)
            idx = desc_lower.find(kw)
            matched_words.append(desc[idx:idx+len(kw)])
            
    if found_severity:
        priority = "Urgent"
        
    # Generate unique list of cited words in order of appearance
    unique_cited = []
    seen = set()
    for w in matched_words:
        if w.lower() not in seen:
            seen.add(w.lower())
            unique_cited.append(f"'{w}'")
            
    if unique_cited:
        cited_str = " and ".join(unique_cited)
        if flag == "NEEDS_REVIEW":
            reason = f"Category is ambiguous; cites {cited_str}."
        else:
            reason = f"Classified because description cites {cited_str}."
    else:
        if flag == "NEEDS_REVIEW":
            reason = "Category is ambiguous from the description."
        else:
            reason = "Classified based on description text."
            
    if not reason.endswith("."):
        reason += "."
        
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            
            rows_to_write = []
            for line_no, row in enumerate(reader, start=2):
                try:
                    if not row or not row.get("complaint_id"):
                        continue
                    
                    if not row.get("description") or not row.get("description").strip():
                        # Handle null or missing description safely
                        classified = {
                            "complaint_id": row.get("complaint_id", f"UNKNOWN-{line_no}"),
                            "category": "Other",
                            "priority": "Low",
                            "reason": "Missing description field.",
                            "flag": "NEEDS_REVIEW"
                        }
                    else:
                        classified = classify_complaint(row)
                    
                    rows_to_write.append(classified)
                except Exception as row_err:
                    print(f"Error processing row on line {line_no}: {row_err}")
                    rows_to_write.append({
                        "complaint_id": row.get("complaint_id", f"ERROR-{line_no}") if row else f"ERROR-{line_no}",
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Error classifying: {str(row_err)}",
                        "flag": "NEEDS_REVIEW"
                    })
                    
            with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows_to_write)
                
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found at: {input_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
