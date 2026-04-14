"""
UC-0A — Complaint Classifier
Production-grade semantic classification engine following the R.I.C.E methodology.
"""
import argparse
import csv
import re
import os
import sys

# ==========================================
# TAXONOMY & ENFORCEMENT RULES (agents.md)
# ==========================================
TAXONOMY = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

# Safeguard against 'Severity Blindness'
URGENT_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

# Safeguard against 'Taxonomy Drift' & 'Hallucinated Sub-categories'
CATEGORY_PATTERNS = {
    "Heat Hazard": [r"heat", r"temperature", r"sun", r"melting", r"bubbling", r"thermal", r"burning", r"4[456]\s?°c"],
    "Heritage Damage": [r"heritage", r"ancient", r"monument", r"historic", r"old city", r"temple", r"step well"],
    "Drain Blockage": [r"drain", r"manhole", r"sewage", r"blocked", r"overflowing drain", r"gutter"],
    "Pothole": [r"pothole", r"crater", r"cavity", r"deep hole"],
    "Flooding": [r"flood", r"waterlogging", r"knee-deep", r"accumulation", r"standing in water", r"rainwater", r"inundated"],
    "Streetlight": [r"streetlight", r"dark", r"lamp", r"unlit", r"flickering", r"sparking", r"light out"],
    "Waste": [r"garbage", r"bins", r"smell", r"waste", r"trash", r"debris", r"dead animal", r"dumped", r"overflowing bin"],
    "Noise": [r"noise", r"music", r"drilling", r"loud", r"midnight", r"acoustic"],
    "Road Damage": [r"crack", r"sinking", r"tiles", r"broken", r"upturned", r"subsidence", r"surface", r"footpath", r"tarmac"]
}

def classify_complaint(row: dict) -> dict:
    """
    R.I.C.E Framework Implementation - Skill: classify_complaint
    ----------------------------------------------------------
    ROLE: Semantic row classifier.
    INTENT: Map raw description text to a structured dictionary with cited evidence.
    CONTEXT: Authorized input fields: [complaint_id, city, description].
    ENFORCEMENT: Strictly use 10-item taxonomy. Prevent severity blindness.
    """
    description = row.get("description", "").lower()
    complaint_id = row.get("complaint_id", "UNKNOWN")
    city = row.get("city", "Unknown City")
    
    # 1. ENFORCEMENT: Severity Trigger Logic
    priority = "Standard"
    urgent_word = None
    for word in URGENT_KEYWORDS:
        if re.search(rf"\b{word}\b", description):
            priority = "Urgent"
            urgent_word = word
            break
            
    # 2. ENFORCEMENT: Taxonomy Drill Logic (Strict category matching)
    category = "Other"
    cite_word = None
    
    # Prioritized iteration to prevent taxonomy drift
    for cat, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, description):
                category = cat
                cite_word = pattern.replace(r"\b", "")
                break
        if category != "Other":
            break
            
    # 3. ENFORCEMENT: Ambiguity Refusal
    flag = "NEEDS_REVIEW" if category == "Other" else ""
        
    # 4. ENFORCEMENT: Justification (Must cite specific words found in description)
    if category != "Other":
        if urgent_word and urgent_word != cite_word:
            reason = f"Classified as {category} in {city} via '{cite_word}'; priority elevated to Urgent due to '{urgent_word}'."
        else:
            reason = f"Justified as {category} in {city} based on the specific mention of '{cite_word}' in the text."
    else:
        reason = f"Classification from {city} is genuinely ambiguous and requires manual review (Other)."
        
    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    R.I.C.E Framework Implementation - Skill: batch_classify
    -------------------------------------------------------
    ROLE: CSV orchestration engine.
    INTENT: Transform source city CSV into classified results CSV.
    CONTEXT: Access to city-specific datasets (e.g., test_hyderabad.csv).
    ENFORCEMENT: Handle null descriptions and malformed rows without crashing.
    """
    if not os.path.exists(input_path):
        print(f"Error: Target file {input_path} not found.")
        sys.exit(1)

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                # Handle nulls/missing descriptions to satisfy skills.md enforcement
                if not row or not row.get("description"):
                    results.append({
                        "complaint_id": row.get("complaint_id", "UNKNOWN"),
                        "category": "Other",
                        "priority": "Standard",
                        "reason": "Missing or null description field.",
                        "flag": "NEEDS_REVIEW"
                    })
                else:
                    results.append(classify_complaint(row))
    except Exception as e:
        print(f"Critical error processing CSV rows: {e}")
        sys.exit(1)

    if not results:
        print("No processable records found.")
        return

    # Aggregate into structured CSV output
    field_mapping = ["complaint_id", "category", "priority", "reason", "flag"]
    try:
        with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=field_mapping)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Critical error generating results file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier (R.I.C.E. Ready)")
    parser.add_argument("--input",  required=True, help="Path to city test CSV")
    parser.add_argument("--output", required=True, help="Path for results CSV")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Audit Complete. Results written to: {args.output}")
