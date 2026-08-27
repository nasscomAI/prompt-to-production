"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import os
import json
from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from litellm import completion
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
ALLOWED_CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

class ComplaintClassification(BaseModel):
    category: Literal[
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
        "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
    ]
    priority: Literal["Urgent", "Standard", "Low"]
    reason: str = Field(description="One sentence citing specific words from description")
    flag: Optional[str] = Field(None, description="NEEDS_REVIEW or blank")

SYSTEM_PROMPT = """
You are a municipal service request classifier for city citizens. Your operational boundary is strictly limited to identifying the appropriate category and priority of a complaint based solely on the provided description.

Your goal is to transform a raw citizen complaint description into a structured classification (category, priority, reason, flag).

ENFORCEMENT RULES:
1. Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
2. Priority must be set to 'Urgent' if the description contains any safety-critical keywords (e.g., injury, child, hospital, hazard).
3. Reason must be exactly one sentence and must cite specific words from the complaint description to justify the chosen category and priority.
4. Flag must be set to 'NEEDS_REVIEW' if the category is genuinely ambiguous or if multiple categories seem equally valid. Otherwise, leave it blank.

Output your response as a valid JSON matching the requested schema.
"""

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using LLM and enforcement rules.
    """
    description = row.get("description", "").lower()
    
    # 1. LLM Call for classification
    try:
        response = completion(
            model="gemini/gemini-1.5-flash", 
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Complaint Description: {row.get('description')}"}
            ],
            response_format={ "type": "json_object" }
        )
        
        raw_result = json.loads(response.choices[0].message.content)
        classification = ComplaintClassification(**raw_result)
        result = classification.model_dump()
        
    except Exception as e:
        # Fallback for ambiguous or failing rows
        print(f"Error classifying row {row.get('complaint_id')}: {e}")
        result = {
            "category": "Other",
            "priority": "Low",
            "reason": f"Classification failed due to technical error.",
            "flag": "NEEDS_REVIEW"
        }

    # 2. Programmatic Priority Enforcement (RICE rule)
    if any(keyword in description for keyword in SEVERITY_KEYWORDS):
        result["priority"] = "Urgent"
        if "reason" in result and "Urgent" not in result["reason"]:
            result["reason"] += " (Priority raised to Urgent due to safety keywords)."

    # Merge results
    return {**row, **result}


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    
    try:
        with open(input_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames + ["category", "priority", "reason", "flag"]
            
            print(f"Starting batch classification for {input_path}...")
            for row in reader:
                classified_row = classify_complaint(row)
                results.append(classified_row)
                print(f"Processed {row.get('complaint_id')}")

        with open(output_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    except FileNotFoundError:
        print(f"Error: Input file {input_path} not found.")
    except Exception as e:
        print(f"Unexpected error during batch processing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
