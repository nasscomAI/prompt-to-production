"""
UC-0A — Complaint Classifier
Implementation based on agents.md and skills.md specifications.
"""
import argparse
import csv
import json
import os
import sys
from typing import Dict, List

# To use an LLM, you would typically use:
# import google.generativeai as genai
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def classify_complaint(description: str) -> Dict:
    """
    Classify a single complaint row using the schema defined in agents.md.
    Note: In a production environment, this would call an LLM.
    For this 'vibe-coded' version, we implement the enforcement rules directly.
    """
    # Allowed Categories from agents.md
    ALLOWED_CATEGORIES = [
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
        "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
    ]
    
    # Severity keywords that must trigger Urgent
    SEVERITY_KEYWORDS = [
        "injury", "child", "school", "hospital", "ambulance", 
        "fire", "hazard", "fell", "collapse"
    ]

    # 1. Determine Category (Simplified taxonomic mapping)
    desc_lower = description.lower()
    category = "Other"
    if "pothole" in desc_lower: category = "Pothole"
    elif "flood" in desc_lower or "underpass" in desc_lower: category = "Flooding"
    elif "streetlight" in desc_lower or "lights out" in desc_lower: category = "Streetlight"
    elif "waste" in desc_lower or "garbage" in desc_lower or "dead animal" in desc_lower: category = "Waste"
    elif "noise" in desc_lower or "music" in desc_lower: category = "Noise"
    elif "road" in desc_lower and ("cracked" in desc_lower or "sinking" in desc_lower): category = "Road Damage"
    elif "heritage" in desc_lower: category = "Heritage Damage"
    elif "heat" in desc_lower: category = "Heat Hazard"
    elif "drain" in desc_lower: category = "Drain Blockage"

    # 2. Determine Priority with strict enforcement
    priority = "Standard"
    is_urgent = any(kw in desc_lower for kw in SEVERITY_KEYWORDS)
    if is_urgent:
        priority = "Urgent"
    elif "noise" in desc_lower or "waste" in desc_lower:
        priority = "Low"

    # 3. Generate Reason (Must cite specific words)
    # Finding the first occurrence of a keyword for the reason
    reason_word = next((kw for kw in SEVERITY_KEYWORDS if kw in desc_lower), None)
    if not reason_word:
        # Fallback to category-related keyword
        reason_word = category.lower()
    
    reason = f"Classified as {category} because description mentions '{reason_word}'."

    # 4. Set Flag for ambiguity
    flag = ""
    if category == "Other" or "safety concern" in desc_lower:
        flag = "NEEDS_REVIEW"

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write results to output CSV.
    Handles missing data and ensures output matches schema.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            
            for row in reader:
                description = row.get("description", "")
                if not description:
                    # Skill enforcement: handle nulls
                    classification = {
                        "category": "Other",
                        "priority": "Low",
                        "reason": "Missing description.",
                        "flag": "NEEDS_REVIEW"
                    }
                else:
                    classification = classify_complaint(description)
                
                # Merge original row with classification
                row.update(classification)
                results.append(row)

    except Exception as e:
        print(f"Error during batch processing: {e}")
        return

    # Write output
    if results:
        output_fields = list(results[0].keys())
        try:
            with open(output_path, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=output_fields)
                writer.writeheader()
                writer.writerows(results)
        except Exception as e:
            print(f"Error writing output file: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to csv")
    parser.add_argument("--output", required=True, help="Path to write results")
    args = parser.parse_args()
    
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
