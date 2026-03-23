"""
UC-0A — Complaint Classifier
Built using the RICE → agents.md → skills.md workflow.
"""
import argparse
import csv
import os
import re

# Taxonomy from agents.md
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Severity keywords from agents.md (MUST trigger Urgent)
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
]

def classify_complaint(description: str) -> dict:
    """
    Classify a single complaint description based on RICE enforcement rules.
    Refined for better keyword matching and justified reasoning.
    """
    description_lower = description.lower()
    
    # 1. Determine Category
    category = "Other"
    match_word = ""

    # Category Mapping Logic
    mappings = {
        "Pothole": ["pothole"],
        "Flooding": ["flood", "water logging", "inundated", "rainwater"],
        "Streetlight": ["streetlight", "lamp", "lights out", "darkness", "tripped"],
        "Waste": ["garbage", "waste", "trash", "dumped", "bins"],
        "Noise": ["noise", "loud", "music", "wedding band", "amplifier", "midnight"],
        "Road Damage": ["road surface", "buckled", "cracked", "sinking", "paving", "broken", "footpath"],
        "Heritage Damage": ["heritage", "monument", "historic", "museum"],
        "Heat Hazard": ["heat", "hot", "sunstroke"],
        "Drain Blockage": ["drain", "sewer", "manhole", "blockage", "draining"]
    }

    # Search for matches prioritized by specific categories
    for cat, keywords in mappings.items():
        for word in keywords:
            if word in description_lower:
                category = cat
                match_word = word
                break
        if category != "Other": break

    # 2. Determine Priority (Enforcement Rule 2 + README)
    priority = "Standard"
    triggered_words = [word for word in URGENT_KEYWORDS if word in description_lower]
    
    if triggered_words:
        priority = "Urgent"
        justification_word = triggered_words[0]
    elif any(word in description_lower for word in ["urgent", "immediate", "emergency"]):
        priority = "Urgent"
        justification_word = "urgency"
    elif "low" in description_lower or "minor" in description_lower:
        priority = "Low"
        justification_word = "low priority"
    else:
        justification_word = match_word if match_word else "general content"

    # 3. Generate Reason (Enforcement Rule 3: cite specific words)
    # Extracts a snippet from the description to fulfill the "cite specific words" rule effectively.
    if triggered_words:
        reason = f"Classified as {priority} because the description mentions '{justification_word}', a critical severity indicator."
    elif category != "Other":
        reason = f"Classified as {category} because the description cites '{match_word}' as the primary issue."
    else:
        reason = "Classified as Other because the description lacks specific municipal taxonomy keywords."

    # 4. Handle Ambiguity (Refusal condition)
    flag = ""
    if category == "Other":
        flag = "NEEDS_REVIEW"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, apply classify_complaint per row, write output CSV.
    Matches skills.md specifications.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if not fieldnames:
                print("Error: Input CSV has no headers.")
                return
                
            output_fields = fieldnames + ["category", "priority", "reason", "flag"]
            
            for row in reader:
                description = row.get("description", "")
                if not description:
                    classification = {
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Empty description provided.",
                        "flag": "NEEDS_REVIEW"
                    }
                else:
                    classification = classify_complaint(description)
                
                row.update(classification)
                results.append(row)

        if not results:
            return

        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fields)
            writer.writeheader()
            writer.writerows(results)

    except Exception as e:
        print(f"Batch processing failed: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
