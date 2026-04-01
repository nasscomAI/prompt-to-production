"""
UC-0A — Complaint Classifier
Implemented using RICE framework for Ahmedabad Civic Response.
"""
import argparse
import csv
import re

ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", 
    "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on enforcement rules in agents.md.
    """
    desc = row.get("description", "").lower()
    
    category = "Other"
    reason = "Categorized as Other due to general nature."
    flag = ""
    
    # Priority triggers (Safety First)
    priority = "Standard"
    urgent_keywords = [k for k in SEVERITY_KEYWORDS if k in desc]
    if urgent_keywords:
        priority = "Urgent"
    
    # Category Logic (Keyword-based mapping)
    if any(re.search(r"\b" + re.escape(k) + r"\b", desc) for k in ["pothole"]):
        category = "Pothole"
        reason = "Uses the word 'Pothole' directly."
    elif any(re.search(r"\b" + re.escape(k) + r"\b", desc) for k in ["melting", "heat", "temperature", "bubbling", "sun"]):
        category = "Heat Hazard"
        reason = "Identified as Heat Hazard citing '{next(k for k in ['melting', 'heat', 'temperature', 'bubbling', 'sun'] if re.search(r'\b' + re.escape(k) + r'\b', desc))}'."
    elif any(re.search(r"\b" + re.escape(k) + r"\b", desc) for k in ["waste", "bins", "overflowing", "garbage"]):
        category = "Waste"
        reason = "Mentions 'waste' or 'bins', classifying it under Waste."
    elif any(re.search(r"\b" + re.escape(k) + r"\b", desc) for k in ["heritage", "ancient", "old city", "step well"]):
        category = "Heritage Damage"
        reason = "Refers to '{next(k for k in ['heritage', 'ancient', 'old city', 'step well'] if re.search(r'\b' + re.escape(k) + r'\b', desc))}' area."
    elif any(re.search(r"\b" + re.escape(k) + r"\b", desc) for k in ["noise", "music", "audible"]):
        category = "Noise"
        reason = "Description mentions 'noise' or 'music' levels."
    elif any(re.search(r"\b" + re.escape(k) + r"\b", desc) for k in ["unlit", "lighting", "wiring", "streetlight"]):
        category = "Streetlight"
        reason = "Issues related to 'unlit' areas or 'lighting'."
    elif any(re.search(r"\b" + re.escape(k) + r"\b", desc) for k in ["flooding", "waterlogged"]):
        category = "Flooding"
        reason = "Reports 'flooding' or 'waterlogged' conditions."
    elif any(re.search(r"\b" + re.escape(k) + r"\b", desc) for k in ["drain"]):
        category = "Drain Blockage"
        reason = "Reports 'drain' related issues."
    elif any(re.search(r"\b" + re.escape(k) + r"\b", desc) for k in ["subsidence", "paving", "bench", "tarmac"]):
        category = "Road Damage"
        reason = "Infrastructure damage like 'subsidence' or 'paving'."

    # Refined Priority (Standard/Low)
    if priority != "Urgent":
        if any(k in desc for k in ["grass", "bench"]):
            priority = "Low"
        else:
            priority = "Standard"

    # Ambiguity check
    count = 0
    if category != "Other":
        if any(k in desc for k in ["waste", "garbage"]) and any(k in desc for k in ["heritage", "old city"]):
            flag = "NEEDS_REVIEW"
        if any(k in desc for k in ["road", "paving"]) and any(k in desc for k in ["drain", "blockage"]):
            flag = "NEEDS_REVIEW"

    # Final Reason refinement to include priority justification
    if priority == "Urgent":
        reason += f" Priority escalated to Urgent due to keyword '{urgent_keywords[0]}'."

    return {
        "complaint_id": row.get("complaint_id"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify, and write results.
    """
    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row.get("description"):
                    results.append({
                        "complaint_id": row.get("complaint_id", "N/A"),
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Missing description.",
                        "flag": "NEEDS_REVIEW"
                    })
                    continue
                results.append(classify_complaint(row))
    except FileNotFoundError:
        print(f"Error: {input_path} not found.")
        return

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
