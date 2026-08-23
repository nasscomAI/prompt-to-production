"""
UC-0A — Complaint Classifier
Implementation utilizing google-genai SDK and structured output schemas.
"""
import os
import csv
import argparse
from typing import Literal
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Lazy load client helper to prevent immediate crash on import if API key is missing
_client = None

def get_client():
    """
    Initialize and return the GenAI client.
    """
    global _client
    if _client is None:
        load_dotenv()
        from google import genai
        # Client automatically picks up GEMINI_API_KEY from environment
        if not os.environ.get("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it in your .env file or environment.")
        _client = genai.Client()
    return _client


# Pydantic schema for structured output classification
class ComplaintClassification(BaseModel):
    category: Literal[
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
        "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
    ] = Field(description="The category of the complaint. Must be one of the allowed categories.")
    priority: Literal["Urgent", "Standard", "Low"] = Field(description="Priority of the complaint.")
    reason: str = Field(description="A single-sentence explanation citing exact words from the complaint description.")
    flag: Literal["NEEDS_REVIEW", "NO_FLAG"] = Field(description="Set to 'NEEDS_REVIEW' if category is ambiguous, otherwise 'NO_FLAG'.")


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row using the Gemini model and structured schema.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get("complaint_id", "UNKNOWN")
    description = row.get("description", "").strip()

    # Pre-process: if description is empty or missing, handle it immediately (null safety)
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "Missing complaint description.",
            "flag": "NEEDS_REVIEW"
        }

    # Define prompt guided by RICE enforcement rules from agents.md
    prompt = f"""
    You are a Civic Complaint Classifier agent. 
    Classify the following citizen complaint description according to these strict RICE rules:

    Allowed Categories:
    - Pothole
    - Flooding
    - Streetlight
    - Waste
    - Noise
    - Road Damage
    - Heritage Damage
    - Heat Hazard
    - Drain Blockage
    - Other

    Priority Rules:
    - If the description contains any of these severity keywords (case-insensitive): injury, child, school, hospital, ambulance, fire, hazard, fell, collapse, the priority MUST be "Urgent".
    - Otherwise, decide if it should be "Standard" or "Low".

    Reason Rule:
    - Must be exactly one sentence.
    - Must cite specific words/phrases from the complaint description to justify the categorization.

    Flag Rule:
    - Set flag to "NEEDS_REVIEW" if the category is genuinely ambiguous, or if it doesn't clearly fit any specific category, or if you had to fall back to "Other". Otherwise, set flag to "NO_FLAG".

    Complaint Description:
    "{description}"
    """

    try:
        client = get_client()
        from google.genai import types
        
        # Try utilizing gemini-2.5-flash as standard
        try:
            response = client.models.generate_content(
                model='gemini-3.1-flash-lite',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ComplaintClassification,
                    temperature=0.0
                ),
            )
        except Exception:
            # Fallback to gemini-1.5-flash if gemini-2.5-flash is not available/supported
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ComplaintClassification,
                    temperature=0.0
                ),
            )

        # Parse output
        import json
        data = json.loads(response.text)
        
        category = data.get("category", "Other")
        priority = data.get("priority", "Standard")
        reason = data.get("reason", "")
        flag = data.get("flag", "")
        if flag == "NO_FLAG":
            flag = ""
        
    except Exception as e:
        # Graceful fallback if API call or parsing fails
        print(f"Warning: Failed to classify row {complaint_id} via API: {e}")
        category = "Other"
        priority = "Standard"
        reason = f"Fallback classification: API processing error. Description: {description[:50]}..."
        flag = "NEEDS_REVIEW"

    # Post-process constraints: programmatic guardrails to guarantee adherence to README rules
    
    # 1. Enforce Allowed Categories list
    allowed_categories = {
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
        "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
    }
    if category not in allowed_categories:
        category = "Other"
        flag = "NEEDS_REVIEW"

    # 2. Enforce Severity Keywords -> Urgent priority rule (prevent severity blindness)
    desc_lower = description.lower()
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    has_severity_keyword = any(kw in desc_lower for kw in severity_keywords)
    
    if has_severity_keyword:
        priority = "Urgent"

    # 3. Clean and enforce one-sentence reason constraint
    reason = reason.strip()
    if not reason:
        reason = f"Classified under {category}."
    else:
        # Basic check to truncate to single sentence if model overgenerated
        sentences = reason.split(". ")
        if len(sentences) > 1:
            reason = sentences[0] + "."

    # 4. Enforce that "Other" category or ambiguous items must be flagged
    if category == "Other" and not flag:
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, and write results to output CSV.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Read rows from input
    rows = []
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        if not fieldnames or "description" not in fieldnames:
            raise ValueError(f"Input CSV is missing required 'description' column. Found: {fieldnames}")
        for row in reader:
            rows.append(row)

    print(f"Loaded {len(rows)} complaints from {input_path}. Commencing classification...")

    # Classify each row
    results = []
    for idx, row in enumerate(rows):
        cid = row.get("complaint_id", f"ROW-{idx}")
        print(f"[{idx+1}/{len(rows)}] Classifying complaint {cid}...")
        classified = classify_complaint(row)
        results.append(classified)

    # Write output to CSV
    output_headers = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_headers)
        writer.writeheader()
        for res in results:
            writer.writerow(res)

    print(f"Successfully processed and wrote {len(results)} records to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
