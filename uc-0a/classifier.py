"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

# Constants from skills.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    
    Referring to skills.md: Classifies based on schema rules, outputs exact keys.
    From agents.md: Enforce exact categories, urgent if keywords present, cite words in reason, flag for ambiguity.
    """
    description = row.get('description', '').strip().lower()
    complaint_id = row.get('complaint_id', '')
    
    if not description:
        # If no description, ambiguous
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "No description provided.",
            "flag": "NEEDS_REVIEW"
        }
    
    # Determine category strictly from keywords (no variations)
    category = "Other"
    cited_words = []
    
    if "pothole" in description:
        category = "Pothole"
        cited_words.append("pothole")
    elif "flood" in description or "water" in description:
        category = "Flooding"
        cited_words.append("flood" if "flood" in description else "water")
    elif "streetlight" in description or "light" in description:
        category = "Streetlight"
        cited_words.append("streetlight" if "streetlight" in description else "light")
    elif "waste" in description or "garbage" in description or "trash" in description:
        category = "Waste"
        cited_words.append("waste" if "waste" in description else "garbage" if "garbage" in description else "trash")
    elif "noise" in description or "loud" in description:
        category = "Noise"
        cited_words.append("noise" if "noise" in description else "loud")
    elif "road" in description and ("damage" in description or "broken" in description):
        category = "Road Damage"
        cited_words.append("road")
        if "damage" in description:
            cited_words.append("damage")
        if "broken" in description:
            cited_words.append("broken")
    elif "heritage" in description or "monument" in description:
        category = "Heritage Damage"
        cited_words.append("heritage" if "heritage" in description else "monument")
    elif "heat" in description or "hot" in description:
        category = "Heat Hazard"
        cited_words.append("heat" if "heat" in description else "hot")
    elif "drain" in description or "blockage" in description:
        category = "Drain Blockage"
        cited_words.append("drain" if "drain" in description else "blockage")
    
    # Determine priority: Urgent if any urgent keyword present (exact match)
    priority = "Standard"
    urgent_cited = []
    for keyword in URGENT_KEYWORDS:
        if keyword in description:
            priority = "Urgent"
            urgent_cited.append(keyword)
            break  # No need to check further
    
    # Reason: one sentence citing specific words
    if cited_words:
        reason = f"Complaint mentions {' and '.join(cited_words)} indicating {category.lower()}."
    else:
        reason = f"Complaint describes issues related to {category.lower()}."
    if priority == "Urgent" and urgent_cited:
        reason += f" Marked urgent due to {urgent_cited[0]}."
    
    # Flag: NEEDS_REVIEW if genuinely ambiguous (category Other and short description)
    flag = ""
    if category == "Other" and len(description.split()) < 10:
        flag = "NEEDS_REVIEW"
    
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str) -> str:
    """
    Read input CSV, classify each row, write results CSV.
    
    Referring to skills.md: Reads input CSV, applies classify_complaint per row, writes output CSV.
    From agents.md: Ensure all rows attempted; on failure, mark with error and NEEDS_REVIEW; raise only for critical issues.
    """
    try:
        with open(input_path, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            rows = list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file {input_path} not found")
    except Exception as e:
        raise ValueError(f"Error reading CSV: {e}")
    
    classified_rows = []
    for row in rows:
        try:
            # Call classify_complaint skill
            classified = classify_complaint(row)
            # Merge original row with classified fields
            new_row = {**row, **classified}
            classified_rows.append(new_row)
        except Exception as e:
            # On failure, per agents.md enforcement: mark with error reason and NEEDS_REVIEW
            new_row = {**row}
            new_row.update({
                "category": "Other",
                "priority": "Low",
                "reason": f"Classification failed: {str(e)}",
                "flag": "NEEDS_REVIEW"
            })
            classified_rows.append(new_row)
    
    # Write output CSV with all fields
    if classified_rows:
        fieldnames = list(classified_rows[0].keys())
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(classified_rows)
        except Exception as e:
            raise ValueError(f"Error writing CSV: {e}")
    
    # Return success message as per skills.md
    return f"Classification complete. Output written to {output_path}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    result = batch_classify(args.input, args.output)
    print(result)
