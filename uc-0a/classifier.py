"""
UC-0A — Complaint Classifier
A functional implementation utilizing rules from agents.md and skills.md.
"""
import argparse
import csv
import json
import os
import time

# Basic .env file reader so we don't need python-dotenv dependency
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#") and "=" in line:
                key, val = line.strip().split("=", 1)
                os.environ[key.strip()] = val.strip().strip("'\"")

# To run this script against a real LLM, ensure google.generativeai is installed
# and GEMINI_API_KEY is set in your environment or in a .env file.
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

SYSTEM_PROMPT = """
role: You are an expert civic complaint classifier operating for a municipal government. Your operational boundary is strict categorisation and prioritisation of citizen complaints based solely on the provided text description. You do not resolve issues, you only classify them into standardized buckets.

intent: Your output must be structurally consistent and verifiable. For each row, you must output exactly a category, a priority level, a one-sentence reason citing specific words from the description, and an optional review flag. Your category must perfectly match one of the predefined strings, and the reason field must demonstrably quote words from the input text justifying the priority or classification chosen.

context: You are allowed to use ONLY the textual description provided in the complaint row. Do not infer external knowledge about the city, weather events not mentioned, or policies. Exclude any personal judgement on the validity of the complaint; trust the text as written even if it seems hyperbolic.

enforcement:
  - Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
  - Priority must be set to 'Urgent' if the description contains any of the exact severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse. (Default to Standard otherwise, or Low if very trivial).
  - Every output row must include a 'reason' field that is exactly one sentence long and cites specific words from the description
  - If the category cannot be definitively determined from the description alone, output category: 'Other' and flag: 'NEEDS_REVIEW'

Output purely a valid JSON object matching this structure:
{
  "category": "...",
  "priority": "...",
  "reason": "...",
  "flag": "..."
}
"""

# Initialize Gemini Client if API key is provided
GENAI_MODEL = None
if HAS_GENAI:
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        GENAI_MODEL = genai.GenerativeModel(
            model_name="gemini-2.5-flash", 
            system_instruction=SYSTEM_PROMPT,
            generation_config={"response_mime_type": "application/json"}
        )

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row based on skills.md rules.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    # Setup the default base dictionary structure to return
    result = {
        "complaint_id": row.get("complaint_id", "UNKNOWN"),
        "category": "Other",
        "priority": "Standard",
        "reason": "Invalid or missing input",
        "flag": "NEEDS_REVIEW"
    }

    description = row.get("description", "").strip()
    if not description:
        return result

    if GENAI_MODEL:
        try:
            prompt = f"Complaint to classify: {description}"
            response = GENAI_MODEL.generate_content(prompt)
            data = json.loads(response.text)
            
            result["category"] = data.get("category", "Other")
            result["priority"] = data.get("priority", "Standard")
            result["reason"] = data.get("reason", "")
            result["flag"] = data.get("flag", "")
            
            # Simple failsafe against bad structured parsing
            if result["category"] not in ["Pothole", "Flooding", "Streetlight", "Waste", "Noise", "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"]:
                result["category"] = "Other"
                result["flag"] = "NEEDS_REVIEW"
                
        except Exception as e:
            result["reason"] = f"Error during AI classification processing: {str(e)}"
    else:
        # Fallback simulated logic if API is unconfigured
        result["reason"] = "LLM Not Configured - Set GEMINI_API_KEY."

    return result

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Implements skills.md batch_classify behaviour.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    results_data = []
    
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row_index, row in enumerate(reader, start=1):
            try:
                classified_row = classify_complaint(row)
                results_data.append(classified_row)
                if GENAI_MODEL:
                    time.sleep(1) # Prevent rapid rate limiting if using free-tier API
            except Exception as e:
                # Do not crash the entire batch; append error row
                results_data.append({
                    "complaint_id": row.get("complaint_id", f"ROW-{row_index}"),
                    "category": "Other",
                    "priority": "Standard",
                    "reason": f"System error occurred processing row: {e}",
                    "flag": "NEEDS_REVIEW"
                })

    if not results_data:
        print("No valid rows were parsed to write.")
        return

    # Write results output
    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input", required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
