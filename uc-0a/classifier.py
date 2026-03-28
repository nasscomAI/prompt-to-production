"""
UC-0A — Complaint Classifier (Offline Version)
Implemented using RICE framework rules from agents.md and skills.md.
Explicitly avoids any external APIs.
"""
import argparse
import csv
import os
import re
import sys

# Standardized categories and simple heuristic keywords
CATEGORIES = {
    "Pothole": ["pothole", "tyre damage"],
    "Flooding": ["flood", "flooded", "water", "rain", "stranded"],
    "Streetlight": ["streetlight", "lights out", "flickering", "dark"],
    "Waste": ["waste", "garbage", "trash", "smell", "animal"],
    "Noise": ["noise", "music", "loud"],
    "Road Damage": ["crack", "sinking", "road surface", "broken"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat", "sun", "temperature"],
    "Drain Blockage": ["drain", "blocked", "manhole"]
}

SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']


def get_sentences(text: str) -> list:
    """Safely extract sentences from a text block."""
    sentences = re.split(r'(?<=[.!?]) +', text.replace('\n', ' '))
    return [s.strip() for s in sentences if s.strip()]


def classify_complaint(row: dict) -> dict:
    """
    Skill 1: classify_complaint
    Categorizes a single citizen complaint description purely using offline matching.
    """
    description = row.get("description", "")
    
    # Initialize output structure
    output = {
        "category": "Other",
        "priority": "Low",
        "reason": "No description provided.",
        "flag": "NEEDS_REVIEW"
    }
    
    if not description:
        return output
        
    desc_lower = description.lower()
    sentences = get_sentences(description)
    
    matched_categories = []
    reason_sentence = ""
    
    # 1. Enforce Taxonomy: Determine category based on keywords
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in desc_lower:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                if not reason_sentence:
                    for s in sentences:
                        if kw in s.lower():
                            reason_sentence = s
                            break
                            
    # Track ambiguity vs exact exact
    if len(matched_categories) == 0:
        output["category"] = "Other"
        output["flag"] = "NEEDS_REVIEW"
        if sentences:
            output["reason"] = sentences[0]
    elif len(matched_categories) > 1:
        # Ambiguous categories -> Pick one but flag it
        output["category"] = matched_categories[0]
        output["flag"] = "NEEDS_REVIEW"
        output["reason"] = reason_sentence
    else:
        # Exactly one category match
        output["category"] = matched_categories[0]
        output["flag"] = ""
        output["reason"] = reason_sentence
        
    # 2. Prevent severity blindness (Urgent keywords explicitly overridden)
    is_urgent = False
    for kw in SEVERITY_KEYWORDS:
        if kw in desc_lower:
            is_urgent = True
            # Update the reason to pinpoint the severe sentence
            for s in sentences:
                if kw in s.lower():
                    output["reason"] = s
                    break
            break
            
    if is_urgent:
        output["priority"] = "Urgent"
    else:
        # Standard default, set to low for completely ambiguous/other
        output["priority"] = "Standard"
        if output["category"] == "Other" and output["flag"] == "NEEDS_REVIEW":
            output["priority"] = "Low"
            
    # Guarantee at least one sentence citation if any match didn't yield a sentence somehow
    if not output["reason"] and sentences:
        output["reason"] = sentences[0]
        
    return output


def batch_classify(input_path: str, output_path: str):
    """
    Skill 2: batch_classify
    Reads an input CSV of citizen complaints, iteratively applies offline classification to each row,
    and writes the complete results to an output CSV. Handles errors so the batch completes.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        sys.exit(1)
        
    results = []
    fieldnames = []
    
    with open(input_path, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        # safely read fieldnames to satisfy Pyre2 type checking
        _fields = reader.fieldnames
        fieldnames = [str(f) for f in _fields] if _fields is not None else []
        
        # Ensure output CSV will have the new classification columns
        for new_col in ["category", "priority", "reason", "flag"]:
            if new_col not in fieldnames:
                fieldnames.append(new_col)
                
        for i, row in enumerate(reader, 1):
            print(f"Processing row {i}...")
            classification = classify_complaint(row)
            
            # Merge results into the row
            for key in ["category", "priority", "reason", "flag"]:
                row[key] = classification.get(key, "")
                
            results.append(row)
            
    # Write to output_path
    with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier (Offline)")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    
    # Check args specifically before running
    args = parser.parse_args()
        
    print(f"Starting offline classification on {args.input}")
    batch_classify(args.input, args.output)
    print(f"Done. Classified results written to {args.output}")
