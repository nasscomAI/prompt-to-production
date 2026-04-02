"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import json
import os
import sys
import traceback
from typing import Optional



def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using simple keyword matching.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    description = row.get("description", "")
    base_result = {
        "complaint_id": row.get("complaint_id", ""),
        "category": "Other",
        "priority": "Low",
        "reason": "Missing description.",
        "flag": "NEEDS_REVIEW"
    }
    if not description:
        return base_result

    desc_lower = description.lower()
    
    category = "Other"
    flag = "NEEDS_REVIEW"
    
    if "pothole" in desc_lower or "crater" in desc_lower:
        category = "Pothole"
        flag = ""
    elif "flood" in desc_lower or "water" in desc_lower:
        category = "Flooding"
        flag = ""
    elif "light" in desc_lower or "dark" in desc_lower:
        category = "Streetlight"
        flag = ""
    elif "waste" in desc_lower or "trash" in desc_lower or "garbage" in desc_lower:
        category = "Waste"
        flag = ""
    elif "noise" in desc_lower or "loud" in desc_lower:
        category = "Noise"
        flag = ""
    elif "road" in desc_lower or "crack" in desc_lower:
        category = "Road Damage"
        flag = ""
    elif "heritage" in desc_lower or "statue" in desc_lower or "monument" in desc_lower:
        category = "Heritage Damage"
        flag = ""
    elif "heat" in desc_lower or "hot" in desc_lower:
        category = "Heat Hazard"
        flag = ""
    elif "drain" in desc_lower or "clog" in desc_lower:
        category = "Drain Blockage"
        flag = ""

    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    priority = "Low"
    reason = f"Classified automatically as {category}."
    
    for kw in severity_keywords:
        if kw in desc_lower:
            priority = "Urgent"
            reason = f"Matched severity keyword: '{kw}'."
            break
            
    if priority == "Low" and category != "Other":
        priority = "Standard"

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
    results = []
    fieldnames = []
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames or []) + ["category", "priority", "reason", "flag"]
            for row in reader:
                try:
                    classification = classify_complaint(row)
                    # Merge classification results into the original row
                    out_row = dict(row)
                    out_row["category"] = classification["category"]
                    out_row["priority"] = classification["priority"]
                    out_row["reason"] = classification["reason"]
                    out_row["flag"] = classification["flag"] if classification["flag"] else ""
                    results.append(out_row)
                except Exception as row_error:
                    print(f"Failed processing row: {row}. Error: {row_error}")
    except FileNotFoundError:
        print(f"Input file {input_path} not found.")
        return False
    except Exception as e:
        print(f"Error reading input file: {e}")
        return False

    if not results:
        print("No results to write. Output file not created.")
        return False

    try:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        return True
    except Exception as e:
        print(f"Error writing output file: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    if batch_classify(args.input, args.output):
        print(f"Done. Results written to {args.output}")
    else:
        sys.exit(1)
