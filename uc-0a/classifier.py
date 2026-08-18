"""
UC-0A — Complaint Classifier
"""
import argparse
import csv
import json
import os
from google import genai
from pydantic import BaseModel

class ClassificationResult(BaseModel):
    category: str
    priority: str
    reason: str
    flag: str

def get_system_instruction():
    agents_path = os.path.join(os.path.dirname(__file__), 'agents.md')
    with open(agents_path, 'r', encoding='utf-8') as f:
        return f.read()

def classify_complaint(client: genai.Client, row: dict, system_instruction: str) -> dict:
    prompt = f"Please classify the following complaint:\n\nDescription: {row.get('description', '')}"
    
    response = client.models.generate_content(
        model='gemini-3.5-flash-lite',
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.0,
            response_mime_type="application/json",
            response_schema=ClassificationResult
        )
    )
    
    try:
        data = json.loads(response.text)
        return {
            "complaint_id": row.get("complaint_id"),
            "category": data.get("category", "Other"),
            "priority": data.get("priority", "Standard"),
            "reason": data.get("reason", ""),
            "flag": data.get("flag", "")
        }
    except Exception as e:
        return {
            "complaint_id": row.get("complaint_id"),
            "category": "Other",
            "priority": "Standard",
            "reason": "Failed to parse AI output",
            "flag": "NEEDS_REVIEW"
        }

def batch_classify(input_path: str, output_path: str):
    client = genai.Client()
    system_instruction = get_system_instruction()
    
    results = []
    
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("description") or not row.get("description").strip():
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Null or empty description",
                    "flag": "NEEDS_REVIEW"
                })
                continue
            
            res = classify_complaint(client, row, system_instruction)
            results.append(res)
            
            # Free tier API rate limit: 5 requests per minute
            # Wait 13 seconds between requests to avoid RESOURCE_EXHAUSTED errors
            import time
            time.sleep(13)
            
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
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
