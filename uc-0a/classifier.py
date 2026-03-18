"""
UC-0A — Complaint Classifier
Starter file. Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import json
import os
import re

# Fallback heuristic rules mimicking the exact RICE rules from agents.md
def heuristic_classify(desc: str) -> dict:
    desc_lower = desc.lower()
    
    category = "Other"
    priority = "Standard"
    reason = "Standard complaint."
    flag = ""
    
    # Category mapping
    if "pothole" in desc_lower:
        category = "Pothole"
    elif "flood" in desc_lower or "rainwater" in desc_lower:
        category = "Flooding"
    elif "drain" in desc_lower:
        category = "Drain Blockage"
    elif "waste" in desc_lower or "garbage" in desc_lower:
        category = "Waste"
    elif "collapse" in desc_lower or "crater" in desc_lower:
        category = "Road Damage"
    elif "heritage" in desc_lower:
        category = "Heritage Damage"
    elif "noise" in desc_lower or "drilling" in desc_lower or "engines" in desc_lower:
        category = "Noise"
        
    # Priority Overrides
    urgent_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    trigger = None
    for kw in urgent_keywords:
        if kw in desc_lower:
            trigger = kw
            break
            
    if trigger:
        priority = "Urgent"
        reason = f"Contains severity keyword '{trigger}' in description."
    else:
        # Provide a reason citing specific words
        # Take the first 5 words as cited words
        words = desc.split()
        cited = " ".join(words[:min(5, len(words))])
        reason = f"Based on description stating: '{cited}...'"
    
    # Ambiguity check
    if category == "Other":
        flag = "NEEDS_REVIEW"
        reason = "Category ambiguous based on description."

    return {
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def classify_complaint_llm(row: dict) -> dict:
    # Try using Gemini API if present
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=gemini_key)
            prompt = f'''
            You are an expert civic services complaint classifier.
            
            Enforcement Rules:
            1. Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
            2. Priority must be exactly: Urgent, Standard, or Low.
            3. Priority MUST be 'Urgent' if the description contains ANY of these severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse.
            4. Reason field must cite specific words directly from the description to justify both category and priority.
            5. If category cannot be confidently determined, output category 'Other' and set flag 'NEEDS_REVIEW'. Otherwise, leave flag blank.
            
            Complaint Description: "{row.get('description', '')}"
            
            Return raw JSON with exactly these keys: "category", "priority", "reason", "flag".
            Do not wrap in markdown tags.
            '''
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"LLM failed, falling back to heuristic: {e}")
            return heuristic_classify(row.get('description', ''))
            
    # Default to heuristic if no API key is easily available to ensure the participant script runs fully
    return heuristic_classify(row.get('description', ''))

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    res = classify_complaint_llm(row)
    # Ensure all required keys exist
    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": res.get("category", "Other"),
        "priority": res.get("priority", "Low"),
        "reason": res.get("reason", "Missing reason"),
        "flag": res.get("flag", "")
    }

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must: flag nulls, not crash on bad rows, produce output even if some rows fail.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
        return

    results = []
    for row in rows:
        try:
            classification = classify_complaint(row)
            results.append(classification)
        except Exception as e:
            print(f"Error classifying row {row.get('complaint_id', 'UNKNOWN')}: {e}")
            results.append({
                "complaint_id": row.get("complaint_id", "ERROR"),
                "category": "Other",
                "priority": "Low",
                "reason": f"System Error: {str(e)}",
                "flag": "NEEDS_REVIEW"
            })

    if not results:
        print("No results to write.")
        return

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
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
