"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv

import re

def classify_complaint(row: dict) -> dict:
    description = row.get("description", "").lower()
    
    # Define taxonomy with priority ordering
    taxonomy = [
        ("Heritage Damage", ["heritage"]),
        ("Drain Blockage", ["drain", "blocked", "stormwater"]),
        ("Flooding", ["flood", "underpass", "rainwater", r"\brain\b"]),
        ("Pothole", ["pothole"]),
        ("Streetlight", ["streetlight", "lamp", "light", r"\bdark\b"]),
        ("Waste", ["waste", "garbage", "trash", "piles"]),
        ("Noise", ["noise", "sound", "drilling", "loud", "trucks idling"]),
        ("Road Damage", ["road damage", "crater", "collapsed"]),
        ("Heat Hazard", ["heat", "sun", r"\bhot\b"])
    ]
    
    # Determine Category
    category = "Other"
    matched_kw = "related content"
    for cat, keywords in taxonomy:
        for kw in keywords:
            if re.search(kw, description):
                category = cat
                matched_kw = kw.replace(r"\b", "")
                break
        if category != "Other":
            break
            
    # Determine Priority
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Standard"
    for kw in urgent_keywords:
        if re.search(rf"\b{kw}", description):
            priority = "Urgent"
            matched_kw = kw
            break
    
    if priority != "Urgent" and row.get("days_open") and int(row.get("days_open")) > 15:
        priority = "Low"

    # Generate Reason
    reason = f"Classified as {category} because description mentions '{matched_kw}'."
    
    # Flag Ambiguity
    flag = "NEEDS_REVIEW" if category == "Other" else ""
    
    return {
        "complaint_id": row.get("complaint_id"),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    results = []
    with open(input_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                results.append(classify_complaint(row))
            except Exception as e:
                results.append({
                    "complaint_id": row.get("complaint_id"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"Error: {str(e)}",
                    "flag": "NEEDS_REVIEW"
                })
                
    keys = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
