import argparse
import csv
import json
import os
import google.generativeai as genai

# Setup Gemini API
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("Warning: GEMINI_API_KEY environment variable not set. Please set it before running.")

# Load RICE configurations mapping
script_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(script_dir, "agents.md"), "r", encoding="utf-8") as f:
    agents_prompt = f.read()

with open(os.path.join(script_dir, "skills.md"), "r", encoding="utf-8") as f:
    skills_prompt = f.read()

SYSTEM_INSTRUCTION = f"{agents_prompt}\n\n{skills_prompt}"

# Initialize the Gemini Model
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=SYSTEM_INSTRUCTION,
    generation_config=genai.types.GenerationConfig(
        response_mime_type="application/json",
        temperature=0.0
    )
)

def classify_complaint(row: dict) -> dict:
    """Classify a single complaint using Gemini constraints."""
    # Build a clean JSON representation of the row logic payload
    payload = json.dumps(row)
    prompt = f"Please classify this complaint row according strictly to the schema rules:\n{payload}"
    
    try:
        response = model.generate_content(prompt)
        result = json.loads(response.text)
        
        # Merge row with results safely
        output = row.copy()
        output["category"] = result.get("category", "Other")
        output["priority"] = result.get("priority", "Standard")
        output["reason"] = result.get("reason", "No reason provided.")
        output["flag"] = result.get("flag", "")
        return output
        
    except Exception as e:
        # Fallback error handling matching skills.md constraints
        output = row.copy()
        output["category"] = "Other"
        output["priority"] = "Standard"
        output["reason"] = f"Error or Ambiguity: {str(e)}"
        output["flag"] = "NEEDS_REVIEW"
        return output

def batch_classify(input_path: str, output_path: str):
    """Read CSV, process rows, write output CSV."""
    with open(input_path, 'r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        fieldnames = list(reader.fieldnames)

    # ensure standard output columns
    for col in ["category", "priority", "reason", "flag"]:
        if col not in fieldnames:
            fieldnames.append(col)

    results = []
    print(f"Processing {len(rows)} complaints from {input_path}")
    for idx, row in enumerate(rows):
        print(f"  Classifying row {idx+1}/{len(rows)}...")
        classified = classify_complaint(row)
        results.append(classified)

    with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    # Validation count
    failed = sum(1 for r in results if r.get('flag') == 'NEEDS_REVIEW')
    print(f"\nDone. {len(results)} total processed. {failed} flagged for review. Results written to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
