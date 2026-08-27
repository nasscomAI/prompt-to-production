"""
UC-0A — Complaint Classifier
Implementation using Gemini JSON outputs via the new `google-genai` SDK and strict RICE rules.
"""
import argparse
import csv
import json
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("ERROR: Please install the correct package using: pip install google-genai")
    sys.exit(1)

def get_system_prompt() -> str:
    """Read the agents.md content to use as the system prompt."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        agents_path = os.path.join(script_dir, 'agents.md')
        with open(agents_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return "You are an expert citizen complaint classifier. Categorize strictly. You MUST always return valid JSON with keys: category, priority, reason, flag."

def classify_complaint(client, row: dict, system_prompt: str) -> dict:
    """
    Classify a single complaint row using the Gemini new SDK JSON mode.
    """
    description = row.get("description", "").lower()

    try:
        # Prompt explicitly asks for JSON response
        prompt = json.dumps(row) + "\n\nCRITICAL: Respond ONLY in pure JSON format with exactly 4 keys: category, priority, reason, flag."
        
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                temperature=0.0
            )
        )
        
        output_str = response.text.replace("```json", "").replace("```", "").strip()
        output = json.loads(output_str)

        category = output.get("category", "Other")
        priority = output.get("priority", "Standard")
        reason = output.get("reason", "No reason provided")
        flag = output.get("flag", "")
        
    except Exception as e:
        print(f"Error classifying {row.get('complaint_id', 'unknown')}: {e}")
        category = "Other"
        priority = "Standard"
        reason = "Error during LLM classification"
        flag = "NEEDS_REVIEW"

    # Enforcement Overlay (Programmatic Fail-safe for Severity Blindness)
    severity_keywords = ["injury", "child", "school", "hospital", "ambulance", "fire", "hazard", "fell", "collapse"]
    if any(keyword in description for keyword in severity_keywords):
        if priority != "Urgent":
            priority = "Urgent"
            reason = f"[Programmatic Override] Severity keyword detected: {reason}"

    # Taxonomy Overrides (Programmatic Fail-safe for Taxonomy drift)
    valid_categories = [
        "Pothole", "Flooding", "Streetlight", "Waste", "Noise", 
        "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
    ]
    if category not in valid_categories:
        category = "Other"
        flag = "NEEDS_REVIEW"
        reason = f"[Programmatic Override] Invalid taxonomy drifted to Other. {reason}"

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
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(">> WARNING: GEMINI_API_KEY environment variable is not set in `.env` or system var!")
        print(">> The script may crash if you don't export it before running.")
    
    # Initialize the new SDK client
    client = genai.Client(api_key=api_key)
    system_prompt = get_system_prompt()
    
    results = []
    
    with open(input_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for i, row in enumerate(reader):
            cid = row.get("complaint_id", "Unknown")
            print(f"Classifying row {i+1} : {cid}...")
            res = classify_complaint(client, row, system_prompt)
            results.append(res)
            
    # Write to output CSV
    if results:
        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    else:
        print("No results to write.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier (Gemini via google-genai)")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    
    print(f"Starting batch classification from {args.input}")
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
