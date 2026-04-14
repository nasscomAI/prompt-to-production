import argparse
import csv
import json
import os
import re
from pydantic import BaseModel, Field
from enum import Enum
from typing import Literal
from google import genai

# UC-0A Taxonomy Enforcement
class CategoryEnum(str, Enum):
    pothole = "Pothole"
    flooding = "Flooding"
    streetlight = "Streetlight"
    waste = "Waste"
    noise = "Noise"
    road_damage = "Road Damage"
    heritage_damage = "Heritage Damage"
    heat_hazard = "Heat Hazard"
    drain_blockage = "Drain Blockage"
    other = "Other"

class PriorityEnum(str, Enum):
    urgent = "Urgent"
    standard = "Standard"
    low = "Low"

class ComplaintClassification(BaseModel):
    category: CategoryEnum = Field(description="Must be exactly one of the allowed categories.")
    priority: PriorityEnum = Field(description="Must be Urgent if severity keywords are present. Otherwise Standard or Low.")
    reason: str = Field(description="Exactly ONE sentence explaining the choice. Must cite specific words from the description.")
    flag: Literal["NEEDS_REVIEW", ""] = Field(description="Set to 'NEEDS_REVIEW' if genuinely ambiguous, otherwise leave as an empty string.", default="")

# Severity keywords that must trigger Urgent
SEVERITY_KEYWORDS = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]

def check_severity(text: str) -> bool:
    """Returns True if any severity keyword is found in the text (case-insensitive)."""
    text = text.lower()
    for word in SEVERITY_KEYWORDS:
        if re.search(rf"\b{word}\b", text):
            return True
    return False

def classify_complaint(client: genai.Client, description: str) -> dict:
    prompt = f"""
Analyze the following citizen complaint:
"{description}"

Follow these exact UC-0A classification rules:
1. Category: Select exactly one category: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
2. Priority: Select exactly one priority: Urgent, Standard, Low. 
   Rule: Use 'Urgent' if severity keywords (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) are present.
3. Reason: Exactly one sentence. Must cite specific words from the description that led to the category and priority choice.
4. Flag: Set to 'NEEDS_REVIEW' if the complaint is genuinely ambiguous (e.g., gibberish or multiple unrelated issues). Otherwise, set to ''.

Return the result in JSON format matching the schema.
"""
    # Using a widely available stable model
    model_id = 'gemini-1.5-flash'
    
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ComplaintClassification,
                temperature=0.0,
            ),
        )
        result = json.loads(response.text)
        
        # UC-0A Fix [Severity Blindness]: Force Urgent if keywords are present in the text
        if check_severity(description):
            if result.get("priority") != "Urgent":
                result["priority"] = "Urgent"
                result["reason"] = f"Priority upgraded to Urgent due to severity keyword detected. {result['reason']}"
        
        # UC-0A Fix [Missing Justification]: Ensure it is a single sentence (basic sanity check)
        if "." in result["reason"]:
            result["reason"] = result["reason"].split(".")[0] + "."
            
        return result
    except Exception as e:
        print(f"Error classifying: {e}")
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": f"Classification failed: {str(e)}",
            "flag": "NEEDS_REVIEW"
        }

def batch_classify(input_csv: str, output_csv: str):
    # Initialize the Gemini client
    try:
        client = genai.Client()
    except Exception as e:
        print(f"Failed to initialize GenAI client. Have you set the GEMINI_API_KEY environment variable?\n{e}")
        return
        
    # Ensure output directory exists (handles 'uc-0a/results_pune.csv')
    output_dir = os.path.dirname(output_csv)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(input_csv):
        print(f"Error: Input file '{input_csv}' not found.")
        return

    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)
        
    # Standardize result columns
    for col in ["category", "priority", "reason", "flag"]:
        if col not in fieldnames: 
            fieldnames.append(col)
    
    if not rows:
        print(f"Warning: Empty input file '{input_csv}'.")
        return
        
    # Detect description column
    text_col = 'description'
    if text_col not in rows[0]:
        options = ['text', 'complaint', 'issue', 'details', 'comment', 'content']
        for col in rows[0].keys():
            if col.lower() in options:
                text_col = col
                break
    
    print(f"Processing dataset using column: '{text_col}'")
    
    for i, row in enumerate(rows):
        description = row.get(text_col, "")
        if not description: continue
        
        print(f"[{i+1}/{len(rows)}] Classifying: {description[:60]}...")
        result = classify_complaint(client, description)
        
        row['category'] = result.get('category', '')
        row['priority'] = result.get('priority', '')
        row['reason'] = result.get('reason', '')
        row['flag'] = result.get('flag', '')
        
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"\n✅ UC-0A Batch complete! Results saved to: {output_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Citizen Complaint Classifier")
    parser.add_argument('--input', required=True, help="Input CSV file path")
    parser.add_argument('--output', required=True, help="Output CSV file path")
    
    args = parser.parse_args()
    batch_classify(args.input, args.output)
