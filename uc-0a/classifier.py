"""
UC-0A — Complaint Classifier
Build this using the RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import json
import os

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Please install google-genai library: pip install google-genai")
    exit(1)

def get_system_instruction() -> str:
    """Reads agents.md to get the RICE prompt for the LLM."""
    agent_path = os.path.join(os.path.dirname(__file__), "agents.md")
    try:
        with open(agent_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print("Warning: agents.md not found, using generic prompt.")
        return "You are an expert citizen complaint classifier. Ensure strictly to RICE rules."

def classify_complaint(client, row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_text = json.dumps(row)
    
    # JSON schema constraint ensures structured response fields matching skills.md
    schema = {
        "type": "OBJECT",
        "properties": {
            "category": {"type": "STRING"},
            "priority": {"type": "STRING"},
            "reason": {"type": "STRING"},
            "flag": {"type": "STRING"}
        },
        "required": ["category", "priority", "reason", "flag"]
    }

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Classify this complaint row ensuring strict adherence to the system instructions and formatting rules:\n{complaint_text}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
                system_instruction=get_system_instruction(),
                temperature=0.0  # zero temperature ensures reproducible exact classification
            ),
        )
        
        result = json.loads(response.text)
        
        row["category"] = result.get("category", "Other")
        row["priority"] = result.get("priority", "Low")
        row["reason"] = result.get("reason", "")
        
        # Verify and normalise flag to either NEEDS_REVIEW or empty
        flag_val = result.get("flag", "")
        if flag_val and flag_val.upper() == "NEEDS_REVIEW":
            row["flag"] = "NEEDS_REVIEW"
        else:
            row["flag"] = ""
            
    except Exception as e:
        row["category"] = "Other"
        row["priority"] = "Low"
        row["reason"] = f"Error during classification: {str(e)}"
        row["flag"] = "NEEDS_REVIEW"
        
    return row

def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Must handle missing fields, flag errors, and save outputs resiliently.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        return

    # Initialize Gemini client. Requires GEMINI_API_KEY environment variable.
    try:
        client = genai.Client()
    except Exception as e:
        print(f"Failed to initialize Gemini Client. Make sure GEMINI_API_KEY is set in your environment. Error: {e}")
        return

    results = []
    fieldnames = []
    
    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = list(reader.fieldnames)
        
        # Append target output classification columns if missing in original sheet
        classification_fields = ["category", "priority", "reason", "flag"]
        for field in classification_fields:
            if field not in fieldnames:
                fieldnames.append(field)
                
        for row in reader:
            print(f"Processing row: {row.get('complaint_id', row.get('id', 'Unknown'))}...")
            classified_row = classify_complaint(client, row)
            results.append(classified_row)
            
    with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
