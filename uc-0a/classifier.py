import argparse
import csv
import os
import sys
import re
from typing import Literal
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# Strict Schema Definition
# ---------------------------------------------------------------------------
class ComplaintClassification(BaseModel):
    category: Literal[
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
        "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
    ]
    priority: Literal["Urgent", "Standard", "Low"]
    reason: str = Field(
        description="Exactly one sentence. Must cite specific words from the description."
    )
    flag: Literal["NEEDS_REVIEW", ""] = Field(
        description="Set to NEEDS_REVIEW when the category is genuinely ambiguous, otherwise leave blank."
    )

# ---------------------------------------------------------------------------
# Core Agent Configuration (R.I.C.E. Framework)
# ---------------------------------------------------------------------------
SYSTEM_INSTRUCTION = """
<ROLE>
Citizen complaint classification agent responsible for evaluating complaint descriptions and categorizing them strictly within predefined taxonomy and severity boundaries.
</ROLE>

<INTENT>
Output a precise classification containing exactly four fields (category, priority, reason, flag) that strictly adhere to the allowed schema and properly identify urgent hazards or ambiguous reports.
</INTENT>

<CONTEXT>
You must rely solely on the text provided in the input complaint description. Do not use outside knowledge to invent new categories or assume severity without explicit keyword triggers.
</CONTEXT>

<ENFORCEMENT>
- category field must contain exact strings only with no variations.
- priority field must be Urgent, Standard, or Low.
- priority field MUST be Urgent if severity keywords are present (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse).
- reason field must be exactly one sentence and MUST cite specific words from the description in quotes.
- flag field must be set to "NEEDS_REVIEW" when the category is genuinely ambiguous, otherwise leave blank ("").
</ENFORCEMENT>
"""

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance", 
    "fire", "hazard", "fell", "collapse"
]

# ---------------------------------------------------------------------------
# Skill 1: classify_complaint
# ---------------------------------------------------------------------------
def classify_complaint(client: genai.Client, description: str) -> dict:
    """
    Classifies a single citizen complaint into a predefined category and priority 
    while generating a reasoned justification. Includes strict error handling.
    """
    if not description or not str(description).strip():
        return {
            "category": "Other",
            "priority": "Low",
            "reason": "Input was empty or malformed.",
            "flag": "NEEDS_REVIEW"
        }

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=description,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=ComplaintClassification,
                temperature=0.1,
            ),
        )
        
        import json
        result = json.loads(response.text)
        
        # ERROR HANDLING / ENFORCEMENT: 
        # Force Urgent priority if severity keywords are present to avoid severity blindness
        desc_lower = description.lower()
        if any(re.search(rf"\b{kw}\b", desc_lower) for kw in SEVERITY_KEYWORDS):
            result["priority"] = "Urgent"

        # ERROR HANDLING / ENFORCEMENT:
        # Strictly restrict categories to the allowed list to prevent taxonomy drift
        allowed_categories = ComplaintClassification.model_fields["category"].annotation.__args__
        if result["category"] not in allowed_categories:
            result["category"] = "Other"
            result["flag"] = "NEEDS_REVIEW"

        return result

    except Exception as e:
        # ERROR HANDLING: Set flag to NEEDS_REVIEW if classification completely fails
        return {
            "category": "Other",
            "priority": "Standard",
            "reason": f"Classification failed due to error: {str(e)}",
            "flag": "NEEDS_REVIEW"
        }

# ---------------------------------------------------------------------------
# Skill 2: batch_classify
# ---------------------------------------------------------------------------
def batch_classify(input_path: str, output_path: str):
    """
    Reads a batch of complaints from an input CSV, applies classify_complaint, 
    and writes the structured results to an output CSV.
    """
    # Graceful error handling for missing files
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)

    client = genai.Client()
    
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    processed_rows = []
    fieldnames = []

    print(f"Reading complaints from: {input_path}")
    try:
        with open(input_path, mode="r", encoding="utf-8-sig") as infile:
            reader = csv.DictReader(infile)
            fieldnames = list(reader.fieldnames or [])
            
            # Ensure the output CSV strictly adheres to the required four-column schema add-ons
            for col in ["category", "priority", "reason", "flag"]:
                if col not in fieldnames:
                    fieldnames.append(col)

            for row_num, row in enumerate(reader, start=1):
                # Attempt to locate the description column automatically
                desc_col = next((col for col in row.keys() if col and "description" in col.lower()), None)
                if not desc_col and row.keys():
                    desc_col = list(row.keys())[0] # Fallback to first column
                
                description = row.get(desc_col, "")
                
                print(f"Classifying row {row_num}...")
                classification = classify_complaint(client, description)
                
                row["category"] = classification["category"]
                row["priority"] = classification["priority"]
                row["reason"] = classification["reason"]
                row["flag"] = classification["flag"]
                
                processed_rows.append(row)
                
    except Exception as e:
        print(f"Error processing input file: {str(e)}", file=sys.stderr)
        sys.exit(1)

    print(f"Writing results to: {output_path}")
    try:
        with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(processed_rows)
        print("Batch classification complete.")
    except Exception as e:
        print(f"Error writing output file: {str(e)}", file=sys.stderr)
        sys.exit(1)

# ---------------------------------------------------------------------------
# CLI Execution Entrypoint
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    args = parser.parse_args()

    if not os.environ.get("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    batch_classify(args.input, args.output)

if __name__ == "__main__":
    main()