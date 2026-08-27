"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re

SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "").strip()
    desc = row.get("description", "").strip()
    
    # Handle empty/missing description
    if not desc:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "The complaint description is empty.",
            "flag": "NEEDS_REVIEW"
        }
        
    # Check severity keywords in description (case-insensitive)
    is_urgent = False
    found_severity_words = []
    desc_lower = desc.lower()
    for word in SEVERITY_KEYWORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', desc_lower):
            is_urgent = True
            found_severity_words.append(word)
            
    priority = "Urgent" if is_urgent else "Standard"
    
    # Define keywords for category mapping
    category_keywords = {
        "Pothole": ["pothole"],
        "Flooding": ["flooded", "flooding", "floods", "water accumulation", "water logging"],
        "Streetlight": ["streetlight", "streetlights", "light out", "lights out", "dark at night", "sparking"],
        "Waste": ["garbage", "waste", "trash", "dumped", "bins", "dead animal", "smell"],
        "Noise": ["music", "noise", "loud", "sound"],
        "Road Damage": ["road surface", "cracked", "sinking", "footpath", "tiles broken", "manhole"],
        "Heritage Damage": ["heritage", "monument", "historic"],
        "Heat Hazard": ["heat", "temperature", "hot", "sunstroke"],
        "Drain Blockage": ["drain", "drainage", "sewer", "blocked"]
    }
    
    matched_categories = []
    matched_words = {}
    
    for cat, kw_list in category_keywords.items():
        found_kws = []
        for kw in kw_list:
            if kw in desc_lower:
                found_kws.append(kw)
        if found_kws:
            matched_categories.append(cat)
            matched_words[cat] = found_kws

    flag = ""
    # Determine final category and flag
    if len(matched_categories) == 0:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = "Classified as Other because the description does not match known category keywords."
    elif len(matched_categories) == 1:
        category = matched_categories[0]
        citation_word = matched_words[category][0]
        
        # Find original casing in desc
        match_idx = desc_lower.find(citation_word)
        citation = desc[match_idx:match_idx+len(citation_word)] if match_idx != -1 else citation_word
        
        if is_urgent:
            reason = f"Classified as {category} because the description mentions '{citation}' and contains severity keyword '{found_severity_words[0]}'."
        else:
            reason = f"Classified as {category} because the description mentions '{citation}'."
    else:
        # Multiple matched categories -> Ambiguous
        # Choose the first one but set flag to NEEDS_REVIEW
        category = matched_categories[0]
        flag = "NEEDS_REVIEW"
        citations = []
        for cat in matched_categories:
            citations.append(f"{cat} ('{matched_words[cat][0]}')")
        reason = f"Category is ambiguous between {', '.join(citations)}."

    # Manually check for specific known ambiguities (e.g. Heritage street, lights out)
    if "heritage" in desc_lower and ("light" in desc_lower or "dark" in desc_lower or "streetlights" in desc_lower):
        flag = "NEEDS_REVIEW"
        
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
    """
    results = []
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            try:
                classified = classify_complaint(row)
                results.append(classified)
            except Exception as e:
                # Log error and produce placeholder to avoid crash
                results.append({
                    "complaint_id": row.get("complaint_id", "ERROR"),
                    "category": "Other",
                    "priority": "Low",
                    "reason": f"Row processing failed: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })
                
    with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
