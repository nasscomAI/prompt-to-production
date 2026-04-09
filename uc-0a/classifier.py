"""
UC-0A — Complaint Classifier
Implements RICE framework rules from agents.md and skills.md
"""
import argparse
import csv
import re

# Allowed categories (enforcement rule 1)
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords that trigger Urgent priority (enforcement rule 2)
SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

# Category classification patterns
CATEGORY_PATTERNS = {
    "Pothole": r"\b(pothole|pit|hole in road|crater|dip in road)\b",
    "Flooding": r"\b(flood|waterlog|water.*log|inundat|overflow|submerg)\b",
    "Streetlight": r"\b(street.*light|lamp|light.*not.*work|light.*out|dark.*street)\b",
    "Waste": r"\b(garbage|waste|trash|rubbish|litter|dump)\b",
    "Noise": r"\b(noise|loud|sound|disturb.*noise|noisy)\b",
    "Road Damage": r"\b(road.*damage|road.*crack|road.*broke|pavement.*damage|broken.*road)\b",
    "Heritage Damage": r"\b(heritage|historic|monument|ancient|archaeolog)\b",
    "Heat Hazard": r"\b(heat|hot|temperature|scorch|burning)\b",
    "Drain Blockage": r"\b(drain|sewer|clog|block.*drain|manhole)\b",
}


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Implements RICE enforcement rules from agents.md and skills.md.
    """
    # Error handling: missing complaint_id
    if "complaint_id" not in row or not row["complaint_id"]:
        raise ValueError("complaint_id is required")
    
    complaint_id = row["complaint_id"]
    description = row.get("description", "")
    
    # Error handling: empty description
    if not description or not description.strip():
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Empty description",
            "flag": "NEEDS_REVIEW"
        }
    
    description_lower = description.lower()
    
    # Category classification
    category = "Other"
    matched_keywords = []
    flag = ""
    
    # Try to match category patterns
    matches = []
    for cat_name, pattern in CATEGORY_PATTERNS.items():
        if re.search(pattern, description_lower, re.IGNORECASE):
            matches.append(cat_name)
            # Extract matched words for reason
            match_obj = re.search(pattern, description_lower, re.IGNORECASE)
            if match_obj:
                matched_keywords.append(match_obj.group(0))
    
    # Category determination
    if len(matches) == 1:
        category = matches[0]
    elif len(matches) > 1:
        # Multiple matches - flag as ambiguous
        category = "Other"
        flag = "NEEDS_REVIEW"
    else:
        # No clear match
        category = "Other"
        flag = "NEEDS_REVIEW"
    
    # Priority classification (enforcement rule 2)
    priority = "Standard"
    severity_found = []
    
    for keyword in SEVERITY_KEYWORDS:
        if keyword in description_lower:
            priority = "Urgent"
            severity_found.append(keyword)
    
    # Adjust priority for low-impact issues if not urgent
    if priority != "Urgent":
        # Check for informational or minor indicators
        if re.search(r"\b(inform|fyi|notice|minor|small)\b", description_lower):
            priority = "Low"
    
    # Generate reason (enforcement rule 3)
    if flag == "NEEDS_REVIEW" and len(matches) > 1:
        reason = f"Description contains multiple complaint types ({', '.join(matches)}), requires manual review"
    elif flag == "NEEDS_REVIEW" and len(matches) == 0:
        reason = "Description does not clearly match any defined category"
    else:
        # Cite specific words from description
        reason_parts = []
        if matched_keywords:
            reason_parts.append(f"mentioned '{matched_keywords[0]}'")
        if severity_found:
            reason_parts.append(f"contains severity keyword '{severity_found[0]}'")
        
        if reason_parts:
            reason = f"Classified as {category} because description {' and '.join(reason_parts)}"
        else:
            reason = f"Classified as {category} based on description content"
    
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
    
    Implements error handling and enforcement rules from skills.md.
    """
    # Error handling: check if input file exists
    try:
        with open(input_path, 'r', encoding='utf-8-sig') as f:
            pass  # Just check if we can open it
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except IOError as e:
        raise FileNotFoundError(f"Cannot read input file {input_path}: {e}")
    
    results = []
    total_rows = 0
    flagged_count = 0
    
    # Read and classify
    try:
        with open(input_path, 'r', encoding='utf-8-sig', newline='') as infile:
            reader = csv.DictReader(infile)
            
            for row_num, row in enumerate(reader, start=1):
                total_rows += 1
                
                try:
                    # Classify the complaint
                    result = classify_complaint(row)
                    results.append(result)
                    
                    if result["flag"] == "NEEDS_REVIEW":
                        flagged_count += 1
                        
                except ValueError as e:
                    # Malformed row - add with error flag
                    results.append({
                        "complaint_id": row.get("complaint_id", f"ROW_{row_num}"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Malformed row: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
                    flagged_count += 1
                    
                except Exception as e:
                    # Unexpected error - add with error flag
                    results.append({
                        "complaint_id": row.get("complaint_id", f"ROW_{row_num}"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": f"Processing error: {str(e)}",
                        "flag": "NEEDS_REVIEW"
                    })
                    flagged_count += 1
    
    except Exception as e:
        raise IOError(f"Error reading input file: {e}")
    
    # Write results
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(results)
            
    except IOError as e:
        raise IOError(f"Cannot write to output file {output_path}: {e}")
    
    # Print summary
    print(f"Processed {total_rows} rows, {flagged_count} flagged for review")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
